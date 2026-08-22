from __future__ import annotations

from dataclasses import dataclass, field

from .errors import AuthorizationDenied, PolicyUnavailable


@dataclass(frozen=True)
class SourceDecision:
    allowed: bool
    decision_id: str
    policy_version: int
    reason: str


@dataclass
class SyntheticPolicyStore:
    """Server-side policy state for two synthetic tenants.

    The store intentionally exposes no client-controlled tenant or role input.
    Mutations advance a policy version, invalidating delegated contexts and
    tenant-scoped retrieval caches issued under the previous version.
    """

    subject_tenants: dict[str, str]
    project_members: dict[str, set[str]]
    project_tenants: dict[str, str]
    source_records: dict[str, tuple[str, str, str, str]]
    source_shares: dict[str, set[str]] = field(default_factory=dict)
    available: bool = True
    version: int = 1

    def _check_available(self) -> None:
        if not self.available:
            raise PolicyUnavailable("Synthetic policy service is unavailable.")

    def tenant_for_subject(self, subject_id: str) -> str | None:
        self._check_available()
        return self.subject_tenants.get(subject_id)

    def current_version(self) -> int:
        self._check_available()
        return self.version

    def _tenant_for_source(self, source_id: str) -> str:
        try:
            return self.source_records[source_id][0]
        except KeyError as exc:
            raise AuthorizationDenied("Source is not visible.") from exc

    def accessible_source_ids(self, subject_id: str, tenant_id: str) -> frozenset[str]:
        self._check_available()
        if self.subject_tenants.get(subject_id) != tenant_id:
            return frozenset()
        allowed: set[str] = set()
        for source_id, (source_tenant, project_id, owner_id, _classification) in self.source_records.items():
            if source_tenant != tenant_id:
                continue
            if owner_id == subject_id or subject_id in self.project_members.get(project_id, set()):
                allowed.add(source_id)
            elif subject_id in self.source_shares.get(source_id, set()):
                allowed.add(source_id)
        return frozenset(allowed)

    def authorize_source(
        self,
        subject_id: str,
        tenant_id: str,
        source_id: str,
        *,
        expected_policy_version: int,
    ) -> SourceDecision:
        self._check_available()
        decision_id = f"decision-{self.version}-{source_id}-{subject_id}"
        if expected_policy_version != self.version:
            return SourceDecision(False, decision_id, self.version, "stale-policy-version")
        if self.subject_tenants.get(subject_id) != tenant_id:
            return SourceDecision(False, decision_id, self.version, "tenant-mismatch")
        if source_id not in self.source_records:
            return SourceDecision(False, decision_id, self.version, "unknown-source")
        allowed = source_id in self.accessible_source_ids(subject_id, tenant_id)
        return SourceDecision(allowed, decision_id, self.version, "allow" if allowed else "acl-deny")

    def share_source(self, source_id: str, recipient_subject: str) -> None:
        self._check_available()
        source_tenant = self._tenant_for_source(source_id)
        if self.subject_tenants.get(recipient_subject) != source_tenant:
            raise AuthorizationDenied("Cross-tenant sharing is not allowed.")
        self.source_shares.setdefault(source_id, set()).add(recipient_subject)
        self.version += 1

    def revoke_share(self, source_id: str, recipient_subject: str) -> None:
        self._check_available()
        self.source_shares.setdefault(source_id, set()).discard(recipient_subject)
        self.version += 1

    def revoke_project_member(self, project_id: str, subject_id: str) -> None:
        self._check_available()
        self.project_members.setdefault(project_id, set()).discard(subject_id)
        self.version += 1
