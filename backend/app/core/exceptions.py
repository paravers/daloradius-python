"""
Custom exceptions for the daloRADIUS application.

This module defines custom exception classes for specific error conditions
that can occur in the application.
"""


class DaloRadiusException(Exception):
    """Base exception for daloRADIUS application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class DatabaseError(DaloRadiusException):
    """Exception raised for database-related errors"""
    pass


class NotFoundError(DaloRadiusException):
    """Exception raised when a requested resource is not found"""
    pass


class ValidationError(DaloRadiusException):
    """Exception raised for validation errors"""
    pass


class BusinessLogicError(DaloRadiusException):
    """Exception raised for business logic violations"""
    pass


class AuthenticationError(DaloRadiusException):
    """Exception raised for authentication failures"""
    pass


class AuthorizationError(DaloRadiusException):
    """Exception raised for authorization failures"""
    pass


class ConfigurationError(DaloRadiusException):
    """Exception raised for configuration errors"""
    pass


class ExternalServiceError(DaloRadiusException):
    """Exception raised for external service errors"""
    pass