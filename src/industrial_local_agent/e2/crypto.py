from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from .errors import IdentityError


def canonical_bytes(value: Any) -> bytes:
    """Serialize one protocol value without ambiguous whitespace or ordering."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: bytes | str) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def b64u_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def b64u_decode(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise IdentityError("Encoded value is empty.")
    if any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for character in value):
        raise IdentityError("Encoded value contains invalid characters.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except ValueError as exc:
        raise IdentityError("Encoded value is malformed.") from exc


@dataclass(frozen=True)
class SigningKey:
    key_id: str
    secret: bytes
    active: bool = True


class HmacKeyRing:
    """Small synthetic key registry with explicit revocation semantics.

    HMAC is used only to make the contract executable without a third-party
    dependency. Production deployment must use institution-approved asymmetric
    signing and key custody.
    """

    def __init__(self, keys: list[SigningKey] | None = None) -> None:
        self._keys = {key.key_id: key for key in keys or []}

    def add(self, key: SigningKey) -> None:
        if not key.key_id or not key.secret:
            raise ValueError("Signing keys require a key ID and secret.")
        self._keys[key.key_id] = key

    def revoke(self, key_id: str) -> None:
        key = self._keys.get(key_id)
        if key is None:
            raise KeyError(key_id)
        self._keys[key_id] = SigningKey(key.key_id, key.secret, active=False)

    def sign(self, key_id: str, domain: str, payload: bytes) -> str:
        key = self._keys.get(key_id)
        if key is None or not key.active:
            raise IdentityError(f"Signing key {key_id!r} is not active.")
        message = domain.encode("utf-8") + b"\0" + payload
        return b64u_encode(hmac.new(key.secret, message, hashlib.sha256).digest())

    def verify(self, key_id: str, domain: str, payload: bytes, signature: str) -> None:
        key = self._keys.get(key_id)
        if key is None or not key.active:
            raise IdentityError(f"Signing key {key_id!r} is unknown or revoked.")
        expected = self.sign(key_id, domain, payload)
        if not isinstance(signature, str) or not hmac.compare_digest(expected, signature):
            raise IdentityError("Signature verification failed.")

    def contains(self, key_id: str) -> bool:
        return key_id in self._keys
