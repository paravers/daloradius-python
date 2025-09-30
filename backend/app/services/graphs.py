"""
Graphs Service Layer

This module contains business logic services for the graphs system.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.graphs import (
    GraphStatisticsRepository,
    LoginStatisticsRepository,
    TrafficStatisticsRepository,
    UserStatisticsRepository,
    SystemMetricsRepository,
    GraphTemplateRepository,
    DashboardWidgetRepository
)
from app.schemas.graphs import (
    GraphDataRequest,
    GraphDataResponse,
    LoginGraphData,
    TrafficGraphData,
    UserActivityGraphData,
    SystemPerformanceGraphData,
    DashboardOverview,
    ChartConfig,
    ChartDataset,
    ChartDataPoint,
    GraphQueryParams
)
from app.models.graphs import GraphType, TimeGranularity


class GraphDataService:
    """Service for graph data processing and chart generation"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.graph_stats_repo = GraphStatisticsRepository(db)
        self.login_stats_repo = LoginStatisticsRepository(db)
        self.traffic_stats_repo = TrafficStatisticsRepository(db)
        self.user_stats_repo = UserStatisticsRepository(db)
        self.system_metrics_repo = SystemMetricsRepository(db)
        self.template_repo = GraphTemplateRepository(db)
        self.widget_repo = DashboardWidgetRepository(db)

    async def get_graph_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Get graph data based on request parameters"""
        if request.graph_type == "overall_logins":
            return await self._get_login_graph_data(request)
        elif request.graph_type == "download_upload_stats":
            return await self._get_traffic_graph_data(request)
        elif request.graph_type == "logged_users":
            return await self._get_user_activity_data(request)
        elif request.graph_type == "alltime_stats":
            return await self._get_alltime_stats_data(request)
        elif request.graph_type == "top_users":
            return await self._get_top_users_data(request)
        elif request.graph_type == "traffic_comparison":
            return await self._get_traffic_comparison_data(request)
        elif request.graph_type == "system_performance":
            return await self._get_system_performance_data(request)
        else:
            raise ValueError(f"Unsupported graph type: {request.graph_type}")

    async def _get_login_graph_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate login statistics graph data"""
        start_date = request.time_range.start_date or date.today() - timedelta(days=30)
        end_date = request.time_range.end_date or date.today()
        granularity = request.time_range.granularity or TimeGranularity.DAY

        trends = await self.login_stats_repo.get_login_trends(start_date, end_date, granularity)

        # Prepare Chart.js data format
        labels = []
        successful_data = []
        failed_data = []
        unique_users_data = []

        for trend in trends:
            if granularity == TimeGranularity.HOUR:
                labels.append(f"{trend['date']} {trend['hour']:02d}:00")
            else:
                labels.append(trend['date'].strftime('%Y-%m-%d'))
            
            successful_data.append(trend['successful_logins'])
            failed_data.append(trend['failed_logins'])
            unique_users_data.append(trend['unique_users'])

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Successful Logins',
                    'data': successful_data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.6)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Failed Logins',
                    'data': failed_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Unique Users',
                    'data': unique_users_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 2,
                    'fill': False
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Count'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Time'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'mode': 'index',
                    'intersect': False
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="Overall Login Statistics",
            subtitle=f"From {start_date} to {end_date}",
            data=chart_data,
            options=chart_options,
            metadata={
                'total_records': len(trends),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'granularity': granularity.value
            },
            generated_at=datetime.now()
        )

    async def _get_traffic_graph_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate traffic statistics graph data"""
        start_date = request.time_range.start_date or date.today() - timedelta(days=30)
        end_date = request.time_range.end_date or date.today()
        granularity = request.time_range.granularity or TimeGranularity.DAY

        trends = await self.traffic_stats_repo.get_traffic_trends(start_date, end_date, granularity)

        labels = []
        upload_data = []
        download_data = []

        for trend in trends:
            if granularity == TimeGranularity.HOUR:
                labels.append(f"{trend['date']} {trend['hour']:02d}:00")
            else:
                labels.append(trend['date'].strftime('%Y-%m-%d'))
            
            upload_data.append(trend['upload_gb'])
            download_data.append(trend['download_gb'])

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Upload (GB)',
                    'data': upload_data,
                    'backgroundColor': 'rgba(255, 206, 86, 0.6)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 2,
                    'fill': True
                },
                {
                    'label': 'Download (GB)',
                    'data': download_data,
                    'backgroundColor': 'rgba(153, 102, 255, 0.6)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 2,
                    'fill': True
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Traffic (GB)'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Time'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="Download/Upload Statistics",
            subtitle=f"Traffic Analysis from {start_date} to {end_date}",
            data=chart_data,
            options=chart_options,
            metadata={
                'total_upload': sum(upload_data),
                'total_download': sum(download_data),
                'avg_daily_upload': sum(upload_data) / len(upload_data) if upload_data else 0,
                'avg_daily_download': sum(download_data) / len(download_data) if download_data else 0
            },
            generated_at=datetime.now()
        )

    async def _get_user_activity_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate user activity graph data"""
        start_date = request.time_range.start_date or date.today() - timedelta(days=30)
        end_date = request.time_range.end_date or date.today()

        trends = await self.user_stats_repo.get_user_growth_trends(start_date, end_date)

        labels = [trend['date'].strftime('%Y-%m-%d') for trend in trends]
        total_users = [trend['total_users'] for trend in trends]
        active_users = [trend['active_users'] for trend in trends]
        online_users = [trend['online_users'] for trend in trends]
        new_users = [trend['new_users'] for trend in trends]

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Users',
                    'data': total_users,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Active Users',
                    'data': active_users,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Online Users',
                    'data': online_users,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'New Users',
                    'data': new_users,
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 2,
                    'fill': False
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'User Count'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="Logged Users Activity",
            subtitle=f"User Activity Trends from {start_date} to {end_date}",
            data=chart_data,
            options=chart_options,
            metadata={
                'latest_total': total_users[-1] if total_users else 0,
                'latest_active': active_users[-1] if active_users else 0,
                'latest_online': online_users[-1] if online_users else 0
            },
            generated_at=datetime.now()
        )

    async def _get_alltime_stats_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate all-time statistics data"""
        # Get comprehensive stats
        login_stats = await self.login_stats_repo.calculate_real_time_stats()
        traffic_stats = await self.traffic_stats_repo.calculate_real_time_stats()
        user_stats = await self.user_stats_repo.calculate_user_metrics()
        system_health = await self.system_metrics_repo.calculate_system_health_score()

        # Create summary chart data
        categories = ['Total Users', 'Active Users', 'Today Logins', 'Active Sessions']
        values = [
            user_stats['total_users'],
            user_stats['active_users'],
            login_stats['today_total_logins'],
            traffic_stats['active_sessions']
        ]

        chart_data = {
            'labels': categories,
            'datasets': [
                {
                    'label': 'Count',
                    'data': values,
                    'backgroundColor': [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(255, 99, 132, 0.6)'
                    ],
                    'borderColor': [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    'borderWidth': 2
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': False
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="All-Time Statistics Overview",
            subtitle="Comprehensive system statistics",
            data=chart_data,
            options=chart_options,
            metadata={
                'login_stats': login_stats,
                'traffic_stats': traffic_stats,
                'user_stats': user_stats,
                'system_health_score': system_health,
                'performance_indicators': {
                    'user_growth_rate': user_stats['growth_rate'],
                    'login_success_rate': login_stats['success_rate'],
                    'system_health': system_health
                }
            },
            generated_at=datetime.now()
        )

    async def _get_top_users_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate top users by traffic data"""
        start_date = request.time_range.start_date or date.today() - timedelta(days=30)
        end_date = request.time_range.end_date or date.today()
        limit = request.time_range.limit or 10

        traffic_type = request.time_range.filters.get('traffic_type', 'total') if request.time_range.filters else 'total'
        top_users = await self.traffic_stats_repo.get_top_users_by_traffic(
            start_date, end_date, limit, traffic_type
        )

        labels = [user['username'] for user in top_users]
        traffic_data = [user['total_gb'] for user in top_users]
        upload_data = [user['upload_gb'] for user in top_users]
        download_data = [user['download_gb'] for user in top_users]

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Traffic (GB)',
                    'data': traffic_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.6)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Upload (GB)',
                    'data': upload_data,
                    'backgroundColor': 'rgba(255, 206, 86, 0.6)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 2
                },
                {
                    'label': 'Download (GB)',
                    'data': download_data,
                    'backgroundColor': 'rgba(153, 102, 255, 0.6)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 2
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'indexAxis': 'y',  # Horizontal bar chart
            'scales': {
                'x': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Traffic (GB)'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title=f"Top {limit} Users by Traffic",
            subtitle=f"Traffic consumption from {start_date} to {end_date}",
            data=chart_data,
            options=chart_options,
            metadata={
                'traffic_type': traffic_type,
                'user_count': len(top_users),
                'total_traffic': sum(traffic_data),
                'top_users_details': top_users
            },
            generated_at=datetime.now()
        )

    async def _get_traffic_comparison_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate traffic comparison data"""
        start_date = request.time_range.start_date or date.today() - timedelta(days=30)
        end_date = request.time_range.end_date or date.today()

        comparison_data = await self.traffic_stats_repo.get_traffic_comparison(start_date, end_date)

        chart_data = {
            'labels': comparison_data['dates'],
            'datasets': [
                {
                    'label': 'Upload (GB)',
                    'data': comparison_data['upload'],
                    'backgroundColor': 'rgba(255, 206, 86, 0.6)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 2,
                    'fill': True
                },
                {
                    'label': 'Download (GB)',
                    'data': comparison_data['download'],
                    'backgroundColor': 'rgba(153, 102, 255, 0.6)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 2,
                    'fill': True
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'stacked': True,
                    'title': {
                        'display': True,
                        'text': 'Traffic (GB)'
                    }
                },
                'x': {
                    'stacked': True,
                    'title': {
                        'display': True,
                        'text': 'Date'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="Traffic Comparison (Upload vs Download)",
            subtitle=f"Stacked area chart from {start_date} to {end_date}",
            data=chart_data,
            options=chart_options,
            metadata=comparison_data,
            generated_at=datetime.now()
        )

    async def _get_system_performance_data(self, request: GraphDataRequest) -> GraphDataResponse:
        """Generate system performance data"""
        hours = 24  # Default to 24 hours
        if request.time_range.filters:
            hours = request.time_range.filters.get('hours', 24)

        performance_data = await self.system_metrics_repo.get_performance_trends(hours)

        labels = [metric['timestamp'].strftime('%H:%M') for metric in performance_data]
        cpu_data = [metric['cpu_usage'] or 0 for metric in performance_data]
        memory_data = [metric['memory_usage'] or 0 for metric in performance_data]
        disk_data = [metric['disk_usage'] or 0 for metric in performance_data]

        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'CPU Usage (%)',
                    'data': cpu_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Memory Usage (%)',
                    'data': memory_data,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 2,
                    'fill': False
                },
                {
                    'label': 'Disk Usage (%)',
                    'data': disk_data,
                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                    'borderColor': 'rgba(255, 206, 86, 1)',
                    'borderWidth': 2,
                    'fill': False
                }
            ]
        }

        chart_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'max': 100,
                    'title': {
                        'display': True,
                        'text': 'Usage (%)'
                    }
                }
            },
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        system_health = await self.system_metrics_repo.calculate_system_health_score()

        return GraphDataResponse(
            graph_type=request.graph_type,
            title="System Performance Monitoring",
            subtitle=f"Last {hours} hours system metrics",
            data=chart_data,
            options=chart_options,
            metadata={
                'system_health_score': system_health,
                'avg_cpu': sum(cpu_data) / len(cpu_data) if cpu_data else 0,
                'avg_memory': sum(memory_data) / len(memory_data) if memory_data else 0,
                'avg_disk': sum(disk_data) / len(disk_data) if disk_data else 0,
                'latest_metrics': performance_data[-1] if performance_data else None
            },
            generated_at=datetime.now()
        )


class DashboardService:
    """Service for dashboard management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.widget_repo = DashboardWidgetRepository(db)
        self.graph_service = GraphDataService(db)
        self.login_stats_repo = LoginStatisticsRepository(db)
        self.traffic_stats_repo = TrafficStatisticsRepository(db)
        self.user_stats_repo = UserStatisticsRepository(db)
        self.system_metrics_repo = SystemMetricsRepository(db)

    async def get_dashboard_overview(self) -> DashboardOverview:
        """Get comprehensive dashboard overview"""
        # Get real-time statistics
        login_stats = await self.login_stats_repo.calculate_real_time_stats()
        traffic_stats = await self.traffic_stats_repo.calculate_real_time_stats()
        user_stats = await self.user_stats_repo.calculate_user_metrics()
        system_health = await self.system_metrics_repo.calculate_system_health_score()

        # Get top users for the last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        top_users = await self.traffic_stats_repo.get_top_users_by_traffic(
            start_date, end_date, limit=5
        )

        return DashboardOverview(
            current_online_users=login_stats['current_online_users'],
            today_logins=login_stats['today_total_logins'],
            today_traffic=int(traffic_stats['today_total']),
            active_sessions=traffic_stats['active_sessions'],
            system_health_score=system_health,
            top_users=top_users,
            recent_activity=[],  # TODO: Implement recent activity
            alerts=[],  # TODO: Implement alerts
            generated_at=datetime.now()
        )

    async def get_dashboard_widgets(
        self, dashboard_id: str, user: str, include_shared: bool = True
    ) -> List[Dict[str, Any]]:
        """Get dashboard widgets with data"""
        widgets = await self.widget_repo.get_by_dashboard(
            dashboard_id, user, include_shared
        )

        widget_data = []
        for widget in widgets:
            # Get widget data based on data source
            data = await self._get_widget_data(widget.data_source, widget.widget_config)
            
            widget_data.append({
                'id': widget.id,
                'name': widget.widget_name,
                'type': widget.widget_type,
                'position': {'x': widget.position_x, 'y': widget.position_y},
                'size': {'width': widget.width, 'height': widget.height},
                'title': widget.title,
                'config': widget.widget_config,
                'data': data,
                'is_visible': widget.is_visible,
                'refresh_interval': widget.refresh_interval
            })

        return widget_data

    async def _get_widget_data(self, data_source: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for a specific widget"""
        if data_source == "login_stats":
            return await self.login_stats_repo.calculate_real_time_stats()
        elif data_source == "traffic_stats":
            return await self.traffic_stats_repo.calculate_real_time_stats()
        elif data_source == "user_stats":
            return await self.user_stats_repo.calculate_user_metrics()
        elif data_source == "system_metrics":
            return await self.system_metrics_repo.get_latest_metrics()
        elif data_source.startswith("graph_"):
            # Handle graph-based widgets
            graph_type = data_source.replace("graph_", "")
            request = GraphDataRequest(
                graph_type=graph_type,
                data_source=data_source,
                time_range=GraphQueryParams(
                    start_date=config.get('start_date'),
                    end_date=config.get('end_date'),
                    granularity=TimeGranularity(config.get('granularity', 'day')),
                    limit=config.get('limit', 100)
                )
            )
            graph_data = await self.graph_service.get_graph_data(request)
            return graph_data.dict()
        else:
            return {}


class GraphTemplateService:
    """Service for graph template management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = GraphTemplateRepository(db)

    async def get_available_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available graph templates"""
        if category:
            templates = await self.template_repo.get_by_category(category)
        else:
            templates = await self.template_repo.get_public_templates()

        return [
            {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'graph_type': template.graph_type.value,
                'title': template.title,
                'subtitle': template.subtitle,
                'config': template.chart_config,
                'data_source': template.data_source,
                'default_filters': template.default_filters,
                'group_by_options': template.group_by_options
            }
            for template in templates
        ]

    async def create_template_from_config(
        self, name: str, config: Dict[str, Any], user: str
    ) -> Dict[str, Any]:
        """Create a new template from configuration"""
        template = await self.template_repo.create(
            name=name,
            description=config.get('description', ''),
            category=config.get('category', 'custom'),
            graph_type=GraphType(config['graph_type']),
            data_source=config['data_source'],
            time_granularity=TimeGranularity(config.get('time_granularity', 'day')),
            chart_config=config.get('chart_config', {}),
            title=config['title'],
            subtitle=config.get('subtitle'),
            x_axis_label=config.get('x_axis_label'),
            y_axis_label=config.get('y_axis_label'),
            default_filters=config.get('default_filters'),
            group_by_options=config.get('group_by_options'),
            created_by=user,
            is_public=config.get('is_public', False)
        )

        return {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'graph_type': template.graph_type.value,
            'created_at': template.created_at
        }


class RealTimeStatsService:
    """Service for real-time statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.login_stats_repo = LoginStatisticsRepository(db)
        self.traffic_stats_repo = TrafficStatisticsRepository(db)
        self.user_stats_repo = UserStatisticsRepository(db)
        self.system_metrics_repo = SystemMetricsRepository(db)

    async def get_live_stats(self) -> Dict[str, Any]:
        """Get live system statistics"""
        login_stats = await self.login_stats_repo.calculate_real_time_stats()
        traffic_stats = await self.traffic_stats_repo.calculate_real_time_stats()
        user_stats = await self.user_stats_repo.calculate_user_metrics()
        system_metrics = await self.system_metrics_repo.get_latest_metrics()
        system_health = await self.system_metrics_repo.calculate_system_health_score()

        return {
            'online_users': login_stats['current_online_users'],
            'today_logins': login_stats['today_total_logins'],
            'today_traffic_gb': traffic_stats['today_total_gb'],
            'active_sessions': traffic_stats['active_sessions'],
            'system_health': system_health,
            'cpu_usage': system_metrics.get('cpu_usage', 0) if system_metrics else 0,
            'memory_usage': system_metrics.get('memory_usage', 0) if system_metrics else 0,
            'disk_usage': system_metrics.get('disk_usage', 0) if system_metrics else 0,
            'radius_response_time': system_metrics.get('radius_response_time', 0) if system_metrics else 0,
            'last_updated': datetime.now()
        }

    async def get_hourly_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get hourly trends for the dashboard"""
        end_date = date.today()
        start_date = end_date - timedelta(days=1)

        # Get hourly login trends
        login_trends = await self.login_stats_repo.get_login_trends(
            start_date, end_date, TimeGranularity.HOUR
        )

        # Get hourly traffic trends
        traffic_trends = await self.traffic_stats_repo.get_traffic_trends(
            start_date, end_date, TimeGranularity.HOUR
        )

        return {
            'login_trends': login_trends,
            'traffic_trends': traffic_trends,
            'hours_covered': hours
        }