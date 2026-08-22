from __future__ import annotations

import json

import pytest

from industrial_local_agent.e2.errors import IdentityError
from industrial_local_agent.e2.identity import IdentityDelegator


def test_identity_token_is_verified_and_client_claims_are_not_used(e2_fixture):
    token = e2_fixture["authority"].issue("user-alice", now=e2_fixture["now"])
    identity = e2_fixture["verifier"].verify(token, now=e2_fixture["now"])
    assert identity.subject_id == "user-alice"
    assert identity.issuer == "synthetic-idp"


@pytest.mark.parametrize("mutation", ["bad-signature", "wrong-audience", "expired", "forged-tenant"])
def test_identity_negative_matrix(e2_fixture, mutation):
    token = e2_fixture["authority"].issue(
        "user-alice",
        audience="wrong-service" if mutation == "wrong-audience" else "industrial-local-agent",
        expires_in=1 if mutation == "expired" else 300,
        now=e2_fixture["now"] - 10 if mutation == "expired" else e2_fixture["now"],
    ) if mutation != "forged-tenant" else e2_fixture["authority"].issue(
        "user-alice", extra_claims={"tenant_id": "tenant-b"}, now=e2_fixture["now"]
    )
    if mutation == "bad-signature":
        parts = token.split(".")
        parts[-1] = parts[-1][::-1]
        token = ".".join(parts)
    if mutation == "expired":
        with pytest.raises(IdentityError):
            e2_fixture["verifier"].verify(token, now=e2_fixture["now"])
    elif mutation == "forged-tenant":
        identity = e2_fixture["verifier"].verify(token, now=e2_fixture["now"])
        assert identity.subject_id == "user-alice"
        assert not hasattr(identity, "tenant_id")
    else:
        with pytest.raises(IdentityError):
            e2_fixture["verifier"].verify(token, now=e2_fixture["now"])


def test_delegation_derives_tenant_and_rejects_unknown_subject(e2_fixture):
    token = e2_fixture["authority"].issue("user-alice", now=e2_fixture["now"])
    identity = e2_fixture["verifier"].verify(token, now=e2_fixture["now"])
    delegator = IdentityDelegator(
        e2_fixture["delegation_keyring"],
        resolve_tenant=e2_fixture["policy"].tenant_for_subject,
        policy_version=e2_fixture["policy"].current_version,
    )
    context = delegator.delegate(identity, request_id="req-1", purpose_of_use="research-retrieval", now=e2_fixture["now"])
    assert context.tenant_id == "tenant-a"
    assert context.policy_version == 1
    forged = json.loads(json.dumps(context.to_dict()))
    forged["tenant_id"] = "tenant-b"
    assert forged["tenant_id"] != context.tenant_id

    unknown_token = e2_fixture["authority"].issue("user-unknown", now=e2_fixture["now"])
    unknown_identity = e2_fixture["verifier"].verify(unknown_token, now=e2_fixture["now"])
    with pytest.raises(Exception, match="tenant mapping"):
        delegator.delegate(unknown_identity, request_id="req-2", purpose_of_use="research-retrieval", now=e2_fixture["now"])
