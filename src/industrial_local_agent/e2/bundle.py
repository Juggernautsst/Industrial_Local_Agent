from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any

from .crypto import HmacKeyRing, canonical_bytes, sha256_hex
from .errors import BundleVerificationError
from .identity import DelegatedIdentityContext
from .storage import StoredSource


BUNDLE_DOMAIN = "industrial-local-agent/e2/authorized-evidence-bundle/v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _sha256_text(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_id: str
    source_version: int
    locator: str
    content: str
    content_hash: str
    classification: str
    decision_id: str

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "source_version": self.source_version,
            "locator": self.locator,
            "content": self.content,
            "content_hash": self.content_hash,
            "classification": self.classification,
            "decision_id": self.decision_id,
        }


@dataclass(frozen=True)
class AuthorizedEvidenceBundle:
    schema_version: str
    bundle_id: str
    request_id: str
    delegation_id: str
    subject_id: str
    tenant_id: str
    audience: str
    purpose_of_use: str
    policy_version: int
    issued_at: int
    expires_at: int
    key_id: str
    retrieval_method: str
    query_fingerprint: str
    evidence: tuple[EvidenceItem, ...]
    signature: str

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "bundle_id": self.bundle_id,
            "request_id": self.request_id,
            "delegation_id": self.delegation_id,
            "subject_id": self.subject_id,
            "tenant_id": self.tenant_id,
            "audience": self.audience,
            "purpose_of_use": self.purpose_of_use,
            "policy_version": self.policy_version,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "key_id": self.key_id,
            "retrieval_method": self.retrieval_method,
            "query_fingerprint": self.query_fingerprint,
            "evidence": [item.to_dict() for item in self.evidence],
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self.unsigned_payload()
        payload["signature"] = self.signature
        return payload

    @classmethod
    def create(
        cls,
        context: DelegatedIdentityContext,
        sources: list[tuple[StoredSource, str]],
        *,
        query: str,
        keyring: HmacKeyRing,
        key_id: str,
        now: int,
        ttl_seconds: int = 30,
    ) -> "AuthorizedEvidenceBundle":
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or ttl_seconds <= 0:
            raise ValueError("Bundle TTL must be a positive integer.")
        evidence = tuple(
            EvidenceItem(
                evidence_id=f"E2-{index:04d}",
                source_id=source.source_id,
                source_version=source.source_version,
                locator="synthetic://source/paragraph/1",
                content=source.content,
                content_hash=source.content_hash,
                classification=source.classification,
                decision_id=decision_id,
            )
            for index, (source, decision_id) in enumerate(sources, start=1)
        )
        unsigned = {
            "schema_version": "e2-bundle.v1",
            "bundle_id": uuid.uuid4().hex,
            "request_id": context.request_id,
            "delegation_id": context.delegation_id,
            "subject_id": context.subject_id,
            "tenant_id": context.tenant_id,
            "audience": context.audience,
            "purpose_of_use": context.purpose_of_use,
            "policy_version": context.policy_version,
            "issued_at": now,
            "expires_at": now + ttl_seconds,
            "key_id": key_id,
            "retrieval_method": "synthetic-sql-forced-scope-lexical",
            "query_fingerprint": sha256_hex(query),
            "evidence": [item.to_dict() for item in evidence],
        }
        signature = keyring.sign(key_id, BUNDLE_DOMAIN, canonical_bytes(unsigned))
        return cls(signature=signature, evidence=evidence, **{key: value for key, value in unsigned.items() if key != "evidence"})

    def verify(
        self,
        keyring: HmacKeyRing,
        context: DelegatedIdentityContext,
        *,
        expected_audience: str,
        now: int,
        max_evidence: int = 20,
    ) -> None:
        if self.schema_version != "e2-bundle.v1":
            raise BundleVerificationError("Bundle schema version is not supported.")
        if not isinstance(context, DelegatedIdentityContext):
            raise BundleVerificationError("Bundle delegation context type is invalid.")
        if not all(
            _nonempty_text(getattr(self, field))
            for field in (
                "bundle_id",
                "request_id",
                "delegation_id",
                "subject_id",
                "tenant_id",
                "audience",
                "purpose_of_use",
                "key_id",
                "retrieval_method",
                "signature",
            )
        ):
            raise BundleVerificationError("Bundle contains an invalid text field.")
        if not _positive_int(self.policy_version):
            raise BundleVerificationError("Bundle policy version is invalid.")
        if not isinstance(self.issued_at, int) or isinstance(self.issued_at, bool):
            raise BundleVerificationError("Bundle issue time is invalid.")
        if not isinstance(self.expires_at, int) or isinstance(self.expires_at, bool):
            raise BundleVerificationError("Bundle expiry time is invalid.")
        if not _sha256_text(self.query_fingerprint):
            raise BundleVerificationError("Bundle query fingerprint is invalid.")
        if self.audience != expected_audience or self.audience != context.audience:
            raise BundleVerificationError("Bundle audience binding is invalid.")
        for field in ("request_id", "delegation_id", "subject_id", "tenant_id", "purpose_of_use"):
            if getattr(self, field) != getattr(context, field):
                raise BundleVerificationError(f"Bundle {field} binding is invalid.")
        if self.policy_version != context.policy_version:
            raise BundleVerificationError("Bundle policy version is stale.")
        if self.expires_at <= self.issued_at or self.expires_at <= now:
            raise BundleVerificationError("Bundle is expired.")
        if (
            not isinstance(self.evidence, tuple)
            or not isinstance(max_evidence, int)
            or isinstance(max_evidence, bool)
            or max_evidence < 0
        ):
            raise BundleVerificationError("Bundle evidence container is invalid.")
        if len(self.evidence) > max_evidence:
            raise BundleVerificationError("Bundle exceeds its evidence bound.")
        evidence_ids: set[str] = set()
        source_ids: set[str] = set()
        for item in self.evidence:
            if not isinstance(item, EvidenceItem):
                raise BundleVerificationError("Bundle evidence item type is invalid.")
            if not all(
                _nonempty_text(getattr(item, field))
                for field in ("evidence_id", "source_id", "locator", "content", "classification", "decision_id")
            ):
                raise BundleVerificationError("Bundle evidence text field is invalid.")
            if not _positive_int(item.source_version) or not _sha256_text(item.content_hash):
                raise BundleVerificationError("Bundle evidence version or hash is invalid.")
            if item.evidence_id in evidence_ids or item.source_id in source_ids:
                raise BundleVerificationError("Bundle contains duplicate evidence or source IDs.")
            evidence_ids.add(item.evidence_id)
            source_ids.add(item.source_id)
            if sha256_hex(item.content) != item.content_hash:
                raise BundleVerificationError("Bundle content hash does not match content.")
            if not item.decision_id or not item.locator:
                raise BundleVerificationError("Bundle evidence locator or decision is missing.")
        try:
            keyring.verify(
                self.key_id,
                BUNDLE_DOMAIN,
                canonical_bytes(self.unsigned_payload()),
                self.signature,
            )
        except Exception as exc:
            raise BundleVerificationError("Bundle signature is invalid.") from exc
