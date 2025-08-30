import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception with standardized error handling."""
    
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the exception for monitoring
        logger.error(f"AppException: {message}", extra={
            "status_code": status_code,
            "details": details,
            "exception_type": self.__class__.__name__
        })

class AuthenticationException(AppException):
    """Authentication and authorization failures."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)

class ValidationException(AppException):
    """Input validation and data format errors."""
    
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if field and details is None:
            details = {"field": field}
        elif field and details:
            details["field"] = field
        super().__init__(message, 422, details)

class FileProcessingException(AppException):
    """File upload, parsing, and processing errors."""
    
    def __init__(self, message: str = "File processing failed", filename: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if filename and details is None:
            details = {"filename": filename}
        elif filename and details:
            details["filename"] = filename
        super().__init__(message, 400, details)

class DatabaseException(AppException):
    """Database connection, query, and data integrity errors."""
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if operation and details is None:
            details = {"operation": operation}
        elif operation and details:
            details["operation"] = operation
        super().__init__(message, 500, details)

class ExternalServiceException(AppException):
    """External API and service integration errors."""
    
    def __init__(self, message: str = "External service failed", service: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        if service and details is None:
            details = {"service": service}
        elif service and details:
            details["service"] = service
        super().__init__(message, 502, details)

class RateLimitException(AppException):
    """Rate limiting and quota exceeded errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        if retry_after and details is None:
            details = {"retry_after": retry_after}
        elif retry_after and details:
            details["retry_after"] = retry_after
        super().__init__(message, 429, details)