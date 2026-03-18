class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found (maps to 404)."""


class BadRequestError(AppException):
    """Invalid request parameters (maps to 400)."""


class ConflictError(AppException):
    """Conflict e.g. duplicate (maps to 409)."""
