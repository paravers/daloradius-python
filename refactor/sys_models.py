"""System Monitoring & Metrics Domain Models
=================================================

These models represent data shown across operator dashboard and reporting
pages (home-main.php, rep-stat-*.php, rep-logs-system.php) and underlying
extension includes (server_info.php, radius_server_info.php, system_logs.php).

Scope (phase 1 - foundational):
 - Enums for service state, severity, metric units, resource types
 - Dashboard statistics (counts, recent auth attempts, online sessions, top users)
 - Core resource usage primitives (CPU, memory, load, disk, network, process)
 - Log viewing structures (system logs listing, tail results)

Further phases (to be implemented in subsequent tasks):
 - Service/daemon detailed status (FreeRADIUS, SQL, LDAP)
 - Health check aggregation and alerting entities
 - Threshold rule definitions

Design Principles:
 - Consistent with existing refactor models (BaseModel config, aliasing)
 - Explicit units and timestamp typing (datetime)
 - Separation between raw metrics and summarized/derived statistics
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator, conint, confloat


class BaseSystemModel(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True


class ServiceState(str, Enum):
    running = "running"
    stopped = "stopped"
    degraded = "degraded"
    unknown = "unknown"
    starting = "starting"
    stopping = "stopping"


class Severity(str, Enum):
    info = "info"
    notice = "notice"
    warning = "warning"
    error = "error"
    critical = "critical"
    alert = "alert"
    emergency = "emergency"


class MetricUnit(str, Enum):
    percent = "%"
    bytes = "bytes"
    seconds = "seconds"
    count = "count"
    load = "load"  # normalized load average value
    kbps = "kbps"
    mbps = "mbps"
    packets = "packets"


class ResourceType(str, Enum):
    cpu = "cpu"
    memory = "memory"
    load = "load"
    disk = "disk"
    network = "network"
    process = "process"
    service = "service"
    system = "system"
    logfile = "logfile"


# ----------------------------- Dashboard Statistics -----------------------------

class DashboardCounts(BaseSystemModel):
    total_users: int = Field(..., ge=0)
    total_nas: int = Field(..., ge=0)
    total_hotspots: int = Field(..., ge=0)


class RecentAuthAttempt(BaseSystemModel):
    username: str
    reply: str  # Access-Accept / Access-Reject / other RADIUS reply
    timestamp: datetime

    @property
    def success(self) -> bool:
        return self.reply.lower() not in {"access-reject", "reject"}


class OnlineSession(BaseSystemModel):
    username: str
    online_since: datetime = Field(..., alias="acct_start_time")
    # Additional fields (NAS IP, session ID) can be added later if needed


class TopUserUsage(BaseSystemModel):
    username: str
    total_session_time_seconds: int = Field(..., ge=0)
    uploaded_bytes: int = Field(..., ge=0)
    downloaded_bytes: int = Field(..., ge=0)

    @property
    def total_bytes(self) -> int:
        return self.uploaded_bytes + self.downloaded_bytes


class DashboardSnapshot(BaseSystemModel):
    generated_at: datetime
    counts: DashboardCounts
    recent_auth_attempts: List[RecentAuthAttempt]
    online_users: List[OnlineSession]
    top_users: List[TopUserUsage]


# ----------------------------- Core Resource Metrics -----------------------------

class CPUStat(BaseSystemModel):
    cores: conint(ge=1) = Field(..., description="Total number of CPU cores")
    user_pct: confloat(ge=0, le=100)
    system_pct: confloat(ge=0, le=100)
    idle_pct: confloat(ge=0, le=100)
    iowait_pct: Optional[confloat(ge=0, le=100)] = None
    steal_pct: Optional[confloat(ge=0, le=100)] = None

    @validator("idle_pct")
    def validate_idle(cls, v):  # pragma: no cover - simple guard
        if v < 0 or v > 100:
            raise ValueError("idle_pct must be between 0 and 100")
        return v


class MemoryStat(BaseSystemModel):
    total_bytes: int = Field(..., ge=0)
    used_bytes: int = Field(..., ge=0)
    free_bytes: int = Field(..., ge=0)
    available_bytes: Optional[int] = Field(None, ge=0)
    swap_total_bytes: Optional[int] = Field(None, ge=0)
    swap_used_bytes: Optional[int] = Field(None, ge=0)

    @property
    def used_pct(self) -> Optional[float]:
        if self.total_bytes:
            return (self.used_bytes / self.total_bytes) * 100
        return None


class LoadAverage(BaseSystemModel):
    one_min: float
    five_min: float
    fifteen_min: float


class DiskPartition(BaseSystemModel):
    mount_point: str
    filesystem: Optional[str] = None
    total_bytes: int = Field(..., ge=0)
    used_bytes: int = Field(..., ge=0)
    free_bytes: int = Field(..., ge=0)
    used_pct: confloat(ge=0, le=100)


class NetworkInterface(BaseSystemModel):
    name: str
    rx_bytes: int = Field(..., ge=0)
    tx_bytes: int = Field(..., ge=0)
    rx_packets: Optional[int] = Field(None, ge=0)
    tx_packets: Optional[int] = Field(None, ge=0)
    speed_mbps: Optional[float] = Field(None, ge=0)
    ipv4_addresses: List[IPv4Address] = []


class ProcessInfo(BaseSystemModel):
    pid: int
    name: str
    cpu_pct: Optional[float] = Field(None, ge=0)
    mem_bytes: Optional[int] = Field(None, ge=0)
    started_at: Optional[datetime] = None
    state: Optional[str] = None  # R, S, D, Z etc.


class ResourceUsage(BaseSystemModel):
    captured_at: datetime
    cpu: CPUStat
    memory: MemoryStat
    load: LoadAverage
    disks: List[DiskPartition]
    network: List[NetworkInterface]
    top_processes: List[ProcessInfo] = []


class SystemOverview(BaseSystemModel):
    hostname: str
    uptime_seconds: Optional[int] = Field(None, ge=0)
    os: Optional[str] = None
    kernel: Optional[str] = None
    architecture: Optional[str] = None
    resource_usage: Optional[ResourceUsage] = None


# ----------------------------- System Logs -----------------------------

class LogFileStat(BaseSystemModel):
    path: str
    size_bytes: Optional[int] = Field(None, ge=0)
    last_modified: Optional[datetime] = None
    readable: bool = True


class LogLine(BaseSystemModel):
    line_number: int = Field(..., ge=1)
    content: str
    timestamp: Optional[datetime] = None  # If parsed from syslog format
    severity: Optional[Severity] = None


class LogTailResult(BaseSystemModel):
    file: LogFileStat
    requested_lines: int
    filter: Optional[str] = None
    lines: List[LogLine]


class SystemLogsView(BaseSystemModel):
    generated_at: datetime
    files: List[LogFileStat]
    tail: Optional[LogTailResult] = None


# ----------------------------- Services & Health -----------------------------

class ServiceStatus(BaseSystemModel):
    name: str
    state: ServiceState
    pid: Optional[int] = None
    uptime_seconds: Optional[int] = Field(None, ge=0)
    version: Optional[str] = None
    last_checked: datetime
    details: Dict[str, Any] = {}


class DatabaseStatus(BaseSystemModel):
    engine: str  # mysql/mariadb/postgresql
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    reachable: bool
    latency_ms: Optional[float] = Field(None, ge=0)
    active_connections: Optional[int] = Field(None, ge=0)
    last_checked: datetime


class RadiusStatus(BaseSystemModel):
    auth_server: ServiceStatus
    accounting_server: Optional[ServiceStatus] = None
    recent_auth_success: Optional[bool] = None
    recent_acct_success: Optional[bool] = None
    detail: Dict[str, Any] = {}


class HealthCheckResult(BaseSystemModel):
    component: str
    resource: ResourceType
    status: ServiceState
    severity: Optional[Severity] = None
    message: Optional[str] = None
    checked_at: datetime
    metrics: Dict[str, Any] = {}


class ComponentHealthSummary(BaseSystemModel):
    generated_at: datetime
    overall_state: ServiceState
    components: List[HealthCheckResult]


# ----------------------------- Alerting & Thresholds -----------------------------

class MetricThreshold(BaseSystemModel):
    resource: ResourceType
    metric: str  # e.g., cpu.user_pct, memory.used_pct
    operator: str = Field(..., regex=r"^(>=|<=|>|<|==|!=)$")
    value: float
    unit: Optional[MetricUnit] = None
    window_seconds: Optional[int] = Field(None, ge=1)
    enabled: bool = True


class AlertRule(BaseSystemModel):
    id: str
    name: str
    description: Optional[str] = None
    thresholds: List[MetricThreshold]
    severity: Severity = Severity.warning
    enabled: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class AlertEvent(BaseSystemModel):
    id: str
    rule_id: Optional[str] = None
    resource: ResourceType
    metric: str
    value: float
    threshold: MetricThreshold
    severity: Severity
    occurred_at: datetime
    resolved_at: Optional[datetime] = None
    message: Optional[str] = None


class AlertSummary(BaseSystemModel):
    generated_at: datetime
    active_alerts: List[AlertEvent]
    recent_alerts: List[AlertEvent]


__all__ = [
    # enums
    "ServiceState", "Severity", "MetricUnit", "ResourceType",
    # dashboard
    "DashboardCounts", "RecentAuthAttempt", "OnlineSession", "TopUserUsage", "DashboardSnapshot",
    # core metrics
    "CPUStat", "MemoryStat", "LoadAverage", "DiskPartition", "NetworkInterface", "ProcessInfo", "ResourceUsage", "SystemOverview",
    # logs
    "LogFileStat", "LogLine", "LogTailResult", "SystemLogsView",
    # services & health
    "ServiceStatus", "DatabaseStatus", "RadiusStatus", "HealthCheckResult", "ComponentHealthSummary",
    # alerts
    "MetricThreshold", "AlertRule", "AlertEvent", "AlertSummary",
]
