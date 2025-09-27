"""
Configuration Management Module Data Models

This module defines Pydantic models mapping the Configuration (config-*.php, mng-rad-* ancillary config) pages
into structured Python schemas for a refactored backend.

Scope (derived from configuration module pages):
- Backups: create/manage/restore/delete
- Cron / Scheduled Tasks
- Database connection settings
- Interface preferences (UI, pagination, theme, language)
- Language selection
- Logging settings
- Mail (SMTP) settings + test mail
- Maintenance operations: disconnect user, test user credentials
- System messages / portal messages
- Operator management (overlaps with user management, placed here for config scope)
- Reports & dashboard user-configurable thresholds/widgets
- User-specific configuration/preferences

Design Principles:
- SOLID: each model single responsibility, extensible via inheritance
- Aliases mimic original PHP form field names for seamless migration
- Validation included for early feedback; permissive where PHP allowed free-form values

Assumptions:
- Some config pages store key/value pairs in a settings table; we model them as cohesive objects.
- Backup operations handled via type + compression flags (tar/gz) though UI may present combined choices.
- Cron jobs simplified to enable/disable + schedule string (crontab expression) + description.
- Reports dashboard widgets modeled as list of enabled widget identifiers.

If later we ingest concrete DB schemas, adjustments may be applied.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
import re


class BaseConfigModel(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True


# ===================== Enums =====================
class BackupType(str, Enum):
    FULL = "full"
    PARTIAL = "partial"  # user chooses subset (e.g., only users or only accounting)

class CompressionType(str, Enum):
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"

class BackupAction(str, Enum):
    CREATE = "create"
    RESTORE = "restore"
    DELETE = "delete"
    DOWNLOAD = "download"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SmtpEncryption(str, Enum):
    NONE = "none"
    SSL = "ssl"
    TLS = "tls"

class MessageType(str, Enum):
    PORTAL = "portal"
    SYSTEM = "system"
    BANNER = "banner"

# ===================== Backup Models =====================
class BackupCreateRequest(BaseConfigModel):
    name: str = Field(..., min_length=1, max_length=128)
    backup_type: BackupType = Field(default=BackupType.FULL, alias="backupType")
    include_radius: bool = Field(True, alias="includeRadius")
    include_users: bool = Field(True, alias="includeUsers")
    include_accounting: bool = Field(True, alias="includeAccounting")
    compression: CompressionType = Field(default=CompressionType.GZIP)
    notes: Optional[str] = None

class BackupResult(BaseConfigModel):
    name: str
    created_at: datetime
    size_bytes: int
    compression: CompressionType
    checksum: Optional[str] = None

class BackupManageRequest(BaseConfigModel):
    action: BackupAction
    name: str
    confirm: bool = False

# ===================== Cron / Scheduled Jobs =====================
class CronJobConfig(BaseConfigModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=128)
    enabled: bool = True
    schedule: str = Field(..., min_length=1, max_length=128, description="Crontab expression")
    command: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = None

    @validator('schedule')
    def validate_schedule(cls, v):
        # Very loose validation: require at least 5 space-separated fields
        if len(v.split()) < 5:
            raise ValueError('Invalid crontab expression (needs at least 5 fields)')
        return v

# ===================== Database Configuration =====================
class DBConfig(BaseConfigModel):
    host: str = Field(..., min_length=1, max_length=128)
    port: int = Field(3306, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=128, alias="dbUser")
    password: str = Field(..., min_length=1, max_length=256, alias="dbPass")
    database: str = Field(..., min_length=1, max_length=128, alias="dbName")
    use_ssl: bool = Field(False, alias="useSSL")

# ===================== Interface / UI Preferences =====================
class InterfaceConfig(BaseConfigModel):
    theme: Optional[str] = Field("default", max_length=64)
    items_per_page: int = Field(25, ge=1, le=500, alias="itemsPerPage")
    language: Optional[str] = Field("en", max_length=8)
    show_advanced: bool = Field(False, alias="showAdvanced")

# ===================== Language Selection =====================
class LanguageConfig(BaseConfigModel):
    active_language: str = Field("en", alias="activeLanguage", max_length=8)
    available_languages: List[str] = Field(default_factory=lambda: ["en"])

# ===================== Logging =====================
class LoggingConfig(BaseConfigModel):
    enabled: bool = True
    level: LogLevel = LogLevel.INFO
    log_to_file: bool = Field(True, alias="logToFile")
    log_file_path: Optional[str] = Field(None, max_length=256, alias="logFilePath")
    max_size_mb: int = Field(10, ge=1, le=1024, alias="maxSizeMB")
    rotate: bool = Field(True)

# ===================== Mail Settings =====================
class MailSettingsConfig(BaseConfigModel):
    smtp_host: str = Field(..., max_length=128, alias="smtpHost")
    smtp_port: int = Field(587, ge=1, le=65535, alias="smtpPort")
    username: Optional[str] = Field(None, max_length=128, alias="smtpUser")
    password: Optional[str] = Field(None, max_length=256, alias="smtpPass")
    encryption: SmtpEncryption = Field(default=SmtpEncryption.TLS, alias="encryption")
    sender_email: EmailStr = Field(..., alias="senderEmail")
    sender_name: Optional[str] = Field(None, max_length=128, alias="senderName")
    timeout_seconds: int = Field(30, ge=1, le=600, alias="timeoutSeconds")
    retries: int = Field(3, ge=0, le=10)

class MailTestRequest(BaseConfigModel):
    recipient: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)

# ===================== Maintenance Operations =====================
class DisconnectUserRequest(BaseConfigModel):
    username: str = Field(..., min_length=1, max_length=64)
    session_id: Optional[str] = Field(None, max_length=128, alias="sessionId")
    nas_ip: Optional[str] = Field(None, max_length=64, alias="nasIp")

class TestUserRequest(BaseConfigModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)
    auth_type: Optional[str] = Field(None, alias="authType")

# ===================== System / Portal Messages =====================
class MessageConfig(BaseConfigModel):
    id: Optional[int] = None
    message_type: MessageType = Field(..., alias="messageType")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    active: bool = True
    starts_at: Optional[datetime] = Field(None, alias="startsAt")
    ends_at: Optional[datetime] = Field(None, alias="endsAt")

# ===================== Operator Management =====================
class OperatorInfo(BaseConfigModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=64)
    password_hash: Optional[str] = Field(None, max_length=256, alias="passwordHash")
    fullname: Optional[str] = Field(None, max_length=200, alias="fullName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    is_active: bool = Field(True, alias="isActive")
    roles: List[str] = Field(default_factory=list)
    last_login: Optional[datetime] = Field(None, alias="lastLogin")

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\-\(\)\s]+$'):  # simple phone pattern
            raise ValueError('Invalid phone format')
        return v

class OperatorCreateRequest(BaseConfigModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=200, alias="fullName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    roles: List[str] = Field(default_factory=list)

class OperatorEditRequest(BaseConfigModel):
    password: Optional[str] = Field(None, min_length=6)
    full_name: Optional[str] = Field(None, max_length=200, alias="fullName")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = Field(None, alias="isActive")

class OperatorDeleteRequest(BaseConfigModel):
    username: str
    confirm: bool = False

class OperatorListItem(BaseConfigModel):
    username: str
    full_name: Optional[str] = Field(None, alias="fullName")
    email: Optional[EmailStr] = None
    is_active: bool = Field(True, alias="isActive")
    roles: List[str] = Field(default_factory=list)
    last_login: Optional[datetime] = Field(None, alias="lastLogin")

class OperatorListResponse(BaseConfigModel):
    operators: List[OperatorListItem]
    total_count: int = Field(..., alias="totalCount")

# ===================== Reports & Dashboard =====================
class ReportsDashboardConfig(BaseConfigModel):
    enabled_widgets: List[str] = Field(default_factory=list, alias="enabledWidgets")
    refresh_interval_sec: int = Field(60, ge=10, le=3600, alias="refreshIntervalSec")

class ReportsConfig(BaseConfigModel):
    default_period_days: int = Field(30, ge=1, le=365, alias="defaultPeriodDays")
    auto_refresh: bool = Field(True, alias="autoRefresh")
    export_formats: List[str] = Field(default_factory=lambda: ["csv", "json"], alias="exportFormats")

# ===================== User Preferences =====================
class UserConfig(BaseConfigModel):
    username: str
    timezone: Optional[str] = Field("UTC", max_length=64)
    date_format: Optional[str] = Field("YYYY-MM-DD", max_length=32, alias="dateFormat")
    time_format: Optional[str] = Field("HH:mm:ss", max_length=32, alias="timeFormat")
    dashboard_layout: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="dashboardLayout")

# ===================== Exports =====================
__all__ = [
    # Enums
    'BackupType','CompressionType','BackupAction','LogLevel','SmtpEncryption','MessageType',
    # Base
    'BaseConfigModel',
    # Backup
    'BackupCreateRequest','BackupResult','BackupManageRequest',
    # Cron
    'CronJobConfig',
    # DB
    'DBConfig',
    # Interface/Language/Logging
    'InterfaceConfig','LanguageConfig','LoggingConfig',
    # Mail
    'MailSettingsConfig','MailTestRequest',
    # Maintenance
    'DisconnectUserRequest','TestUserRequest',
    # Messages
    'MessageConfig',
    # Operator
    'OperatorInfo','OperatorCreateRequest','OperatorEditRequest','OperatorDeleteRequest','OperatorListItem','OperatorListResponse',
    # Reports
    'ReportsDashboardConfig','ReportsConfig',
    # User Prefs
    'UserConfig',
]
