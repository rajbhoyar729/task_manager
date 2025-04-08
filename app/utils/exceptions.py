class CustomException(Exception):
    """
    Base exception class for application-specific errors.
    
    Attributes:
        message (str): Human-readable error description.
        status_code (int): HTTP status code (default: 400).
        request_id (str): Unique identifier for request tracing.
    
    Example:
        raise CustomException("Invalid credentials", 401, request_id="abc123")
    """
    
    def __init__(self, message: str, status_code: int = 400, request_id: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id

    def __str__(self):
        return f"{self.status_code} - {self.message} [Request ID: {self.request_id}]"