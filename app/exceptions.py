# Base exception for the application.
class AppError(Exception):
    """Base exception for the application."""
    pass

# Exception raised for database operation errors.
class DatabaseError(AppError):
    """Exception raised for errors during database operations."""
    # Initialize with an optional original exception for traceback.
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

# Exception raised for authentication-related errors.
class AuthError(AppError):
    """Exception raised for authentication-related errors."""
    pass
