from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass
from typing import Callable, Mapping

from .crypto import HmacKeyRing, SigningKey, b64u_decode, b64u_encode, canonical_bytes
from .errors import IdentityError, PolicyError


TOKEN_DOMAIN = "industrial-local-agent/e2/mock-id-token/v1"
DELEGATION_DOMAIN = "industrial-local-agent/e2/delegated-context/v1"
SUPPORTED_TOKEN_ALGORITHM = "HS256-SYNTHETIC"


def _now() -> int:
    return int(time.time())


@dataclass(frozen=True)
class VerifiedIdentity:
    subject_id: str
    issuer: str
    token_id: str
    authentication_time: int
    assurance_level: str


class IdentityTokenAuthority:
    """Synthetic issuer used by tests; it is not an OIDC implementation."""

    def __init__(
        self,
        keyring: HmacKeyRing | None = None,
        issuer: str = "synthetic-idp",
        key_id: str = "idp-key-1",
    ) -> None:
        self.keyring = keyring or HmacKeyRing([SigningKey(key_id, b"synthetic-idp-secret")])
        self.issuer = issuer
        self.key_id = key_id

    def issue(
        self,
        subject_id: str,
        *,
        audience: str = "industrial-local-agent",
        expires_in: int = 300,
        now: int | None = None,
        extra_claims: Mapping[str, object] | None = None,
    ) -> str:
        if not subject_id or not audience or expires_in <= 0:
            raise ValueError("Synthetic token requires subject, audience, and positive TTL.")
        issued_at = _now() if now is None else now
        payload: dict[str, object] = {
            "iss": self.issuer,
            "sub": subject_id,
            "aud": audience,
            "iat": issued_at,
            "exp": issued_at + expires_in,
            "jti": secrets.token_hex(16),
            "auth_time": issued_at,
            "acr": "synthetic-mfa",
        }
        if extra_claims:
            payload.update(extra_claims)
        header = {"alg": SUPPORTED_TOKEN_ALGORITHM, "kid": self.key_id, "typ": "JWT"}
        encoded_header = b64u_encode(canonical_bytes(header))
        encoded_payload = b64u_encode(canonical_bytes(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = self.keyring.sign(self.key_id, TOKEN_DOMAIN, signing_input)
        return f"{encoded_header}.{encoded_payload}.{signature}"


class IdentityTokenVerifier:
    def __init__(
        self,
        keyring: HmacKeyRing,
        *,
        issuer: str = "synthetic-idp",
        audience: str = "industrial-local-agent",
        clock_skew_seconds: int = 5,
    ) -> None:
        self.keyring = keyring
        self.issuer = issuer
        self.audience = audience
        self.clock_skew_seconds = clock_skew_seconds
        self._revoked_tokens: set[str] = set()

    def revoke_token(self, token_id: str) -> None:
        self._revoked_tokens.add(token_id)

    def verify(self, token: str, *, now: int | None = None) -> VerifiedIdentity:
        if not isinstance(token, str) or token.count(".") != 2:
            raise IdentityError("Identity token must contain three segments.")
        encoded_header, encoded_payload, signature = token.split(".")
        try:
            header = json.loads(b64u_decode(encoded_header))
            payload = json.loads(b64u_decode(encoded_payload))
        except (IdentityError, json.JSONDecodeError) as exc:
            raise IdentityError("Identity token JSON is malformed.") from exc
        if not isinstance(header, dict) or header.get("alg") != SUPPORTED_TOKEN_ALGORITHM:
            raise IdentityError("Identity token algorithm is not allowed.")
        key_id = header.get("kid")
        if not isinstance(key_id, str):
            raise IdentityError("Identity token key ID is missing.")
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        try:
            self.keyring.verify(key_id, TOKEN_DOMAIN, signing_input, signature)
        except IdentityError as exc:
            raise IdentityError("Identity token signature is invalid.") from exc
        if not isinstance(payload, dict):
            raise IdentityError("Identity token payload is not an object.")
        required = {"iss", "sub", "aud", "iat", "exp", "jti", "auth_time", "acr"}
        if not required.issubset(payload):
            raise IdentityError("Identity token is missing required claims.")
        if payload["iss"] != self.issuer or payload["aud"] != self.audience:
            raise IdentityError("Identity token issuer or audience is not trusted.")
        if not isinstance(payload["sub"], str) or not payload["sub"]:
            raise IdentityError("Identity token subject is invalid.")
        if not all(isinstance(payload[name], int) for name in ("iat", "exp", "auth_time")):
            raise IdentityError("Identity token time claims are invalid.")
        current = _now() if now is None else now
        if payload["iat"] > current + self.clock_skew_seconds:
            raise IdentityError("Identity token is not yet valid.")
        if payload["exp"] <= current - self.clock_skew_seconds:
            raise IdentityError("Identity token is expired.")
        token_id = payload["jti"]
        if not isinstance(token_id, str) or token_id in self._revoked_tokens:
            raise IdentityError("Identity token is revoked or invalid.")
        assurance = payload["acr"]
        if not isinstance(assurance, str) or not assurance:
            raise IdentityError("Identity assurance claim is invalid.")
        return VerifiedIdentity(
            subject_id=payload["sub"],
            issuer=payload["iss"],
            token_id=token_id,
            authentication_time=payload["auth_time"],
            assurance_level=assurance,
        )


@dataclass(frozen=True)
class DelegatedIdentityContext:
    schema_version: str
    delegation_id: str
    request_id: str
    subject_id: str
    tenant_id: str
    issuer: str
    audience: str
    authentication_time: int
    assurance_level: str
    authorization_snapshot_id: str
    policy_version: int
    purpose_of_use: str
    issued_at: int
    expires_at: int
    key_id: str
    signature: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "delegation_id": self.delegation_id,
            "request_id": self.request_id,
            "subject_id": self.subject_id,
            "tenant_id": self.tenant_id,
            "issuer": self.issuer,
            "audience": self.audience,
            "authentication_time": self.authentication_time,
            "assurance_level": self.assurance_level,
            "authorization_snapshot_id": self.authorization_snapshot_id,
            "policy_version": self.policy_version,
            "purpose_of_use": self.purpose_of_use,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "key_id": self.key_id,
        }

    def to_dict(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["signature"] = self.signature
        return payload

    def verify(
        self,
        keyring: HmacKeyRing,
        *,
        expected_audience: str,
        now: int,
    ) -> None:
        if self.schema_version != "e2-delegation.v1":
            raise IdentityError("Delegated identity schema version is not supported.")
        if self.audience != expected_audience or not self.tenant_id or not self.subject_id:
            raise IdentityError("Delegated identity audience or subject binding is invalid.")
        if self.expires_at <= self.issued_at or self.expires_at <= now or self.issued_at > now + 5:
            raise IdentityError("Delegated identity is expired or not yet valid.")
        try:
            keyring.verify(
                self.key_id,
                DELEGATION_DOMAIN,
                canonical_bytes(self.unsigned_payload()),
                self.signature,
            )
        except IdentityError as exc:
            raise IdentityError("Delegated identity signature is invalid.") from exc


class IdentityDelegator:
    def __init__(
        self,
        keyring: HmacKeyRing | None = None,
        *,
        audience: str = "e2-retrieval",
        key_id: str = "delegation-key-1",
        ttl_seconds: int = 60,
        resolve_tenant: Callable[[str], str | None],
        policy_version: Callable[[], int],
    ) -> None:
        self.keyring = keyring or HmacKeyRing([SigningKey(key_id, b"synthetic-delegation-secret")])
        self.audience = audience
        self.key_id = key_id
        self.ttl_seconds = ttl_seconds
        self.resolve_tenant = resolve_tenant
        self.policy_version = policy_version

    def delegate(
        self,
        identity: VerifiedIdentity,
        *,
        request_id: str,
        purpose_of_use: str,
        now: int | None = None,
    ) -> DelegatedIdentityContext:
        if not request_id or purpose_of_use not in {"research-retrieval", "research-chat-context"}:
            raise PolicyError("Delegation request or purpose is not allowed.")
        tenant_id = self.resolve_tenant(identity.subject_id)
        if not tenant_id:
            raise PolicyError("No server-side tenant mapping exists for this subject.")
        issued_at = _now() if now is None else now
        policy_version = self.policy_version()
        unsigned = {
            "schema_version": "e2-delegation.v1",
            "delegation_id": secrets.token_hex(16),
            "request_id": request_id,
            "subject_id": identity.subject_id,
            "tenant_id": tenant_id,
            "issuer": identity.issuer,
            "audience": self.audience,
            "authentication_time": identity.authentication_time,
            "assurance_level": identity.assurance_level,
            "authorization_snapshot_id": f"synthetic-policy-{policy_version}",
            "policy_version": policy_version,
            "purpose_of_use": purpose_of_use,
            "issued_at": issued_at,
            "expires_at": issued_at + self.ttl_seconds,
            "key_id": self.key_id,
        }
        signature = self.keyring.sign(self.key_id, DELEGATION_DOMAIN, canonical_bytes(unsigned))
        return DelegatedIdentityContext(signature=signature, **unsigned)
