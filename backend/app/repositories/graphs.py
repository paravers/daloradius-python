"""
Graphs Repository

This module contains repository classes for graphs data access.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import func, and_, or_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from app.models.graphs import (
    GraphStatistics,
    LoginStatistics,
    TrafficStatistics,
    UserStatistics,
    SystemMetrics,
    GraphTemplate,
    DashboardWidget,
    GraphType,
    TimeGranularity
)
from app.models.user import User, UserSession
from app.models.radacct import RadAcct
from app.models.radcheck import RadCheck
from app.models.nas import Nas


class GraphStatisticsRepository:
    """Repository for graph statistics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> GraphStatistics:
        """Create a new graph statistics record"""
        stat = GraphStatistics(**kwargs)
        self.db.add(stat)
        await self.db.commit()
        await self.db.refresh(stat)
        return stat

    async def get_by_id(self, stat_id: int) -> Optional[GraphStatistics]:
        """Get graph statistics by ID"""
        result = await self.db.execute(
            select(GraphStatistics).where(GraphStatistics.id == stat_id)
        )
        return result.scalar_one_or_none()

    async def get_by_type_and_period(
        self,
        graph_type: str,
        metric_name: str,
        time_period: str,
        start_date: date,
        end_date: date
    ) -> List[GraphStatistics]:
        """Get statistics by type and time period"""
        result = await self.db.execute(
            select(GraphStatistics)
            .where(
                and_(
                    GraphStatistics.graph_type == graph_type,
                    GraphStatistics.metric_name == metric_name,
                    GraphStatistics.time_period == time_period,
                    GraphStatistics.recorded_date >= start_date,
                    GraphStatistics.recorded_date <= end_date
                )
            )
            .order_by(GraphStatistics.recorded_date, GraphStatistics.recorded_hour)
        )
        return result.scalars().all()

    async def aggregate_data(
        self,
        graph_type: str,
        metric_name: str,
        start_date: date,
        end_date: date,
        granularity: TimeGranularity
    ) -> List[Dict[str, Any]]:
        """Aggregate statistics data by granularity"""
        if granularity == TimeGranularity.HOUR:
            return await self._aggregate_hourly(graph_type, metric_name, start_date, end_date)
        elif granularity == TimeGranularity.DAY:
            return await self._aggregate_daily(graph_type, metric_name, start_date, end_date)
        elif granularity == TimeGranularity.WEEK:
            return await self._aggregate_weekly(graph_type, metric_name, start_date, end_date)
        elif granularity == TimeGranularity.MONTH:
            return await self._aggregate_monthly(graph_type, metric_name, start_date, end_date)
        elif granularity == TimeGranularity.YEAR:
            return await self._aggregate_yearly(graph_type, metric_name, start_date, end_date)

    async def _aggregate_hourly(
        self, graph_type: str, metric_name: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Aggregate data by hour"""
        result = await self.db.execute(
            select(
                GraphStatistics.recorded_date,
                GraphStatistics.recorded_hour,
                func.sum(GraphStatistics.value_count).label('total_count'),
                func.sum(GraphStatistics.value_sum).label('total_sum'),
                func.avg(GraphStatistics.value_avg).label('avg_value'),
                func.min(GraphStatistics.value_min).label('min_value'),
                func.max(GraphStatistics.value_max).label('max_value')
            )
            .where(
                and_(
                    GraphStatistics.graph_type == graph_type,
                    GraphStatistics.metric_name == metric_name,
                    GraphStatistics.recorded_date >= start_date,
                    GraphStatistics.recorded_date <= end_date,
                    GraphStatistics.recorded_hour.isnot(None)
                )
            )
            .group_by(GraphStatistics.recorded_date, GraphStatistics.recorded_hour)
            .order_by(GraphStatistics.recorded_date, GraphStatistics.recorded_hour)
        )
        
        return [
            {
                'date': row.recorded_date,
                'hour': row.recorded_hour,
                'datetime': datetime.combine(row.recorded_date, datetime.min.time()) + timedelta(hours=row.recorded_hour),
                'count': row.total_count or 0,
                'sum': row.total_sum or 0,
                'avg': row.avg_value or 0,
                'min': row.min_value or 0,
                'max': row.max_value or 0
            }
            for row in result
        ]

    async def _aggregate_daily(
        self, graph_type: str, metric_name: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Aggregate data by day"""
        result = await self.db.execute(
            select(
                GraphStatistics.recorded_date,
                func.sum(GraphStatistics.value_count).label('total_count'),
                func.sum(GraphStatistics.value_sum).label('total_sum'),
                func.avg(GraphStatistics.value_avg).label('avg_value'),
                func.min(GraphStatistics.value_min).label('min_value'),
                func.max(GraphStatistics.value_max).label('max_value')
            )
            .where(
                and_(
                    GraphStatistics.graph_type == graph_type,
                    GraphStatistics.metric_name == metric_name,
                    GraphStatistics.recorded_date >= start_date,
                    GraphStatistics.recorded_date <= end_date
                )
            )
            .group_by(GraphStatistics.recorded_date)
            .order_by(GraphStatistics.recorded_date)
        )
        
        return [
            {
                'date': row.recorded_date,
                'count': row.total_count or 0,
                'sum': row.total_sum or 0,
                'avg': row.avg_value or 0,
                'min': row.min_value or 0,
                'max': row.max_value or 0
            }
            for row in result
        ]

    async def _aggregate_weekly(
        self, graph_type: str, metric_name: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Aggregate data by week"""
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('week', recorded_date) as week_start,
                    SUM(value_count) as total_count,
                    SUM(value_sum) as total_sum,
                    AVG(value_avg) as avg_value,
                    MIN(value_min) as min_value,
                    MAX(value_max) as max_value
                FROM graph_statistics 
                WHERE graph_type = :graph_type 
                    AND metric_name = :metric_name
                    AND recorded_date >= :start_date 
                    AND recorded_date <= :end_date
                GROUP BY DATE_TRUNC('week', recorded_date)
                ORDER BY week_start
            """),
            {
                'graph_type': graph_type,
                'metric_name': metric_name,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        return [
            {
                'week_start': row.week_start,
                'count': row.total_count or 0,
                'sum': row.total_sum or 0,
                'avg': row.avg_value or 0,
                'min': row.min_value or 0,
                'max': row.max_value or 0
            }
            for row in result
        ]

    async def _aggregate_monthly(
        self, graph_type: str, metric_name: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Aggregate data by month"""
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('month', recorded_date) as month_start,
                    SUM(value_count) as total_count,
                    SUM(value_sum) as total_sum,
                    AVG(value_avg) as avg_value,
                    MIN(value_min) as min_value,
                    MAX(value_max) as max_value
                FROM graph_statistics 
                WHERE graph_type = :graph_type 
                    AND metric_name = :metric_name
                    AND recorded_date >= :start_date 
                    AND recorded_date <= :end_date
                GROUP BY DATE_TRUNC('month', recorded_date)
                ORDER BY month_start
            """),
            {
                'graph_type': graph_type,
                'metric_name': metric_name,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        return [
            {
                'month_start': row.month_start,
                'count': row.total_count or 0,
                'sum': row.total_sum or 0,
                'avg': row.avg_value or 0,
                'min': row.min_value or 0,
                'max': row.max_value or 0
            }
            for row in result
        ]

    async def _aggregate_yearly(
        self, graph_type: str, metric_name: str, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Aggregate data by year"""
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('year', recorded_date) as year_start,
                    SUM(value_count) as total_count,
                    SUM(value_sum) as total_sum,
                    AVG(value_avg) as avg_value,
                    MIN(value_min) as min_value,
                    MAX(value_max) as max_value
                FROM graph_statistics 
                WHERE graph_type = :graph_type 
                    AND metric_name = :metric_name
                    AND recorded_date >= :start_date 
                    AND recorded_date <= :end_date
                GROUP BY DATE_TRUNC('year', recorded_date)
                ORDER BY year_start
            """),
            {
                'graph_type': graph_type,
                'metric_name': metric_name,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        return [
            {
                'year_start': row.year_start,
                'count': row.total_count or 0,
                'sum': row.total_sum or 0,
                'avg': row.avg_value or 0,
                'min': row.min_value or 0,
                'max': row.max_value or 0
            }
            for row in result
        ]


class LoginStatisticsRepository:
    """Repository for login statistics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> LoginStatistics:
        """Create login statistics record"""
        stat = LoginStatistics(**kwargs)
        self.db.add(stat)
        await self.db.commit()
        await self.db.refresh(stat)
        return stat

    async def get_by_date_range(
        self, start_date: date, end_date: date, granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[LoginStatistics]:
        """Get login statistics by date range"""
        query = select(LoginStatistics).where(
            and_(
                LoginStatistics.stat_date >= start_date,
                LoginStatistics.stat_date <= end_date
            )
        )
        
        if granularity == TimeGranularity.HOUR:
            query = query.where(LoginStatistics.stat_hour.isnot(None))
        else:
            query = query.where(LoginStatistics.stat_hour.is_(None))
            
        query = query.order_by(LoginStatistics.stat_date, LoginStatistics.stat_hour)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_login_trends(
        self, start_date: date, end_date: date, granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[Dict[str, Any]]:
        """Get login trends data"""
        stats = await self.get_by_date_range(start_date, end_date, granularity)
        
        return [
            {
                'date': stat.stat_date,
                'hour': stat.stat_hour,
                'total_logins': stat.total_logins,
                'successful_logins': stat.successful_logins,
                'failed_logins': stat.failed_logins,
                'unique_users': stat.unique_users,
                'success_rate': (stat.successful_logins / stat.total_logins * 100) if stat.total_logins > 0 else 0,
                'avg_response_time': stat.avg_response_time,
                'peak_concurrent_users': stat.peak_concurrent_users
            }
            for stat in stats
        ]

    async def get_nas_breakdown(
        self, start_date: date, end_date: date
    ) -> Dict[str, int]:
        """Get NAS device breakdown"""
        result = await self.db.execute(
            select(LoginStatistics.nas_breakdown)
            .where(
                and_(
                    LoginStatistics.stat_date >= start_date,
                    LoginStatistics.stat_date <= end_date,
                    LoginStatistics.nas_breakdown.isnot(None)
                )
            )
        )
        
        combined_breakdown = {}
        for row in result.scalars():
            if row:
                for nas_ip, count in row.items():
                    combined_breakdown[nas_ip] = combined_breakdown.get(nas_ip, 0) + count
                    
        return combined_breakdown

    async def calculate_real_time_stats(self) -> Dict[str, Any]:
        """Calculate real-time login statistics"""
        today = date.today()
        
        # Get today's stats
        result = await self.db.execute(
            select(LoginStatistics)
            .where(LoginStatistics.stat_date == today)
            .order_by(desc(LoginStatistics.stat_hour))
        )
        today_stats = result.scalars().all()
        
        # Calculate current online users from RadAcct
        online_users_result = await self.db.execute(
            select(func.count(RadAcct.username.distinct()))
            .where(
                and_(
                    RadAcct.acctstoptime.is_(None),
                    RadAcct.acctstarttime >= datetime.now() - timedelta(hours=24)
                )
            )
        )
        current_online = online_users_result.scalar() or 0
        
        # Aggregate today's data
        total_logins = sum(stat.total_logins for stat in today_stats)
        successful_logins = sum(stat.successful_logins for stat in today_stats)
        failed_logins = sum(stat.failed_logins for stat in today_stats)
        unique_users = max((stat.unique_users for stat in today_stats), default=0)
        
        return {
            'current_online_users': current_online,
            'today_total_logins': total_logins,
            'today_successful_logins': successful_logins,
            'today_failed_logins': failed_logins,
            'today_unique_users': unique_users,
            'success_rate': (successful_logins / total_logins * 100) if total_logins > 0 else 0,
            'last_updated': datetime.now()
        }


class TrafficStatisticsRepository:
    """Repository for traffic statistics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> TrafficStatistics:
        """Create traffic statistics record"""
        stat = TrafficStatistics(**kwargs)
        self.db.add(stat)
        await self.db.commit()
        await self.db.refresh(stat)
        return stat

    async def get_by_date_range(
        self, start_date: date, end_date: date, granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[TrafficStatistics]:
        """Get traffic statistics by date range"""
        query = select(TrafficStatistics).where(
            and_(
                TrafficStatistics.stat_date >= start_date,
                TrafficStatistics.stat_date <= end_date
            )
        )
        
        if granularity == TimeGranularity.HOUR:
            query = query.where(TrafficStatistics.stat_hour.isnot(None))
        else:
            query = query.where(TrafficStatistics.stat_hour.is_(None))
            
        query = query.order_by(TrafficStatistics.stat_date, TrafficStatistics.stat_hour)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_traffic_trends(
        self, start_date: date, end_date: date, granularity: TimeGranularity = TimeGranularity.DAY
    ) -> List[Dict[str, Any]]:
        """Get traffic trends data"""
        stats = await self.get_by_date_range(start_date, end_date, granularity)
        
        return [
            {
                'date': stat.stat_date,
                'hour': stat.stat_hour,
                'upload_bytes': stat.total_upload,
                'download_bytes': stat.total_download,
                'total_bytes': stat.total_traffic,
                'upload_gb': round(stat.total_upload / (1024**3), 2),
                'download_gb': round(stat.total_download / (1024**3), 2),
                'total_gb': round(stat.total_traffic / (1024**3), 2),
                'sessions': stat.total_sessions,
                'active_sessions': stat.active_sessions,
                'avg_session_duration': stat.avg_session_duration,
                'unique_users': stat.unique_users
            }
            for stat in stats
        ]

    async def get_top_users_by_traffic(
        self, start_date: date, end_date: date, limit: int = 10, traffic_type: str = 'total'
    ) -> List[Dict[str, Any]]:
        """Get top users by traffic usage"""
        if traffic_type == 'upload':
            order_field = desc(RadAcct.acctoutputoctets)
            traffic_field = RadAcct.acctoutputoctets
        elif traffic_type == 'download':
            order_field = desc(RadAcct.acctinputoctets)
            traffic_field = RadAcct.acctinputoctets
        else:
            order_field = desc(RadAcct.acctinputoctets + RadAcct.acctoutputoctets)
            traffic_field = RadAcct.acctinputoctets + RadAcct.acctoutputoctets

        result = await self.db.execute(
            select(
                RadAcct.username,
                func.sum(RadAcct.acctinputoctets).label('total_download'),
                func.sum(RadAcct.acctoutputoctets).label('total_upload'),
                func.sum(RadAcct.acctinputoctets + RadAcct.acctoutputoctets).label('total_traffic'),
                func.count(RadAcct.radacctid).label('session_count'),
                func.sum(RadAcct.acctsessiontime).label('total_time')
            )
            .where(
                and_(
                    RadAcct.acctstarttime >= datetime.combine(start_date, datetime.min.time()),
                    RadAcct.acctstarttime <= datetime.combine(end_date, datetime.max.time())
                )
            )
            .group_by(RadAcct.username)
            .order_by(order_field)
            .limit(limit)
        )
        
        return [
            {
                'username': row.username,
                'total_download': row.total_download or 0,
                'total_upload': row.total_upload or 0,
                'total_traffic': row.total_traffic or 0,
                'download_gb': round((row.total_download or 0) / (1024**3), 2),
                'upload_gb': round((row.total_upload or 0) / (1024**3), 2),
                'total_gb': round((row.total_traffic or 0) / (1024**3), 2),
                'session_count': row.session_count,
                'total_time': row.total_time or 0,
                'avg_session_time': (row.total_time / row.session_count) if row.session_count > 0 else 0
            }
            for row in result
        ]

    async def get_traffic_comparison(
        self, start_date: date, end_date: date, comparison_type: str = 'daily'
    ) -> Dict[str, Any]:
        """Get traffic comparison data"""
        stats = await self.get_by_date_range(start_date, end_date)
        
        if not stats:
            return {'upload': [], 'download': [], 'dates': []}
        
        upload_data = []
        download_data = []
        dates = []
        
        for stat in stats:
            dates.append(stat.stat_date.strftime('%Y-%m-%d'))
            upload_data.append(round(stat.total_upload / (1024**3), 2))  # Convert to GB
            download_data.append(round(stat.total_download / (1024**3), 2))  # Convert to GB
        
        return {
            'dates': dates,
            'upload': upload_data,
            'download': download_data,
            'total_upload': sum(upload_data),
            'total_download': sum(download_data),
            'avg_daily_upload': sum(upload_data) / len(upload_data) if upload_data else 0,
            'avg_daily_download': sum(download_data) / len(download_data) if download_data else 0
        }

    async def calculate_real_time_stats(self) -> Dict[str, Any]:
        """Calculate real-time traffic statistics"""
        today = date.today()
        
        # Get today's traffic from RadAcct
        result = await self.db.execute(
            select(
                func.sum(RadAcct.acctinputoctets).label('total_download'),
                func.sum(RadAcct.acctoutputoctets).label('total_upload'),
                func.count(RadAcct.radacctid.distinct()).label('total_sessions'),
                func.count(
                    func.case(
                        (RadAcct.acctstoptime.is_(None), RadAcct.radacctid)
                    )
                ).label('active_sessions')
            )
            .where(
                RadAcct.acctstarttime >= datetime.combine(today, datetime.min.time())
            )
        )
        
        row = result.first()
        
        return {
            'today_download': row.total_download or 0,
            'today_upload': row.total_upload or 0,
            'today_total': (row.total_download or 0) + (row.total_upload or 0),
            'today_download_gb': round((row.total_download or 0) / (1024**3), 2),
            'today_upload_gb': round((row.total_upload or 0) / (1024**3), 2),
            'today_total_gb': round(((row.total_download or 0) + (row.total_upload or 0)) / (1024**3), 2),
            'total_sessions': row.total_sessions or 0,
            'active_sessions': row.active_sessions or 0,
            'last_updated': datetime.now()
        }


class UserStatisticsRepository:
    """Repository for user statistics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> UserStatistics:
        """Create user statistics record"""
        stat = UserStatistics(**kwargs)
        self.db.add(stat)
        await self.db.commit()
        await self.db.refresh(stat)
        return stat

    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[UserStatistics]:
        """Get user statistics by date range"""
        result = await self.db.execute(
            select(UserStatistics)
            .where(
                and_(
                    UserStatistics.stat_date >= start_date,
                    UserStatistics.stat_date <= end_date
                )
            )
            .order_by(UserStatistics.stat_date)
        )
        return result.scalars().all()

    async def get_user_growth_trends(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get user growth trends"""
        stats = await self.get_by_date_range(start_date, end_date)
        
        return [
            {
                'date': stat.stat_date,
                'total_users': stat.total_users,
                'active_users': stat.active_users,
                'new_users': stat.new_users,
                'online_users': stat.online_users,
                'growth_rate': ((stat.new_users / stat.total_users) * 100) if stat.total_users > 0 else 0,
                'activity_rate': ((stat.active_users / stat.total_users) * 100) if stat.total_users > 0 else 0,
                'online_rate': ((stat.online_users / stat.total_users) * 100) if stat.total_users > 0 else 0
            }
            for stat in stats
        ]

    async def get_user_distribution(self, target_date: date) -> Dict[str, Any]:
        """Get user distribution by activity level"""
        result = await self.db.execute(
            select(UserStatistics)
            .where(UserStatistics.stat_date == target_date)
        )
        stat = result.scalar_one_or_none()
        
        if not stat:
            return {
                'power_users': 0,
                'occasional_users': 0,
                'inactive_users': 0,
                'total_users': 0
            }
        
        return {
            'power_users': stat.power_users_count,
            'occasional_users': stat.occasional_users_count,
            'inactive_users': stat.inactive_users_count,
            'total_users': stat.total_users,
            'power_users_percentage': (stat.power_users_count / stat.total_users * 100) if stat.total_users > 0 else 0,
            'occasional_users_percentage': (stat.occasional_users_count / stat.total_users * 100) if stat.total_users > 0 else 0,
            'inactive_users_percentage': (stat.inactive_users_count / stat.total_users * 100) if stat.total_users > 0 else 0
        }

    async def calculate_user_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive user metrics"""
        # Total users
        total_users_result = await self.db.execute(
            select(func.count(RadCheck.username.distinct()))
        )
        total_users = total_users_result.scalar() or 0
        
        # Active users (logged in within last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users_result = await self.db.execute(
            select(func.count(RadAcct.username.distinct()))
            .where(RadAcct.acctstarttime >= thirty_days_ago)
        )
        active_users = active_users_result.scalar() or 0
        
        # Online users
        online_users_result = await self.db.execute(
            select(func.count(RadAcct.username.distinct()))
            .where(RadAcct.acctstoptime.is_(None))
        )
        online_users = online_users_result.scalar() or 0
        
        # New users (created in last 30 days)
        new_users_result = await self.db.execute(
            select(func.count(User.id))
            .where(User.created_at >= thirty_days_ago)
        )
        new_users = new_users_result.scalar() or 0
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'online_users': online_users,
            'new_users': new_users,
            'activity_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'online_rate': (online_users / total_users * 100) if total_users > 0 else 0,
            'growth_rate': (new_users / total_users * 100) if total_users > 0 else 0,
            'last_updated': datetime.now()
        }


class SystemMetricsRepository:
    """Repository for system metrics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> SystemMetrics:
        """Create system metrics record"""
        metric = SystemMetrics(**kwargs)
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_by_time_range(
        self, 
        start_time: datetime, 
        end_time: datetime,
        metric_type: Optional[str] = None
    ) -> List[SystemMetrics]:
        """Get system metrics by time range"""
        query = select(SystemMetrics).where(
            and_(
                SystemMetrics.recorded_at >= start_time,
                SystemMetrics.recorded_at <= end_time
            )
        )
        
        if metric_type:
            query = query.where(SystemMetrics.metric_type == metric_type)
            
        query = query.order_by(SystemMetrics.recorded_at)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_performance_trends(
        self, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get system performance trends"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        metrics = await self.get_by_time_range(start_time, end_time)
        
        return [
            {
                'timestamp': metric.recorded_at,
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'disk_usage': metric.disk_usage,
                'network_in': metric.network_in,
                'network_out': metric.network_out,
                'radius_requests': metric.radius_requests,
                'radius_response_time': metric.radius_response_time,
                'db_connections': metric.db_connections,
                'db_query_time': metric.db_query_time
            }
            for metric in metrics
        ]

    async def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get latest system metrics"""
        result = await self.db.execute(
            select(SystemMetrics)
            .order_by(desc(SystemMetrics.recorded_at))
            .limit(1)
        )
        metric = result.scalar_one_or_none()
        
        if not metric:
            return None
        
        return {
            'timestamp': metric.recorded_at,
            'cpu_usage': metric.cpu_usage,
            'memory_usage': metric.memory_usage,
            'disk_usage': metric.disk_usage,
            'network_in': metric.network_in,
            'network_out': metric.network_out,
            'radius_requests': metric.radius_requests,
            'radius_accepts': metric.radius_accepts,
            'radius_rejects': metric.radius_rejects,
            'radius_response_time': metric.radius_response_time,
            'db_connections': metric.db_connections,
            'db_query_time': metric.db_query_time,
            'db_size': metric.db_size
        }

    async def calculate_system_health_score(self) -> float:
        """Calculate overall system health score"""
        latest = await self.get_latest_metrics()
        
        if not latest:
            return 0.0
        
        # Weight different metrics
        cpu_score = max(0, 100 - (latest.get('cpu_usage', 0)))
        memory_score = max(0, 100 - (latest.get('memory_usage', 0)))
        disk_score = max(0, 100 - (latest.get('disk_usage', 0)))
        
        # Response time score (assume good < 100ms, bad > 1000ms)
        response_time = latest.get('radius_response_time', 0)
        if response_time < 100:
            response_score = 100
        elif response_time > 1000:
            response_score = 0
        else:
            response_score = 100 - ((response_time - 100) / 9)
        
        # Calculate weighted average
        total_score = (
            cpu_score * 0.3 +
            memory_score * 0.3 +
            disk_score * 0.2 +
            response_score * 0.2
        )
        
        return round(total_score, 1)


class GraphTemplateRepository:
    """Repository for graph template operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> GraphTemplate:
        """Create graph template"""
        template = GraphTemplate(**kwargs)
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_by_id(self, template_id: int) -> Optional[GraphTemplate]:
        """Get template by ID"""
        result = await self.db.execute(
            select(GraphTemplate).where(GraphTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str, is_active: bool = True) -> List[GraphTemplate]:
        """Get templates by category"""
        query = select(GraphTemplate).where(GraphTemplate.category == category)
        
        if is_active:
            query = query.where(GraphTemplate.is_active == True)
            
        query = query.order_by(GraphTemplate.sort_order, GraphTemplate.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_public_templates(self) -> List[GraphTemplate]:
        """Get all public templates"""
        result = await self.db.execute(
            select(GraphTemplate)
            .where(
                and_(
                    GraphTemplate.is_public == True,
                    GraphTemplate.is_active == True
                )
            )
            .order_by(GraphTemplate.category, GraphTemplate.sort_order, GraphTemplate.name)
        )
        return result.scalars().all()

    async def update(self, template_id: int, **kwargs) -> Optional[GraphTemplate]:
        """Update graph template"""
        template = await self.get_by_id(template_id)
        if not template:
            return None
        
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        await self.db.commit()
        await self.db.refresh(template)
        return template


class DashboardWidgetRepository:
    """Repository for dashboard widget operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> DashboardWidget:
        """Create dashboard widget"""
        widget = DashboardWidget(**kwargs)
        self.db.add(widget)
        await self.db.commit()
        await self.db.refresh(widget)
        return widget

    async def get_by_id(self, widget_id: int) -> Optional[DashboardWidget]:
        """Get widget by ID"""
        result = await self.db.execute(
            select(DashboardWidget).where(DashboardWidget.id == widget_id)
        )
        return result.scalar_one_or_none()

    async def get_by_dashboard(
        self, dashboard_id: str, user: str, include_shared: bool = True
    ) -> List[DashboardWidget]:
        """Get widgets by dashboard and user"""
        query = select(DashboardWidget).where(
            and_(
                DashboardWidget.dashboard_id == dashboard_id,
                DashboardWidget.is_visible == True
            )
        )
        
        if include_shared:
            query = query.where(
                or_(
                    DashboardWidget.created_by == user,
                    DashboardWidget.is_shared == True
                )
            )
        else:
            query = query.where(DashboardWidget.created_by == user)
        
        query = query.order_by(DashboardWidget.position_y, DashboardWidget.position_x)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_position(
        self, widget_id: int, position_x: int, position_y: int
    ) -> Optional[DashboardWidget]:
        """Update widget position"""
        widget = await self.get_by_id(widget_id)
        if not widget:
            return None
        
        widget.position_x = position_x
        widget.position_y = position_y
        
        await self.db.commit()
        await self.db.refresh(widget)
        return widget

    async def update_size(
        self, widget_id: int, width: int, height: int
    ) -> Optional[DashboardWidget]:
        """Update widget size"""
        widget = await self.get_by_id(widget_id)
        if not widget:
            return None
        
        widget.width = width
        widget.height = height
        
        await self.db.commit()
        await self.db.refresh(widget)
        return widget

    async def delete(self, widget_id: int) -> bool:
        """Delete widget"""
        widget = await self.get_by_id(widget_id)
        if not widget:
            return False
        
        await self.db.delete(widget)
        await self.db.commit()
        return True