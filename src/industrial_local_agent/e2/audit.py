from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass
from typing import Mapping

from .crypto import HmacKeyRing, canonical_bytes
from .errors import AuditError, AuditUnavailable


AUDIT_DOMAIN = "industrial-local-agent/e2/audit-event/v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class AuditReceipt:
    event_id: str
    sequence: int
    previous_hash: str
    event_hash: str
    key_id: str
    signature: str


class ContentFreeAuditSink:
    """Hash-chain audit sink that rejects content-bearing event fields."""

    ALLOWED_KEYS = {
        "event_type",
        "request_id",
        "delegation_id",
        "subject_id",
        "tenant_id",
        "policy_version",
        "decision_ids",
        "source_ids",
        "source_hashes",
        "bundle_id",
        "outcome",
    }

    def __init__(self, keyring: HmacKeyRing, *, key_id: str = "audit-key-1") -> None:
        self.keyring = keyring
        self.key_id = key_id
        self.available = True
        self._events: list[tuple[dict[str, object], AuditReceipt]] = []

    @classmethod
    def _validate_event(cls, event: Mapping[str, object]) -> None:
        if set(event) - cls.ALLOWED_KEYS:
            raise AuditError("Audit event contains a forbidden content-bearing field.")
        for field in ("event_type", "request_id", "tenant_id"):
            if not isinstance(event.get(field), str) or not event[field]:
                raise AuditError("Audit event is missing required identity fields.")
        for field in ("delegation_id", "subject_id", "bundle_id", "outcome"):
            if field in event and (not isinstance(event[field], str) or not event[field]):
                raise AuditError("Audit event contains an invalid identity field.")
        if "policy_version" in event and (
            not isinstance(event["policy_version"], int)
            or isinstance(event["policy_version"], bool)
            or event["policy_version"] <= 0
        ):
            raise AuditError("Audit event policy version is invalid.")
        for field in ("decision_ids", "source_ids", "source_hashes"):
            if field not in event:
                continue
            values = event[field]
            if not isinstance(values, (list, tuple)) or not all(isinstance(value, str) and value for value in values):
                raise AuditError("Audit event contains an invalid identifier list.")
            if field == "source_hashes" and not all(_SHA256_RE.fullmatch(value) for value in values):
                raise AuditError("Audit event contains an invalid source hash.")

    def append(self, event: Mapping[str, object], *, now: int | None = None) -> AuditReceipt:
        if not self.available:
            raise AuditUnavailable("Audit sink is unavailable.")
        self._validate_event(event)
        sequence = len(self._events) + 1
        previous_hash = self._events[-1][1].event_hash if self._events else "0" * 64
        body = {
            "sequence": sequence,
            "previous_hash": previous_hash,
            "timestamp": int(time.time()) if now is None else now,
            **dict(event),
        }
        event_hash = hashlib.sha256(canonical_bytes(body)).hexdigest()
        signature = self.keyring.sign(
            self.key_id,
            AUDIT_DOMAIN,
            canonical_bytes({"event_hash": event_hash, "sequence": sequence}),
        )
        receipt = AuditReceipt(
            event_id=uuid.uuid4().hex,
            sequence=sequence,
            previous_hash=previous_hash,
            event_hash=event_hash,
            key_id=self.key_id,
            signature=signature,
        )
        self._events.append((body, receipt))
        return receipt

    @property
    def events(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(event) for event, _receipt in self._events)

    @property
    def receipts(self) -> tuple[AuditReceipt, ...]:
        return tuple(receipt for _event, receipt in self._events)

    def verify_chain(self) -> None:
        """Verify event ordering, hash links, and receipt signatures."""

        previous_hash = "0" * 64
        structural_keys = {"sequence", "previous_hash", "timestamp"}
        for expected_sequence, (event, receipt) in enumerate(self._events, start=1):
            payload = {key: value for key, value in event.items() if key not in structural_keys}
            self._validate_event(payload)
            if receipt.sequence != expected_sequence or event.get("sequence") != expected_sequence:
                raise AuditError("Audit event sequence is invalid.")
            if event.get("previous_hash") != previous_hash or receipt.previous_hash != previous_hash:
                raise AuditError("Audit hash-chain link is invalid.")
            event_hash = hashlib.sha256(canonical_bytes(event)).hexdigest()
            if event_hash != receipt.event_hash:
                raise AuditError("Audit event hash is invalid.")
            try:
                self.keyring.verify(
                    receipt.key_id,
                    AUDIT_DOMAIN,
                    canonical_bytes({"event_hash": event_hash, "sequence": expected_sequence}),
                    receipt.signature,
                )
            except Exception as exc:
                raise AuditError("Audit receipt signature is invalid.") from exc
            previous_hash = event_hash
