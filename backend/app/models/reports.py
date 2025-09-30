"""
Reports Data Models

This module contains all the data models for the reporting system.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Float, JSON, func, ForeignKey, BigInteger, DECIMAL,
    Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class ReportType(str, enum.Enum):
    """Report type enumeration"""
    ONLINE_USERS = "online_users"
    HISTORY = "history"
    LAST_CONNECT = "last_connect"
    NEW_USERS = "new_users"
    TOP_USERS = "top_users"
    USERNAME_REPORT = "username_report"
    BATCH_REPORT = "batch_report"
    SYSTEM_LOGS = "system_logs"
    SYSTEM_STATUS = "system_status"
    HEARTBEAT = "heartbeat"


class LogLevel(str, enum.Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SystemStatus(str, enum.Enum):
    """System status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class UpsStatus(Base):
    """UPS (Uninterruptible Power Supply) monitoring status"""
    __tablename__ = "ups_status"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # UPS identification
    ups_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ups_model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ups_serial: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Power status
    status: Mapped[SystemStatus] = mapped_column(SQLEnum(SystemStatus), default=SystemStatus.OFFLINE)
    battery_charge: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    battery_runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Minutes
    input_voltage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Volts
    output_voltage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Volts
    load_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    
    # Temperature and environment
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Celsius
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    
    # Timestamps
    last_test_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_battery_replacement: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class RaidStatus(Base):
    """RAID array status monitoring"""
    __tablename__ = "raid_status"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # RAID identification
    array_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raid_level: Mapped[str] = mapped_column(String(16), nullable=False)  # RAID0, RAID1, RAID5, etc.
    controller_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # RAID status
    status: Mapped[SystemStatus] = mapped_column(SQLEnum(SystemStatus), default=SystemStatus.OFFLINE)
    total_disks: Mapped[int] = mapped_column(Integer, nullable=False)
    active_disks: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_disks: Mapped[int] = mapped_column(Integer, default=0)
    spare_disks: Mapped[int] = mapped_column(Integer, default=0)
    
    # Storage information
    total_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # Bytes
    used_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # Bytes
    available_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # Bytes
    
    # Performance metrics
    read_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # MB/s
    write_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # MB/s
    
    # Error information
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    last_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class HeartBeat(Base):
    """System heartbeat monitoring"""
    __tablename__ = "heartbeat"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Service identification
    service_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(32), nullable=False)  # radius, web, database, etc.
    host_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status information
    status: Mapped[SystemStatus] = mapped_column(SQLEnum(SystemStatus), default=SystemStatus.OFFLINE)
    response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Milliseconds
    uptime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Seconds
    
    # Health metrics
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    memory_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    disk_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    
    # Timestamps
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_response: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class ReportTemplate(Base):
    """Report templates for custom reports"""
    __tablename__ = "report_templates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Template details
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False)
    
    # Template configuration
    query_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    display_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    filter_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class ReportGeneration(Base):
    """Report generation history and status"""
    __tablename__ = "report_generations"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Report details
    report_name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType), nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("report_templates.id"), nullable=True)
    
    # Generation parameters
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    date_range_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_range_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Generation status
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, running, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    result_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    generated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationship
    template: Mapped[Optional["ReportTemplate"]] = relationship("ReportTemplate", lazy="selectin")


class ServerMonitoring(Base):
    """Server monitoring and performance metrics"""
    __tablename__ = "server_monitoring"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Server identification
    server_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    server_type: Mapped[str] = mapped_column(String(32), nullable=False)  # web, database, radius, etc.
    
    # System metrics
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)  # Percentage
    memory_usage: Mapped[float] = mapped_column(Float, nullable=False)  # Percentage
    disk_usage: Mapped[float] = mapped_column(Float, nullable=False)  # Percentage
    network_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # MB/s
    network_out: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # MB/s
    
    # System information
    uptime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Seconds
    load_average: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # 1min, 5min, 15min
    active_connections: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Service status
    services_status: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)


# Create indexes for better performance
Index('idx_ups_status_created_at', UpsStatus.created_at)
Index('idx_raid_status_created_at', RaidStatus.created_at)
Index('idx_heartbeat_service_status', HeartBeat.service_name, HeartBeat.status)
Index('idx_heartbeat_last_heartbeat', HeartBeat.last_heartbeat)
Index('idx_report_generation_type_status', ReportGeneration.report_type, ReportGeneration.status)
Index('idx_server_monitoring_name_recorded', ServerMonitoring.server_name, ServerMonitoring.recorded_at)