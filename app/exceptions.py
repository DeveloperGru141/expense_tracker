class AppError(Exception):
    """Base exception for the application."""
    pass

class DatabaseError(AppError):
    """Exception raised for errors during database operations."""
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class AuthError(AppError):
    """Exception raised for authentication-related errors."""
    pass
