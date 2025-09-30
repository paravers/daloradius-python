"""
Reports Pydantic Schemas

This module contains all the Pydantic schemas for the reporting system.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.reports import ReportType, LogLevel, SystemStatus


# =============================================================================
# Base Schemas
# =============================================================================

class PaginatedResponse(BaseModel):
    """Base paginated response schema"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# =============================================================================
# UPS Status Schemas
# =============================================================================

class UpsStatusBase(BaseModel):
    """UPS status base schema"""
    ups_name: str = Field(..., description="UPS device name")
    ups_model: Optional[str] = Field(None, description="UPS model")
    ups_serial: Optional[str] = Field(None, description="UPS serial number")
    location: Optional[str] = Field(None, description="Physical location")
    battery_charge: Optional[float] = Field(None, ge=0, le=100, description="Battery charge percentage")
    battery_runtime: Optional[int] = Field(None, ge=0, description="Battery runtime in minutes")
    input_voltage: Optional[float] = Field(None, ge=0, description="Input voltage")
    output_voltage: Optional[float] = Field(None, ge=0, description="Output voltage")
    load_percentage: Optional[float] = Field(None, ge=0, le=100, description="Load percentage")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")


class UpsStatusCreate(UpsStatusBase):
    """UPS status creation schema"""
    status: SystemStatus = Field(SystemStatus.OFFLINE, description="UPS status")


class UpsStatusUpdate(BaseModel):
    """UPS status update schema"""
    ups_model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[SystemStatus] = None
    battery_charge: Optional[float] = Field(None, ge=0, le=100)
    battery_runtime: Optional[int] = Field(None, ge=0)
    input_voltage: Optional[float] = Field(None, ge=0)
    output_voltage: Optional[float] = Field(None, ge=0)
    load_percentage: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = None
    humidity: Optional[float] = Field(None, ge=0, le=100)
    last_test_date: Optional[datetime] = None
    last_battery_replacement: Optional[datetime] = None


class UpsStatusResponse(UpsStatusBase):
    """UPS status response schema"""
    id: int
    status: SystemStatus
    last_test_date: Optional[datetime]
    last_battery_replacement: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# RAID Status Schemas
# =============================================================================

class RaidStatusBase(BaseModel):
    """RAID status base schema"""
    array_name: str = Field(..., description="RAID array name")
    raid_level: str = Field(..., description="RAID level (RAID0, RAID1, etc.)")
    controller_name: Optional[str] = Field(None, description="RAID controller name")
    total_disks: int = Field(..., ge=1, description="Total number of disks")
    active_disks: int = Field(..., ge=0, description="Number of active disks")
    failed_disks: int = Field(0, ge=0, description="Number of failed disks")
    spare_disks: int = Field(0, ge=0, description="Number of spare disks")
    total_size: Optional[int] = Field(None, ge=0, description="Total size in bytes")
    used_size: Optional[int] = Field(None, ge=0, description="Used size in bytes")
    available_size: Optional[int] = Field(None, ge=0, description="Available size in bytes")
    read_rate: Optional[float] = Field(None, ge=0, description="Read rate in MB/s")
    write_rate: Optional[float] = Field(None, ge=0, description="Write rate in MB/s")


class RaidStatusCreate(RaidStatusBase):
    """RAID status creation schema"""
    status: SystemStatus = Field(SystemStatus.OFFLINE, description="RAID status")


class RaidStatusUpdate(BaseModel):
    """RAID status update schema"""
    controller_name: Optional[str] = None
    status: Optional[SystemStatus] = None
    total_disks: Optional[int] = Field(None, ge=1)
    active_disks: Optional[int] = Field(None, ge=0)
    failed_disks: Optional[int] = Field(None, ge=0)
    spare_disks: Optional[int] = Field(None, ge=0)
    total_size: Optional[int] = Field(None, ge=0)
    used_size: Optional[int] = Field(None, ge=0)
    available_size: Optional[int] = Field(None, ge=0)
    read_rate: Optional[float] = Field(None, ge=0)
    write_rate: Optional[float] = Field(None, ge=0)
    last_error: Optional[str] = None
    error_count: Optional[int] = Field(None, ge=0)


class RaidStatusResponse(RaidStatusBase):
    """RAID status response schema"""
    id: int
    status: SystemStatus
    last_error: Optional[str]
    error_count: int
    last_check: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# HeartBeat Schemas
# =============================================================================

class HeartBeatBase(BaseModel):
    """HeartBeat base schema"""
    service_name: str = Field(..., description="Service name")
    service_type: str = Field(..., description="Service type")
    host_name: str = Field(..., description="Host name")
    ip_address: Optional[str] = Field(None, description="IP address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Port number")
    response_time: Optional[float] = Field(None, ge=0, description="Response time in milliseconds")
    uptime: Optional[int] = Field(None, ge=0, description="Uptime in seconds")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, ge=0, le=100, description="Memory usage percentage")
    disk_usage: Optional[float] = Field(None, ge=0, le=100, description="Disk usage percentage")


class HeartBeatCreate(HeartBeatBase):
    """HeartBeat creation schema"""
    status: SystemStatus = Field(SystemStatus.OFFLINE, description="Service status")


class HeartBeatUpdate(BaseModel):
    """HeartBeat update schema"""
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    status: Optional[SystemStatus] = None
    response_time: Optional[float] = Field(None, ge=0)
    uptime: Optional[int] = Field(None, ge=0)
    cpu_usage: Optional[float] = Field(None, ge=0, le=100)
    memory_usage: Optional[float] = Field(None, ge=0, le=100)
    disk_usage: Optional[float] = Field(None, ge=0, le=100)
    last_heartbeat: Optional[datetime] = None
    last_response: Optional[datetime] = None


class HeartBeatResponse(HeartBeatBase):
    """HeartBeat response schema"""
    id: int
    status: SystemStatus
    last_heartbeat: Optional[datetime]
    last_response: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Report Template Schemas
# =============================================================================

class ReportTemplateBase(BaseModel):
    """Report template base schema"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    report_type: ReportType = Field(..., description="Report type")
    query_config: Optional[Dict[str, Any]] = Field(None, description="Query configuration")
    display_config: Optional[Dict[str, Any]] = Field(None, description="Display configuration")
    filter_config: Optional[Dict[str, Any]] = Field(None, description="Filter configuration")
    is_public: bool = Field(False, description="Is template public")
    is_active: bool = Field(True, description="Is template active")


class ReportTemplateCreate(ReportTemplateBase):
    """Report template creation schema"""
    created_by: Optional[str] = Field(None, description="Created by user")


class ReportTemplateUpdate(BaseModel):
    """Report template update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    query_config: Optional[Dict[str, Any]] = None
    display_config: Optional[Dict[str, Any]] = None
    filter_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(ReportTemplateBase):
    """Report template response schema"""
    id: int
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Report Generation Schemas
# =============================================================================

class ReportGenerationBase(BaseModel):
    """Report generation base schema"""
    report_name: str = Field(..., description="Report name")
    report_type: ReportType = Field(..., description="Report type")
    template_id: Optional[int] = Field(None, description="Template ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    date_range_start: Optional[datetime] = Field(None, description="Date range start")
    date_range_end: Optional[datetime] = Field(None, description="Date range end")


class ReportGenerationCreate(ReportGenerationBase):
    """Report generation creation schema"""
    generated_by: Optional[str] = Field(None, description="Generated by user")


class ReportGenerationUpdate(BaseModel):
    """Report generation update schema"""
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result_count: Optional[int] = Field(None, ge=0)
    file_path: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class ReportGenerationResponse(ReportGenerationBase):
    """Report generation response schema"""
    id: int
    status: str
    progress: int
    result_count: Optional[int]
    file_path: Optional[str]
    file_size: Optional[int]
    error_message: Optional[str]
    generated_by: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Server Monitoring Schemas
# =============================================================================

class ServerMonitoringBase(BaseModel):
    """Server monitoring base schema"""
    server_name: str = Field(..., description="Server name")
    ip_address: str = Field(..., description="IP address")
    server_type: str = Field(..., description="Server type")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    network_in: Optional[float] = Field(None, ge=0, description="Network in MB/s")
    network_out: Optional[float] = Field(None, ge=0, description="Network out MB/s")
    uptime: Optional[int] = Field(None, ge=0, description="Uptime in seconds")
    load_average: Optional[str] = Field(None, description="Load average")
    active_connections: Optional[int] = Field(None, ge=0, description="Active connections")
    services_status: Optional[Dict[str, Any]] = Field(None, description="Services status")


class ServerMonitoringCreate(ServerMonitoringBase):
    """Server monitoring creation schema"""
    pass


class ServerMonitoringResponse(ServerMonitoringBase):
    """Server monitoring response schema"""
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Report Query Schemas
# =============================================================================

class OnlineUsersReportQuery(BaseModel):
    """Online users report query"""
    nas_ip: Optional[str] = None
    username: Optional[str] = None
    session_timeout_min: Optional[int] = Field(None, ge=1)


class HistoryReportQuery(BaseModel):
    """History report query"""
    username: Optional[str] = None
    nas_ip: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_time_min: Optional[int] = Field(None, ge=0)


class NewUsersReportQuery(BaseModel):
    """New users report query"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_name: Optional[str] = None


class TopUsersReportQuery(BaseModel):
    """Top users report query"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(10, ge=1, le=100)
    order_by: str = Field("total_traffic", regex="^(total_traffic|session_time|session_count)$")


class SystemLogQuery(BaseModel):
    """System log query"""
    log_level: Optional[LogLevel] = None
    logger_name: Optional[str] = None
    username: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None


class BatchReportQuery(BaseModel):
    """Batch report query"""
    batch_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# =============================================================================
# Report Response Schemas
# =============================================================================

class OnlineUserReport(BaseModel):
    """Online user report item"""
    username: str
    nas_ip_address: str
    session_id: str
    start_time: datetime
    session_duration: int  # seconds
    input_octets: int
    output_octets: int
    framed_ip_address: Optional[str]


class HistoryReportItem(BaseModel):
    """History report item"""
    username: str
    session_start: datetime
    session_end: Optional[datetime]
    session_time: int  # seconds
    input_octets: int
    output_octets: int
    nas_ip_address: str
    terminate_cause: Optional[str]


class NewUserReportItem(BaseModel):
    """New user report item"""
    username: str
    created_date: datetime
    first_login: Optional[datetime]
    group_name: Optional[str]
    email: Optional[str]
    status: str


class TopUserReportItem(BaseModel):
    """Top user report item"""
    username: str
    total_traffic: int  # bytes
    session_time: int  # seconds
    session_count: int
    last_session: Optional[datetime]


class SystemLogReportItem(BaseModel):
    """System log report item"""
    timestamp: datetime
    log_level: str
    logger_name: str
    message: str
    username: Optional[str]
    ip_address: Optional[str]


class BatchReportItem(BaseModel):
    """Batch report item"""
    batch_name: str
    description: Optional[str]
    user_count: int
    success_count: int
    failed_count: int
    created_date: datetime


# =============================================================================
# System Status Report Schemas
# =============================================================================

class SystemStatusReport(BaseModel):
    """System status report"""
    server_status: List[Dict[str, Any]]
    service_status: List[Dict[str, Any]]
    ups_status: List[UpsStatusResponse]
    raid_status: List[RaidStatusResponse]
    heartbeat_status: List[HeartBeatResponse]
    generated_at: datetime


# =============================================================================
# List Response Schemas
# =============================================================================

class UpsStatusListResponse(PaginatedResponse):
    """UPS status list response"""
    items: List[UpsStatusResponse]


class RaidStatusListResponse(PaginatedResponse):
    """RAID status list response"""
    items: List[RaidStatusResponse]


class HeartBeatListResponse(PaginatedResponse):
    """HeartBeat list response"""
    items: List[HeartBeatResponse]


class ReportTemplateListResponse(PaginatedResponse):
    """Report template list response"""
    items: List[ReportTemplateResponse]


class ReportGenerationListResponse(PaginatedResponse):
    """Report generation list response"""
    items: List[ReportGenerationResponse]


class ServerMonitoringListResponse(PaginatedResponse):
    """Server monitoring list response"""
    items: List[ServerMonitoringResponse]