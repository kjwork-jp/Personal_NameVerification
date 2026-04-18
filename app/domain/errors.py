"""Domain/service error types."""


class ValidationError(Exception):
    """Raised when input validation fails."""


class ConflictError(Exception):
    """Raised when data conflicts with current state or uniqueness constraints."""


class NotFoundError(Exception):
    """Raised when target resource was not found."""


class StateTransitionError(Exception):
    """Raised when an invalid state transition is requested."""


class AuthorizationError(Exception):
    """Raised when caller role is not authorized for requested action."""
