"""
System Configuration Schema Definitions

This module contains Pydantic schemas for system configuration operations
including request/response models for API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

from ..models.access_control import MessageType


# Base schemas
class BaseConfigSchema(BaseModel):
    """Base configuration schema"""

    class Config:
        from_attributes = True
        use_enum_values = True


# System Configuration schemas
class SystemConfigBase(BaseConfigSchema):
    """Base system configuration schema"""
    config_key: str = Field(..., min_length=1, max_length=128)
    config_value: Optional[str] = Field(None)
    config_type: str = Field("string", regex="^(string|integer|boolean|json)$")
    category: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = Field(None)
    is_encrypted: bool = Field(False)
    is_system: bool = Field(False)
    requires_restart: bool = Field(False)


class SystemConfigCreate(SystemConfigBase):
    """Schema for creating system configuration"""
    updated_by: Optional[str] = Field(None, max_length=64)


class SystemConfigUpdate(BaseConfigSchema):
    """Schema for updating system configuration"""
    config_value: Optional[str] = Field(None)
    config_type: Optional[str] = Field(
        None, regex="^(string|integer|boolean|json)$")
    category: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None)
    is_encrypted: Optional[bool] = Field(None)
    requires_restart: Optional[bool] = Field(None)
    updated_by: Optional[str] = Field(None, max_length=64)


class SystemConfigResponse(SystemConfigBase):
    """Schema for system configuration API responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = None


# Mail Settings schemas
class MailSettingsBase(BaseConfigSchema):
    """Base mail settings schema"""
    smtp_server: str = Field(..., min_length=1, max_length=255)
    smtp_port: int = Field(587, ge=1, le=65535)
    smtp_username: str = Field(..., min_length=1, max_length=255)
    smtp_password: str = Field(..., min_length=1, max_length=255)
    use_tls: bool = Field(True)
    use_ssl: bool = Field(False)
    from_email: EmailStr
    from_name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = Field(True)


class MailSettingsCreate(MailSettingsBase):
    """Schema for creating mail settings"""
    is_default: bool = Field(False)
    updated_by: Optional[str] = Field(None, max_length=64)


class MailSettingsUpdate(BaseConfigSchema):
    """Schema for updating mail settings"""
    smtp_server: Optional[str] = Field(None, min_length=1, max_length=255)
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_username: Optional[str] = Field(None, min_length=1, max_length=255)
    smtp_password: Optional[str] = Field(None, min_length=1, max_length=255)
    use_tls: Optional[bool] = Field(None)
    use_ssl: Optional[bool] = Field(None)
    from_email: Optional[EmailStr] = Field(None)
    from_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = Field(None)
    is_default: Optional[bool] = Field(None)
    updated_by: Optional[str] = Field(None, max_length=64)


class MailSettingsResponse(MailSettingsBase):
    """Schema for mail settings API responses"""
    id: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = None


class MailTestRequest(BaseConfigSchema):
    """Schema for testing mail settings"""
    recipient: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    mail_settings_id: Optional[int] = Field(
        None, description="Use specific mail settings, or default if not provided")


class MailTestResponse(BaseConfigSchema):
    """Schema for mail test results"""
    success: bool
    message: str
    tested_at: datetime
    details: Optional[Dict[str, Any]] = None


# Backup History schemas
class BackupHistoryBase(BaseConfigSchema):
    """Base backup history schema"""
    backup_name: str = Field(..., min_length=1, max_length=255)
    backup_type: str = Field(..., regex="^(full|incremental|differential)$")
    backup_path: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    compression_type: Optional[str] = Field(
        None, regex="^(none|gzip|bzip2|xz)$")
    description: Optional[str] = Field(None)


class BackupHistoryCreate(BackupHistoryBase):
    """Schema for creating backup history record"""
    backup_date: Optional[datetime] = Field(None)
    status: str = Field(
        "pending", regex="^(pending|running|completed|failed)$")
    created_by: Optional[str] = Field(None, max_length=64)


class BackupHistoryUpdate(BaseConfigSchema):
    """Schema for updating backup history"""
    status: Optional[str] = Field(
        None, regex="^(pending|running|completed|failed)$")
    error_message: Optional[str] = Field(None)
    file_size: Optional[int] = Field(None, ge=0)
    completion_time: Optional[datetime] = Field(None)


class BackupHistoryResponse(BackupHistoryBase):
    """Schema for backup history API responses"""
    id: int
    backup_date: datetime
    status: str
    error_message: Optional[str] = None
    completion_time: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Cron Job schemas
class CronJobBase(BaseConfigSchema):
    """Base cron job schema"""
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None)
    schedule: str = Field(..., min_length=1, max_length=128)  # Cron expression
    command: str = Field(..., min_length=1, max_length=1000)
    is_enabled: bool = Field(True)
    max_runtime: Optional[int] = Field(None, ge=1)  # seconds
    max_retries: int = Field(3, ge=0, le=10)


class CronJobCreate(CronJobBase):
    """Schema for creating cron job"""
    created_by: Optional[str] = Field(None, max_length=64)


class CronJobUpdate(BaseConfigSchema):
    """Schema for updating cron job"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None)
    schedule: Optional[str] = Field(None, min_length=1, max_length=128)
    command: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_enabled: Optional[bool] = Field(None)
    max_runtime: Optional[int] = Field(None, ge=1)
    max_retries: Optional[int] = Field(None, ge=0, le=10)


class CronJobResponse(CronJobBase):
    """Schema for cron job API responses"""
    id: int
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    last_output: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


# Message schemas
class MessageBase(BaseConfigSchema):
    """Base message schema"""
    type: MessageType
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for creating message"""
    created_by: Optional[str] = Field(None, max_length=32)


class MessageUpdate(BaseConfigSchema):
    """Schema for updating message"""
    type: Optional[MessageType] = Field(None)
    content: Optional[str] = Field(None, min_length=1)
    modified_by: Optional[str] = Field(None, max_length=32)


class MessageResponse(MessageBase):
    """Schema for message API responses"""
    id: int
    created_on: datetime
    created_by: Optional[str] = None
    modified_on: Optional[datetime] = None
    modified_by: Optional[str] = None


# System Log schemas (read-only)
class SystemLogResponse(BaseConfigSchema):
    """Schema for system log API responses"""
    id: int
    log_level: str
    logger_name: str
    message: str
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    timestamp: datetime


# Configuration group schemas
class ConfigurationGroupRequest(BaseConfigSchema):
    """Schema for requesting configuration groups"""
    categories: Optional[List[str]] = Field(None)
    include_system: bool = Field(False)
    include_encrypted: bool = Field(False)


class ConfigurationGroupResponse(BaseConfigSchema):
    """Schema for configuration group responses"""
    category: str
    configs: List[SystemConfigResponse]
    total_count: int


# Bulk operation schemas
class BulkConfigUpdateRequest(BaseConfigSchema):
    """Schema for bulk configuration updates"""
    updates: Dict[str, str] = Field(..., min_items=1)
    updated_by: Optional[str] = Field(None, max_length=64)


class BulkConfigUpdateResponse(BaseConfigSchema):
    """Schema for bulk configuration update responses"""
    updated_configs: List[SystemConfigResponse]
    failed_updates: List[Dict[str, str]]
    success_count: int
    error_count: int


# Configuration backup schemas
class ConfigBackupRequest(BaseConfigSchema):
    """Schema for creating configuration backup"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    categories: Optional[List[str]] = Field(None)
    include_encrypted: bool = Field(False)


class ConfigBackupResponse(BaseConfigSchema):
    """Schema for configuration backup responses"""
    backup_id: int
    name: str
    description: Optional[str] = None
    config_count: int
    created_at: datetime
    created_by: Optional[str] = None


class ConfigRestoreRequest(BaseConfigSchema):
    """Schema for restoring configuration backup"""
    backup_id: int
    categories: Optional[List[str]] = Field(None)
    overwrite_existing: bool = Field(True)


class ConfigRestoreResponse(BaseConfigSchema):
    """Schema for configuration restore responses"""
    restored_configs: List[SystemConfigResponse]
    skipped_configs: List[str]
    success_count: int
    skip_count: int


# Search and filter schemas
class ConfigSearchParams(BaseConfigSchema):
    """Schema for configuration search parameters"""
    search_term: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    config_type: Optional[str] = Field(None)
    is_system: Optional[bool] = Field(None)
    is_encrypted: Optional[bool] = Field(None)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class ConfigSearchResponse(BaseConfigSchema):
    """Schema for configuration search responses"""
    configs: List[SystemConfigResponse]
    total_count: int
    page_info: Dict[str, Any]


# Statistics schemas
class ConfigStatisticsResponse(BaseConfigSchema):
    """Schema for configuration statistics"""
    total_configs: int
    system_configs: int
    user_configs: int
    encrypted_configs: int
    categories: List[Dict[str, Any]]
    recent_updates: int


class BackupStatisticsResponse(BaseConfigSchema):
    """Schema for backup statistics"""
    total_backups: int
    successful_backups: int
    recent_backups: int
    success_rate: float
    latest_backup: Optional[BackupHistoryResponse] = None


# System information schemas
class SystemInfoResponse(BaseConfigSchema):
    """Schema for system information"""
    version: str
    uptime: str
    database_status: str
    mail_status: str
    backup_status: str
    active_cron_jobs: int
    system_load: Optional[Dict[str, Any]] = None


# Error response schemas
class ConfigErrorResponse(BaseConfigSchema):
    """Schema for configuration error responses"""
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


# Export all schemas
__all__ = [
    # Base
    "BaseConfigSchema",

    # System Configuration
    "SystemConfigBase",
    "SystemConfigCreate",
    "SystemConfigUpdate",
    "SystemConfigResponse",

    # Mail Settings
    "MailSettingsBase",
    "MailSettingsCreate",
    "MailSettingsUpdate",
    "MailSettingsResponse",
    "MailTestRequest",
    "MailTestResponse",

    # Backup History
    "BackupHistoryBase",
    "BackupHistoryCreate",
    "BackupHistoryUpdate",
    "BackupHistoryResponse",

    # Cron Jobs
    "CronJobBase",
    "CronJobCreate",
    "CronJobUpdate",
    "CronJobResponse",

    # Messages
    "MessageBase",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",

    # System Logs
    "SystemLogResponse",

    # Configuration Groups
    "ConfigurationGroupRequest",
    "ConfigurationGroupResponse",

    # Bulk Operations
    "BulkConfigUpdateRequest",
    "BulkConfigUpdateResponse",

    # Backup/Restore
    "ConfigBackupRequest",
    "ConfigBackupResponse",
    "ConfigRestoreRequest",
    "ConfigRestoreResponse",

    # Search/Filter
    "ConfigSearchParams",
    "ConfigSearchResponse",

    # Statistics
    "ConfigStatisticsResponse",
    "BackupStatisticsResponse",
    "SystemInfoResponse",

    # Error
    "ConfigErrorResponse"
]
