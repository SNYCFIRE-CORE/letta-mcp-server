"""
Custom exceptions for Letta MCP Server
"""

from typing import Optional, Dict, Any

class LettaMCPError(Exception):
    """Base exception for Letta MCP Server"""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        result = {
            "error": self.message,
            "type": self.__class__.__name__
        }
        
        if self.code:
            result["code"] = self.code
        
        if self.details:
            result["details"] = self.details
        
        return result

class ConfigurationError(LettaMCPError):
    """Raised when there's a configuration issue"""
    
    def __init__(self, message: str, missing_field: Optional[str] = None):
        details = {}
        if missing_field:
            details["missing_field"] = missing_field
        
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            details=details
        )

class APIError(LettaMCPError):
    """Raised when the Letta API returns an error"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None
    ):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response"] = response_body
        
        code = f"API_ERROR_{status_code}" if status_code else "API_ERROR"
        
        super().__init__(
            message=message,
            code=code,
            details=details
        )

class ValidationError(LettaMCPError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )

class NotFoundError(LettaMCPError):
    """Raised when a resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code="NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class TimeoutError(LettaMCPError):
    """Raised when an operation times out"""
    
    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            code="TIMEOUT",
            details={
                "operation": operation,
                "timeout_seconds": timeout_seconds
            }
        )

class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        
        super().__init__(
            message=message,
            status_code=429,
            response_body=details
        )

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401
        )

class PermissionError(APIError):
    """Raised when user lacks permission"""
    
    def __init__(self, message: str = "Permission denied", resource: Optional[str] = None):
        details = {}
        if resource:
            details["resource"] = resource
        
        super().__init__(
            message=message,
            status_code=403,
            response_body=details
        )