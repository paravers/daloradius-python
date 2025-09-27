"""
daloRADIUS Reports Module Data Models

This module contains Pydantic models for all data structures used in the Reports functionality.
These models represent the data structures from the PHP files in app/operators/rep-*.php files.

Models follow SOLID principles:
- SRP: Each model has a single responsibility 
- OCP: Models are extensible through inheritance
- DIP: Models depend on abstractions (base classes)
- ISP: Interfaces are segregated by functionality
- LSP: Derived models can replace base models

Reports Covered:
- rep-main.php: Main reports dashboard
- rep-online.php: Online users from radacct table (active sessions)
- rep-topusers.php: Top users by traffic/time from radacct aggregation
- rep-username.php: User-specific RADIUS attributes from radcheck/radreply
- rep-newusers.php: New user registration statistics from dalouserinfo
- rep-lastconnect.php: Authentication attempts from radpostauth table
- rep-history.php: System history from multiple dalo* tables
- rep-batch-list.php: Batch user creation summary from dalobatchhistory
- rep-batch-details.php: Detailed batch user information
- rep-logs-*.php: Log file display (radius, daloradius, system, boot)
- rep-hb-dashboard.php: Heartbeat monitoring from dalonode table
- rep-stat-*.php: System statistics (server info via libraries)

Database Tables Used:
- radacct: Accounting records for online users and top users
- radpostauth: Authentication attempts for last connect report
- radcheck/radreply: User attributes for username report
- dalouserinfo: User information for new users report
- dalobatchhistory: Batch creation history
- dalouserbillinfo: User billing information for batch details
- dalonode: Node heartbeat information
- daloproxys, dalorealms, dalooperators, etc.: System history
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from ipaddress import IPv4Address, IPv6Address


class BaseReportModel(BaseModel):
    """Base model for all report-related data structures"""
    
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


class ReportType(str, Enum):
    """Report type enumeration for session management"""
    ONLINE_USERS = "reportsOnlineUsers"
    TOP_USERS = "TopUsers"
    NEW_USERS = "newUsers"
    LAST_CONNECTION_ATTEMPTS = "reportsLastConnectionAttempts"
    BATCH_LIST = "reportsBatchList"
    BATCH_DETAILS = "batchDetails"
    USERNAME_ATTRIBUTES = "usernameAttributes"
    SYSTEM_HISTORY = "systemHistory"
    HEARTBEAT_DASHBOARD = "heartbeatDashboard"
    SERVER_STATISTICS = "serverStatistics"
    LOG_FILES = "logFiles"


class TerminateCause(str, Enum):
    """RADIUS session termination causes"""
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


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"
    EMERGENCY = "EMERGENCY"


class StatType(str, Enum):
    """Statistics type enumeration"""
    SERVER = "server"
    UPS = "ups"
    SERVICES = "services"
    RAID = "raid"
    NETWORK = "network"
    DISK = "disk"
    MEMORY = "memory"
    CPU = "cpu"


# ============================================================================
# Online Users Report Models (rep-online.php)
# ============================================================================

class OnlineUserRecord(BaseReportModel):
    """Model for online user records from radacct table"""
    
    username: str = Field(..., description="RADIUS username")
    firstname: Optional[str] = Field(None, description="User first name from userinfo")
    lastname: Optional[str] = Field(None, description="User last name from userinfo")
    framedipaddress: Optional[Union[IPv4Address, IPv6Address]] = Field(
        None, description="Framed IP address assigned to user"
    )
    callingstationid: Optional[str] = Field(None, description="Calling station ID (MAC address)")
    calledstationid: Optional[str] = Field(None, description="Called station ID (Hotspot MAC)")
    acctstarttime: datetime = Field(..., description="Session start time")
    acctsessiontime: int = Field(0, description="Session duration in seconds")
    acctsessionid: str = Field(..., description="Unique session identifier")
    nasipaddress: Optional[Union[IPv4Address, IPv6Address]] = Field(
        None, description="NAS IP address"
    )
    nasshortname: Optional[str] = Field(None, description="NAS short name")
    hotspot: Optional[str] = Field(None, description="Hotspot name")
    acctinputoctets: int = Field(0, description="Upload bytes", alias="upload")
    acctoutputoctets: int = Field(0, description="Download bytes", alias="download")
    
    @property
    def total_traffic(self) -> int:
        """Calculate total traffic in bytes"""
        return self.acctinputoctets + self.acctoutputoctets
    
    @property
    def session_duration_formatted(self) -> str:
        """Format session duration as HH:MM:SS"""
        hours = self.acctsessiontime // 3600
        minutes = (self.acctsessiontime % 3600) // 60
        seconds = self.acctsessiontime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class OnlineUsersReportQuery(BaseReportModel):
    """Query parameters for online users report"""
    
    username: Optional[str] = Field(None, description="Username filter (partial match)")
    order_by: str = Field("username", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.ASC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class OnlineUsersReportResult(BaseReportModel):
    """Result container for online users report"""
    
    users: List[OnlineUserRecord] = Field(default_factory=list, description="Online user records")
    total_count: int = Field(0, description="Total number of online users")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")
    
    @root_validator
    def calculate_total_pages(cls, values):
        """Calculate total pages based on total count and per_page"""
        total_count = values.get('total_count', 0)
        per_page = values.get('per_page', 25)
        values['total_pages'] = (total_count + per_page - 1) // per_page
        return values


# ============================================================================
# Top Users Report Models (rep-topusers.php)
# ============================================================================

class TopUserRecord(BaseReportModel):
    """Model for top users report aggregated data"""
    
    username: str = Field(..., description="RADIUS username")
    framedipaddress: Optional[Union[IPv4Address, IPv6Address]] = Field(
        None, description="Most recent framed IP address"
    )
    acctstarttime: Optional[datetime] = Field(None, description="First session start time")
    acctstoptime: Optional[datetime] = Field(None, description="Most recent session end time")
    total_time: int = Field(0, description="Total session time in seconds", alias="Time")
    total_upload: int = Field(0, description="Total upload bytes", alias="Upload")
    total_download: int = Field(0, description="Total download bytes", alias="Download")
    acctterminatecause: Optional[TerminateCause] = Field(
        None, description="Most recent termination cause"
    )
    nasipaddress: Optional[Union[IPv4Address, IPv6Address]] = Field(
        None, description="Most recent NAS IP address"
    )
    
    @property
    def total_traffic(self) -> int:
        """Calculate total traffic in bytes"""
        return self.total_upload + self.total_download
    
    @property
    def total_time_formatted(self) -> str:
        """Format total time as HH:MM:SS"""
        hours = self.total_time // 3600
        minutes = (self.total_time % 3600) // 60
        seconds = self.total_time % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class TopUsersReportQuery(BaseReportModel):
    """Query parameters for top users report"""
    
    username: Optional[str] = Field(None, description="Username filter (partial match)")
    startdate: Optional[date] = Field(None, description="Start date for filtering")
    enddate: Optional[date] = Field(None, description="End date for filtering")
    order_by: str = Field("username", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.ASC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class TopUsersReportResult(BaseReportModel):
    """Result container for top users report"""
    
    users: List[TopUserRecord] = Field(default_factory=list, description="Top user records")
    total_count: int = Field(0, description="Total number of users")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


# ============================================================================
# Username Report Models (rep-username.php)
# ============================================================================

class UserAttributeRecord(BaseReportModel):
    """Model for user attribute records from radcheck/radreply tables"""
    
    id: int = Field(..., description="Record ID")
    username: str = Field(..., description="RADIUS username")
    attribute: str = Field(..., description="RADIUS attribute name")
    op: str = Field(..., description="Operator (=, :=, !=, etc.)")
    value: str = Field(..., description="Attribute value")
    table_type: str = Field(..., description="Source table (radcheck or radreply)")


class UsernameReportQuery(BaseReportModel):
    """Query parameters for username-specific report"""
    
    username: str = Field(..., description="Specific username to query")
    order_by: str = Field("id", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.ASC, description="Sort direction")


class UsernameReportResult(BaseReportModel):
    """Result container for username report"""
    
    username: str = Field(..., description="Queried username")
    radcheck_records: List[UserAttributeRecord] = Field(
        default_factory=list, description="Check attributes"
    )
    radreply_records: List[UserAttributeRecord] = Field(
        default_factory=list, description="Reply attributes"
    )
    total_records: int = Field(0, description="Total number of attribute records")


# ============================================================================
# New Users Report Models (rep-newusers.php)
# ============================================================================

class NewUsersStatistic(BaseReportModel):
    """Model for new users statistics by period"""
    
    period: str = Field(..., description="Time period (e.g., 'January 2024')")
    users: int = Field(0, description="Number of new users in period")
    month: date = Field(..., description="Month date for sorting")


class NewUsersReportQuery(BaseReportModel):
    """Query parameters for new users report"""
    
    startdate: Optional[date] = Field(None, description="Start date for filtering")
    enddate: Optional[date] = Field(None, description="End date for filtering")
    order_by: str = Field("month", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.DESC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class NewUsersReportResult(BaseReportModel):
    """Result container for new users report"""
    
    statistics: List[NewUsersStatistic] = Field(
        default_factory=list, description="New users statistics"
    )
    total_count: int = Field(0, description="Total number of periods")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


# ============================================================================
# Batch Report Models (rep-batch*.php)
# ============================================================================

class BatchListRecord(BaseReportModel):
    """Model for batch list records from rep-batch-list.php"""
    
    id: int = Field(..., description="Batch ID")
    batch_name: str = Field(..., description="Batch identifier")
    batch_description: Optional[str] = Field(None, description="Batch description")
    batch_status: str = Field(..., description="Batch status")
    total_users: int = Field(0, description="Total number of users in batch")
    active_users: int = Field(0, description="Number of active users")
    planname: Optional[str] = Field(None, description="Associated plan name")
    plancost: Optional[Decimal] = Field(None, description="Plan cost")
    plancurrency: Optional[str] = Field(None, description="Plan currency")
    batch_cost: Optional[Decimal] = Field(None, description="Total batch cost")
    hotspot_name: Optional[str] = Field(None, description="Associated hotspot name")
    creationdate: datetime = Field(..., description="Batch creation timestamp")
    creationby: str = Field(..., description="Created by operator")
    updatedate: Optional[datetime] = Field(None, description="Last update timestamp")
    updateby: Optional[str] = Field(None, description="Last updated by operator")
    
    @validator('batch_description')
    def clean_batch_description(cls, v):
        """Clean description, return (n/a) if empty"""
        return v if v and v.strip() else "(n/a)"
    
    @validator('planname')
    def clean_planname(cls, v):
        """Clean plan name, return (n/d) if empty"""
        return v if v and v.strip() else "(n/d)"
    
    @validator('hotspot_name')
    def clean_hotspot_name(cls, v):
        """Clean hotspot name, return (n/d) if empty"""
        return v if v and v.strip() else "(n/d)"


class BatchUserDetail(BaseReportModel):
    """Model for individual user in batch details"""
    
    username: str = Field(..., description="Username")
    status: str = Field(..., description="User accounting status")
    acctstarttime: Optional[datetime] = Field(None, description="First accounting time")


class BatchDetailsRecord(BaseReportModel):
    """Model for batch details from rep-batch-details.php"""
    
    # Batch summary (same as BatchListRecord)
    id: int = Field(..., description="Batch ID")
    batch_name: str = Field(..., description="Batch identifier")
    batch_description: Optional[str] = Field(None, description="Batch description")
    batch_status: str = Field(..., description="Batch status")
    total_users: int = Field(0, description="Total number of users in batch")
    active_users: int = Field(0, description="Number of active users")
    planname: Optional[str] = Field(None, description="Associated plan name")
    plancost: Optional[Decimal] = Field(None, description="Plan cost")
    plancurrency: Optional[str] = Field(None, description="Plan currency")
    batch_cost: Optional[Decimal] = Field(None, description="Total batch cost")
    hotspot_name: Optional[str] = Field(None, description="Associated hotspot name")
    creationdate: datetime = Field(..., description="Batch creation timestamp")
    creationby: str = Field(..., description="Created by operator")
    updatedate: Optional[datetime] = Field(None, description="Last update timestamp")
    updateby: Optional[str] = Field(None, description="Last updated by operator")
    
    # User details list
    users: List[BatchUserDetail] = Field(default_factory=list, description="Users in this batch")


class BatchReportQuery(BaseReportModel):
    """Query parameters for batch reports"""
    
    batch_name: Optional[str] = Field(None, description="Specific batch name filter")
    order_by: str = Field("id", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.ASC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class BatchReportResult(BaseReportModel):
    """Result container for batch list reports"""
    
    batches: List[BatchListRecord] = Field(default_factory=list, description="Batch records")
    total_count: int = Field(0, description="Total number of batches")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


class BatchDetailsResult(BaseReportModel):
    """Result container for batch details report"""
    
    batch_details: BatchDetailsRecord = Field(..., description="Batch details and users")
    user_count: int = Field(0, description="Number of users in details table")


# ============================================================================
# Log Report Models (rep-logs*.php)
# NOTE: These reports display log files, not database records
# ============================================================================

class LogFileType(str, Enum):
    """Log file type enumeration"""
    RADIUS = "radius"
    DALORADIUS = "daloradius"
    SYSTEM = "system"
    BOOT = "boot"


class LogFilter(str, Enum):
    """Log filter enumeration"""
    # For RADIUS logs
    AUTH = "Auth"
    INFO = "Info"
    ERROR = "Error"
    
    # For daloRADIUS logs
    QUERY = "QUERY"
    NOTICE = "NOTICE"
    INSERT = "INSERT"
    SELECT = "SELECT"


class LogReportQuery(BaseReportModel):
    """Query parameters for log file reports"""
    
    log_type: LogFileType = Field(..., description="Type of log file")
    count: int = Field(50, ge=1, le=10000, description="Number of lines to display")
    filter: Optional[str] = Field(None, description="Filter pattern for log entries")


class LogReportResult(BaseReportModel):
    """Result container for log file reports"""
    
    log_type: LogFileType = Field(..., description="Type of log file")
    log_file_path: Optional[str] = Field(None, description="Path to log file")
    lines: List[str] = Field(default_factory=list, description="Log file lines")
    total_lines: int = Field(0, description="Total number of lines displayed")
    filter_applied: Optional[str] = Field(None, description="Filter that was applied")
    success: bool = Field(True, description="Whether log was successfully read")
    error_message: Optional[str] = Field(None, description="Error message if read failed")


# ============================================================================
# Heartbeat Report Models (rep-hb*.php)
# ============================================================================

class HeartbeatNodeRecord(BaseReportModel):
    """Model for heartbeat node records from dalonode table (rep-hb-dashboard.php)"""
    
    hotspotname: Optional[str] = Field(None, description="Associated hotspot name")
    wan_iface: Optional[str] = Field(None, description="WAN interface name")
    wan_ip: Optional[Union[IPv4Address, IPv6Address]] = Field(None, description="WAN IP address")
    wan_mac: Optional[str] = Field(None, description="WAN MAC address")
    wan_gateway: Optional[Union[IPv4Address, IPv6Address]] = Field(None, description="WAN gateway")
    wifi_iface: Optional[str] = Field(None, description="WiFi interface name")
    wifi_ip: Optional[Union[IPv4Address, IPv6Address]] = Field(None, description="WiFi IP address")
    wifi_mac: Optional[str] = Field(None, description="WiFi MAC address")
    wifi_ssid: Optional[str] = Field(None, description="WiFi SSID")
    wifi_key: Optional[str] = Field(None, description="WiFi key")
    wifi_channel: Optional[int] = Field(None, description="WiFi channel")
    lan_iface: Optional[str] = Field(None, description="LAN interface name")
    lan_mac: Optional[str] = Field(None, description="LAN MAC address")
    lan_ip: Optional[Union[IPv4Address, IPv6Address]] = Field(None, description="LAN IP address")
    uptime: Optional[str] = Field(None, description="System uptime")
    memfree: Optional[str] = Field(None, description="Free memory")
    cpu: Optional[str] = Field(None, description="CPU usage")
    wan_bup: Optional[int] = Field(None, description="WAN bandwidth up")
    wan_bdown: Optional[int] = Field(None, description="WAN bandwidth down")
    firmware: Optional[str] = Field(None, description="Firmware version")
    firmware_revision: Optional[str] = Field(None, description="Firmware revision")
    mac: Optional[str] = Field(None, description="Node MAC address")
    time: Optional[datetime] = Field(None, description="Last check-in time")
    
    @validator('hotspotname')
    def clean_hotspotname(cls, v):
        """Clean hotspot name, return (n/d) if empty"""
        return v if v and v.strip() else "(n/d)"


class HeartbeatDashboardSummary(BaseReportModel):
    """Model for heartbeat dashboard summary statistics"""
    
    total_nodes: int = Field(0, description="Total number of monitored nodes")
    online_nodes: int = Field(0, description="Number of online nodes")
    offline_nodes: int = Field(0, description="Number of offline nodes")
    warning_nodes: int = Field(0, description="Number of nodes with warnings")
    last_update: Optional[datetime] = Field(None, description="Last heartbeat update")
    soft_delay_minutes: int = Field(0, description="Soft delay threshold in minutes")
    hard_delay_minutes: int = Field(0, description="Hard delay threshold in minutes")


class HeartbeatReportQuery(BaseReportModel):
    """Query parameters for heartbeat reports"""
    
    hotspot_name: Optional[str] = Field(None, description="Specific hotspot filter")
    order_by: str = Field("id", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.ASC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class HeartbeatReportResult(BaseReportModel):
    """Result container for heartbeat reports"""
    
    nodes: List[HeartbeatNodeRecord] = Field(default_factory=list, description="Heartbeat node records")
    summary: Optional[HeartbeatDashboardSummary] = Field(None, description="Dashboard summary")
    total_count: int = Field(0, description="Total number of nodes")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


# ============================================================================
# Statistical Report Models (rep-stat*.php)
# NOTE: Most stat reports just include external libraries, not database records
# ============================================================================

class ServerInfoRecord(BaseReportModel):
    """Model for server information (rep-stat-server.php)"""
    
    hostname: Optional[str] = Field(None, description="Server hostname")
    kernel_version: Optional[str] = Field(None, description="Kernel version")
    uptime: Optional[str] = Field(None, description="System uptime")
    load_average: Optional[str] = Field(None, description="System load average")
    cpu_info: Optional[str] = Field(None, description="CPU information")
    memory_total: Optional[str] = Field(None, description="Total memory")
    memory_free: Optional[str] = Field(None, description="Free memory")
    disk_usage: Optional[Dict[str, Any]] = Field(None, description="Disk usage information")
    network_interfaces: Optional[List[Dict[str, Any]]] = Field(None, description="Network interfaces")


class StatReportQuery(BaseReportModel):
    """Query parameters for statistical reports"""
    
    stat_type: StatType = Field(..., description="Type of statistics")
    refresh: bool = Field(False, description="Force refresh of statistics")


class StatReportResult(BaseReportModel):
    """Result container for statistical reports"""
    
    stat_type: StatType = Field(..., description="Type of statistics")
    server_info: Optional[ServerInfoRecord] = Field(None, description="Server information")
    success: bool = Field(True, description="Whether statistics were successfully gathered")
    error_message: Optional[str] = Field(None, description="Error message if gathering failed")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


# ============================================================================
# Last Connection Attempts Report Models (rep-lastconnect.php)
# NOTE: This reports authentication attempts from radpostauth table, not connections
# ============================================================================

class RadiusReply(str, Enum):
    """RADIUS reply enumeration"""
    ACCESS_ACCEPT = "Access-Accept"
    ACCESS_REJECT = "Access-Reject"
    ACCESS_CHALLENGE = "Access-Challenge"


class AuthenticationAttemptRecord(BaseReportModel):
    """Model for authentication attempt records from radpostauth table"""
    
    fullname: Optional[str] = Field(None, description="User full name (firstname + lastname)")
    username: str = Field(..., description="RADIUS username", alias="user")
    password: Optional[str] = Field(None, alias="pass", description="Password (may be hidden)")
    reply: RadiusReply = Field(..., description="RADIUS reply")
    authdate: datetime = Field(..., description="Authentication timestamp")
    
    @validator('fullname')
    def clean_fullname(cls, v):
        """Clean fullname, return (n/a) if empty"""
        return v if v and v.strip() else "(n/a)"


class LastConnectReportQuery(BaseReportModel):
    """Query parameters for last connect attempts report"""
    
    username: Optional[str] = Field(None, description="Username filter (partial match)")
    startdate: Optional[date] = Field(None, description="Start date for filtering")
    enddate: Optional[date] = Field(None, description="End date for filtering")
    radius_reply: str = Field("Any", description="RADIUS reply filter")
    order_by: str = Field("authdate", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.DESC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class LastConnectReportResult(BaseReportModel):
    """Result container for authentication attempts report"""
    
    records: List[AuthenticationAttemptRecord] = Field(
        default_factory=list, description="Authentication attempt records"
    )
    total_count: int = Field(0, description="Total number of attempts")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


# ============================================================================
# History Report Models (rep-history.php)
# NOTE: Shows creation/update history across multiple tables
# ============================================================================

class SystemHistoryRecord(BaseReportModel):
    """Model for system history records from multiple tables"""
    
    section: str = Field(..., description="Section/table type (proxy, realm, userinfo, etc.)")
    item: str = Field(..., description="Item identifier (name, username, id)")
    creationdate: Optional[datetime] = Field(None, description="Creation timestamp")
    creationby: Optional[str] = Field(None, description="Created by operator")
    updatedate: Optional[datetime] = Field(None, description="Last update timestamp")
    updateby: Optional[str] = Field(None, description="Last updated by operator")
    
    @validator('creationby', 'updateby', 'item')
    def clean_empty_fields(cls, v):
        """Clean empty fields, return (n/a) if empty"""
        return v if v and v.strip() else "(n/a)"


class HistoryReportQuery(BaseReportModel):
    """Query parameters for system history report"""
    
    order_by: str = Field("creationdate", description="Column to sort by")
    order_type: SortOrder = Field(SortOrder.DESC, description="Sort direction")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(25, ge=1, le=500, description="Records per page")


class HistoryReportResult(BaseReportModel):
    """Result container for system history report"""
    
    records: List[SystemHistoryRecord] = Field(default_factory=list, description="History records")
    total_count: int = Field(0, description="Total number of history records")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(25, description="Records per page")
    total_pages: int = Field(0, description="Total number of pages")


# ============================================================================
# Report Session Management Models
# ============================================================================

class ReportSession(BaseReportModel):
    """Model for report session state management"""
    
    report_table: str = Field(..., description="Database table being queried")
    report_query: str = Field(..., description="SQL WHERE clause for the report")
    report_type: ReportType = Field(..., description="Type of report")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    
    @root_validator
    def set_expiration(cls, values):
        """Set expiration time to 24 hours from creation"""
        if 'expires_at' not in values and 'created_at' in values:
            from datetime import timedelta
            values['expires_at'] = values['created_at'] + timedelta(hours=24)
        return values


# ============================================================================
# Common Report Utilities
# ============================================================================

class PaginationInfo(BaseReportModel):
    """Pagination information for reports"""
    
    current_page: int = Field(1, ge=1, description="Current page number")
    per_page: int = Field(25, ge=1, le=1000, description="Records per page")
    total_records: int = Field(0, description="Total number of records")
    total_pages: int = Field(0, description="Total number of pages")
    has_previous: bool = Field(False, description="Whether there is a previous page")
    has_next: bool = Field(False, description="Whether there is a next page")
    
    @root_validator
    def calculate_pagination(cls, values):
        """Calculate pagination properties"""
        current_page = values.get('current_page', 1)
        per_page = values.get('per_page', 25)
        total_records = values.get('total_records', 0)
        
        total_pages = (total_records + per_page - 1) // per_page if total_records > 0 else 0
        has_previous = current_page > 1
        has_next = current_page < total_pages
        
        values.update({
            'total_pages': total_pages,
            'has_previous': has_previous,
            'has_next': has_next
        })
        return values


class ExportFormat(str, Enum):
    """Export format enumeration"""
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


class ReportExportRequest(BaseReportModel):
    """Model for report export requests"""
    
    report_type: ReportType = Field(..., description="Type of report to export")
    format: ExportFormat = Field(..., description="Export format")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Report query parameters")
    include_headers: bool = Field(True, description="Include column headers in export")
    max_records: Optional[int] = Field(None, description="Maximum number of records to export")


# ============================================================================
# Model Registration for Dynamic Import
# ============================================================================

# Dictionary of all models for easy access
REPORT_MODELS = {
    # Base models
    'BaseReportModel': BaseReportModel,
    'PaginationInfo': PaginationInfo,
    'ReportSession': ReportSession,
    'ReportExportRequest': ReportExportRequest,
    
    # Online users
    'OnlineUserRecord': OnlineUserRecord,
    'OnlineUsersReportQuery': OnlineUsersReportQuery,
    'OnlineUsersReportResult': OnlineUsersReportResult,
    
    # Top users
    'TopUserRecord': TopUserRecord,
    'TopUsersReportQuery': TopUsersReportQuery,
    'TopUsersReportResult': TopUsersReportResult,
    
    # Username reports
    'UserAttributeRecord': UserAttributeRecord,
    'UsernameReportQuery': UsernameReportQuery,
    'UsernameReportResult': UsernameReportResult,
    
    # New users
    'NewUsersStatistic': NewUsersStatistic,
    'NewUsersReportQuery': NewUsersReportQuery,
    'NewUsersReportResult': NewUsersReportResult,
    
    # Last connection attempts (authentication)
    'AuthenticationAttemptRecord': AuthenticationAttemptRecord,
    'LastConnectReportQuery': LastConnectReportQuery,
    'LastConnectReportResult': LastConnectReportResult,
    
    # Batch reports
    'BatchListRecord': BatchListRecord,
    'BatchUserDetail': BatchUserDetail,
    'BatchDetailsRecord': BatchDetailsRecord,
    'BatchReportQuery': BatchReportQuery,
    'BatchReportResult': BatchReportResult,
    'BatchDetailsResult': BatchDetailsResult,
    
    # Log reports
    'LogReportQuery': LogReportQuery,
    'LogReportResult': LogReportResult,
    
    # Heartbeat reports
    'HeartbeatNodeRecord': HeartbeatNodeRecord,
    'HeartbeatDashboardSummary': HeartbeatDashboardSummary,
    'HeartbeatReportQuery': HeartbeatReportQuery,
    'HeartbeatReportResult': HeartbeatReportResult,
    
    # Statistical reports
    'ServerInfoRecord': ServerInfoRecord,
    'StatReportQuery': StatReportQuery,
    'StatReportResult': StatReportResult,
    
    # History reports
    'SystemHistoryRecord': SystemHistoryRecord,
    'HistoryReportQuery': HistoryReportQuery,
    'HistoryReportResult': HistoryReportResult,
}

# Export all models for convenient importing
__all__ = list(REPORT_MODELS.keys()) + [
    'SortOrder', 'ReportType', 'TerminateCause', 'LogLevel', 'StatType', 'ExportFormat',
    'RadiusReply', 'LogFileType', 'LogFilter'
]