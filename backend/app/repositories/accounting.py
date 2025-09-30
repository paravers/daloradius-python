"""
Accounting Repository Module

This module provides data access layer for accounting-related operations,
supporting session tracking, traffic analysis, and usage statistics.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import desc, asc, and_, or_, func, text, case, extract
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

from app.models.accounting import (
    RadAcct, RadAcctUpdate, UserTrafficSummary, NasTrafficSummary
)
from app.models.billing import BillingPlan
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import logger


class AccountingRepository:
    """Repository for RADIUS accounting operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # =====================================================================
    # Basic CRUD Operations
    # =====================================================================
    
    async def get_all_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_field: str = "acctstarttime",
        sort_order: str = "desc"
    ) -> Tuple[List[RadAcct], int]:
        """Get all accounting sessions with filtering and pagination"""
        try:
            query = self.session.query(RadAcct)
            
            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            sort_column = getattr(RadAcct, sort_field, RadAcct.acctstarttime)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (page - 1) * page_size
            sessions = query.offset(offset).limit(page_size).all()
            
            return sessions, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching accounting sessions: {str(e)}")
            raise DatabaseError(f"Failed to fetch accounting sessions: {str(e)}")
    
    async def get_session_by_id(self, radacctid: int) -> Optional[RadAcct]:
        """Get accounting session by ID"""
        try:
            return self.session.query(RadAcct).filter(RadAcct.radacctid == radacctid).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching session {radacctid}: {str(e)}")
            raise DatabaseError(f"Failed to fetch session: {str(e)}")
    
    async def get_active_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        nas_ip: Optional[str] = None,
        username: Optional[str] = None
    ) -> Tuple[List[RadAcct], int]:
        """Get active sessions (no stop time)"""
        try:
            query = self.session.query(RadAcct).filter(RadAcct.acctstoptime.is_(None))
            
            if nas_ip:
                query = query.filter(RadAcct.nasipaddress == nas_ip)
            
            if username:
                query = query.filter(RadAcct.username.ilike(f"%{username}%"))
            
            # Get total count
            total = query.count()
            
            # Apply pagination and sorting
            offset = (page - 1) * page_size
            sessions = query.order_by(desc(RadAcct.acctstarttime)).offset(offset).limit(page_size).all()
            
            return sessions, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching active sessions: {str(e)}")
            raise DatabaseError(f"Failed to fetch active sessions: {str(e)}")
    
    async def get_user_sessions(
        self,
        username: str,
        page: int = 1,
        page_size: int = 20,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Tuple[List[RadAcct], int]:
        """Get sessions for a specific user"""
        try:
            query = self.session.query(RadAcct).filter(RadAcct.username == username)
            
            if date_from:
                query = query.filter(RadAcct.acctstarttime >= date_from)
            
            if date_to:
                query = query.filter(RadAcct.acctstarttime <= date_to)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and sorting
            offset = (page - 1) * page_size
            sessions = query.order_by(desc(RadAcct.acctstarttime)).offset(offset).limit(page_size).all()
            
            return sessions, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user sessions for {username}: {str(e)}")
            raise DatabaseError(f"Failed to fetch user sessions: {str(e)}")
    
    # =====================================================================
    # Statistics and Analytics
    # =====================================================================
    
    async def get_session_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get session statistics for a time period"""
        try:
            query = self.session.query(RadAcct)
            
            # Apply date filters
            if date_from:
                query = query.filter(RadAcct.acctstarttime >= date_from)
            if date_to:
                query = query.filter(RadAcct.acctstarttime <= date_to)
            
            # Apply additional filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Calculate statistics
            stats = query.with_entities(
                func.count(RadAcct.radacctid).label('total_sessions'),
                func.count(
                    case([(RadAcct.acctstoptime.is_(None), 1)])
                ).label('active_sessions'),
                func.count(
                    case([(RadAcct.acctstoptime.isnot(None), 1)])
                ).label('completed_sessions'),
                func.sum(RadAcct.acctsessiontime).label('total_session_time'),
                func.avg(RadAcct.acctsessiontime).label('avg_session_time'),
                func.count(func.distinct(RadAcct.username)).label('unique_users'),
                func.sum(RadAcct.acctinputoctets + RadAcct.acctoutputoctets).label('total_bytes'),
                func.sum(RadAcct.acctinputoctets).label('total_input_octets'),
                func.sum(RadAcct.acctoutputoctets).label('total_output_octets')
            ).first()
            
            return {
                'total_sessions': stats.total_sessions or 0,
                'active_sessions': stats.active_sessions or 0,
                'completed_sessions': stats.completed_sessions or 0,
                'total_session_time': stats.total_session_time or 0,
                'average_session_duration': int(stats.avg_session_time or 0),
                'unique_users': stats.unique_users or 0,
                'total_bytes': stats.total_bytes or 0,
                'total_input_octets': stats.total_input_octets or 0,
                'total_output_octets': stats.total_output_octets or 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error calculating session statistics: {str(e)}")
            raise DatabaseError(f"Failed to calculate session statistics: {str(e)}")
    
    async def get_top_users_by_traffic(
        self,
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top users by traffic consumption"""
        try:
            query = self.session.query(RadAcct)
            
            if date_from:
                query = query.filter(RadAcct.acctstarttime >= date_from)
            if date_to:
                query = query.filter(RadAcct.acctstarttime <= date_to)
            
            # Group by username and calculate totals
            results = query.with_entities(
                RadAcct.username,
                func.count(RadAcct.radacctid).label('total_sessions'),
                func.sum(RadAcct.acctinputoctets + RadAcct.acctoutputoctets).label('total_bytes'),
                func.sum(RadAcct.acctsessiontime).label('total_session_time'),
                func.max(RadAcct.acctstarttime).label('last_session')
            ).group_by(RadAcct.username)\
             .order_by(desc('total_bytes'))\
             .limit(limit).all()
            
            # Add ranking
            top_users = []
            for rank, result in enumerate(results, 1):
                top_users.append({
                    'username': result.username,
                    'total_sessions': result.total_sessions,
                    'total_bytes': result.total_bytes or 0,
                    'total_session_time': result.total_session_time or 0,
                    'last_session': result.last_session,
                    'rank': rank
                })
            
            return top_users
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching top users: {str(e)}")
            raise DatabaseError(f"Failed to fetch top users: {str(e)}")
    
    async def get_hourly_traffic_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get hourly traffic distribution"""
        try:
            query = self.session.query(RadAcct)
            
            if date_from:
                query = query.filter(RadAcct.acctstarttime >= date_from)
            if date_to:
                query = query.filter(RadAcct.acctstarttime <= date_to)
            
            # Group by hour and calculate statistics
            results = query.with_entities(
                extract('hour', RadAcct.acctstarttime).label('hour'),
                func.count(RadAcct.radacctid).label('session_count'),
                func.sum(RadAcct.acctinputoctets + RadAcct.acctoutputoctets).label('total_bytes'),
                func.count(func.distinct(RadAcct.username)).label('unique_users')
            ).group_by('hour')\
             .order_by('hour').all()
            
            # Format results
            hourly_data = []
            for result in results:
                hourly_data.append({
                    'hour': int(result.hour),
                    'session_count': result.session_count,
                    'total_bytes': result.total_bytes or 0,
                    'unique_users': result.unique_users
                })
            
            return hourly_data
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching hourly distribution: {str(e)}")
            raise DatabaseError(f"Failed to fetch hourly distribution: {str(e)}")
    
    async def get_nas_usage_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get NAS usage statistics"""
        try:
            query = self.session.query(RadAcct)
            
            if date_from:
                query = query.filter(RadAcct.acctstarttime >= date_from)
            if date_to:
                query = query.filter(RadAcct.acctstarttime <= date_to)
            
            # Group by NAS IP and calculate statistics
            results = query.with_entities(
                RadAcct.nasipaddress,
                func.count(RadAcct.radacctid).label('total_sessions'),
                func.count(
                    case([(RadAcct.acctstoptime.is_(None), 1)])
                ).label('active_sessions'),
                func.sum(RadAcct.acctinputoctets + RadAcct.acctoutputoctets).label('total_bytes')
            ).group_by(RadAcct.nasipaddress)\
             .order_by(desc('total_sessions')).all()
            
            # Format results
            nas_stats = []
            for result in results:
                nas_stats.append({
                    'nasipaddress': result.nasipaddress,
                    'total_sessions': result.total_sessions,
                    'active_sessions': result.active_sessions,
                    'total_bytes': result.total_bytes or 0,
                    'utilization_percentage': 0.0  # Would need NAS capacity data to calculate
                })
            
            return nas_stats
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching NAS statistics: {str(e)}")
            raise DatabaseError(f"Failed to fetch NAS statistics: {str(e)}")
    
    # =====================================================================
    # Custom Queries and Reports
    # =====================================================================
    
    async def execute_custom_query(
        self,
        query_sql: str,
        parameters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Execute custom SQL query with safety checks"""
        try:
            # Basic safety checks
            query_lower = query_sql.lower().strip()
            
            # Only allow SELECT statements
            if not query_lower.startswith('select'):
                raise ValueError("Only SELECT queries are allowed")
            
            # Block dangerous keywords
            dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'truncate', 'alter']
            if any(keyword in query_lower for keyword in dangerous_keywords):
                raise ValueError("Query contains prohibited keywords")
            
            # Add limit if not present
            if 'limit' not in query_lower:
                query_sql += f" LIMIT {limit}"
            
            # Execute query
            start_time = datetime.now()
            result = self.session.execute(text(query_sql), parameters or {})
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Fetch results
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
            
            return {
                'columns': columns,
                'rows': rows,
                'total_rows': len(rows),
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Error executing custom query: {str(e)}")
            raise DatabaseError(f"Failed to execute custom query: {str(e)}")
    
    # =====================================================================
    # Maintenance Operations
    # =====================================================================
    
    async def cleanup_old_sessions(
        self,
        days_old: int = 365,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """Clean up old accounting sessions"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Count records to be deleted
            count_query = self.session.query(func.count(RadAcct.radacctid)).filter(
                RadAcct.acctstarttime < cutoff_date,
                RadAcct.acctstoptime.isnot(None)  # Only delete completed sessions
            )
            record_count = count_query.scalar()
            
            if not dry_run and record_count > 0:
                # Delete old records
                delete_query = self.session.query(RadAcct).filter(
                    RadAcct.acctstarttime < cutoff_date,
                    RadAcct.acctstoptime.isnot(None)
                )
                deleted_count = delete_query.delete(synchronize_session=False)
                self.session.commit()
                
                return {
                    'operation_type': 'cleanup',
                    'affected_rows': deleted_count,
                    'success': True,
                    'message': f"Deleted {deleted_count} old session records"
                }
            else:
                return {
                    'operation_type': 'cleanup_dry_run',
                    'affected_rows': record_count,
                    'success': True,
                    'message': f"Would delete {record_count} old session records"
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Error during cleanup operation: {str(e)}")
            raise DatabaseError(f"Cleanup operation failed: {str(e)}")
    
    # =====================================================================
    # Helper Methods
    # =====================================================================
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query"""
        for key, value in filters.items():
            if value is None:
                continue
                
            if key == 'username':
                query = query.filter(RadAcct.username.ilike(f"%{value}%"))
            elif key == 'groupname':
                query = query.filter(RadAcct.groupname == value)
            elif key == 'nasipaddress':
                query = query.filter(RadAcct.nasipaddress == value)
            elif key == 'framedipaddress':
                query = query.filter(RadAcct.framedipaddress == value)
            elif key == 'callingstationid':
                query = query.filter(RadAcct.callingstationid.ilike(f"%{value}%"))
            elif key == 'servicetype':
                query = query.filter(RadAcct.servicetype == value)
            elif key == 'start_date':
                query = query.filter(RadAcct.acctstarttime >= value)
            elif key == 'end_date':
                query = query.filter(RadAcct.acctstarttime <= value)
            elif key == 'active_only' and value:
                query = query.filter(RadAcct.acctstoptime.is_(None))
            elif key == 'status':
                if value == 'active':
                    query = query.filter(RadAcct.acctstoptime.is_(None))
                elif value == 'stopped':
                    query = query.filter(RadAcct.acctstoptime.isnot(None))
            elif key == 'min_input_octets':
                query = query.filter(RadAcct.acctinputoctets >= value)
            elif key == 'max_input_octets':
                query = query.filter(RadAcct.acctinputoctets <= value)
            elif key == 'min_output_octets':
                query = query.filter(RadAcct.acctoutputoctets >= value)
            elif key == 'max_output_octets':
                query = query.filter(RadAcct.acctoutputoctets <= value)
            elif key == 'min_session_time':
                query = query.filter(RadAcct.acctsessiontime >= value)
            elif key == 'max_session_time':
                query = query.filter(RadAcct.acctsessiontime <= value)
        
        return query


# =====================================================================
# User Traffic Summary Repository
# =====================================================================

class UserTrafficSummaryRepository:
    """Repository for user traffic summary operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_user_summary(
        self,
        username: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[UserTrafficSummary]:
        """Get traffic summary for a user"""
        try:
            query = self.session.query(UserTrafficSummary).filter(
                UserTrafficSummary.username == username
            )
            
            if date_from:
                query = query.filter(UserTrafficSummary.summary_date >= date_from)
            if date_to:
                query = query.filter(UserTrafficSummary.summary_date <= date_to)
            
            return query.order_by(desc(UserTrafficSummary.summary_date)).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user traffic summary: {str(e)}")
            raise DatabaseError(f"Failed to fetch user traffic summary: {str(e)}")


# =====================================================================
# NAS Traffic Summary Repository  
# =====================================================================

class NasTrafficSummaryRepository:
    """Repository for NAS traffic summary operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_nas_summary(
        self,
        nasipaddress: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[NasTrafficSummary]:
        """Get traffic summary for a NAS"""
        try:
            query = self.session.query(NasTrafficSummary).filter(
                NasTrafficSummary.nasipaddress == nasipaddress
            )
            
            if date_from:
                query = query.filter(NasTrafficSummary.summary_date >= date_from)
            if date_to:
                query = query.filter(NasTrafficSummary.summary_date <= date_to)
            
            return query.order_by(desc(NasTrafficSummary.summary_date)).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error fetching NAS traffic summary: {str(e)}")
            raise DatabaseError(f"Failed to fetch NAS traffic summary: {str(e)}")


# Export repositories
__all__ = [
    "AccountingRepository",
    "UserTrafficSummaryRepository", 
    "NasTrafficSummaryRepository",
]