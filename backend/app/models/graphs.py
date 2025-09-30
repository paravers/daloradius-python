"""
Graphs Data Models

This module contains data models for graph statistics and visualization.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean, 
    Float, JSON, func, BigInteger, DECIMAL, Index
)
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.models.base import Base


class GraphType(str, enum.Enum):
    """Graph type enumeration"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    DOUGHNUT = "doughnut"
    RADAR = "radar"
    POLAR = "polar"


class TimeGranularity(str, enum.Enum):
    """Time granularity enumeration"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class GraphStatistics(Base):
    """Graph statistics data cache"""
    __tablename__ = "graph_statistics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Graph identification
    graph_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    time_period: Mapped[str] = mapped_column(String(32), nullable=False)  # daily, weekly, monthly, yearly
    
    # Time dimensions
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    recorded_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-23 for hourly stats
    
    # Statistical values
    value_count: Mapped[int] = mapped_column(Integer, default=0)
    value_sum: Mapped[float] = mapped_column(Float, default=0.0)
    value_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Additional metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class LoginStatistics(Base):
    """Login statistics aggregated data"""
    __tablename__ = "login_statistics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Time dimensions
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    stat_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # For hourly breakdown
    
    # Login metrics
    total_logins: Mapped[int] = mapped_column(Integer, default=0)
    successful_logins: Mapped[int] = mapped_column(Integer, default=0)
    failed_logins: Mapped[int] = mapped_column(Integer, default=0)
    unique_users: Mapped[int] = mapped_column(Integer, default=0)
    
    # Geographic and device breakdown
    nas_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # NAS IP -> count
    user_agent_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Performance metrics
    avg_response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    peak_concurrent_users: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class TrafficStatistics(Base):
    """Traffic statistics aggregated data"""
    __tablename__ = "traffic_statistics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Time dimensions
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    stat_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Traffic metrics (in bytes)
    total_upload: Mapped[int] = mapped_column(BigInteger, default=0)
    total_download: Mapped[int] = mapped_column(BigInteger, default=0)
    total_traffic: Mapped[int] = mapped_column(BigInteger, default=0)
    
    # Session metrics
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    active_sessions: Mapped[int] = mapped_column(Integer, default=0)
    avg_session_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in seconds
    
    # User and device metrics
    unique_users: Mapped[int] = mapped_column(Integer, default=0)
    nas_device_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Top users and devices (JSON arrays with top 10)
    top_upload_users: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    top_download_users: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    top_nas_devices: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class UserStatistics(Base):
    """User statistics aggregated data"""
    __tablename__ = "user_statistics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Time dimensions
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    stat_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # User metrics
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)  # Users who logged in
    new_users: Mapped[int] = mapped_column(Integer, default=0)  # New registrations
    online_users: Mapped[int] = mapped_column(Integer, default=0)  # Currently online
    
    # User activity metrics
    avg_session_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_daily_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # bytes per user
    user_retention_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # percentage
    
    # User categorization
    power_users_count: Mapped[int] = mapped_column(Integer, default=0)  # Top 10% by usage
    occasional_users_count: Mapped[int] = mapped_column(Integer, default=0)
    inactive_users_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Geographic distribution (top locations)
    geographic_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class SystemMetrics(Base):
    """System performance metrics for graphs"""
    __tablename__ = "system_metrics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Time dimensions
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # System metrics
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disk_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_in: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    network_out: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # RADIUS specific metrics
    radius_requests: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    radius_accepts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    radius_rejects: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    radius_response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Database metrics
    db_connections: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    db_query_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    db_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Additional metrics
    custom_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class GraphTemplate(Base):
    """Graph template configurations"""
    __tablename__ = "graph_templates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Template details
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # login, traffic, user, system
    
    # Graph configuration
    graph_type: Mapped[GraphType] = mapped_column(String(32), nullable=False)
    data_source: Mapped[str] = mapped_column(String(128), nullable=False)  # API endpoint or data source
    time_granularity: Mapped[TimeGranularity] = mapped_column(String(32), nullable=False)
    
    # Chart configuration
    chart_config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Chart.js configuration
    
    # Display settings
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    x_axis_label: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    y_axis_label: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Filtering and grouping
    default_filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    group_by_options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Template metadata
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class DashboardWidget(Base):
    """Dashboard widget configurations"""
    __tablename__ = "dashboard_widgets"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Widget details
    widget_name: Mapped[str] = mapped_column(String(128), nullable=False)
    widget_type: Mapped[str] = mapped_column(String(64), nullable=False)  # chart, metric, table, etc.
    dashboard_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # Dashboard identifier
    
    # Position and layout
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=4)  # Grid units
    height: Mapped[int] = mapped_column(Integer, default=3)  # Grid units
    
    # Widget configuration
    data_source: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_interval: Mapped[int] = mapped_column(Integer, default=300)  # seconds
    widget_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Display settings
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    show_title: Mapped[bool] = mapped_column(Boolean, default=True)
    background_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    border_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    
    # Widget metadata
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    is_resizable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_movable: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # User and permissions
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


# Create indexes for better performance
Index('idx_graph_statistics_type_date', GraphStatistics.graph_type, GraphStatistics.recorded_date)
Index('idx_graph_statistics_metric_period', GraphStatistics.metric_name, GraphStatistics.time_period)
Index('idx_login_statistics_date_hour', LoginStatistics.stat_date, LoginStatistics.stat_hour)
Index('idx_traffic_statistics_date_hour', TrafficStatistics.stat_date, TrafficStatistics.stat_hour)
Index('idx_user_statistics_date_hour', UserStatistics.stat_date, UserStatistics.stat_hour)
Index('idx_system_metrics_recorded_type', SystemMetrics.recorded_at, SystemMetrics.metric_type)
Index('idx_graph_templates_category_active', GraphTemplate.category, GraphTemplate.is_active)
Index('idx_dashboard_widgets_dashboard_position', DashboardWidget.dashboard_id, DashboardWidget.position_x, DashboardWidget.position_y)