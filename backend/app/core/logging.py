"""
Logging Configuration Module

This module provides centralized logging configuration for the daloRADIUS application,
supporting both development and production environments with structured logging.
"""

import logging
import logging.handlers

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output in development
    """

    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'logging.INFO': '\033[32m',       # Green
        'logging.WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format log record with colors"""
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for production environments
    """

    def format(self, record):
        """Format log record as structured JSON"""
        import json

        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno',
                           'pathname', 'filename', 'module', 'exc_info',
                           'exc_text', 'stack_info', 'lineno', 'funcName',
                           'created', 'msecs', 'relativeCreated', 'thread',
                           'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logging() -> None:
    """
    Configure application logging
    """
    # Create logs directory if it doesn't exist
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.is_development:
        # Colored format for development
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Structured format for production
        console_formatter = StructuredFormatter()

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if settings.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT
        )

        # Always use structured format for file logging
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure specific loggers

    # SQLAlchemy logging (reduce verbosity in production)
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    if settings.is_production:
        sqlalchemy_logger.setLevel(logging.WARNING)
    else:
        sqlalchemy_logger.setLevel(logging.INFO)

    # FastAPI/Uvicorn logging
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(logging.INFO)

    # Application logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Security logger (always logging.INFO level or higher)
    security_logger = logging.getLogger('app.security')
    security_logger.setLevel(max(logging.INFO, root_logger.level))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class AuditLogger:
    """
    Specialized logger for audit events
    """

    def __init__(self):
        self.logger = get_logger('app.audit')

    def log_user_action(self, user_id: str, action: str, resource: str,
                        details: Optional[dict] = None):
        """Log user actions for audit trail"""
        audit_data = {
            'audit_type': 'user_action',
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details or {}
        }
        self.logger.info("User action", extra=audit_data)

    def log_security_event(self, event_type: str, severity: str,
                           details: Optional[dict] = None):
        """Log security events"""
        security_data = {
            'audit_type': 'security_event',
            'event_type': event_type,
            'severity': severity,
            'details': details or {}
        }

        if severity.lower() in ['high', 'critical']:
            self.logger.error("Security event", extra=security_data)
        elif severity.lower() == 'medium':
            self.logger.warning("Security event", extra=security_data)
        else:
            self.logger.info("Security event", extra=security_data)

    def log_system_event(self, event_type: str, message: str,
                         details: Optional[dict] = None):
        """Log system events"""
        system_data = {
            'audit_type': 'system_event',
            'event_type': event_type,
            'message': message,
            'details': details or {}
        }
        self.logger.info("System event", extra=system_data)


# Global audit logger instance
audit_logger = AuditLogger()
