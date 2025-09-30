"""
Reports Repository Layer

This module contains the repository classes for handling database operations
related to the reporting system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from app.models.reports import (
    UpsStatus, RaidStatus, HeartBeat, ReportTemplate,
    ReportGeneration, ServerMonitoring, ReportType,
    SystemStatus, LogLevel
)
from app.models.system import SystemLog
from app.models.user import BatchHistory
from app.models.radius import RadAcct, RadPostAuth
from app.models.user import User
from app.repositories.base import BaseRepository


class UpsStatusRepository(BaseRepository[UpsStatus]):
    """Repository for UPS status operations"""

    def __init__(self, db: Session):
        super().__init__(db, UpsStatus)

    def get_by_name(self, ups_name: str) -> Optional[UpsStatus]:
        """Get UPS by name"""
        return self.db.query(UpsStatus).filter(UpsStatus.ups_name == ups_name).first()

    def get_active_ups(self) -> List[UpsStatus]:
        """Get all active UPS devices"""
        return self.db.query(UpsStatus).filter(
            UpsStatus.status.in_([SystemStatus.ONLINE, SystemStatus.WARNING])
        ).all()

    def get_ups_with_low_battery(self, threshold: float = 20.0) -> List[UpsStatus]:
        """Get UPS devices with low battery"""
        return self.db.query(UpsStatus).filter(
            UpsStatus.battery_charge < threshold
        ).all()

    def get_ups_status_summary(self) -> Dict[str, int]:
        """Get UPS status summary"""
        result = self.db.query(
            UpsStatus.status,
            func.count(UpsStatus.id).label('count')
        ).group_by(UpsStatus.status).all()

        return {status.value: count for status, count in result}


class RaidStatusRepository(BaseRepository[RaidStatus]):
    """Repository for RAID status operations"""

    def __init__(self, db: Session):
        super().__init__(db, RaidStatus)

    def get_by_array_name(self, array_name: str) -> Optional[RaidStatus]:
        """Get RAID by array name"""
        return self.db.query(RaidStatus).filter(RaidStatus.array_name == array_name).first()

    def get_degraded_arrays(self) -> List[RaidStatus]:
        """Get degraded RAID arrays"""
        return self.db.query(RaidStatus).filter(
            or_(
                RaidStatus.failed_disks > 0,
                RaidStatus.status == SystemStatus.WARNING
            )
        ).all()

    def get_arrays_by_controller(self, controller_name: str) -> List[RaidStatus]:
        """Get arrays by controller name"""
        return self.db.query(RaidStatus).filter(
            RaidStatus.controller_name == controller_name
        ).all()

    def get_raid_status_summary(self) -> Dict[str, int]:
        """Get RAID status summary"""
        result = self.db.query(
            RaidStatus.status,
            func.count(RaidStatus.id).label('count')
        ).group_by(RaidStatus.status).all()

        return {status.value: count for status, count in result}


class HeartBeatRepository(BaseRepository[HeartBeat]):
    """Repository for HeartBeat operations"""

    def __init__(self, db: Session):
        super().__init__(db, HeartBeat)

    def get_by_service(self, service_name: str, host_name: str) -> Optional[HeartBeat]:
        """Get heartbeat by service and host"""
        return self.db.query(HeartBeat).filter(
            and_(
                HeartBeat.service_name == service_name,
                HeartBeat.host_name == host_name
            )
        ).first()

    def get_services_by_type(self, service_type: str) -> List[HeartBeat]:
        """Get services by type"""
        return self.db.query(HeartBeat).filter(
            HeartBeat.service_type == service_type
        ).all()

    def get_offline_services(self) -> List[HeartBeat]:
        """Get offline services"""
        return self.db.query(HeartBeat).filter(
            HeartBeat.status == SystemStatus.OFFLINE
        ).all()

    def get_services_by_status(self, status: SystemStatus) -> List[HeartBeat]:
        """Get services by status"""
        return self.db.query(HeartBeat).filter(
            HeartBeat.status == status
        ).all()

    def get_heartbeat_summary(self) -> Dict[str, int]:
        """Get heartbeat status summary"""
        result = self.db.query(
            HeartBeat.status,
            func.count(HeartBeat.id).label('count')
        ).group_by(HeartBeat.status).all()

        return {status.value: count for status, count in result}


class ReportTemplateRepository(BaseRepository[ReportTemplate]):
    """Repository for report template operations"""

    def __init__(self, db: Session):
        super().__init__(db, ReportTemplate)

    def get_by_name(self, name: str) -> Optional[ReportTemplate]:
        """Get template by name"""
        return self.db.query(ReportTemplate).filter(ReportTemplate.name == name).first()

    def get_by_type(self, report_type: ReportType) -> List[ReportTemplate]:
        """Get templates by report type"""
        return self.db.query(ReportTemplate).filter(
            ReportTemplate.report_type == report_type
        ).all()

    def get_public_templates(self) -> List[ReportTemplate]:
        """Get public templates"""
        return self.db.query(ReportTemplate).filter(
            and_(
                ReportTemplate.is_public == True,
                ReportTemplate.is_active == True
            )
        ).all()

    def get_user_templates(self, username: str) -> List[ReportTemplate]:
        """Get user's templates"""
        return self.db.query(ReportTemplate).filter(
            and_(
                ReportTemplate.created_by == username,
                ReportTemplate.is_active == True
            )
        ).all()


class ReportGenerationRepository(BaseRepository[ReportGeneration]):
    """Repository for report generation operations"""

    def __init__(self, db: Session):
        super().__init__(db, ReportGeneration)

    def get_by_status(self, status: str) -> List[ReportGeneration]:
        """Get reports by status"""
        return self.db.query(ReportGeneration).filter(
            ReportGeneration.status == status
        ).all()

    def get_user_reports(self, username: str) -> List[ReportGeneration]:
        """Get user's reports"""
        return self.db.query(ReportGeneration).filter(
            ReportGeneration.generated_by == username
        ).order_by(desc(ReportGeneration.created_at)).all()

    def get_pending_reports(self) -> List[ReportGeneration]:
        """Get pending reports"""
        return self.db.query(ReportGeneration).filter(
            ReportGeneration.status.in_(["pending", "running"])
        ).all()

    def get_completed_reports(self, limit: int = 50) -> List[ReportGeneration]:
        """Get completed reports"""
        return self.db.query(ReportGeneration).filter(
            ReportGeneration.status == "completed"
        ).order_by(desc(ReportGeneration.completed_at)).limit(limit).all()


class ServerMonitoringRepository(BaseRepository[ServerMonitoring]):
    """Repository for server monitoring operations"""

    def __init__(self, db: Session):
        super().__init__(db, ServerMonitoring)

    def get_by_server(self, server_name: str, hours: int = 24) -> List[ServerMonitoring]:
        """Get monitoring data for a server"""
        since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if hours < 24:
            since = datetime.utcnow() - timedelta(hours=hours)

        return self.db.query(ServerMonitoring).filter(
            and_(
                ServerMonitoring.server_name == server_name,
                ServerMonitoring.recorded_at >= since
            )
        ).order_by(ServerMonitoring.recorded_at).all()

    def get_latest_by_server(self, server_name: str) -> Optional[ServerMonitoring]:
        """Get latest monitoring data for a server"""
        return self.db.query(ServerMonitoring).filter(
            ServerMonitoring.server_name == server_name
        ).order_by(desc(ServerMonitoring.recorded_at)).first()

    def get_all_latest(self) -> List[ServerMonitoring]:
        """Get latest monitoring data for all servers"""
        subquery = self.db.query(
            ServerMonitoring.server_name,
            func.max(ServerMonitoring.recorded_at).label('max_time')
        ).group_by(ServerMonitoring.server_name).subquery()

        return self.db.query(ServerMonitoring).join(
            subquery,
            and_(
                ServerMonitoring.server_name == subquery.c.server_name,
                ServerMonitoring.recorded_at == subquery.c.max_time
            )
        ).all()


class ReportsRepository:
    """Main repository for report generation and data analysis"""

    def __init__(self, db: Session):
        self.db = db

    # =============================================================================
    # Online Users Report
    # =============================================================================

    def get_online_users(self, nas_ip: Optional[str] = None,
                         username: Optional[str] = None,
                         session_timeout_min: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get online users report"""
        query = self.db.query(RadAcct).filter(
            RadAcct.acctstoptime.is_(None)  # Still online
        )

        if nas_ip:
            query = query.filter(RadAcct.nasipaddress == nas_ip)

        if username:
            query = query.filter(RadAcct.username.like(f"%{username}%"))

        if session_timeout_min:
            timeout_threshold = datetime.utcnow() - timedelta(minutes=session_timeout_min)
            query = query.filter(RadAcct.acctstarttime >= timeout_threshold)

        sessions = query.order_by(desc(RadAcct.acctstarttime)).all()

        return [
            {
                'username': session.username,
                'nas_ip_address': session.nasipaddress,
                'session_id': session.acctsessionid,
                'start_time': session.acctstarttime,
                'session_duration': int((datetime.utcnow() - session.acctstarttime).total_seconds()),
                'input_octets': session.acctinputoctets or 0,
                'output_octets': session.acctoutputoctets or 0,
                'framed_ip_address': session.framedipaddress
            }
            for session in sessions
        ]

    # =============================================================================
    # History Report
    # =============================================================================

    def get_history_report(self, username: Optional[str] = None,
                           nas_ip: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           session_time_min: Optional[int] = None,
                           limit: int = 1000) -> List[Dict[str, Any]]:
        """Get history report"""
        query = self.db.query(RadAcct).filter(
            RadAcct.acctstoptime.isnot(None)  # Completed sessions
        )

        if username:
            query = query.filter(RadAcct.username.like(f"%{username}%"))

        if nas_ip:
            query = query.filter(RadAcct.nasipaddress == nas_ip)

        if start_date:
            query = query.filter(RadAcct.acctstarttime >= start_date)

        if end_date:
            query = query.filter(RadAcct.acctstarttime <= end_date)

        if session_time_min:
            query = query.filter(RadAcct.acctsessiontime >=
                                 session_time_min * 60)

        sessions = query.order_by(
            desc(RadAcct.acctstarttime)).limit(limit).all()

        return [
            {
                'username': session.username,
                'session_start': session.acctstarttime,
                'session_end': session.acctstoptime,
                'session_time': session.acctsessiontime or 0,
                'input_octets': session.acctinputoctets or 0,
                'output_octets': session.acctoutputoctets or 0,
                'nas_ip_address': session.nasipaddress,
                'terminate_cause': session.acctterminatecause
            }
            for session in sessions
        ]

    # =============================================================================
    # Last Connect Report
    # =============================================================================

    def get_last_connect_report(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get last connect report"""
        # Get latest auth attempt for each user
        subquery = self.db.query(
            RadPostAuth.username,
            func.max(RadPostAuth.authdate).label('last_auth')
        ).group_by(RadPostAuth.username).subquery()

        query = self.db.query(RadPostAuth).join(
            subquery,
            and_(
                RadPostAuth.username == subquery.c.username,
                RadPostAuth.authdate == subquery.c.last_auth
            )
        ).order_by(desc(RadPostAuth.authdate)).limit(limit)

        auth_records = query.all()

        return [
            {
                'username': record.username,
                'last_connect': record.authdate,
                'nas_ip_address': record.nasipaddress,
                'reply': record.reply,
                'auth_status': 'Success' if record.reply == 'Access-Accept' else 'Failed'
            }
            for record in auth_records
        ]

    # =============================================================================
    # New Users Report
    # =============================================================================

    def get_new_users_report(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             group_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get new users report"""
        query = self.db.query(User)

        if start_date:
            query = query.filter(User.created_at >= start_date)

        if end_date:
            query = query.filter(User.created_at <= end_date)

        # Note: group filtering would need additional join with user groups

        users = query.order_by(desc(User.created_at)).all()

        result = []
        for user in users:
            # Get first login from RadPostAuth
            first_login = self.db.query(RadPostAuth.authdate).filter(
                and_(
                    RadPostAuth.username == user.username,
                    RadPostAuth.reply == 'Access-Accept'
                )
            ).order_by(RadPostAuth.authdate).first()

            result.append({
                'username': user.username,
                'created_date': user.created_at,
                'first_login': first_login[0] if first_login else None,
                'group_name': None,  # Would need group relationship
                'email': user.email,
                'status': 'active' if user.is_active else 'inactive'
            })

        return result

    # =============================================================================
    # Top Users Report
    # =============================================================================

    def get_top_users_report(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             limit: int = 10,
                             order_by: str = "total_traffic") -> List[Dict[str, Any]]:
        """Get top users report"""
        query = self.db.query(
            RadAcct.username,
            func.sum(RadAcct.acctinputoctets +
                     RadAcct.acctoutputoctets).label('total_traffic'),
            func.sum(RadAcct.acctsessiontime).label('total_session_time'),
            func.count(RadAcct.radacctid).label('session_count'),
            func.max(RadAcct.acctstarttime).label('last_session')
        ).filter(
            RadAcct.acctstoptime.isnot(None)
        ).group_by(RadAcct.username)

        if start_date:
            query = query.filter(RadAcct.acctstarttime >= start_date)

        if end_date:
            query = query.filter(RadAcct.acctstarttime <= end_date)

        # Order by the specified field
        if order_by == "total_traffic":
            query = query.order_by(desc('total_traffic'))
        elif order_by == "session_time":
            query = query.order_by(desc('total_session_time'))
        elif order_by == "session_count":
            query = query.order_by(desc('session_count'))

        results = query.limit(limit).all()

        return [
            {
                'username': result.username,
                'total_traffic': int(result.total_traffic or 0),
                'session_time': int(result.total_session_time or 0),
                'session_count': result.session_count,
                'last_session': result.last_session
            }
            for result in results
        ]

    # =============================================================================
    # System Logs Report
    # =============================================================================

    def get_system_logs_report(self, log_level: Optional[LogLevel] = None,
                               logger_name: Optional[str] = None,
                               username: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               search_text: Optional[str] = None,
                               limit: int = 1000) -> List[Dict[str, Any]]:
        """Get system logs report"""
        query = self.db.query(SystemLog)

        if log_level:
            query = query.filter(SystemLog.log_level == log_level.value)

        if logger_name:
            query = query.filter(
                SystemLog.logger_name.like(f"%{logger_name}%"))

        if username:
            query = query.filter(SystemLog.username.like(f"%{username}%"))

        if start_date:
            query = query.filter(SystemLog.created_at >= start_date)

        if end_date:
            query = query.filter(SystemLog.created_at <= end_date)

        if search_text:
            query = query.filter(SystemLog.message.like(f"%{search_text}%"))

        logs = query.order_by(desc(SystemLog.created_at)).limit(limit).all()

        return [
            {
                'timestamp': log.created_at,
                'log_level': log.log_level,
                'logger_name': log.logger_name,
                'message': log.message,
                'username': log.username,
                'ip_address': log.ip_address
            }
            for log in logs
        ]

    # =============================================================================
    # Batch Report
    # =============================================================================

    def get_batch_report(self, batch_name: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get batch operations report"""
        query = self.db.query(BatchHistory)

        if batch_name:
            query = query.filter(
                BatchHistory.batch_name.like(f"%{batch_name}%"))

        # Note: BatchHistory model needs created_at field for date filtering

        batches = query.order_by(desc(BatchHistory.id)).all()

        return [
            {
                'batch_name': batch.batch_name,
                'description': batch.batch_description,
                'user_count': 0,  # Would need to calculate from related records
                'success_count': 0,  # Would need to calculate from related records
                'failed_count': 0,  # Would need to calculate from related records
                'created_date': None  # Would need created_at field
            }
            for batch in batches
        ]

    # =============================================================================
    # System Status Report
    # =============================================================================

    def get_system_status_report(self) -> Dict[str, Any]:
        """Get comprehensive system status report"""
        # Server monitoring
        server_monitoring = ServerMonitoringRepository(
            self.db).get_all_latest()

        # UPS status
        ups_repository = UpsStatusRepository(self.db)
        ups_status = ups_repository.get_all()
        ups_summary = ups_repository.get_ups_status_summary()

        # RAID status
        raid_repository = RaidStatusRepository(self.db)
        raid_status = raid_repository.get_all()
        raid_summary = raid_repository.get_raid_status_summary()

        # Heartbeat status
        heartbeat_repository = HeartBeatRepository(self.db)
        heartbeat_status = heartbeat_repository.get_all()
        heartbeat_summary = heartbeat_repository.get_heartbeat_summary()

        return {
            'server_status': [
                {
                    'server_name': server.server_name,
                    'ip_address': server.ip_address,
                    'server_type': server.server_type,
                    'cpu_usage': server.cpu_usage,
                    'memory_usage': server.memory_usage,
                    'disk_usage': server.disk_usage,
                    'uptime': server.uptime,
                    'recorded_at': server.recorded_at
                }
                for server in server_monitoring
            ],
            'service_status': [
                {
                    'service_name': service.service_name,
                    'host_name': service.host_name,
                    'status': service.status.value,
                    'response_time': service.response_time,
                    'last_heartbeat': service.last_heartbeat
                }
                for service in heartbeat_status
            ],
            'ups_status': ups_status,
            'raid_status': raid_status,
            'heartbeat_status': heartbeat_status,
            'summaries': {
                'ups': ups_summary,
                'raid': raid_summary,
                'heartbeat': heartbeat_summary
            },
            'generated_at': datetime.utcnow()
        }
