from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from .audit import ContentFreeAuditSink
from .crypto import HmacKeyRing, SigningKey
from .identity import IdentityTokenAuthority, IdentityTokenVerifier
from .policy import SyntheticPolicyStore
from .service import E2RetrievalService, RetrievalResponse
from .storage import SQLiteForcedScopeAdapter, synthetic_source


DEMO_NOW = 1_700_000_000


class DemoRuntime:
    """One isolated, synthetic E2 runtime shared by CLI and Web demos."""

    def __init__(self, fixture_path: Path) -> None:
        raw = json.loads(fixture_path.read_text("utf-8"))
        sources = [
            synthetic_source(
                item["source_id"],
                item["tenant_id"],
                item["project_id"],
                item["owner_id"],
                item["content"],
            )
            for item in raw["sources"]
        ]
        self.users = tuple(
            {
                "subject_id": item["subject_id"],
                "tenant_id": item["tenant_id"],
                "role": item["role"],
            }
            for item in raw["users"]
        )
        self.sources = tuple(
            {
                "source_id": item["source_id"],
                "tenant_id": item["tenant_id"],
                "project_id": item["project_id"],
                "owner_id": item["owner_id"],
                "classification": "internal",
            }
            for item in raw["sources"]
        )
        self.policy = SyntheticPolicyStore(
            subject_tenants={item["subject_id"]: item["tenant_id"] for item in raw["users"]},
            project_members={item["project_id"]: set(item["members"]) for item in raw["projects"]},
            project_tenants={item["project_id"]: item["tenant_id"] for item in raw["projects"]},
            source_records={
                item["source_id"]: (
                    item["tenant_id"],
                    item["project_id"],
                    item["owner_id"],
                    "internal",
                )
                for item in raw["sources"]
            },
        )
        self.storage = SQLiteForcedScopeAdapter(sources)
        idp_keys = HmacKeyRing([SigningKey("idp-key-1", b"demo-idp-secret")])
        delegation_keys = HmacKeyRing([SigningKey("delegation-key-1", b"demo-delegation-secret")])
        bundle_keys = HmacKeyRing([SigningKey("bundle-key-1", b"demo-bundle-secret")])
        audit_keys = HmacKeyRing([SigningKey("audit-key-1", b"demo-audit-secret")])
        self.authority = IdentityTokenAuthority(idp_keys)
        self.verifier = IdentityTokenVerifier(idp_keys)
        self.audit = ContentFreeAuditSink(audit_keys)
        self.bundle_keys = bundle_keys
        self.service = E2RetrievalService(
            policy=self.policy,
            storage=self.storage,
            token_verifier=self.verifier,
            delegation_keyring=delegation_keys,
            bundle_keyring=bundle_keys,
            audit_sink=self.audit,
            clock=lambda: DEMO_NOW,
        )
        self.request_number = 0

    def token(self, subject_id: str) -> str:
        return self.authority.issue(subject_id, now=DEMO_NOW)

    def retrieve(self, subject_id: str, query: str, label: str) -> RetrievalResponse:
        self.request_number += 1
        request_id = f"demo-{label}-{self.request_number}"
        return self.service.retrieve(
            self.token(subject_id),
            request_id=request_id,
            query=query,
        )

    def context_for(self, subject_id: str, request_id: str, delegation_id: str):
        identity = self.verifier.verify(self.token(subject_id), now=DEMO_NOW)
        context = self.service._delegator.delegate(
            identity,
            request_id=request_id,
            purpose_of_use="research-retrieval",
            now=DEMO_NOW,
        )
        return dataclasses.replace(context, delegation_id=delegation_id)

    def public_state(self) -> dict[str, Any]:
        return {
            "users": list(self.users),
            "sources": list(self.sources),
            "policy_version": self.policy.version,
            "source_a2_shared_with_alice": "user-alice" in self.policy.source_shares.get("source-a2", set()),
            "audit_event_count": len(self.audit.events),
            "synthetic_only": True,
            "model_connected": False,
        }

    def close(self) -> None:
        self.storage.close()
