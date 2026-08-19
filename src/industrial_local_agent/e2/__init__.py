"""Synthetic E2 identity-aware retrieval vertical slice.

This package is deliberately model-free and uses only synthetic data.  It is
an executable contract for the future enterprise retrieval boundary, not a
production IdP, database, or cryptographic implementation.
"""

from .audit import AuditReceipt, ContentFreeAuditSink
from .bundle import AuthorizedEvidenceBundle
from .identity import (
    DelegatedIdentityContext,
    IdentityDelegator,
    IdentityTokenAuthority,
    IdentityTokenVerifier,
    VerifiedIdentity,
)
from .policy import SyntheticPolicyStore
from .service import E2RetrievalService
from .storage import SQLiteForcedScopeAdapter

__all__ = [
    "AuthorizedEvidenceBundle",
    "AuditReceipt",
    "ContentFreeAuditSink",
    "DelegatedIdentityContext",
    "E2RetrievalService",
    "IdentityDelegator",
    "IdentityTokenAuthority",
    "IdentityTokenVerifier",
    "SQLiteForcedScopeAdapter",
    "SyntheticPolicyStore",
    "VerifiedIdentity",
]
