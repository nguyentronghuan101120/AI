from typing import Any, Optional

class BaseExceptionResponse(Exception):
    """Base exception class for the application."""
    
    def __init__(
        self,
        status_code: int = 500,
        message: str = "An error occurred",
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert the exception to a dictionary format."""
        return {
            "status_code": self.status_code,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        } 