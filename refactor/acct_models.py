"""
daloRADIUS Accounting Module Data Models

This module contains Pydantic models for all data structures used in the Accounting functionality.
These models represent the data structures from the PHP files in app/operators/acct-*.php files.

Models follow SOLID principles:
- SRP: Each model has a single responsibility 
- OCP: Models are extensible through inheritance
- DIP: Models depend on abstractions (base classes)
- ISP: Interfaces are segregated by functionality
- LSP: Derived models can replace base models
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from ipaddress import IPv4Address


class BaseAcctModel(BaseModel):
    """Base model for all accounting-related data structures"""
    
    class Config:
        # Enable ORM mode for database integration
        orm_mode = True
        # Use enum values instead of enum names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Validate assignments
        validate_assignment = True


class SortOrder(str, Enum):
    """Sort order enumeration - follows ISP principle"""
    ASC = "asc"
    DESC = "desc"


class TerminateCause(str, Enum):
    """RADIUS session termination causes - follows OCP principle for extension"""
    UNKNOWN = "Unknown"
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


class RadiusAttribute(str, Enum):
    """RADIUS attributes - follows ISP principle"""
    MAX_ALL_SESSION = "Max-All-Session"
    MAX_DAILY_SESSION = "Max-Daily-Session"
    MAX_WEEKLY_SESSION = "Max-Weekly-Session"
    MAX_MONTHLY_SESSION = "Max-Monthly-Session"
    EXPIRATION = "Expiration"
    SESSION_TIMEOUT = "Session-Timeout"
    IDLE_TIMEOUT = "Idle-Timeout"
    ACCT_INTERIM_INTERVAL = "Acct-Interim-Interval"
    SIMULTANEOUS_USE = "Simultaneous-Use"


# =====================================================================
# Core Accounting Record Models - SRP: Single responsibility per model
# =====================================================================

class RadiusAccountingRecord(BaseAcctModel):
    """
    Core RADIUS accounting record model
    Maps to radacct table structure
    """
    radacctid: Optional[int] = Field(None, alias="RadAcctId", description="Unique accounting record ID")
    username: str = Field(..., description="Username of the session")
    realm: Optional[str] = Field(None, description="Realm/domain of the user")
    session_id: str = Field(..., alias="acctsessionid", description="Unique session identifier")
    nas_ip_address: IPv4Address = Field(..., alias="NASIPAddress", description="NAS device IP address")
    nas_port_id: Optional[str] = Field(None, alias="nasportid", description="NAS port identifier")
    nas_port_type: Optional[str] = Field(None, alias="nasporttype", description="NAS port type")
    framed_ip_address: Optional[IPv4Address] = Field(None, alias="FramedIPAddress", description="User's assigned IP address")
    calling_station_id: Optional[str] = Field(None, alias="callingstationid", description="Client MAC address")
    called_station_id: Optional[str] = Field(None, alias="calledstationid", description="NAS MAC address/SSID")
    start_time: Optional[datetime] = Field(None, alias="AcctStartTime", description="Session start timestamp")
    stop_time: Optional[datetime] = Field(None, alias="AcctStopTime", description="Session stop timestamp")
    session_time: Optional[int] = Field(None, alias="AcctSessionTime", description="Session duration in seconds")
    input_octets: Optional[int] = Field(None, alias="AcctInputOctets", description="Bytes received from user")
    output_octets: Optional[int] = Field(None, alias="AcctOutputOctets", description="Bytes sent to user")
    input_packets: Optional[int] = Field(None, alias="acctinputpackets", description="Packets received from user")
    output_packets: Optional[int] = Field(None, alias="acctoutputpackets", description="Packets sent to user")
    terminate_cause: Optional[TerminateCause] = Field(None, alias="AcctTerminateCause", description="Session termination reason")
    nas_identifier: Optional[str] = Field(None, alias="nasidentifier", description="NAS identifier string")
    unique_id: Optional[str] = Field(None, alias="acctuniqueid", description="Unique session identifier")
    class_attribute: Optional[str] = Field(None, alias="class", description="Class attribute")
    
    @validator('session_time')
    def validate_session_time(cls, v):
        """Ensure session time is non-negative"""
        if v is not None and v < 0:
            raise ValueError('Session time must be non-negative')
        return v
    
    @validator('input_octets', 'output_octets', 'input_packets', 'output_packets')
    def validate_counters(cls, v):
        """Ensure traffic counters are non-negative"""
        if v is not None and v < 0:
            raise ValueError('Traffic counters must be non-negative')
        return v
    
    @validator('terminate_cause', pre=True)
    def normalize_terminate_cause(cls, v):
        """Normalize terminate cause - convert '0' to 'Unknown'"""
        if v == '0' or v == 0:
            return TerminateCause.UNKNOWN
        return v


class HotspotInfo(BaseAcctModel):
    """
    Hotspot information model
    Maps to dalohotspots table structure - SRP principle
    """
    id: Optional[int] = Field(None, description="Hotspot unique ID")
    name: str = Field(..., description="Hotspot name")
    mac_address: Optional[str] = Field(None, alias="mac", description="Hotspot MAC address")
    location: Optional[str] = Field(None, description="Physical location")
    description: Optional[str] = Field(None, description="Hotspot description")
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        """Validate MAC address format if provided"""
        if v and v.strip():
            # Basic MAC address validation (allowing different formats)
            import re
            mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            if not re.match(mac_pattern, v):
                # Try alternative format without separators
                if not re.match(r'^[0-9A-Fa-f]{12}$', v.replace(':', '').replace('-', '')):
                    raise ValueError('Invalid MAC address format')
        return v


class AccountingRecordWithHotspot(RadiusAccountingRecord):
    """
    Extended accounting record with hotspot information
    Follows OCP principle - extends base without modification
    """
    hotspot: Optional[HotspotInfo] = Field(None, description="Associated hotspot information")


# =====================================================================
# Query Parameter Models - ISP: Interface segregation by query type
# =====================================================================

class BaseQueryParams(BaseAcctModel):
    """Base query parameters - follows ISP principle"""
    order_by: str = Field("acctstarttime", description="Field to order by")
    order_type: SortOrder = Field(SortOrder.DESC, description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Records per page")


class DateRangeParams(BaseAcctModel):
    """Date range query parameters - follows SRP principle"""
    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")
    
    @root_validator
    def validate_date_range(cls, values):
        """Ensure end date is after start date"""
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise ValueError('End date must be after start date')
        return values


class UsernameQueryParams(BaseQueryParams):
    """Username-specific query parameters"""
    username: Optional[str] = Field(None, description="Username to filter by")


class IPAddressQueryParams(BaseQueryParams):
    """IP address query parameters"""
    framed_ip_address: Optional[IPv4Address] = Field(None, description="IP address to filter by")


class NASQueryParams(BaseQueryParams):
    """NAS-specific query parameters"""
    nas_ip_address: Optional[IPv4Address] = Field(None, description="NAS IP address to filter by")


class HotspotQueryParams(BaseQueryParams):
    """Hotspot query parameters"""
    hotspot: Optional[List[str]] = Field(None, description="List of hotspot names")
    
    @validator('hotspot', pre=True)
    def clean_hotspot_names(cls, v):
        """Clean hotspot names by removing % characters and empty values"""
        if not v:
            return v
        if isinstance(v, str):
            v = [v]
        cleaned = []
        for item in v:
            if item:
                clean_item = item.replace('%', '').strip()
                if clean_item and clean_item not in cleaned:
                    cleaned.append(clean_item)
        return cleaned or None


class DateRangeQueryParams(BaseQueryParams, DateRangeParams):
    """Combined date range and base query parameters"""
    pass


class ActiveUserQueryParams(BaseQueryParams, DateRangeParams):
    """Active user query parameters"""
    username: Optional[str] = Field(None, description="Username to filter by")


class PlansUsageQueryParams(BaseQueryParams, DateRangeParams):
    """Plans usage query parameters"""
    username: Optional[str] = Field(None, description="Username to filter by")
    plan_name: Optional[str] = Field(None, alias="planname", description="Plan name to filter by")


class DateRangeAccountingQueryParams(BaseQueryParams, DateRangeParams):
    """Date range accounting query parameters with username filter"""
    username: Optional[str] = Field(None, description="Username to filter by")
    
    @validator('username')
    def clean_username(cls, v):
        """Clean username by removing % characters"""
        if v:
            return v.replace('%', '').strip()
        return v


# =====================================================================
# Response Models - SRP: Single responsibility for different responses
# =====================================================================

class PaginationInfo(BaseAcctModel):
    """Pagination information model"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
    total_records: int = Field(..., description="Total number of records")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class BaseListResponse(BaseAcctModel):
    """Base response model for list endpoints"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("", description="Response message")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")


class AccountingRecordListResponse(BaseListResponse):
    """Response model for accounting record lists"""
    records: List[RadiusAccountingRecord] = Field([], description="List of accounting records")


class HotspotAccountingResponse(BaseListResponse):
    """Response model for hotspot accounting data"""
    records: List[AccountingRecordWithHotspot] = Field([], description="Accounting records with hotspot info")


# =====================================================================
# Active Users Models - SRP: Dedicated models for active user tracking
# =====================================================================

class UserSessionStatus(str, Enum):
    """User session status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    ENDED = "ended"
    QUOTA_EXCEEDED = "quota_exceeded"
    TIME_EXCEEDED = "time_exceeded"


class ActiveUserRecord(BaseAcctModel):
    """Active user record with usage information"""
    username: str = Field(..., description="Username")
    attribute: RadiusAttribute = Field(..., description="RADIUS attribute name")
    max_time_expiration: Optional[Union[int, str]] = Field(None, description="Maximum allowed session time or expiration date")
    used_time: int = Field(0, description="Total used time in seconds")
    status: UserSessionStatus = Field(..., description="Current session status")
    usage_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Usage percentage")
    time_left: Optional[int] = Field(None, description="Time left in seconds (for time-based attributes)")
    days_until_expiration: Optional[int] = Field(None, description="Days until expiration (for date-based attributes)")
    
    @validator('max_time_expiration')
    def validate_max_time_expiration(cls, v, values):
        """Validate max_time_expiration based on attribute type"""
        attribute = values.get('attribute')
        if attribute == RadiusAttribute.EXPIRATION:
            # For expiration attribute, this should be a date string
            if isinstance(v, int):
                raise ValueError('Expiration attribute should have date value, not integer')
        elif attribute == RadiusAttribute.MAX_ALL_SESSION:
            # For time-based attributes, this should be an integer
            if isinstance(v, str):
                try:
                    return int(v)
                except ValueError:
                    raise ValueError('Time-based attribute should have integer value')
        return v
    
    @validator('usage_percentage')
    def calculate_usage_percentage(cls, v, values):
        """Calculate usage percentage based on used time and max expiration"""
        attribute = values.get('attribute')
        max_time = values.get('max_time_expiration')
        used_time = values.get('used_time', 0)
        
        if attribute == RadiusAttribute.MAX_ALL_SESSION and max_time and isinstance(max_time, int) and max_time > 0:
            return min((used_time / max_time) * 100, 100.0)
        return 0.0


class ActiveUsersResponse(BaseListResponse):
    """Response model for active users query"""
    users: List[ActiveUserRecord] = Field([], description="List of active users")


# =====================================================================
# Plans and Usage Models - SRP: Dedicated models for plan management
# =====================================================================

class PlanInfo(BaseAcctModel):
    """Plan information model"""
    plan_name: str = Field(..., description="Plan name")
    plan_type: Optional[str] = Field(None, description="Plan type")
    time_bank: Optional[int] = Field(None, alias="plantimebank", description="Total time allowance in seconds")
    time_type: Optional[str] = Field(None, alias="planTimeType", description="Plan time type")
    data_bank: Optional[int] = Field(None, description="Total data allowance in bytes")


class UserPlanUsage(BaseAcctModel):
    """User plan usage model"""
    username: str = Field(..., description="Username")
    plan_name: str = Field(..., alias="planname", description="Associated plan name")
    session_time: int = Field(0, alias="sessiontime", description="Total session time used")
    plan_time_bank: Optional[int] = Field(None, alias="plantimebank", description="Plan time allowance")
    plan_time_type: Optional[str] = Field(None, alias="planTimeType", description="Plan time type")
    upload_octets: int = Field(0, alias="upload", description="Total upload bytes")
    download_octets: int = Field(0, alias="download", description="Total download bytes") 
    total_traffic: int = Field(0, description="Total traffic (input + output octets)")
    usage_percentage: float = Field(0.0, ge=0.0, description="Time usage percentage")
    
    @validator('total_traffic', always=True)
    def calculate_total_traffic(cls, v, values):
        """Calculate total traffic from upload and download"""
        upload = values.get('upload_octets', 0)
        download = values.get('download_octets', 0)
        return upload + download
    
    @validator('usage_percentage', always=True)
    def calculate_usage_percentage(cls, v, values):
        """Calculate usage percentage based on session time and plan time bank"""
        session_time = values.get('session_time', 0)
        plan_time_bank = values.get('plan_time_bank')
        if plan_time_bank and plan_time_bank > 0:
            return (session_time / plan_time_bank) * 100
        return 0.0
    
    @validator('total_traffic')
    def ensure_positive_traffic(cls, v):
        """Ensure total traffic is non-negative"""
        return max(0, v or 0)


class PlansUsageResponse(BaseListResponse):
    """Response model for plans usage query"""
    usage_records: List[UserPlanUsage] = Field([], description="List of plan usage records")


# =====================================================================
# Maintenance Models - SRP: Dedicated models for maintenance operations
# =====================================================================

class CleanupOperation(BaseAcctModel):
    """Cleanup operation parameters"""
    username: Optional[str] = Field(None, description="Username to clean up stale sessions for")
    end_date: Optional[date] = Field(None, alias="enddate", description="Cleanup records before this date")
    cleanup_type: str = Field("stale_sessions", description="Type of cleanup operation")
    
    @root_validator
    def validate_cleanup_params(cls, values):
        """Ensure either username or end_date is provided"""
        username = values.get('username')
        end_date = values.get('end_date')
        if not username and not end_date:
            raise ValueError('Either username or end_date must be provided')
        return values


class CleanupResult(BaseAcctModel):
    """Cleanup operation result"""
    success: bool = Field(..., description="Whether cleanup was successful")
    message: str = Field(..., description="Result message")
    records_affected: int = Field(0, description="Number of records affected")
    operation_type: str = Field(..., description="Type of operation performed")
    username: Optional[str] = Field(None, description="Username that was cleaned up")
    end_date: Optional[date] = Field(None, description="End date used for cleanup")


class DeleteOperation(BaseAcctModel):
    """Delete operation parameters"""
    delete_type: str = Field(..., description="Type of deletion")
    date_criteria: Optional[date] = Field(None, description="Date criteria for deletion")
    username: Optional[str] = Field(None, description="Username filter for deletion")
    confirmed: bool = Field(False, description="Confirmation flag")


class DeleteResult(BaseAcctModel):
    """Delete operation result"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Result message")
    records_deleted: int = Field(0, description="Number of records deleted")
    operation_type: str = Field(..., description="Type of operation performed")


# =====================================================================
# Statistics and Aggregation Models - SRP: Dedicated statistical models
# =====================================================================

class TrafficStatistics(BaseAcctModel):
    """Traffic statistics model"""
    total_input_octets: int = Field(0, description="Total input octets")
    total_output_octets: int = Field(0, description="Total output octets")
    total_input_packets: int = Field(0, description="Total input packets")
    total_output_packets: int = Field(0, description="Total output packets")
    average_session_time: float = Field(0.0, description="Average session time")
    total_sessions: int = Field(0, description="Total number of sessions")


class UsageStatistics(BaseAcctModel):
    """Usage statistics model"""
    username: str = Field(..., description="Username")
    total_session_time: int = Field(0, description="Total session time in seconds")
    total_traffic: int = Field(0, description="Total traffic in bytes")
    session_count: int = Field(0, description="Number of sessions")
    first_session: Optional[datetime] = Field(None, description="First session timestamp")
    last_session: Optional[datetime] = Field(None, description="Last session timestamp")
    traffic_stats: TrafficStatistics = Field(default_factory=TrafficStatistics, description="Detailed traffic statistics")


class AccountingStatisticsResponse(BaseAcctModel):
    """Response model for accounting statistics"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("Statistics retrieved successfully", description="Response message")
    statistics: List[UsageStatistics] = Field([], description="List of usage statistics")
    summary: TrafficStatistics = Field(default_factory=TrafficStatistics, description="Summary statistics")


# =====================================================================
# Custom Query Models - OCP: Open for extension with custom queries
# =====================================================================

class CustomQueryParams(BaseAcctModel):
    """Custom query parameters"""
    query: str = Field(..., description="Custom SQL query string")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")


class CustomQueryResult(BaseAcctModel):
    """Custom query result"""
    success: bool = Field(..., description="Whether query was successful")
    message: str = Field(..., description="Result message")
    columns: List[str] = Field([], description="Column names")
    data: List[List[Any]] = Field([], description="Query result data")
    row_count: int = Field(0, description="Number of rows returned")


# =====================================================================
# Export Models - SRP: Dedicated models for data export
# =====================================================================

class ExportFormat(str, Enum):
    """Export format enumeration"""
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    JSON = "json"


class ExportParams(BaseAcctModel):
    """Export parameters"""
    format: ExportFormat = Field(ExportFormat.CSV, description="Export format")
    table: str = Field(..., description="Table to export")
    query: Optional[str] = Field(None, description="Custom query for export")
    filename: Optional[str] = Field(None, description="Custom filename")


class ExportResult(BaseAcctModel):
    """Export operation result"""
    success: bool = Field(..., description="Whether export was successful")
    message: str = Field(..., description="Result message")
    file_path: Optional[str] = Field(None, description="Path to exported file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    record_count: int = Field(0, description="Number of records exported")


# =====================================================================
# Error Models - SRP: Dedicated error handling
# =====================================================================

class ValidationError(BaseAcctModel):
    """Validation error model"""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class ErrorResponse(BaseAcctModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    errors: Optional[List[ValidationError]] = Field(None, description="List of validation errors")
    error_code: Optional[str] = Field(None, description="Error code")


# =====================================================================
# Model Registry - DIP: Dependency inversion for model factory
# =====================================================================

class AcctModelRegistry:
    """
    Registry for all accounting models
    Follows DIP principle - provides abstraction for model creation
    """
    
    _models = {
        # Core models
        'radius_accounting_record': RadiusAccountingRecord,
        'hotspot_info': HotspotInfo,
        'accounting_record_with_hotspot': AccountingRecordWithHotspot,
        
        # Query parameter models
        'username_query_params': UsernameQueryParams,
        'ip_address_query_params': IPAddressQueryParams,
        'nas_query_params': NASQueryParams,
        'hotspot_query_params': HotspotQueryParams,
        'date_range_query_params': DateRangeQueryParams,
        'date_range_accounting_query_params': DateRangeAccountingQueryParams,
        'active_user_query_params': ActiveUserQueryParams,
        'plans_usage_query_params': PlansUsageQueryParams,
        
        # Response models
        'accounting_record_list_response': AccountingRecordListResponse,
        'hotspot_accounting_response': HotspotAccountingResponse,
        'active_users_response': ActiveUsersResponse,
        'plans_usage_response': PlansUsageResponse,
        'accounting_statistics_response': AccountingStatisticsResponse,
        
        # Operation models
        'cleanup_operation': CleanupOperation,
        'cleanup_result': CleanupResult,
        'delete_operation': DeleteOperation,
        'delete_result': DeleteResult,
        
        # Export models
        'export_params': ExportParams,
        'export_result': ExportResult,
        
        # Error models
        'error_response': ErrorResponse,
        'validation_error': ValidationError,
        
        # Custom query models
        'custom_query_params': CustomQueryParams,
        'custom_query_result': CustomQueryResult,
    }
    
    @classmethod
    def get_model(cls, model_name: str) -> BaseAcctModel:
        """Get model class by name - follows DIP principle"""
        if model_name not in cls._models:
            raise ValueError(f"Unknown model: {model_name}")
        return cls._models[model_name]
    
    @classmethod
    def list_models(cls) -> List[str]:
        """List all available model names"""
        return list(cls._models.keys())
    
    @classmethod
    def register_model(cls, name: str, model_class: type):
        """Register a new model - follows OCP principle"""
        if not issubclass(model_class, BaseAcctModel):
            raise ValueError("Model must inherit from BaseAcctModel")
        cls._models[name] = model_class


# Export all models for easy importing
__all__ = [
    # Base classes
    'BaseAcctModel',
    
    # Enums
    'SortOrder',
    'TerminateCause', 
    'RadiusAttribute',
    'UserSessionStatus',
    'ExportFormat',
    
    # Core models
    'RadiusAccountingRecord',
    'HotspotInfo', 
    'AccountingRecordWithHotspot',
    
    # Query parameter models
    'BaseQueryParams',
    'DateRangeParams',
    'UsernameQueryParams',
    'IPAddressQueryParams', 
    'NASQueryParams',
    'HotspotQueryParams',
    'DateRangeQueryParams',
    'DateRangeAccountingQueryParams',
    'ActiveUserQueryParams',
    'PlansUsageQueryParams',
    
    # Response models
    'PaginationInfo',
    'BaseListResponse',
    'AccountingRecordListResponse',
    'HotspotAccountingResponse',
    'ActiveUsersResponse',
    'PlansUsageResponse',
    'AccountingStatisticsResponse',
    
    # Active users models
    'ActiveUserRecord',
    
    # Plans models
    'PlanInfo',
    'UserPlanUsage',
    
    # Maintenance models
    'CleanupOperation',
    'CleanupResult',
    'DeleteOperation', 
    'DeleteResult',
    
    # Statistics models
    'TrafficStatistics',
    'UsageStatistics',
    
    # Custom query models
    'CustomQueryParams',
    'CustomQueryResult',
    
    # Export models
    'ExportParams',
    'ExportResult',
    
    # Error models
    'ValidationError',
    'ErrorResponse',
    
    # Registry
    'AcctModelRegistry',
]