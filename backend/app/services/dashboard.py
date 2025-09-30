"""
Dashboard Service

Provides comprehensive dashboard functionality including statistics aggregation,
real-time data processing, and dashboard widget management.
"""

from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import asyncio
from collections import defaultdict

from app.models.accounting import RadAcct, RadPostAuth
from app.models.user import User
from app.models.nas import Nas
from app.repositories.accounting import AccountingRepository
from app.repositories.user import UserRepository
from app.repositories.nas import NasRepository


class DashboardService:
    """
    Service for dashboard data aggregation and management
    """

    def __init__(self, db: Session):
        self.db = db
        self.accounting_repo = AccountingRepository(db)
        self.user_repo = UserRepository(db)
        self.nas_repo = NasRepository(db)

    async def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics
        
        Returns:
            Dictionary containing all dashboard statistics
        """
        try:
            # Run statistics calculations concurrently for better performance
            stats_tasks = [
                self._get_user_statistics(),
                self._get_session_statistics(),
                self._get_traffic_statistics(),
                self._get_nas_statistics(),
                self._get_revenue_statistics(),
                self._calculate_system_health()
            ]
            
            results = await asyncio.gather(*stats_tasks)
            
            # Combine all statistics
            combined_stats = {}
            for result in results:
                combined_stats.update(result)
            
            combined_stats['last_updated'] = datetime.utcnow()
            
            return combined_stats
            
        except Exception as e:
            raise Exception(f"Failed to get dashboard statistics: {str(e)}")

    async def _get_user_statistics(self) -> Dict[str, Any]:
        """Get user-related statistics"""
        total_users = await self.user_repo.count()
        active_users = await self.user_repo.count_active()
        
        # Users created today
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        new_users_today = await self.user_repo.count_created_since(today_start)
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_today': new_users_today,
            'user_growth_rate': self._calculate_growth_rate('users', 30)
        }

    async def _get_session_statistics(self) -> Dict[str, Any]:
        """Get session-related statistics"""
        # Total and active sessions
        total_sessions = await self.accounting_repo.count_total_sessions()
        active_sessions = await self.accounting_repo.count_active_sessions()
        
        # Today's sessions
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        today_sessions = await self.accounting_repo.count_sessions_by_date(today_start)
        today_logins = await self.accounting_repo.count_logins_by_date(today_start)
        
        # Failed authentications today
        failed_logins_today = await self.accounting_repo.count_failed_logins_today()
        
        # Session duration statistics
        avg_session_duration = await self.accounting_repo.get_average_session_duration()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'today_sessions': today_sessions,
            'today_logins': today_logins,
            'failed_logins_today': failed_logins_today,
            'avg_session_duration_minutes': avg_session_duration
        }

    async def _get_traffic_statistics(self) -> Dict[str, Any]:
        """Get traffic-related statistics"""
        # Today's traffic
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        today_traffic = await self.accounting_repo.get_traffic_by_date(today_start)
        
        # Total traffic
        total_traffic = await self.accounting_repo.get_total_traffic()
        
        # This week's traffic
        week_start = datetime.utcnow() - timedelta(days=7)
        week_traffic = await self.accounting_repo.get_traffic_since(week_start)
        
        # This month's traffic
        month_start = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)
        month_traffic = await self.accounting_repo.get_traffic_since(month_start)
        
        return {
            'today_traffic_gb': round(
                (today_traffic.get('input_octets', 0) + today_traffic.get('output_octets', 0)) / (1024**3), 
                2
            ),
            'week_traffic_gb': round(
                (week_traffic.get('input_octets', 0) + week_traffic.get('output_octets', 0)) / (1024**3), 
                2
            ),
            'month_traffic_gb': round(
                (month_traffic.get('input_octets', 0) + month_traffic.get('output_octets', 0)) / (1024**3), 
                2
            ),
            'total_traffic_tb': round(
                (total_traffic.get('input_octets', 0) + total_traffic.get('output_octets', 0)) / (1024**4), 
                2
            )
        }

    async def _get_nas_statistics(self) -> Dict[str, Any]:
        """Get NAS-related statistics"""
        total_nas = await self.nas_repo.count()
        active_nas = await self.nas_repo.count_active()
        
        # NAS response times (mock data - would integrate with monitoring)
        avg_response_time = 45.2  # milliseconds
        
        return {
            'total_nas': total_nas,
            'active_nas': active_nas,
            'nas_availability_percent': round((active_nas / max(total_nas, 1)) * 100, 1),
            'avg_nas_response_time_ms': avg_response_time
        }

    async def _get_revenue_statistics(self) -> Dict[str, Any]:
        """Get revenue-related statistics"""
        # Monthly revenue calculation
        month_start = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)
        
        # Mock revenue calculation - in production, integrate with billing service
        monthly_revenue = 15420.50  # Would calculate from billing records
        yearly_revenue = 180000.00
        
        return {
            'monthly_revenue': monthly_revenue,
            'yearly_revenue': yearly_revenue,
            'revenue_growth_percent': 12.5  # Mock growth rate
        }

    async def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        # Health factors
        health_factors = []
        
        # Database connectivity (mock - would check actual DB health)
        health_factors.append(95.0)
        
        # Session load factor
        active_sessions = await self.accounting_repo.count_active_sessions()
        session_load = min(100, max(0, 100 - (active_sessions / 1000) * 50))
        health_factors.append(session_load)
        
        # NAS availability
        total_nas = await self.nas_repo.count()
        active_nas = await self.nas_repo.count_active()
        nas_health = (active_nas / max(total_nas, 1)) * 100
        health_factors.append(nas_health)
        
        # Authentication success rate
        failed_logins = await self.accounting_repo.count_failed_logins_today()
        total_logins = await self.accounting_repo.count_logins_today()
        if total_logins > 0:
            auth_success_rate = ((total_logins - failed_logins) / total_logins) * 100
            health_factors.append(auth_success_rate)
        else:
            health_factors.append(100.0)
        
        # Calculate overall health score
        overall_health = sum(health_factors) / len(health_factors)
        
        return {
            'system_health_score': round(overall_health, 1),
            'health_factors': {
                'database_health': health_factors[0],
                'session_load_health': health_factors[1],
                'nas_health': health_factors[2],
                'auth_success_health': health_factors[3] if len(health_factors) > 3 else 100.0
            }
        }

    def _calculate_growth_rate(self, metric_type: str, days: int) -> float:
        """Calculate growth rate for a given metric over specified days"""
        # Mock implementation - in production, calculate actual growth
        growth_rates = {
            'users': 5.2,
            'revenue': 8.7,
            'sessions': 12.1,
            'traffic': 15.6
        }
        return growth_rates.get(metric_type, 0.0)

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics for dashboard widgets
        
        Returns:
            Dictionary containing real-time system metrics
        """
        try:
            current_time = datetime.utcnow()
            
            # Real-time statistics
            online_users = await self.accounting_repo.count_active_sessions()
            
            # Last hour statistics
            hour_ago = current_time - timedelta(hours=1)
            sessions_last_hour = await self.accounting_repo.count_sessions_since(hour_ago)
            traffic_last_hour = await self.accounting_repo.get_traffic_since(hour_ago)
            
            # Today's failed logins
            failed_logins_today = await self.accounting_repo.count_failed_logins_today()
            
            return {
                'timestamp': current_time,
                'online_users_now': online_users,
                'sessions_last_hour': sessions_last_hour,
                'traffic_last_hour_gb': round(
                    (traffic_last_hour.get('input_octets', 0) + traffic_last_hour.get('output_octets', 0)) / (1024**3),
                    2
                ),
                'failed_logins_today': failed_logins_today,
                'system_load_percent': 45.2,  # Mock system load
                'memory_usage_percent': 68.1,
                'disk_usage_percent': 75.8
            }
            
        except Exception as e:
            raise Exception(f"Failed to get real-time metrics: {str(e)}")

    async def get_top_users_analysis(self, 
                                   days: int = 7, 
                                   metric: str = 'traffic',
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top users analysis by various metrics
        
        Args:
            days: Number of days to analyze
            metric: Metric to analyze ('traffic', 'sessions', 'duration')
            limit: Number of top users to return
            
        Returns:
            List of top users with analysis data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            if metric == 'traffic':
                return await self.accounting_repo.get_top_users_by_traffic(start_date, limit)
            elif metric == 'sessions':
                return await self.accounting_repo.get_top_users_by_sessions(start_date, limit)
            elif metric == 'duration':
                return await self.accounting_repo.get_top_users_by_duration(start_date, limit)
            else:
                raise ValueError(f"Invalid metric: {metric}")
                
        except Exception as e:
            raise Exception(f"Failed to get top users analysis: {str(e)}")

    async def get_trend_data(self, 
                           metric: str, 
                           days: int = 30, 
                           granularity: str = 'day') -> List[Dict[str, Any]]:
        """
        Get trend data for dashboard charts
        
        Args:
            metric: Metric to get trend for ('sessions', 'traffic', 'users', 'revenue')
            days: Number of days of historical data
            granularity: Data granularity ('hour', 'day', 'week')
            
        Returns:
            List of trend data points
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            if metric == 'sessions':
                return await self.accounting_repo.get_sessions_trend(start_date, end_date, granularity)
            elif metric == 'traffic':
                return await self.accounting_repo.get_traffic_trend(start_date, end_date, granularity)
            elif metric == 'users':
                return await self._get_user_growth_trend(start_date, end_date, granularity)
            elif metric == 'revenue':
                return await self._get_revenue_trend(start_date, end_date, granularity)
            else:
                raise ValueError(f"Invalid metric: {metric}")
                
        except Exception as e:
            raise Exception(f"Failed to get trend data: {str(e)}")

    async def _get_user_growth_trend(self, 
                                   start_date: datetime, 
                                   end_date: datetime, 
                                   granularity: str) -> List[Dict[str, Any]]:
        """Get user growth trend data"""
        # Mock implementation - in production, query actual user creation data
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Mock user growth data
            new_users = 5 + (current_date.day % 10)  # Simulate varying growth
            total_users = 1000 + (current_date - start_date).days * 5
            
            trend_data.append({
                'date': current_date.date(),
                'new_users': new_users,
                'total_users': total_users
            })
            
            if granularity == 'day':
                current_date += timedelta(days=1)
            elif granularity == 'week':
                current_date += timedelta(weeks=1)
            else:
                current_date += timedelta(hours=1)
        
        return trend_data

    async def _get_revenue_trend(self, 
                               start_date: datetime, 
                               end_date: datetime, 
                               granularity: str) -> List[Dict[str, Any]]:
        """Get revenue trend data"""
        # Mock implementation - in production, integrate with billing service
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Mock revenue data
            daily_revenue = 500 + (current_date.day % 20) * 25
            
            trend_data.append({
                'date': current_date.date(),
                'revenue': daily_revenue,
                'currency': 'USD'
            })
            
            if granularity == 'day':
                current_date += timedelta(days=1)
            elif granularity == 'week':
                current_date += timedelta(weeks=1)
            else:
                current_date += timedelta(hours=1)
        
        return trend_data

    async def get_system_alerts(self) -> List[Dict[str, Any]]:
        """
        Get current system alerts and warnings
        
        Returns:
            List of active system alerts
        """
        alerts = []
        
        try:
            # Check for high session count
            active_sessions = await self.accounting_repo.count_active_sessions()
            if active_sessions > 500:  # Configurable threshold
                alerts.append({
                    'id': 1,
                    'severity': 'warning',
                    'title': 'High Session Count',
                    'message': f'Active sessions ({active_sessions}) approaching limit',
                    'timestamp': datetime.utcnow(),
                    'acknowledged': False
                })
            
            # Check for failed authentication rate
            failed_logins = await self.accounting_repo.count_failed_logins_today()
            total_logins = await self.accounting_repo.count_logins_today()
            
            if total_logins > 0 and (failed_logins / total_logins) > 0.1:  # >10% failure rate
                alerts.append({
                    'id': 2,
                    'severity': 'warning',
                    'title': 'High Authentication Failure Rate',
                    'message': f'Authentication failure rate is {(failed_logins/total_logins)*100:.1f}%',
                    'timestamp': datetime.utcnow(),
                    'acknowledged': False
                })
            
            # Check for inactive NAS devices
            total_nas = await self.nas_repo.count()
            active_nas = await self.nas_repo.count_active()
            
            if total_nas > 0 and (active_nas / total_nas) < 0.9:  # <90% availability
                alerts.append({
                    'id': 3,
                    'severity': 'error',
                    'title': 'NAS Device Issues',
                    'message': f'{total_nas - active_nas} NAS devices are inactive',
                    'timestamp': datetime.utcnow(),
                    'acknowledged': False
                })
            
            return alerts
            
        except Exception as e:
            # Return a system error alert if we can't check other alerts
            return [{
                'id': 999,
                'severity': 'error',
                'title': 'System Monitoring Error',
                'message': f'Unable to check system status: {str(e)}',
                'timestamp': datetime.utcnow(),
                'acknowledged': False
            }]