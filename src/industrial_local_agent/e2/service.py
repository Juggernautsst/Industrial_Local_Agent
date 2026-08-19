from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Mapping

from .audit import ContentFreeAuditSink
from .bundle import AuthorizedEvidenceBundle
from .crypto import HmacKeyRing, sha256_hex
from .errors import AuthorizationDenied, IdentityError, PolicyError
from .identity import (
    DelegatedIdentityContext,
    IdentityDelegator,
    IdentityTokenVerifier,
)
from .policy import SyntheticPolicyStore
from .storage import SQLiteForcedScopeAdapter


@dataclass(frozen=True)
class RetrievalResponse:
    bundle: AuthorizedEvidenceBundle
    audit_receipt_event_id: str


class E2RetrievalService:
    """Model-free synthetic E2 retrieval orchestration."""

    def __init__(
        self,
        *,
        policy: SyntheticPolicyStore,
        storage: SQLiteForcedScopeAdapter,
        token_verifier: IdentityTokenVerifier,
        delegation_keyring: HmacKeyRing,
        bundle_keyring: HmacKeyRing,
        audit_sink: ContentFreeAuditSink,
        audience: str = "e2-retrieval",
        bundle_key_id: str = "bundle-key-1",
        clock=None,
    ) -> None:
        self.policy = policy
        self.storage = storage
        self.token_verifier = token_verifier
        self.delegation_keyring = delegation_keyring
        self.bundle_keyring = bundle_keyring
        self.audit_sink = audit_sink
        self.audience = audience
        self.bundle_key_id = bundle_key_id
        self.clock = clock or (lambda: int(time.time()))
        self._seen_requests: set[str] = set()
        self._seen_delegations: set[str] = set()
        self._cache: dict[tuple[str, str, int, str], frozenset[str]] = {}
        self._delegator = IdentityDelegator(
            delegation_keyring,
            audience=audience,
            resolve_tenant=self.policy.tenant_for_subject,
            policy_version=self.policy.current_version,
        )

    def retrieve(
        self,
        token: str,
        *,
        request_id: str,
        query: str,
        purpose_of_use: str = "research-retrieval",
        client_claims: Mapping[str, object] | None = None,
        top_k: int = 5,
    ) -> RetrievalResponse:
        now = int(self.clock())
        if not request_id or not isinstance(request_id, str):
            raise IdentityError("Request ID is required.")
        if client_claims:
            forbidden = {"subject_id", "tenant_id", "role", "group", "clearance", "policy_version"}
            if forbidden.intersection(client_claims):
                raise IdentityError("Client identity and authorization claims are ignored and rejected.")
        if request_id in self._seen_requests:
            raise IdentityError("Request replay is rejected.")
        identity = self.token_verifier.verify(token, now=now)
        context = self._delegator.delegate(
            identity,
            request_id=request_id,
            purpose_of_use=purpose_of_use,
            now=now,
        )
        context.verify(
            self.delegation_keyring,
            expected_audience=self.audience,
            now=now,
        )
        if context.delegation_id in self._seen_delegations:
            raise IdentityError("Delegated identity replay is rejected.")
        current_policy_version = self.policy.current_version()
        if current_policy_version != context.policy_version:
            raise PolicyError("Delegated identity policy snapshot is stale.")
        if not isinstance(query, str) or not query.strip() or len(query) > 500:
            raise PolicyError("Retrieval query is empty or exceeds its bound.")
        if not 1 <= top_k <= 20:
            raise PolicyError("Retrieval limit is outside the bounded range.")

        cache_key = (
            context.tenant_id,
            context.subject_id,
            context.policy_version,
            sha256_hex(query),
        )
        allowed_ids = self._cache.get(cache_key)
        if allowed_ids is None:
            allowed_ids = self.policy.accessible_source_ids(context.subject_id, context.tenant_id)
        scope_handle = self.storage.issue_forced_scope(
            tenant_id=context.tenant_id,
            subject_id=context.subject_id,
            policy_version=context.policy_version,
            source_ids=allowed_ids,
        )
        candidates = self.storage.retrieve(scope_handle, query, limit=top_k)
        authorized: list[tuple[object, str]] = []
        for source in candidates:
            decision = self.policy.authorize_source(
                context.subject_id,
                context.tenant_id,
                source.source_id,
                expected_policy_version=context.policy_version,
            )
            if not decision.allowed:
                raise AuthorizationDenied("Source authorization changed during retrieval.")
            authorized.append((source, decision.decision_id))

        bundle = AuthorizedEvidenceBundle.create(
            context,
            authorized,
            query=query,
            keyring=self.bundle_keyring,
            key_id=self.bundle_key_id,
            now=now,
        )
        bundle.verify(
            self.bundle_keyring,
            context,
            expected_audience=self.audience,
            now=now,
        )
        receipt = self.audit_sink.append(
            {
                "event_type": "authorized-retrieval",
                "request_id": context.request_id,
                "delegation_id": context.delegation_id,
                "subject_id": context.subject_id,
                "tenant_id": context.tenant_id,
                "policy_version": context.policy_version,
                "decision_ids": [decision_id for _source, decision_id in authorized],
                "source_ids": [source.source_id for source, _decision_id in authorized],
                "source_hashes": [source.content_hash for source, _decision_id in authorized],
                "bundle_id": bundle.bundle_id,
                "outcome": "authorized-bundle-issued",
            },
            now=now,
        )
        self._cache[cache_key] = frozenset(source.source_id for source, _decision_id in authorized)
        self._seen_requests.add(request_id)
        self._seen_delegations.add(context.delegation_id)
        return RetrievalResponse(bundle=bundle, audit_receipt_event_id=receipt.event_id)

    def verify_bundle_for_context(
        self,
        bundle: AuthorizedEvidenceBundle,
        context: DelegatedIdentityContext,
    ) -> None:
        """Public worker-side verification hook; it never invokes a model."""

        bundle.verify(
            self.bundle_keyring,
            context,
            expected_audience=self.audience,
            now=int(self.clock()),
        )
