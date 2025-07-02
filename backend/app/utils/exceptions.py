class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 422)

class FileProcessingException(AppException):
    def __init__(self, message: str = "File processing failed"):
        super().__init__(message, 400)

class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, 500)