class ChatbotException(Exception):
    """Base exception class for the chatbot application"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Authentication Exceptions
class AuthenticationError(ChatbotException):
    """Exception raised for authentication errors"""
    def __init__(self, message="Authentication failed", status_code=401):
        super().__init__(message, status_code)

class InvalidCredentialsError(AuthenticationError):
    """Exception raised for invalid credentials"""
    def __init__(self, message="Invalid username or password"):
        super().__init__(message, 401)

class UserExistsError(ChatbotException):
    """Exception raised when trying to create a user that already exists"""
    def __init__(self, message="User already exists"):
        super().__init__(message, 409)

class RegistrationError(ChatbotException):
    """Exception raised for registration errors"""
    def __init__(self, message="Registration failed"):
        super().__init__(message, 400)

class SessionExpiredError(AuthenticationError):
    """Exception raised when a session has expired"""
    def __init__(self, message="Session has expired. Please log in again."):
        super().__init__(message, 401)

# Database Exceptions
class DatabaseError(ChatbotException):
    """Exception raised for database errors"""
    def __init__(self, message="Database error occurred", status_code=500):
        super().__init__(message, status_code)

class ConnectionError(DatabaseError):
    """Exception raised for database connection errors"""
    def __init__(self, message="Failed to connect to database"):
        super().__init__(message, 503)

# LLM Model Exceptions
class LLMError(ChatbotException):
    """Exception raised for LLM-related errors"""
    def __init__(self, message="Error with language model", status_code=500):
        super().__init__(message, status_code)

class ModelConnectionError(LLMError):
    """Exception raised when unable to connect to the LLM service"""
    def __init__(self, message="Unable to connect to language model service"):
        super().__init__(message, 503)

class ModelResponseError(LLMError):
    """Exception raised when the LLM response is invalid or incomplete"""
    def __init__(self, message="Received invalid response from language model"):
        super().__init__(message, 500)

class ModelTimeoutError(LLMError):
    """Exception raised when the LLM request times out"""
    def __init__(self, message="Language model request timed out"):
        super().__init__(message, 504)

# Rate Limiting Exceptions
class RateLimitExceededError(ChatbotException):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded. Please try again later."):
        super().__init__(message, 429)

# Input Validation Exceptions
class ValidationError(ChatbotException):
    """Exception raised for input validation errors"""
    def __init__(self, message="Invalid input"):
        super().__init__(message, 400)

class InvalidEmailError(ValidationError):
    """Exception raised for invalid email format"""
    def __init__(self, message="Invalid email format"):
        super().__init__(message)

class WeakPasswordError(ValidationError):
    """Exception raised for weak passwords"""
    def __init__(self, message="Password does not meet security requirements"):
        super().__init__(message)

# Chat History Exceptions
class ChatHistoryError(ChatbotException):
    """Exception raised for chat history errors"""
    def __init__(self, message="Error accessing chat history"):
        super().__init__(message, 500)

class NoHistoryFoundError(ChatHistoryError):
    """Exception raised when no chat history is found"""
    def __init__(self, message="No chat history found"):
        super().__init__(message, 404)

# Resource Exceptions
class ResourceExhaustedError(ChatbotException):
    """Exception raised when system resources are exhausted"""
    def __init__(self, message="System resources exhausted"):
        super().__init__(message, 503)

# Helper functions for exception handling
def raise_auth_error(message="Authentication failed"):
    """Raise an authentication error with a custom message"""
    raise AuthenticationError(message)

def raise_db_error(message="Database error occurred"):
    """Raise a database error with a custom message"""
    raise DatabaseError(message)

def raise_model_error(message="Error with language model"):
    """Raise a model error with a custom message"""
    raise LLMError(message)

def handle_exception(e):
    """Handle exceptions and return appropriate status code and message"""
    if isinstance(e, ChatbotException):
        return e.status_code, e.message
    else:
        return 500, f"Internal Server Error: {str(e)}"
