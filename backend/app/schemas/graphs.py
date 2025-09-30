"""
Graphs Pydantic Schemas

This module contains all the Pydantic schemas for the graphs system.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.graphs import GraphType, TimeGranularity


# =============================================================================
# Base Schemas
# =============================================================================

class ChartDataPoint(BaseModel):
    """Individual chart data point"""
    x: Union[str, int, float, datetime]
    y: Union[int, float]
    label: Optional[str] = None


class ChartDataset(BaseModel):
    """Chart dataset for Chart.js"""
    label: str
    data: List[Union[ChartDataPoint, int, float]]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None
    borderWidth: Optional[int] = 1
    fill: Optional[bool] = False
    tension: Optional[float] = 0.1


class ChartConfig(BaseModel):
    """Chart.js configuration"""
    type: GraphType
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


# =============================================================================
# Graph Statistics Schemas
# =============================================================================

class GraphStatisticsBase(BaseModel):
    """Graph statistics base schema"""
    graph_type: str = Field(..., description="Graph type identifier")
    metric_name: str = Field(..., description="Metric name")
    time_period: str = Field(..., description="Time period (daily, weekly, monthly, yearly)")
    recorded_date: date = Field(..., description="Date of record")
    recorded_hour: Optional[int] = Field(None, ge=0, le=23, description="Hour of record for hourly stats")
    value_count: int = Field(0, ge=0, description="Count of values")
    value_sum: float = Field(0.0, description="Sum of values")
    value_avg: Optional[float] = Field(None, description="Average value")
    value_min: Optional[float] = Field(None, description="Minimum value")
    value_max: Optional[float] = Field(None, description="Maximum value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class GraphStatisticsCreate(GraphStatisticsBase):
    """Graph statistics creation schema"""
    pass


class GraphStatisticsUpdate(BaseModel):
    """Graph statistics update schema"""
    value_count: Optional[int] = Field(None, ge=0)
    value_sum: Optional[float] = None
    value_avg: Optional[float] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class GraphStatisticsResponse(GraphStatisticsBase):
    """Graph statistics response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Login Statistics Schemas
# =============================================================================

class LoginStatisticsBase(BaseModel):
    """Login statistics base schema"""
    stat_date: date = Field(..., description="Statistics date")
    stat_hour: Optional[int] = Field(None, ge=0, le=23, description="Hour for hourly breakdown")
    total_logins: int = Field(0, ge=0, description="Total login attempts")
    successful_logins: int = Field(0, ge=0, description="Successful logins")
    failed_logins: int = Field(0, ge=0, description="Failed logins")
    unique_users: int = Field(0, ge=0, description="Unique users")
    nas_breakdown: Optional[Dict[str, int]] = Field(None, description="NAS IP breakdown")
    user_agent_breakdown: Optional[Dict[str, int]] = Field(None, description="User agent breakdown")
    avg_response_time: Optional[float] = Field(None, ge=0, description="Average response time in ms")
    peak_concurrent_users: Optional[int] = Field(None, ge=0, description="Peak concurrent users")


class LoginStatisticsCreate(LoginStatisticsBase):
    """Login statistics creation schema"""
    pass


class LoginStatisticsUpdate(BaseModel):
    """Login statistics update schema"""
    total_logins: Optional[int] = Field(None, ge=0)
    successful_logins: Optional[int] = Field(None, ge=0)
    failed_logins: Optional[int] = Field(None, ge=0)
    unique_users: Optional[int] = Field(None, ge=0)
    nas_breakdown: Optional[Dict[str, int]] = None
    user_agent_breakdown: Optional[Dict[str, int]] = None
    avg_response_time: Optional[float] = Field(None, ge=0)
    peak_concurrent_users: Optional[int] = Field(None, ge=0)


class LoginStatisticsResponse(LoginStatisticsBase):
    """Login statistics response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Traffic Statistics Schemas
# =============================================================================

class TrafficStatisticsBase(BaseModel):
    """Traffic statistics base schema"""
    stat_date: date = Field(..., description="Statistics date")
    stat_hour: Optional[int] = Field(None, ge=0, le=23, description="Hour for hourly breakdown")
    total_upload: int = Field(0, ge=0, description="Total upload bytes")
    total_download: int = Field(0, ge=0, description="Total download bytes")
    total_traffic: int = Field(0, ge=0, description="Total traffic bytes")
    total_sessions: int = Field(0, ge=0, description="Total sessions")
    active_sessions: int = Field(0, ge=0, description="Active sessions")
    avg_session_duration: Optional[float] = Field(None, ge=0, description="Average session duration in seconds")
    unique_users: int = Field(0, ge=0, description="Unique users")
    nas_device_count: int = Field(0, ge=0, description="NAS device count")
    top_upload_users: Optional[Dict[str, Any]] = Field(None, description="Top upload users")
    top_download_users: Optional[Dict[str, Any]] = Field(None, description="Top download users")
    top_nas_devices: Optional[Dict[str, Any]] = Field(None, description="Top NAS devices")


class TrafficStatisticsCreate(TrafficStatisticsBase):
    """Traffic statistics creation schema"""
    pass


class TrafficStatisticsUpdate(BaseModel):
    """Traffic statistics update schema"""
    total_upload: Optional[int] = Field(None, ge=0)
    total_download: Optional[int] = Field(None, ge=0)
    total_traffic: Optional[int] = Field(None, ge=0)
    total_sessions: Optional[int] = Field(None, ge=0)
    active_sessions: Optional[int] = Field(None, ge=0)
    avg_session_duration: Optional[float] = Field(None, ge=0)
    unique_users: Optional[int] = Field(None, ge=0)
    nas_device_count: Optional[int] = Field(None, ge=0)
    top_upload_users: Optional[Dict[str, Any]] = None
    top_download_users: Optional[Dict[str, Any]] = None
    top_nas_devices: Optional[Dict[str, Any]] = None


class TrafficStatisticsResponse(TrafficStatisticsBase):
    """Traffic statistics response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# User Statistics Schemas
# =============================================================================

class UserStatisticsBase(BaseModel):
    """User statistics base schema"""
    stat_date: date = Field(..., description="Statistics date")
    stat_hour: Optional[int] = Field(None, ge=0, le=23, description="Hour for hourly breakdown")
    total_users: int = Field(0, ge=0, description="Total users")
    active_users: int = Field(0, ge=0, description="Active users")
    new_users: int = Field(0, ge=0, description="New users")
    online_users: int = Field(0, ge=0, description="Currently online users")
    avg_session_time: Optional[float] = Field(None, ge=0, description="Average session time")
    avg_daily_usage: Optional[float] = Field(None, ge=0, description="Average daily usage in bytes")
    user_retention_rate: Optional[float] = Field(None, ge=0, le=100, description="User retention rate percentage")
    power_users_count: int = Field(0, ge=0, description="Power users count")
    occasional_users_count: int = Field(0, ge=0, description="Occasional users count")
    inactive_users_count: int = Field(0, ge=0, description="Inactive users count")
    geographic_distribution: Optional[Dict[str, Any]] = Field(None, description="Geographic distribution")


class UserStatisticsCreate(UserStatisticsBase):
    """User statistics creation schema"""
    pass


class UserStatisticsUpdate(BaseModel):
    """User statistics update schema"""
    total_users: Optional[int] = Field(None, ge=0)
    active_users: Optional[int] = Field(None, ge=0)
    new_users: Optional[int] = Field(None, ge=0)
    online_users: Optional[int] = Field(None, ge=0)
    avg_session_time: Optional[float] = Field(None, ge=0)
    avg_daily_usage: Optional[float] = Field(None, ge=0)
    user_retention_rate: Optional[float] = Field(None, ge=0, le=100)
    power_users_count: Optional[int] = Field(None, ge=0)
    occasional_users_count: Optional[int] = Field(None, ge=0)
    inactive_users_count: Optional[int] = Field(None, ge=0)
    geographic_distribution: Optional[Dict[str, Any]] = None


class UserStatisticsResponse(UserStatisticsBase):
    """User statistics response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# System Metrics Schemas
# =============================================================================

class SystemMetricsBase(BaseModel):
    """System metrics base schema"""
    recorded_at: datetime = Field(..., description="Recording timestamp")
    metric_type: str = Field(..., description="Metric type")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, ge=0, le=100, description="Memory usage percentage")
    disk_usage: Optional[float] = Field(None, ge=0, le=100, description="Disk usage percentage")
    network_in: Optional[float] = Field(None, ge=0, description="Network in MB/s")
    network_out: Optional[float] = Field(None, ge=0, description="Network out MB/s")
    radius_requests: Optional[int] = Field(None, ge=0, description="RADIUS requests")
    radius_accepts: Optional[int] = Field(None, ge=0, description="RADIUS accepts")
    radius_rejects: Optional[int] = Field(None, ge=0, description="RADIUS rejects")
    radius_response_time: Optional[float] = Field(None, ge=0, description="RADIUS response time in ms")
    db_connections: Optional[int] = Field(None, ge=0, description="Database connections")
    db_query_time: Optional[float] = Field(None, ge=0, description="Database query time in ms")
    db_size: Optional[int] = Field(None, ge=0, description="Database size in bytes")
    custom_metrics: Optional[Dict[str, Any]] = Field(None, description="Custom metrics")


class SystemMetricsCreate(SystemMetricsBase):
    """System metrics creation schema"""
    pass


class SystemMetricsResponse(SystemMetricsBase):
    """System metrics response schema"""
    id: int

    class Config:
        from_attributes = True


# =============================================================================
# Graph Template Schemas
# =============================================================================

class GraphTemplateBase(BaseModel):
    """Graph template base schema"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category")
    graph_type: GraphType = Field(..., description="Graph type")
    data_source: str = Field(..., description="Data source or API endpoint")
    time_granularity: TimeGranularity = Field(..., description="Time granularity")
    chart_config: Dict[str, Any] = Field(..., description="Chart.js configuration")
    title: str = Field(..., description="Chart title")
    subtitle: Optional[str] = Field(None, description="Chart subtitle")
    x_axis_label: Optional[str] = Field(None, description="X-axis label")
    y_axis_label: Optional[str] = Field(None, description="Y-axis label")
    default_filters: Optional[Dict[str, Any]] = Field(None, description="Default filters")
    group_by_options: Optional[List[str]] = Field(None, description="Group by options")
    is_public: bool = Field(True, description="Is template public")
    is_active: bool = Field(True, description="Is template active")
    sort_order: int = Field(0, description="Sort order")


class GraphTemplateCreate(GraphTemplateBase):
    """Graph template creation schema"""
    created_by: Optional[str] = Field(None, description="Created by user")


class GraphTemplateUpdate(BaseModel):
    """Graph template update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    graph_type: Optional[GraphType] = None
    data_source: Optional[str] = None
    time_granularity: Optional[TimeGranularity] = None
    chart_config: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    default_filters: Optional[Dict[str, Any]] = None
    group_by_options: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class GraphTemplateResponse(GraphTemplateBase):
    """Graph template response schema"""
    id: int
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Dashboard Widget Schemas
# =============================================================================

class DashboardWidgetBase(BaseModel):
    """Dashboard widget base schema"""
    widget_name: str = Field(..., description="Widget name")
    widget_type: str = Field(..., description="Widget type")
    dashboard_id: Optional[str] = Field(None, description="Dashboard identifier")
    position_x: int = Field(0, ge=0, description="X position")
    position_y: int = Field(0, ge=0, description="Y position")
    width: int = Field(4, ge=1, le=12, description="Width in grid units")
    height: int = Field(3, ge=1, le=12, description="Height in grid units")
    data_source: str = Field(..., description="Data source")
    refresh_interval: int = Field(300, ge=30, description="Refresh interval in seconds")
    widget_config: Dict[str, Any] = Field(..., description="Widget configuration")
    title: str = Field(..., description="Widget title")
    show_title: bool = Field(True, description="Show title")
    background_color: Optional[str] = Field(None, description="Background color")
    border_color: Optional[str] = Field(None, description="Border color")
    is_visible: bool = Field(True, description="Is widget visible")
    is_resizable: bool = Field(True, description="Is widget resizable")
    is_movable: bool = Field(True, description="Is widget movable")
    is_shared: bool = Field(False, description="Is widget shared")


class DashboardWidgetCreate(DashboardWidgetBase):
    """Dashboard widget creation schema"""
    created_by: str = Field(..., description="Created by user")


class DashboardWidgetUpdate(BaseModel):
    """Dashboard widget update schema"""
    widget_name: Optional[str] = None
    widget_type: Optional[str] = None
    dashboard_id: Optional[str] = None
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=1, le=12)
    height: Optional[int] = Field(None, ge=1, le=12)
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = Field(None, ge=30)
    widget_config: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    show_title: Optional[bool] = None
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    is_visible: Optional[bool] = None
    is_resizable: Optional[bool] = None
    is_movable: Optional[bool] = None
    is_shared: Optional[bool] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    """Dashboard widget response schema"""
    id: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Query and Filter Schemas
# =============================================================================

class GraphQueryParams(BaseModel):
    """Graph query parameters"""
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    granularity: Optional[TimeGranularity] = Field(TimeGranularity.DAY, description="Time granularity")
    limit: Optional[int] = Field(100, ge=1, le=10000, description="Result limit")
    group_by: Optional[str] = Field(None, description="Group by field")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class GraphDataRequest(BaseModel):
    """Graph data request schema"""
    graph_type: str = Field(..., description="Graph type")
    data_source: str = Field(..., description="Data source")
    time_range: GraphQueryParams = Field(..., description="Time range and parameters")
    chart_config: Optional[Dict[str, Any]] = Field(None, description="Chart configuration overrides")


class GraphDataResponse(BaseModel):
    """Graph data response schema"""
    graph_type: str
    title: str
    subtitle: Optional[str] = None
    data: Dict[str, Any]  # Chart.js data format
    options: Optional[Dict[str, Any]] = None  # Chart.js options
    metadata: Optional[Dict[str, Any]] = None
    generated_at: datetime


# =============================================================================
# Specific Graph Data Schemas
# =============================================================================

class LoginGraphData(BaseModel):
    """Login graph specific data"""
    dates: List[str]
    successful_logins: List[int]
    failed_logins: List[int]
    unique_users: List[int]
    total_logins: List[int]


class TrafficGraphData(BaseModel):
    """Traffic graph specific data"""
    dates: List[str]
    upload_data: List[int]
    download_data: List[int]
    total_traffic: List[int]
    session_count: List[int]


class UserActivityGraphData(BaseModel):
    """User activity graph specific data"""
    dates: List[str]
    online_users: List[int]
    active_users: List[int]
    new_users: List[int]
    total_users: List[int]


class SystemPerformanceGraphData(BaseModel):
    """System performance graph specific data"""
    timestamps: List[datetime]
    cpu_usage: List[float]
    memory_usage: List[float]
    disk_usage: List[float]
    network_in: List[float]
    network_out: List[float]


# =============================================================================
# Aggregate Data Schemas
# =============================================================================

class DashboardOverview(BaseModel):
    """Dashboard overview data"""
    current_online_users: int
    today_logins: int
    today_traffic: int
    active_sessions: int
    system_health_score: float
    top_users: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    generated_at: datetime


class GraphsListResponse(BaseModel):
    """Graphs list response schema"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int