"""
RADIUS Authentication and Authorization Pydantic Schemas

This module contains Pydantic models for RADIUS check/reply attributes
and accounting data validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from ipaddress import IPv4Address


class RadiusOperator(str, Enum):
    """RADIUS check operators"""
    EQUAL = "=="
    NOT_EQUAL = "!="
    SET = ":="
    ADD = "+="
    SUBTRACT = "-="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    REGEX_MATCH = "=~"
    REGEX_NOT_MATCH = "!~"


class SessionStatus(str, Enum):
    """Accounting session status"""
    START = "Start"
    STOP = "Stop"  
    UPDATE = "Interim-Update"


class StopCause(str, Enum):
    """Session termination causes"""
    USER_REQUEST = "User-Request"
    LOST_CARRIER = "Lost-Carrier"
    LOST_SERVICE = "Lost-Service"
    IDLE_TIMEOUT = "Idle-Timeout"
    SESSION_TIMEOUT = "Session-Timeout"
    ADMIN_RESET = "Admin-Reset"
    ADMIN_REBOOT = "Admin-Reboot"
    PORT_ERROR = "Port-Error"
    NAS_ERROR = "NAS-Error"
    NAS_REQUEST = "NAS-Request"
    NAS_REBOOT = "NAS-Reboot"
    PORT_UNNEEDED = "Port-Unneeded"
    PORT_PREEMPTED = "Port-Preempted"
    PORT_SUSPENDED = "Port-Suspended"
    SERVICE_UNAVAILABLE = "Service-Unavailable"
    CALLBACK = "Callback"
    USER_ERROR = "User-Error"
    HOST_REQUEST = "Host-Request"


# RADIUS Check (Authorization) schemas
class RadcheckBase(BaseModel):
    """Base RADIUS check schema"""
    username: str = Field(..., max_length=64, description="User or group name")
    attribute: str = Field(..., max_length=64, description="RADIUS attribute name")
    op: RadiusOperator = Field(..., description="RADIUS operator")
    value: str = Field(..., max_length=253, description="Attribute value")


class RadcheckCreate(RadcheckBase):
    """Schema for creating RADIUS check"""
    pass


class RadcheckUpdate(BaseModel):
    """Schema for updating RADIUS check"""
    attribute: Optional[str] = Field(None, max_length=64)
    op: Optional[RadiusOperator] = None
    value: Optional[str] = Field(None, max_length=253)


class RadcheckResponse(RadcheckBase):
    """Schema for RADIUS check responses"""
    id: int

    class Config:
        from_attributes = True


# RADIUS Reply (Authorization) schemas  
class RadreplyBase(BaseModel):
    """Base RADIUS reply schema"""
    username: str = Field(..., max_length=64, description="User or group name")
    attribute: str = Field(..., max_length=64, description="RADIUS attribute name")
    op: RadiusOperator = Field(..., description="RADIUS operator")
    value: str = Field(..., max_length=253, description="Attribute value")


class RadreplyCreate(RadreplyBase):
    """Schema for creating RADIUS reply"""
    pass


class RadreplyUpdate(BaseModel):
    """Schema for updating RADIUS reply"""
    attribute: Optional[str] = Field(None, max_length=64)
    op: Optional[RadiusOperator] = None
    value: Optional[str] = Field(None, max_length=253)


class RadreplyResponse(RadreplyBase):
    """Schema for RADIUS reply responses"""
    id: int

    class Config:
        from_attributes = True


# Group check/reply schemas
class RadgroupcheckBase(BaseModel):
    """Base RADIUS group check schema"""
    groupname: str = Field(..., max_length=64, description="Group name")
    attribute: str = Field(..., max_length=64, description="RADIUS attribute name")
    op: RadiusOperator = Field(..., description="RADIUS operator")
    value: str = Field(..., max_length=253, description="Attribute value")


class RadgroupcheckCreate(RadgroupcheckBase):
    """Schema for creating RADIUS group check"""
    pass


class RadgroupcheckResponse(RadgroupcheckBase):
    """Schema for RADIUS group check responses"""
    id: int

    class Config:
        from_attributes = True


class RadgroupreplyBase(BaseModel):
    """Base RADIUS group reply schema"""
    groupname: str = Field(..., max_length=64, description="Group name")
    attribute: str = Field(..., max_length=64, description="RADIUS attribute name")
    op: RadiusOperator = Field(..., description="RADIUS operator")
    value: str = Field(..., max_length=253, description="Attribute value")


class RadgroupreplyCreate(RadgroupreplyBase):
    """Schema for creating RADIUS group reply"""
    pass


class RadgroupreplyResponse(RadgroupreplyBase):
    """Schema for RADIUS group reply responses"""
    id: int

    class Config:
        from_attributes = True


# Group management schemas
class GroupListResponse(BaseModel):
    """Group list response schema"""
    groups: List[str] = Field(..., description="List of group names")
    total: int = Field(..., description="Total number of groups")


class GroupAttributesResponse(BaseModel):
    """Group attributes response schema"""
    groupname: str = Field(..., description="Group name")
    check_attributes: List[RadgroupcheckResponse] = Field(..., description="Group check attributes")
    reply_attributes: List[RadgroupreplyResponse] = Field(..., description="Group reply attributes")
    total_attributes: int = Field(..., description="Total number of attributes")


class GroupStatisticsResponse(BaseModel):
    """Group statistics response schema"""
    total_groups: int = Field(..., description="Total number of groups")
    total_check_attributes: int = Field(..., description="Total number of check attributes")
    total_reply_attributes: int = Field(..., description="Total number of reply attributes")
    groups_with_attributes: int = Field(..., description="Number of groups with attributes")


# RADIUS Accounting schemas
class RadacctBase(BaseModel):
    """Base RADIUS accounting schema"""
    username: Optional[str] = Field(None, max_length=64, description="Username")
    realm: Optional[str] = Field(None, max_length=64, description="Realm")
    nas_ip_address: Optional[IPv4Address] = Field(None, description="NAS IP address")
    nas_port_id: Optional[str] = Field(None, max_length=32, description="NAS port ID")
    nas_port_type: Optional[str] = Field(None, max_length=32, description="NAS port type")
    acct_start_time: Optional[datetime] = Field(None, description="Session start time")
    acct_stop_time: Optional[datetime] = Field(None, description="Session stop time")
    acct_session_id: Optional[str] = Field(None, max_length=64, description="Session ID")
    acct_session_time: Optional[int] = Field(None, ge=0, description="Session duration in seconds")
    acct_authentic: Optional[str] = Field(None, max_length=32, description="Authentication method")
    connect_info_start: Optional[str] = Field(None, max_length=50, description="Start connection info")
    connect_info_stop: Optional[str] = Field(None, max_length=50, description="Stop connection info")
    acct_input_octets: Optional[int] = Field(None, ge=0, description="Input bytes")
    acct_output_octets: Optional[int] = Field(None, ge=0, description="Output bytes")
    called_station_id: Optional[str] = Field(None, max_length=50, description="Called station ID")
    calling_station_id: Optional[str] = Field(None, max_length=50, description="Calling station ID")
    acct_terminate_cause: Optional[StopCause] = Field(None, description="Termination cause")
    service_type: Optional[str] = Field(None, max_length=32, description="Service type")
    framed_protocol: Optional[str] = Field(None, max_length=32, description="Framed protocol")
    framed_ip_address: Optional[IPv4Address] = Field(None, description="Framed IP address")


class RadacctCreate(RadacctBase):
    """Schema for creating RADIUS accounting record"""
    acct_unique_id: str = Field(..., max_length=32, description="Unique accounting ID")
    

class RadacctUpdate(BaseModel):
    """Schema for updating RADIUS accounting record"""
    acct_stop_time: Optional[datetime] = None
    acct_session_time: Optional[int] = Field(None, ge=0)
    acct_input_octets: Optional[int] = Field(None, ge=0)
    acct_output_octets: Optional[int] = Field(None, ge=0)
    acct_terminate_cause: Optional[StopCause] = None
    connect_info_stop: Optional[str] = Field(None, max_length=50)


class RadacctResponse(RadacctBase):
    """Schema for RADIUS accounting responses"""
    radacctid: int
    acct_unique_id: str

    @property
    def session_duration_formatted(self) -> str:
        """Format session time as HH:MM:SS"""
        if not self.acct_session_time:
            return "00:00:00"
        
        hours = self.acct_session_time // 3600
        minutes = (self.acct_session_time % 3600) // 60
        seconds = self.acct_session_time % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def data_usage_mb(self) -> float:
        """Calculate total data usage in MB"""
        input_bytes = self.acct_input_octets or 0
        output_bytes = self.acct_output_octets or 0
        return (input_bytes + output_bytes) / (1024 * 1024)

    class Config:
        from_attributes = True


# NAS (Network Access Server) schemas
class NasBase(BaseModel):
    """Base NAS schema"""
    nasname: str = Field(..., max_length=128, description="NAS name/identifier")
    shortname: str = Field(..., max_length=32, description="Short name")
    type: str = Field(..., max_length=30, description="NAS type")
    ports: Optional[int] = Field(None, ge=0, description="Number of ports")
    secret: str = Field(..., max_length=60, description="Shared secret")
    server: Optional[str] = Field(None, max_length=64, description="Server address")
    community: Optional[str] = Field(None, max_length=50, description="SNMP community")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class NasCreate(NasBase):
    """Schema for creating NAS"""
    pass


class NasUpdate(BaseModel):
    """Schema for updating NAS"""
    shortname: Optional[str] = Field(None, max_length=32)
    type: Optional[str] = Field(None, max_length=30)
    ports: Optional[int] = Field(None, ge=0)
    secret: Optional[str] = Field(None, max_length=60)
    server: Optional[str] = Field(None, max_length=64)
    community: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class NasResponse(NasBase):
    """Schema for NAS responses"""
    id: int
    is_active: Optional[bool] = True
    last_seen: Optional[datetime] = None
    total_requests: Optional[int] = 0
    successful_requests: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NasListResponse(BaseModel):
    """Schema for NAS list responses"""
    devices: List[NasResponse]
    total: int
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    pages: int

    class Config:
        from_attributes = True


class NasMonitoringResponse(BaseModel):
    """Schema for NAS monitoring responses"""
    nas_id: int
    check_time: datetime
    ping_success: Optional[bool] = None
    ping_latency_ms: Optional[int] = None
    radius_auth_success: Optional[bool] = None
    radius_acct_success: Optional[bool] = None
    radius_response_time_ms: Optional[int] = None
    snmp_success: Optional[bool] = None
    cpu_usage_percent: Optional[int] = None
    memory_usage_percent: Optional[int] = None
    uptime_seconds: Optional[int] = None
    active_sessions: Optional[int] = None
    total_ports: Optional[int] = None
    status: str = "unknown"

    class Config:
        from_attributes = True


# Authentication schemas
class RadiusAuthRequest(BaseModel):
    """Schema for RADIUS authentication requests"""
    username: str = Field(..., max_length=64)
    password: str = Field(..., description="User password")
    nas_ip_address: Optional[IPv4Address] = None
    nas_port: Optional[int] = Field(None, ge=0, le=65535)
    calling_station_id: Optional[str] = Field(None, max_length=50)
    called_station_id: Optional[str] = Field(None, max_length=50)


class RadiusAuthResponse(BaseModel):
    """Schema for RADIUS authentication responses"""
    success: bool
    message: str
    reply_attributes: Dict[str, Any] = {}
    session_timeout: Optional[int] = None
    idle_timeout: Optional[int] = None


# Statistics and reporting schemas
class UserSessionStats(BaseModel):
    """User session statistics"""
    username: str
    total_sessions: int = 0
    active_sessions: int = 0
    total_session_time: int = 0  # in seconds
    total_input_octets: int = 0
    total_output_octets: int = 0
    last_session_start: Optional[datetime] = None
    last_session_stop: Optional[datetime] = None

    @property
    def total_data_usage_mb(self) -> float:
        """Total data usage in MB"""
        return (self.total_input_octets + self.total_output_octets) / (1024 * 1024)

    @property
    def average_session_time(self) -> int:
        """Average session time in seconds"""
        if self.total_sessions == 0:
            return 0
        # Exclude active sessions from average calculation
        completed_sessions = self.total_sessions - self.active_sessions
        if completed_sessions == 0:
            return 0
        return self.total_session_time // completed_sessions


class NasStats(BaseModel):
    """NAS statistics"""
    nas_name: str
    nas_ip: str
    total_sessions: int = 0
    active_sessions: int = 0
    total_users: int = 0
    total_data_usage_mb: float = 0.0


class SystemStats(BaseModel):
    """System-wide statistics"""
    total_users: int = 0
    active_users: int = 0
    total_sessions: int = 0
    active_sessions: int = 0
    total_nas: int = 0
    active_nas: int = 0
    total_data_usage_gb: float = 0.0
    today_sessions: int = 0
    today_data_usage_gb: float = 0.0


# Query/Filter schemas
class AccountingQuery(BaseModel):
    """Schema for accounting queries"""
    username: Optional[str] = None
    nas_ip_address: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_status: Optional[SessionStatus] = None
    calling_station_id: Optional[str] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class RadiusAttributeTemplate(BaseModel):
    """Template for common RADIUS attributes"""
    name: str = Field(..., max_length=64)
    description: str = Field(..., max_length=200)
    attribute_type: str = Field(..., description="check or reply")
    default_operator: RadiusOperator
    common_values: List[str] = []
    is_system: bool = Field(False, description="System-defined template")


# Batch operations
class BatchRadiusAttribute(BaseModel):
    """Schema for batch RADIUS attribute operations"""
    usernames: List[str] = Field(..., description="List of usernames")
    attributes: List[Dict[str, Any]] = Field(..., description="List of attributes to apply")
    operation: str = Field(..., description="add, update, or delete")


class BulkAccountingImport(BaseModel):
    """Schema for bulk accounting data import"""
    accounting_records: List[RadacctCreate] = Field(..., max_items=1000)
    validate_only: bool = Field(False, description="Only validate, don't import")
    update_existing: bool = Field(False, description="Update existing records")