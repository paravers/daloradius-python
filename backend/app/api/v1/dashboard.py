"""
Dashboard API Routes

Comprehensive dashboard endpoints including system statistics,
real-time data, and overview information.
"""

from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.accounting import AccountingService
from app.services.user import UserService
from app.services.nas import NasService
from app.services.billing import BillingService
from app.repositories.accounting import AccountingRepository
from app.repositories.user import UserRepository
from app.repositories.nas import NasRepository
from app.repositories.billing import BillingRepository


router = APIRouter()


# Pydantic models for dashboard responses
class DashboardStats(BaseModel):
    """Dashboard statistics summary"""
    total_users: int = Field(description="Total number of users")
    active_users: int = Field(description="Currently active users")
    total_sessions: int = Field(description="Total session count")
    active_sessions: int = Field(description="Currently active sessions")
    total_nas: int = Field(description="Total NAS devices")
    active_nas: int = Field(description="Active NAS devices")
    total_hotspots: int = Field(description="Total hotspots")
    today_logins: int = Field(description="Logins today")
    today_sessions: int = Field(description="Sessions today")
    today_traffic_gb: float = Field(description="Traffic today in GB")
    monthly_revenue: float = Field(description="Monthly revenue")
    system_health_score: float = Field(
        description="System health score (0-100)")
    last_updated: datetime = Field(description="Last update timestamp")


class RecentActivity(BaseModel):
    """Recent system activity"""
    id: int
    timestamp: datetime
    activity_type: str = Field(description="Type of activity")
    description: str = Field(description="Activity description")
    username: Optional[str] = Field(description="Related username")
    status: str = Field(description="Activity status")


class SystemAlert(BaseModel):
    """System alert information"""
    id: int
    severity: str = Field(description="Alert severity level")
    title: str = Field(description="Alert title")
    message: str = Field(description="Alert message")
    timestamp: datetime = Field(description="Alert timestamp")
    acknowledged: bool = Field(description="Whether alert is acknowledged")


class TopUser(BaseModel):
    """Top user by traffic or usage"""
    username: str
    traffic_gb: float = Field(description="Traffic in GB")
    sessions: int = Field(description="Number of sessions")
    last_login: Optional[datetime] = Field(description="Last login time")


class QuickStats(BaseModel):
    """Quick statistics for dashboard widgets"""
    online_users_now: int
    sessions_last_hour: int
    traffic_last_hour_gb: float
    failed_logins_today: int
    nas_response_time_ms: float


class DashboardOverview(BaseModel):
    """Complete dashboard overview response"""
    stats: DashboardStats
    recent_activity: List[RecentActivity]
    system_alerts: List[SystemAlert]
    top_users: List[TopUser]
    quick_stats: QuickStats
    charts_data: Optional[Dict[str, Any]] = Field(
        description="Chart data for dashboard widgets")


class SystemStatus(BaseModel):
    """System status information"""
    database_status: str = Field(description="Database connection status")
    radius_status: str = Field(description="RADIUS server status")
    cache_status: str = Field(description="Cache system status")
    disk_usage_percent: float = Field(description="Disk usage percentage")
    memory_usage_percent: float = Field(description="Memory usage percentage")
    cpu_usage_percent: float = Field(description="CPU usage percentage")
    uptime_hours: float = Field(description="System uptime in hours")


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard statistics

    Returns key metrics and statistics for the dashboard overview
    """
    try:
        # Initialize repositories and services
        user_repo = UserRepository(db)
        accounting_repo = AccountingRepository(db)
        nas_repo = NasRepository(db)
        billing_repo = BillingRepository(db)

        user_service = UserService(user_repo, accounting_repo)
        accounting_service = AccountingService(accounting_repo)
        nas_service = NasService(nas_repo)
        billing_service = BillingService(billing_repo)

        # Calculate statistics
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())

        # User statistics
        total_users = await user_repo.count()
        active_users = await user_repo.count_active()

        # Session statistics
        total_sessions = await accounting_repo.count_total_sessions()
        active_sessions = await accounting_repo.count_active_sessions()
        today_sessions = await accounting_repo.count_sessions_by_date(today_start)

        # Login statistics
        today_logins = await accounting_repo.count_logins_by_date(today_start)

        # Traffic statistics
        today_traffic = await accounting_repo.get_traffic_by_date(today_start)
        today_traffic_gb = (today_traffic.get(
            'input_octets', 0) + today_traffic.get('output_octets', 0)) / (1024**3)

        # NAS statistics
        total_nas = await nas_repo.count()
        active_nas = await nas_repo.count_active()

        # Hotspot count (estimated from NAS if no dedicated hotspot table)
        total_hotspots = total_nas  # Placeholder

        # Revenue statistics (monthly)
        month_start = datetime(today.year, today.month, 1)
        monthly_revenue = await billing_service.get_monthly_revenue(month_start)

        # System health score (basic calculation)
        health_factors = [
            100 if active_sessions < 1000 else max(
                0, 100 - (active_sessions - 1000) / 10),
            100 if active_nas == total_nas else (
                active_nas / max(total_nas, 1)) * 100,
            90  # Placeholder for other health factors
        ]
        system_health_score = sum(health_factors) / len(health_factors)

        return DashboardStats(
            total_users=total_users,
            active_users=active_users,
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            total_nas=total_nas,
            active_nas=active_nas,
            total_hotspots=total_hotspots,
            today_logins=today_logins,
            today_sessions=today_sessions,
            today_traffic_gb=round(today_traffic_gb, 2),
            monthly_revenue=monthly_revenue,
            system_health_score=round(system_health_score, 1),
            last_updated=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard statistics: {str(e)}"
        )


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    include_charts: bool = Query(
        False, description="Include chart data in response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete dashboard overview including stats, activities, and alerts

    Provides all data needed for the main dashboard page
    """
    try:
        # Get main statistics
        stats = await get_dashboard_stats(db, current_user)

        # Initialize repositories
        accounting_repo = AccountingRepository(db)

        # Get recent activity (last 10 activities)
        recent_activities = await accounting_repo.get_recent_activities(limit=10)
        recent_activity = [
            RecentActivity(
                id=i + 1,
                timestamp=activity.get('timestamp', datetime.utcnow()),
                activity_type=activity.get('type', 'login'),
                description=activity.get(
                    'description', f"User {activity.get('username', 'unknown')} logged in"),
                username=activity.get('username'),
                status=activity.get('status', 'success')
            )
            for i, activity in enumerate(recent_activities)
        ]

        # Get system alerts (mock data for now)
        system_alerts = [
            SystemAlert(
                id=1,
                severity="warning",
                title="High Session Count",
                message="Active sessions approaching limit",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                acknowledged=False
            )
        ] if stats.active_sessions > 500 else []

        # Get top users by traffic (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        top_users_data = await accounting_repo.get_top_users_by_traffic(
            start_date=week_ago,
            limit=5
        )

        top_users = [
            TopUser(
                username=user.get('username', 'unknown'),
                traffic_gb=round(user.get('total_traffic', 0) / (1024**3), 2),
                sessions=user.get('session_count', 0),
                last_login=user.get('last_login')
            )
            for user in top_users_data
        ]

        # Calculate quick stats
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        quick_stats = QuickStats(
            online_users_now=await accounting_repo.count_active_sessions(),
            sessions_last_hour=await accounting_repo.count_sessions_since(hour_ago),
            traffic_last_hour_gb=round(
                (await accounting_repo.get_traffic_since(hour_ago)).get('total', 0) / (1024**3),
                2
            ),
            failed_logins_today=await accounting_repo.count_failed_logins_today(),
            nas_response_time_ms=50.0  # Placeholder
        )

        # Optional chart data
        charts_data = None
        if include_charts:
            charts_data = {
                "sessions_trend": await accounting_repo.get_sessions_trend(days=7),
                "traffic_trend": await accounting_repo.get_traffic_trend(days=7),
                "user_activity": await accounting_repo.get_user_activity_trend(days=30)
            }

        return DashboardOverview(
            stats=stats,
            recent_activity=recent_activity,
            system_alerts=system_alerts,
            top_users=top_users,
            quick_stats=quick_stats,
            charts_data=charts_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard overview: {str(e)}"
        )


@router.get("/system-status", response_model=SystemStatus)
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive system status information

    Returns system health metrics and status indicators
    """
    try:
        # Database status check
        try:
            await db.execute("SELECT 1")
            database_status = "healthy"
        except Exception:
            database_status = "error"

        # Basic system metrics (mock data - in production, integrate with system monitoring)
        system_status = SystemStatus(
            database_status=database_status,
            radius_status="healthy",  # Would check RADIUS server connectivity
            cache_status="healthy",   # Would check Redis/cache connectivity
            disk_usage_percent=75.5,  # Would get from system monitoring
            memory_usage_percent=68.2,
            cpu_usage_percent=45.8,
            uptime_hours=168.5  # Would get actual system uptime
        )

        return system_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system status: {str(e)}"
        )


@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = Query(
        20, ge=1, le=100, description="Number of activities to return"),
    activity_type: Optional[str] = Query(
        None, description="Filter by activity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent system activities with pagination

    Returns recent user activities, logins, and system events
    """
    try:
        accounting_repo = AccountingRepository(db)

        activities = await accounting_repo.get_recent_activities(
            limit=limit,
            activity_type=activity_type
        )

        return {
            "activities": activities,
            "total": len(activities),
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent activities: {str(e)}"
        )


@router.get("/alerts")
async def get_system_alerts(
    severity: Optional[str] = Query(
        None, description="Filter by severity level"),
    acknowledged: Optional[bool] = Query(
        None, description="Filter by acknowledgment status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system alerts and notifications

    Returns system alerts based on various criteria
    """
    try:
        # Mock alerts - in production, this would query an alerts table or monitoring system
        all_alerts = [
            SystemAlert(
                id=1,
                severity="warning",
                title="High Session Count",
                message="Active sessions approaching configured limit",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                acknowledged=False
            ),
            SystemAlert(
                id=2,
                severity="info",
                title="Daily Backup Completed",
                message="Daily database backup completed successfully",
                timestamp=datetime.utcnow() - timedelta(hours=2),
                acknowledged=True
            )
        ]

        # Apply filters
        filtered_alerts = all_alerts
        if severity:
            filtered_alerts = [
                alert for alert in filtered_alerts if alert.severity == severity]
        if acknowledged is not None:
            filtered_alerts = [
                alert for alert in filtered_alerts if alert.acknowledged == acknowledged]

        return {
            "alerts": filtered_alerts,
            "total": len(filtered_alerts),
            "unacknowledged_count": len([a for a in all_alerts if not a.acknowledged])
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system alerts: {str(e)}"
        )
