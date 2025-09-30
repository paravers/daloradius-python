"""
Accounting Schemas

This module provides Pydantic schemas for accounting/session statistics
and reporting functionality, supporting various accounting queries and analytics.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
import enum


class SessionStatusEnum(str, enum.Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    STOPPED = "stopped"
    EXPIRED = "expired"


class AccountingTimeRangeEnum(str, enum.Enum):
    """Time range for accounting queries"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    CUSTOM = "custom"


# =====================================================================
# Base Accounting Schemas
# =====================================================================

class RadAcctBase(BaseModel):
    """Base schema for RADIUS accounting records"""
    username: Optional[str] = Field(None, description="Username")
    realm: Optional[str] = Field(None, description="Authentication realm")
    acctsessionid: Optional[str] = Field(None, description="Session ID")
    acctuniqueid: Optional[str] = Field(None, description="Unique session ID")
    groupname: Optional[str] = Field(None, description="User group")
    nasipaddress: Optional[str] = Field(None, description="NAS IP address")
    nasportid: Optional[str] = Field(None, description="NAS port ID")
    nasporttype: Optional[str] = Field(None, description="NAS port type")
    calledstationid: Optional[str] = Field(None, description="Called station ID")
    callingstationid: Optional[str] = Field(None, description="Calling station ID")
    framedipaddress: Optional[str] = Field(None, description="Framed IP address")
    servicetype: Optional[str] = Field(None, description="Service type")
    acctstarttime: Optional[datetime] = Field(None, description="Session start time")
    acctstoptime: Optional[datetime] = Field(None, description="Session stop time")
    acctsessiontime: Optional[int] = Field(None, description="Session duration in seconds")
    acctinputoctets: Optional[int] = Field(0, description="Input bytes")
    acctoutputoctets: Optional[int] = Field(0, description="Output bytes")
    acctinputpackets: Optional[int] = Field(0, description="Input packets")
    acctoutputpackets: Optional[int] = Field(0, description="Output packets")
    acctterminatecause: Optional[str] = Field(None, description="Termination cause")


class RadAcctResponse(RadAcctBase):
    """Schema for accounting record responses"""
    radacctid: int = Field(..., description="Accounting record ID")
    
    # Computed properties
    total_bytes: Optional[int] = Field(None, description="Total bytes transferred")
    total_packets: Optional[int] = Field(None, description="Total packets transferred")
    is_active: Optional[bool] = Field(None, description="Is session active")
    formatted_duration: Optional[str] = Field(None, description="Human readable duration")
    
    class Config:
        from_attributes = True


class RadAcctCreate(RadAcctBase):
    """Schema for creating accounting records"""
    username: str = Field(..., description="Username is required")
    acctsessionid: str = Field(..., description="Session ID is required")
    acctuniqueid: str = Field(..., description="Unique session ID is required")
    nasipaddress: str = Field(..., description="NAS IP address is required")


class RadAcctUpdate(BaseModel):
    """Schema for updating accounting records"""
    acctstoptime: Optional[datetime] = None
    acctsessiontime: Optional[int] = None
    acctinputoctets: Optional[int] = None
    acctoutputoctets: Optional[int] = None
    acctinputpackets: Optional[int] = None
    acctoutputpackets: Optional[int] = None
    acctterminatecause: Optional[str] = None


# =====================================================================
# Query and Filter Schemas
# =====================================================================

class AccountingQueryFilters(BaseModel):
    """Filters for accounting queries"""
    username: Optional[str] = Field(None, description="Filter by username")
    groupname: Optional[str] = Field(None, description="Filter by group name")
    nasipaddress: Optional[str] = Field(None, description="Filter by NAS IP address")
    framedipaddress: Optional[str] = Field(None, description="Filter by framed IP address")
    callingstationid: Optional[str] = Field(None, description="Filter by calling station ID")
    servicetype: Optional[str] = Field(None, description="Filter by service type")
    
    # Time range filters
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    time_range: Optional[AccountingTimeRangeEnum] = Field(None, description="Predefined time range")
    
    # Session status filters
    status: Optional[SessionStatusEnum] = Field(None, description="Session status")
    active_only: Optional[bool] = Field(False, description="Show only active sessions")
    
    # Traffic filters
    min_input_octets: Optional[int] = Field(None, description="Minimum input bytes")
    max_input_octets: Optional[int] = Field(None, description="Maximum input bytes")
    min_output_octets: Optional[int] = Field(None, description="Minimum output bytes")
    max_output_octets: Optional[int] = Field(None, description="Maximum output bytes")
    min_session_time: Optional[int] = Field(None, description="Minimum session duration")
    max_session_time: Optional[int] = Field(None, description="Maximum session duration")


class AccountingQuery(BaseModel):
    """Complete accounting query with filters and pagination"""
    filters: Optional[AccountingQueryFilters] = Field(default_factory=AccountingQueryFilters)
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Page size")
    sort_field: str = Field("acctstarttime", description="Sort field")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")


# =====================================================================
# Statistics and Analytics Schemas
# =====================================================================

class SessionStatistics(BaseModel):
    """Session statistics summary"""
    total_sessions: int = Field(0, description="Total sessions")
    active_sessions: int = Field(0, description="Active sessions")
    completed_sessions: int = Field(0, description="Completed sessions")
    average_session_duration: Optional[int] = Field(None, description="Average session duration in seconds")
    total_session_time: int = Field(0, description="Total session time in seconds")
    unique_users: int = Field(0, description="Number of unique users")


class TrafficStatistics(BaseModel):
    """Traffic statistics summary"""
    total_input_octets: int = Field(0, description="Total input bytes")
    total_output_octets: int = Field(0, description="Total output bytes")
    total_bytes: int = Field(0, description="Total bytes transferred")
    total_input_packets: int = Field(0, description="Total input packets")
    total_output_packets: int = Field(0, description="Total output packets")
    total_packets: int = Field(0, description="Total packets transferred")
    average_throughput: Optional[float] = Field(None, description="Average throughput in bytes/second")


class UserTrafficSummaryResponse(BaseModel):
    """User traffic summary response"""
    username: str = Field(..., description="Username")
    summary_date: date = Field(..., description="Summary date")
    total_sessions: int = Field(0, description="Total sessions")
    total_session_time: int = Field(0, description="Total session time")
    total_input_octets: int = Field(0, description="Total input bytes")
    total_output_octets: int = Field(0, description="Total output bytes")
    total_input_packets: int = Field(0, description="Total input packets")
    total_output_packets: int = Field(0, description="Total output packets")
    avg_session_time: Optional[int] = Field(None, description="Average session time")
    avg_throughput: Optional[int] = Field(None, description="Average throughput")
    peak_input_rate: Optional[int] = Field(None, description="Peak input rate")
    peak_output_rate: Optional[int] = Field(None, description="Peak output rate")
    first_session_start: Optional[datetime] = Field(None, description="First session start time")
    last_session_stop: Optional[datetime] = Field(None, description="Last session stop time")
    
    class Config:
        from_attributes = True


class NasTrafficSummaryResponse(BaseModel):
    """NAS traffic summary response"""
    nasipaddress: str = Field(..., description="NAS IP address")
    summary_date: date = Field(..., description="Summary date")
    total_sessions: int = Field(0, description="Total sessions")
    active_sessions: int = Field(0, description="Active sessions")
    completed_sessions: int = Field(0, description="Completed sessions")
    total_input_octets: int = Field(0, description="Total input bytes")
    total_output_octets: int = Field(0, description="Total output bytes")
    avg_session_duration: Optional[int] = Field(None, description="Average session duration")
    peak_concurrent_sessions: Optional[int] = Field(None, description="Peak concurrent sessions")
    
    class Config:
        from_attributes = True


class AccountingOverview(BaseModel):
    """Comprehensive accounting overview"""
    session_stats: SessionStatistics = Field(..., description="Session statistics")
    traffic_stats: TrafficStatistics = Field(..., description="Traffic statistics")
    time_period: str = Field(..., description="Time period description")
    last_updated: datetime = Field(..., description="Last update time")


# =====================================================================
# Report Schemas
# =====================================================================

class TopUsersReport(BaseModel):
    """Top users by traffic report"""
    username: str = Field(..., description="Username")
    total_sessions: int = Field(0, description="Total sessions")
    total_bytes: int = Field(0, description="Total bytes transferred")
    total_session_time: int = Field(0, description="Total session time")
    last_session: Optional[datetime] = Field(None, description="Last session time")
    rank: int = Field(..., description="Ranking position")


class HourlyTrafficReport(BaseModel):
    """Hourly traffic distribution report"""
    hour: int = Field(..., description="Hour of day (0-23)")
    session_count: int = Field(0, description="Number of sessions")
    total_bytes: int = Field(0, description="Total bytes in this hour")
    unique_users: int = Field(0, description="Unique users in this hour")


class DailyTrafficReport(BaseModel):
    """Daily traffic report"""
    date: date = Field(..., description="Report date")
    session_count: int = Field(0, description="Number of sessions")
    total_bytes: int = Field(0, description="Total bytes")
    unique_users: int = Field(0, description="Unique users")
    peak_concurrent_sessions: int = Field(0, description="Peak concurrent sessions")


class NasUsageReport(BaseModel):
    """NAS usage statistics report"""
    nasipaddress: str = Field(..., description="NAS IP address")
    nas_name: Optional[str] = Field(None, description="NAS name")
    total_sessions: int = Field(0, description="Total sessions")
    active_sessions: int = Field(0, description="Active sessions")
    total_bytes: int = Field(0, description="Total bytes")
    utilization_percentage: float = Field(0.0, description="Utilization percentage")


class CustomQueryResult(BaseModel):
    """Custom query result"""
    columns: List[str] = Field(..., description="Column names")
    rows: List[List[Any]] = Field(..., description="Result rows")
    total_rows: int = Field(..., description="Total number of rows")
    execution_time: float = Field(..., description="Query execution time in seconds")


# =====================================================================
# Maintenance Schemas
# =====================================================================

class MaintenanceOperation(BaseModel):
    """Maintenance operation parameters"""
    operation_type: str = Field(..., description="Operation type")
    target_table: Optional[str] = Field(None, description="Target table")
    date_before: Optional[datetime] = Field(None, description="Delete records before this date")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional conditions")
    dry_run: bool = Field(True, description="Dry run mode")


class MaintenanceResult(BaseModel):
    """Maintenance operation result"""
    operation_type: str = Field(..., description="Operation type")
    affected_rows: int = Field(..., description="Number of affected rows")
    execution_time: float = Field(..., description="Execution time in seconds")
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Result message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


# =====================================================================
# Paginated Response Schemas
# =====================================================================

class PaginatedAccountingResponse(BaseModel):
    """Paginated accounting records response"""
    data: List[RadAcctResponse] = Field(..., description="Accounting records")
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class PaginatedTopUsersResponse(BaseModel):
    """Paginated top users response"""
    data: List[TopUsersReport] = Field(..., description="Top users data")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")


# Export schemas
__all__ = [
    "SessionStatusEnum",
    "AccountingTimeRangeEnum",
    "RadAcctBase",
    "RadAcctResponse", 
    "RadAcctCreate",
    "RadAcctUpdate",
    "AccountingQueryFilters",
    "AccountingQuery",
    "SessionStatistics",
    "TrafficStatistics",
    "UserTrafficSummaryResponse",
    "NasTrafficSummaryResponse",
    "AccountingOverview",
    "TopUsersReport",
    "HourlyTrafficReport",
    "DailyTrafficReport",
    "NasUsageReport",
    "CustomQueryResult",
    "MaintenanceOperation",
    "MaintenanceResult",
    "PaginatedAccountingResponse",
    "PaginatedTopUsersResponse",
]