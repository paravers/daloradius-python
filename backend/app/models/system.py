"""
System Management Data Models

This module contains SQLAlchemy models for system configuration,
logging, backup management, and administrative operations.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class SystemConfig(Base):
    """System configuration settings"""
    __tablename__ = "systemconfig"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Configuration details
    config_key: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True, index=True)
    config_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_type: Mapped[str] = mapped_column(
        String(32), default="string")  # string, integer, boolean, json
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Configuration metadata
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False)  # System configs can't be deleted
    requires_restart: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class SystemLog(Base):
    """System activity and audit logs"""
    __tablename__ = "systemlogs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Log details
    # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_level: Mapped[str] = mapped_column(
        String(16), nullable=False, index=True)
    logger_name: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Context information
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True)

    # Additional data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    exception_traceback: Mapped[Optional[str]
                                ] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True)


class BackupHistory(Base):
    """Database backup history"""
    __tablename__ = "backuphistory"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Backup details
    backup_name: Mapped[str] = mapped_column(String(255), nullable=False)
    backup_type: Mapped[str] = mapped_column(
        String(32), nullable=False)  # full, incremental, differential
    backup_size: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)  # Size in bytes
    backup_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Backup status
    status: Mapped[str] = mapped_column(
        String(32), default="running")  # running, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Backup metadata
    tables_included: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True)  # JSON list of tables
    compression_used: Mapped[bool] = mapped_column(Boolean, default=False)
    encryption_used: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]
                         ] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class CronJob(Base):
    """Scheduled cron jobs configuration"""
    __tablename__ = "cronjobs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Job details
    job_name: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True)
    job_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    command: Mapped[str] = mapped_column(Text, nullable=False)

    # Schedule
    cron_expression: Mapped[str] = mapped_column(String(128), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    # Job status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)
    last_status: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True)  # success, failed, running
    last_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Job metadata
    max_runtime: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)  # Max runtime in seconds
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class MailSettings(Base):
    """Email configuration settings"""
    __tablename__ = "mailsettings"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # SMTP configuration
    smtp_server: Mapped[str] = mapped_column(String(255), nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, default=587)
    smtp_username: Mapped[str] = mapped_column(String(255), nullable=False)
    smtp_password: Mapped[str] = mapped_column(
        String(255), nullable=False)  # Should be encrypted

    # Email settings
    use_tls: Mapped[bool] = mapped_column(Boolean, default=True)
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=False)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Configuration metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class MailQueue(Base):
    """Email queue for outgoing messages"""
    __tablename__ = "mailqueue"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Email details
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    to_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Message content
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Email metadata
    priority: Mapped[int] = mapped_column(
        Integer, default=5)  # 1 = highest, 10 = lowest
    status: Mapped[str] = mapped_column(
        String(32), default="pending")  # pending, sending, sent, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    # Additional data
    template_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True)
    template_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    scheduled_at: Mapped[Optional[datetime]
                         ] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)


class NotificationTemplate(Base):
    """Email and notification templates"""
    __tablename__ = "notificationtemplates"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Template details
    template_name: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True)
    template_type: Mapped[str] = mapped_column(
        String(32), nullable=False)  # email, sms, push
    # user_welcome, password_reset, etc.
    category: Mapped[str] = mapped_column(String(64), nullable=False)

    # Template content
    subject: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)  # For emails
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Template metadata
    variables: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True)  # JSON list of available variables
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class ApiKey(Base):
    """API keys for external integrations"""
    __tablename__ = "apikeys"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # API key details
    key_name: Mapped[str] = mapped_column(String(128), nullable=False)
    api_key: Mapped[str] = mapped_column(
        String(128), nullable=False, unique=True, index=True)
    secret_key: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True)

    # Permissions and restrictions
    permissions: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True)  # JSON list of permissions
    allowed_ips: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True)  # JSON list of allowed IPs
    rate_limit: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)  # Requests per minute

    # Key status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)


class DatabaseMaintenance(Base):
    """Database maintenance operations log"""
    __tablename__ = "dbmaintenance"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Operation details
    operation_type: Mapped[str] = mapped_column(
        String(32), nullable=False)  # vacuum, reindex, analyze, cleanup
    table_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)
    operation_details: Mapped[Optional[str]
                              ] = mapped_column(Text, nullable=True)

    # Operation results
    status: Mapped[str] = mapped_column(
        String(32), default="running")  # running, completed, failed
    rows_affected: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)
    size_before: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)  # Size in bytes
    size_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[int]
                             ] = mapped_column(Integer, nullable=True)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]
                         ] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True)


class SessionStore(Base):
    """Application session storage"""
    __tablename__ = "sessions"

    # Primary key (using session_id as primary key)
    session_id: Mapped[str] = mapped_column(
        String(128), primary_key=True, index=True)

    # Session data
    session_data: Mapped[str] = mapped_column(
        Text, nullable=False)  # JSON encoded session data
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Session metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True)


class AuditTrail(Base):
    """Audit trail for all system changes"""
    __tablename__ = "audittrail"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Audit details
    table_name: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True)
    record_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(
        String(16), nullable=False, index=True)  # INSERT, UPDATE, DELETE

    # Change details
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    changed_fields: Mapped[Optional[List[str]]
                           ] = mapped_column(JSON, nullable=True)

    # Context information
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True)
