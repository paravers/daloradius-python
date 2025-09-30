"""
Accounting Service Module

This module provides business logic for accounting/session statistics
and reporting functionality, implementing comprehensive analytics and monitoring.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.repositories.accounting import (
    AccountingRepository,
    UserTrafficSummaryRepository,
    NasTrafficSummaryRepository
)
from app.schemas.accounting import (
    RadAcctResponse, RadAcctCreate, RadAcctUpdate,
    AccountingQuery, AccountingQueryFilters,
    SessionStatistics, TrafficStatistics, AccountingOverview,
    TopUsersReport, HourlyTrafficReport, DailyTrafficReport,
    NasUsageReport, CustomQueryResult, MaintenanceResult,
    PaginatedAccountingResponse, PaginatedTopUsersResponse,
    UserTrafficSummaryResponse, NasTrafficSummaryResponse,
    AccountingTimeRangeEnum
)
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError
from app.core.logging import logger


class AccountingService:
    """Service for accounting operations and analytics"""

    def __init__(self, repository: AccountingRepository):
        self.repository = repository

    async def get_accounting_sessions(
        self,
        query: AccountingQuery
    ) -> PaginatedAccountingResponse:
        """Get paginated accounting sessions with filtering"""
        try:
            # Validate pagination parameters
            if query.page < 1:
                raise ValidationError("Page must be greater than 0")
            if query.page_size < 1 or query.page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Process time range filters
            filters = self._process_filters(query.filters)

            # Get sessions from repository
            sessions, total = await self.repository.get_all_sessions(
                page=query.page,
                page_size=query.page_size,
                filters=filters,
                sort_field=query.sort_field,
                sort_order=query.sort_order
            )

            # Convert to response models
            session_responses = [self._to_response_model(
                session) for session in sessions]

            # Calculate pagination info
            total_pages = (total + query.page_size - 1) // query.page_size

            return PaginatedAccountingResponse(
                data=session_responses,
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages,
                has_next=query.page < total_pages,
                has_prev=query.page > 1
            )

        except Exception as e:
            logger.error(f"Error in get_accounting_sessions: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get accounting sessions: {str(e)}")

    async def get_session_by_id(self, session_id: int) -> RadAcctResponse:
        """Get accounting session by ID"""
        try:
            session = await self.repository.get_session_by_id(session_id)
            if not session:
                raise NotFoundError(f"Session with ID {session_id} not found")

            return self._to_response_model(session)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_session_by_id: {str(e)}")
            raise BusinessLogicError(f"Failed to get session: {str(e)}")

    async def get_active_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        nas_ip: Optional[str] = None,
        username: Optional[str] = None
    ) -> PaginatedAccountingResponse:
        """Get active sessions with filtering"""
        try:
            # Validate pagination
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get active sessions
            sessions, total = await self.repository.get_active_sessions(
                page=page,
                page_size=page_size,
                nas_ip=nas_ip,
                username=username
            )

            # Convert to response models
            session_responses = [self._to_response_model(
                session) for session in sessions]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedAccountingResponse(
                data=session_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )

        except Exception as e:
            logger.error(f"Error in get_active_sessions: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get active sessions: {str(e)}")

    async def get_user_sessions(
        self,
        username: str,
        page: int = 1,
        page_size: int = 20,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> PaginatedAccountingResponse:
        """Get sessions for a specific user"""
        try:
            # Validate input
            if not username:
                raise ValidationError("Username is required")

            # Get user sessions
            sessions, total = await self.repository.get_user_sessions(
                username=username,
                page=page,
                page_size=page_size,
                date_from=date_from,
                date_to=date_to
            )

            # Convert to response models
            session_responses = [self._to_response_model(
                session) for session in sessions]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedAccountingResponse(
                data=session_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            )

        except Exception as e:
            logger.error(f"Error in get_user_sessions: {str(e)}")
            raise BusinessLogicError(f"Failed to get user sessions: {str(e)}")

    async def get_accounting_overview(
        self,
        time_range: Optional[AccountingTimeRangeEnum] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        filters: Optional[AccountingQueryFilters] = None
    ) -> AccountingOverview:
        """Get comprehensive accounting overview"""
        try:
            # Calculate date range
            if time_range and not date_from and not date_to:
                date_from, date_to = self._calculate_time_range(time_range)

            # Process filters
            filter_dict = self._process_filters(filters)
            filter_dict.update({
                'start_date': date_from,
                'end_date': date_to
            })

            # Get statistics
            stats = await self.repository.get_session_statistics(
                date_from=date_from,
                date_to=date_to,
                filters=filter_dict
            )

            # Create response models
            session_stats = SessionStatistics(
                total_sessions=stats['total_sessions'],
                active_sessions=stats['active_sessions'],
                completed_sessions=stats['completed_sessions'],
                average_session_duration=stats['average_session_duration'],
                total_session_time=stats['total_session_time'],
                unique_users=stats['unique_users']
            )

            traffic_stats = TrafficStatistics(
                total_input_octets=stats['total_input_octets'],
                total_output_octets=stats['total_output_octets'],
                total_bytes=stats['total_bytes'],
                total_input_packets=0,  # Not available in basic stats
                total_output_packets=0,  # Not available in basic stats
                total_packets=0,  # Not available in basic stats
                average_throughput=self._calculate_average_throughput(
                    stats['total_bytes'], stats['total_session_time']
                )
            )

            # Generate time period description
            time_period = self._format_time_period(
                time_range, date_from, date_to)

            return AccountingOverview(
                session_stats=session_stats,
                traffic_stats=traffic_stats,
                time_period=time_period,
                last_updated=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error in get_accounting_overview: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get accounting overview: {str(e)}")

    async def get_top_users_report(
        self,
        limit: int = 10,
        page: int = 1,
        page_size: int = 20,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> PaginatedTopUsersResponse:
        """Get top users by traffic consumption"""
        try:
            # Get top users data
            top_users_data = await self.repository.get_top_users_by_traffic(
                limit=limit * page,  # Get more data for pagination
                date_from=date_from,
                date_to=date_to
            )

            # Convert to response models
            top_users = []
            for user_data in top_users_data:
                top_users.append(TopUsersReport(
                    username=user_data['username'],
                    total_sessions=user_data['total_sessions'],
                    total_bytes=user_data['total_bytes'],
                    total_session_time=user_data['total_session_time'],
                    last_session=user_data['last_session'],
                    rank=user_data['rank']
                ))

            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_users = top_users[start_idx:end_idx]

            total_pages = (len(top_users) + page_size - 1) // page_size

            return PaginatedTopUsersResponse(
                data=paginated_users,
                total=len(top_users),
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_top_users_report: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get top users report: {str(e)}")

    async def get_hourly_traffic_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[HourlyTrafficReport]:
        """Get hourly traffic distribution report"""
        try:
            hourly_data = await self.repository.get_hourly_traffic_distribution(
                date_from=date_from,
                date_to=date_to
            )

            # Convert to response models
            hourly_reports = []
            for data in hourly_data:
                hourly_reports.append(HourlyTrafficReport(
                    hour=data['hour'],
                    session_count=data['session_count'],
                    total_bytes=data['total_bytes'],
                    unique_users=data['unique_users']
                ))

            return hourly_reports

        except Exception as e:
            logger.error(f"Error in get_hourly_traffic_report: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get hourly traffic report: {str(e)}")

    async def get_nas_usage_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[NasUsageReport]:
        """Get NAS usage statistics report"""
        try:
            nas_data = await self.repository.get_nas_usage_statistics(
                date_from=date_from,
                date_to=date_to
            )

            # Convert to response models
            nas_reports = []
            for data in nas_data:
                nas_reports.append(NasUsageReport(
                    nasipaddress=data['nasipaddress'],
                    nas_name=None,  # Would need NAS repository to get name
                    total_sessions=data['total_sessions'],
                    active_sessions=data['active_sessions'],
                    total_bytes=data['total_bytes'],
                    utilization_percentage=data['utilization_percentage']
                ))

            return nas_reports

        except Exception as e:
            logger.error(f"Error in get_nas_usage_report: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get NAS usage report: {str(e)}")

    async def execute_custom_query(
        self,
        query_sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> CustomQueryResult:
        """Execute custom accounting query"""
        try:
            # Validate query
            if not query_sql or not query_sql.strip():
                raise ValidationError("Query SQL is required")

            if limit < 1 or limit > 10000:
                raise ValidationError("Limit must be between 1 and 10000")

            # Execute query
            result = await self.repository.execute_custom_query(
                query_sql=query_sql,
                parameters=parameters,
                limit=limit
            )

            return CustomQueryResult(
                columns=result['columns'],
                rows=result['rows'],
                total_rows=result['total_rows'],
                execution_time=result['execution_time']
            )

        except Exception as e:
            logger.error(f"Error in execute_custom_query: {str(e)}")
            raise BusinessLogicError(
                f"Failed to execute custom query: {str(e)}")

    async def cleanup_old_sessions(
        self,
        days_old: int = 365,
        dry_run: bool = True
    ) -> MaintenanceResult:
        """Clean up old accounting sessions"""
        try:
            # Validate parameters
            if days_old < 30:
                raise ValidationError(
                    "Cannot delete sessions less than 30 days old")

            # Execute cleanup
            result = await self.repository.cleanup_old_sessions(
                days_old=days_old,
                dry_run=dry_run
            )

            return MaintenanceResult(
                operation_type=result['operation_type'],
                affected_rows=result['affected_rows'],
                execution_time=0.0,  # Repository doesn't track this
                success=result['success'],
                message=result['message']
            )

        except Exception as e:
            logger.error(f"Error in cleanup_old_sessions: {str(e)}")
            raise BusinessLogicError(
                f"Failed to cleanup old sessions: {str(e)}")

    # =====================================================================
    # Helper Methods
    # =====================================================================

    def _to_response_model(self, session) -> RadAcctResponse:
        """Convert database model to response model"""
        return RadAcctResponse(
            radacctid=session.radacctid,
            username=session.username,
            realm=session.realm,
            acctsessionid=session.acctsessionid,
            acctuniqueid=session.acctuniqueid,
            groupname=session.groupname,
            nasipaddress=str(
                session.nasipaddress) if session.nasipaddress else None,
            nasportid=session.nasportid,
            nasporttype=session.nasporttype,
            calledstationid=session.calledstationid,
            callingstationid=session.callingstationid,
            framedipaddress=str(
                session.framedipaddress) if session.framedipaddress else None,
            servicetype=session.servicetype,
            acctstarttime=session.acctstarttime,
            acctstoptime=session.acctstoptime,
            acctsessiontime=session.acctsessiontime,
            acctinputoctets=session.acctinputoctets or 0,
            acctoutputoctets=session.acctoutputoctets or 0,
            acctinputpackets=session.acctinputpackets or 0,
            acctoutputpackets=session.acctoutputpackets or 0,
            acctterminatecause=session.acctterminatecause,
            total_bytes=session.total_bytes,
            total_packets=session.total_packets,
            is_active=session.is_active,
            formatted_duration=self._format_duration(session.acctsessiontime)
        )

    def _process_filters(self, filters: Optional[AccountingQueryFilters]) -> Dict[str, Any]:
        """Process filters and convert to repository format"""
        if not filters:
            return {}

        filter_dict = {}

        # Direct field mappings
        for field in ['username', 'groupname', 'nasipaddress', 'framedipaddress',
                      'callingstationid', 'servicetype']:
            value = getattr(filters, field, None)
            if value:
                filter_dict[field] = value

        # Date range handling
        if filters.time_range and not filters.start_date and not filters.end_date:
            start_date, end_date = self._calculate_time_range(
                filters.time_range)
            filter_dict['start_date'] = start_date
            filter_dict['end_date'] = end_date
        else:
            if filters.start_date:
                filter_dict['start_date'] = filters.start_date
            if filters.end_date:
                filter_dict['end_date'] = filters.end_date

        # Status filters
        if filters.status:
            filter_dict['status'] = filters.status
        if filters.active_only:
            filter_dict['active_only'] = filters.active_only

        # Traffic filters
        for field in ['min_input_octets', 'max_input_octets', 'min_output_octets',
                      'max_output_octets', 'min_session_time', 'max_session_time']:
            value = getattr(filters, field, None)
            if value is not None:
                filter_dict[field] = value

        return filter_dict

    def _calculate_time_range(self, time_range: AccountingTimeRangeEnum) -> tuple[datetime, datetime]:
        """Calculate start and end dates for predefined time ranges"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if time_range == AccountingTimeRangeEnum.TODAY:
            return today, now
        elif time_range == AccountingTimeRangeEnum.YESTERDAY:
            yesterday = today - timedelta(days=1)
            return yesterday, today
        elif time_range == AccountingTimeRangeEnum.THIS_WEEK:
            week_start = today - timedelta(days=today.weekday())
            return week_start, now
        elif time_range == AccountingTimeRangeEnum.LAST_WEEK:
            week_start = today - timedelta(days=today.weekday() + 7)
            week_end = week_start + timedelta(days=7)
            return week_start, week_end
        elif time_range == AccountingTimeRangeEnum.THIS_MONTH:
            month_start = today.replace(day=1)
            return month_start, now
        elif time_range == AccountingTimeRangeEnum.LAST_MONTH:
            if today.month == 1:
                last_month_start = today.replace(
                    year=today.year-1, month=12, day=1)
            else:
                last_month_start = today.replace(month=today.month-1, day=1)

            current_month_start = today.replace(day=1)
            return last_month_start, current_month_start
        elif time_range == AccountingTimeRangeEnum.THIS_YEAR:
            year_start = today.replace(month=1, day=1)
            return year_start, now
        else:
            # Default to last 30 days
            return today - timedelta(days=30), now

    def _calculate_average_throughput(self, total_bytes: int, total_session_time: int) -> Optional[float]:
        """Calculate average throughput in bytes per second"""
        if total_session_time and total_session_time > 0:
            return float(total_bytes) / float(total_session_time)
        return None

    def _format_time_period(
        self,
        time_range: Optional[AccountingTimeRangeEnum],
        date_from: Optional[datetime],
        date_to: Optional[datetime]
    ) -> str:
        """Format time period description"""
        if time_range:
            return time_range.value.replace('_', ' ').title()
        elif date_from and date_to:
            return f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"
        elif date_from:
            return f"From {date_from.strftime('%Y-%m-%d')}"
        elif date_to:
            return f"Until {date_to.strftime('%Y-%m-%d')}"
        else:
            return "All time"

    def _format_duration(self, seconds: Optional[int]) -> Optional[str]:
        """Format duration in human readable format"""
        if not seconds:
            return None

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# =====================================================================
# User Traffic Summary Service
# =====================================================================

class UserTrafficSummaryService:
    """Service for user traffic summary operations"""

    def __init__(self, repository: UserTrafficSummaryRepository):
        self.repository = repository

    async def get_user_traffic_summary(
        self,
        username: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[UserTrafficSummaryResponse]:
        """Get traffic summary for a user"""
        try:
            summaries = await self.repository.get_user_summary(
                username=username,
                date_from=date_from,
                date_to=date_to
            )

            return [
                UserTrafficSummaryResponse.from_orm(summary)
                for summary in summaries
            ]

        except Exception as e:
            logger.error(f"Error getting user traffic summary: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get user traffic summary: {str(e)}")


# =====================================================================
# NAS Traffic Summary Service
# =====================================================================

class NasTrafficSummaryService:
    """Service for NAS traffic summary operations"""

    def __init__(self, repository: NasTrafficSummaryRepository):
        self.repository = repository

    async def get_nas_traffic_summary(
        self,
        nasipaddress: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[NasTrafficSummaryResponse]:
        """Get traffic summary for a NAS"""
        try:
            summaries = await self.repository.get_nas_summary(
                nasipaddress=nasipaddress,
                date_from=date_from,
                date_to=date_to
            )

            return [
                NasTrafficSummaryResponse.from_orm(summary)
                for summary in summaries
            ]

        except Exception as e:
            logger.error(f"Error getting NAS traffic summary: {str(e)}")
            raise BusinessLogicError(
                f"Failed to get NAS traffic summary: {str(e)}")


# Export services
__all__ = [
    "AccountingService",
    "UserTrafficSummaryService",
    "NasTrafficSummaryService",
]
