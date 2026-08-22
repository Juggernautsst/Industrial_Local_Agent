class E2Error(Exception):
    """Base error for the synthetic E2 boundary."""


class IdentityError(E2Error):
    """The token or delegated identity context is invalid."""


class PolicyError(E2Error):
    """The policy service cannot make a safe decision."""


class PolicyUnavailable(PolicyError):
    """Policy state is unavailable; callers must fail closed."""


class AuthorizationDenied(PolicyError):
    """The verified identity is not authorized for the requested resource."""


class StorageError(E2Error):
    """The forced-scope storage adapter rejected an operation."""


class AuditError(E2Error):
    """Mandatory audit could not be completed or verified."""


class AuditUnavailable(AuditError):
    """The audit sink is unavailable; no bundle may be returned."""


class BundleError(E2Error):
    """The authorized evidence bundle is malformed or invalid."""


class BundleVerificationError(BundleError):
    """A bundle failed signature, binding, freshness, or content checks."""
