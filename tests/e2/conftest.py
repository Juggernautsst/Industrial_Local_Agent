from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src"))

from industrial_local_agent.e2.audit import ContentFreeAuditSink
from industrial_local_agent.e2.crypto import HmacKeyRing, SigningKey
from industrial_local_agent.e2.identity import IdentityTokenAuthority, IdentityTokenVerifier
from industrial_local_agent.e2.policy import SyntheticPolicyStore
from industrial_local_agent.e2.service import E2RetrievalService
from industrial_local_agent.e2.storage import SQLiteForcedScopeAdapter, synthetic_source


@pytest.fixture
def e2_fixture():
    raw = json.loads((ROOT / "fixtures/e2/synthetic_corpus.json").read_text("utf-8"))
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
    policy = SyntheticPolicyStore(
        subject_tenants={item["subject_id"]: item["tenant_id"] for item in raw["users"]},
        project_members={
            item["project_id"]: set(item["members"])
            for item in raw["projects"]
        },
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
    storage = SQLiteForcedScopeAdapter(sources)
    idp_keyring = HmacKeyRing([SigningKey("idp-key-1", b"synthetic-idp-secret")])
    authority = IdentityTokenAuthority(idp_keyring)
    verifier = IdentityTokenVerifier(idp_keyring)
    delegation_keyring = HmacKeyRing([SigningKey("delegation-key-1", b"synthetic-delegation-secret")])
    bundle_keyring = HmacKeyRing([SigningKey("bundle-key-1", b"synthetic-bundle-secret")])
    audit_keyring = HmacKeyRing([SigningKey("audit-key-1", b"synthetic-audit-secret")])
    audit = ContentFreeAuditSink(audit_keyring)
    service = E2RetrievalService(
        policy=policy,
        storage=storage,
        token_verifier=verifier,
        delegation_keyring=delegation_keyring,
        bundle_keyring=bundle_keyring,
        audit_sink=audit,
        clock=lambda: 1_700_000_000,
    )
    return {
        "raw": raw,
        "policy": policy,
        "storage": storage,
        "authority": authority,
        "verifier": verifier,
        "delegation_keyring": delegation_keyring,
        "bundle_keyring": bundle_keyring,
        "audit": audit,
        "service": service,
        "now": 1_700_000_000,
    }
