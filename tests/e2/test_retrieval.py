from __future__ import annotations

import dataclasses

import pytest

from industrial_local_agent.e2.errors import (
    AuditError,
    AuditUnavailable,
    AuthorizationDenied,
    BundleVerificationError,
    IdentityError,
    PolicyUnavailable,
)


def token_for(e2_fixture, subject: str):
    return e2_fixture["authority"].issue(subject, now=e2_fixture["now"])


def test_same_tenant_project_access_and_forced_scope(e2_fixture):
    response = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-a1",
        query="waveguide transmission",
    )
    assert [item.source_id for item in response.bundle.evidence] == ["source-a1"]
    assert response.bundle.tenant_id == "tenant-a"
    assert response.bundle.subject_id == "user-alice"
    assert response.bundle.audience == "e2-retrieval"
    assert response.bundle.signature
    assert len(e2_fixture["audit"].events) == 1
    assert "content" not in e2_fixture["audit"].events[0]


def test_cross_tenant_isolation_and_client_claim_rejection(e2_fixture):
    response = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-carol"),
        request_id="req-b1",
        query="control result",
    )
    assert [item.source_id for item in response.bundle.evidence] == ["source-b1"]
    with pytest.raises(IdentityError, match="claims"):
        e2_fixture["service"].retrieve(
            token_for(e2_fixture, "user-alice"),
            request_id="req-a2",
            query="control result",
            client_claims={"tenant_id": "tenant-b", "role": "admin"},
        )


def test_same_tenant_explicit_share_and_revoke_invalidate_context(e2_fixture):
    before = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-share-before",
        query="linewidth reviewer",
    )
    assert before.bundle.evidence == ()
    e2_fixture["policy"].share_source("source-a2", "user-alice")
    shared = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-share-after",
        query="linewidth reviewer",
    )
    assert [item.source_id for item in shared.bundle.evidence] == ["source-a2"]
    e2_fixture["policy"].revoke_share("source-a2", "user-alice")
    revoked = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-share-revoked",
        query="linewidth reviewer",
    )
    assert revoked.bundle.evidence == ()
    assert revoked.bundle.policy_version > shared.bundle.policy_version


def test_source_is_reauthorized_after_candidate_selection(e2_fixture, monkeypatch):
    policy = e2_fixture["policy"]
    original_authorize = policy.authorize_source

    def mutate_acl_before_reauthorization(subject_id, tenant_id, source_id, *, expected_policy_version):
        # Simulate an ACL update after storage returned the candidate source.
        if source_id == "source-a1":
            policy.source_records[source_id] = ("tenant-a", "project-a2", "user-bob", "internal")
        return original_authorize(
            subject_id,
            tenant_id,
            source_id,
            expected_policy_version=expected_policy_version,
        )

    monkeypatch.setattr(policy, "authorize_source", mutate_acl_before_reauthorization)
    with pytest.raises(AuthorizationDenied, match="authorization changed"):
        e2_fixture["service"].retrieve(
            token_for(e2_fixture, "user-alice"),
            request_id="req-source-race",
            query="waveguide",
        )
    assert e2_fixture["audit"].events == ()


def test_bundle_mutation_wrong_audience_expiry_and_revoked_key_fail(e2_fixture):
    response = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-bundle-negative",
        query="waveguide",
    )
    bundle = response.bundle
    verified_token = e2_fixture["verifier"].verify(
        token_for(e2_fixture, "user-alice"), now=e2_fixture["now"]
    )
    context = e2_fixture["service"]._delegator.delegate(
        verified_token,
        request_id="req-bundle-negative",
        purpose_of_use="research-retrieval",
        now=e2_fixture["now"],
    )
    context = dataclasses.replace(context, delegation_id=bundle.delegation_id)
    with pytest.raises(BundleVerificationError):
        bundle.verify(e2_fixture["bundle_keyring"], dataclasses.replace(context, request_id="other"), expected_audience="e2-retrieval", now=e2_fixture["now"])
    with pytest.raises(BundleVerificationError):
        bundle.verify(e2_fixture["bundle_keyring"], context, expected_audience="wrong-audience", now=e2_fixture["now"])
    with pytest.raises(BundleVerificationError, match="expired"):
        bundle.verify(e2_fixture["bundle_keyring"], context, expected_audience="e2-retrieval", now=e2_fixture["now"] + 31)
    with pytest.raises(BundleVerificationError):
        bundle.verify(
            e2_fixture["bundle_keyring"],
            context,
            expected_audience="e2-retrieval",
            now=e2_fixture["now"],
            max_evidence=0,
        )
    unknown_key = dataclasses.replace(bundle, key_id="unknown-key")
    with pytest.raises(BundleVerificationError):
        unknown_key.verify(e2_fixture["bundle_keyring"], context, expected_audience="e2-retrieval", now=e2_fixture["now"])
    downgraded = dataclasses.replace(bundle, schema_version="e2-bundle.v0")
    with pytest.raises(BundleVerificationError):
        downgraded.verify(e2_fixture["bundle_keyring"], context, expected_audience="e2-retrieval", now=e2_fixture["now"])
    tampered = dataclasses.replace(bundle, evidence=(dataclasses.replace(bundle.evidence[0], content="tampered"),))
    with pytest.raises(BundleVerificationError):
        tampered.verify(e2_fixture["bundle_keyring"], context, expected_audience="e2-retrieval", now=e2_fixture["now"])
    e2_fixture["bundle_keyring"].revoke("bundle-key-1")
    with pytest.raises(BundleVerificationError):
        bundle.verify(e2_fixture["bundle_keyring"], context, expected_audience="e2-retrieval", now=e2_fixture["now"])


def test_policy_outage_and_audit_failure_fail_closed(e2_fixture):
    e2_fixture["policy"].available = False
    with pytest.raises(PolicyUnavailable):
        e2_fixture["service"].retrieve(token_for(e2_fixture, "user-alice"), request_id="req-policy-down", query="waveguide")

    e2_fixture["policy"].available = True
    e2_fixture["audit"].available = False
    with pytest.raises(AuditUnavailable):
        e2_fixture["service"].retrieve(token_for(e2_fixture, "user-alice"), request_id="req-audit-down", query="waveguide")


def test_request_replay_is_rejected_and_cache_is_tenant_scoped(e2_fixture):
    service = e2_fixture["service"]
    first = service.retrieve(token_for(e2_fixture, "user-alice"), request_id="req-replay", query="waveguide")
    with pytest.raises(IdentityError, match="replay"):
        service.retrieve(token_for(e2_fixture, "user-alice"), request_id="req-replay", query="waveguide")
    second = service.retrieve(token_for(e2_fixture, "user-alice"), request_id="req-cache", query="waveguide")
    assert first.bundle.evidence[0].source_id == second.bundle.evidence[0].source_id
    assert second.bundle.tenant_id == "tenant-a"
    other_tenant = service.retrieve(token_for(e2_fixture, "user-carol"), request_id="req-cache-b", query="control result")
    assert other_tenant.bundle.tenant_id == "tenant-b"
    assert [item.source_id for item in other_tenant.bundle.evidence] == ["source-b1"]


def test_audit_is_content_free_and_hash_chained(e2_fixture):
    response = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-audit-chain-1",
        query="waveguide",
    )
    second = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-audit-chain-2",
        query="waveguide",
    )
    assert response.audit_receipt_event_id != second.audit_receipt_event_id
    receipts = e2_fixture["audit"].receipts
    assert receipts[0].previous_hash == "0" * 64
    assert receipts[1].previous_hash == receipts[0].event_hash
    assert all("content" not in event and "prompt" not in event for event in e2_fixture["audit"].events)
    e2_fixture["audit"].verify_chain()


def test_audit_chain_detects_event_mutation(e2_fixture):
    e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-audit-tamper",
        query="waveguide",
    )
    e2_fixture["audit"]._events[0][0]["tenant_id"] = "tenant-b"
    with pytest.raises(AuditError, match="hash"):
        e2_fixture["audit"].verify_chain()


def test_audit_rejects_nested_content_and_invalid_hash_values(e2_fixture):
    with pytest.raises(AuditError, match="identifier list"):
        e2_fixture["audit"].append(
            {
                "event_type": "authorized-retrieval",
                "request_id": "req-audit-content",
                "tenant_id": "tenant-a",
                "source_ids": [{"content": "secret"}],
            }
        )
    with pytest.raises(AuditError, match="source hash"):
        e2_fixture["audit"].append(
            {
                "event_type": "authorized-retrieval",
                "request_id": "req-audit-hash",
                "tenant_id": "tenant-a",
                "source_hashes": ["not-a-digest"],
            }
        )


def test_forced_scope_is_parameterized_and_tenant_bound(e2_fixture):
    handle = e2_fixture["storage"].issue_forced_scope(
        tenant_id="tenant-a",
        subject_id="user-alice",
        policy_version=1,
        source_ids=frozenset({"source-a1", "source-b1"}),
    )
    sources = e2_fixture["storage"].retrieve(
        handle,
        "waveguide' OR source-b1",
    )
    assert [source.source_id for source in sources] == ["source-a1"]


def test_bundle_schema_and_type_downgrades_fail_closed(e2_fixture):
    response = e2_fixture["service"].retrieve(
        token_for(e2_fixture, "user-alice"),
        request_id="req-schema-types",
        query="waveguide",
    )
    bundle = response.bundle
    context = e2_fixture["service"]._delegator.delegate(
        e2_fixture["verifier"].verify(token_for(e2_fixture, "user-alice"), now=e2_fixture["now"]),
        request_id="req-schema-types",
        purpose_of_use="research-retrieval",
        now=e2_fixture["now"],
    )
    for mutation in (
        dataclasses.replace(bundle, policy_version=True),
        dataclasses.replace(bundle, query_fingerprint="not-a-sha256"),
        dataclasses.replace(bundle, query_fingerprint=None),
        dataclasses.replace(bundle, evidence=[*bundle.evidence]),
        dataclasses.replace(bundle, evidence=(dataclasses.replace(bundle.evidence[0], source_version=0),)),
        dataclasses.replace(bundle, evidence=(dataclasses.replace(bundle.evidence[0], content_hash=None),)),
    ):
        with pytest.raises(BundleVerificationError):
            mutation.verify(
                e2_fixture["bundle_keyring"],
                context,
                expected_audience="e2-retrieval",
                now=e2_fixture["now"],
            )


def test_retrieval_path_has_no_model_or_tool_dependency(e2_fixture):
    import sys

    before = {name for name in sys.modules if name == "ollama" or name.startswith("tidy3d") or name.startswith("mcp")}
    e2_fixture["service"].retrieve(token_for(e2_fixture, "user-alice"), request_id="req-model-free", query="waveguide")
    after = {name for name in sys.modules if name == "ollama" or name.startswith("tidy3d") or name.startswith("mcp")}
    assert after == before
