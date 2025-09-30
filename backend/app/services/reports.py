"""
Reports Service Layer

This module contains the business logic for the reporting system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.reports import (
    UpsStatus, RaidStatus, HeartBeat, ReportTemplate,
    ReportGeneration, ServerMonitoring, ReportType,
    SystemStatus, LogLevel
)
from app.repositories.reports import (
    UpsStatusRepository, RaidStatusRepository, HeartBeatRepository,
    ReportTemplateRepository, ReportGenerationRepository,
    ServerMonitoringRepository, ReportsRepository
)
from app.schemas.reports import (
    UpsStatusCreate, UpsStatusUpdate, UpsStatusResponse,
    RaidStatusCreate, RaidStatusUpdate, RaidStatusResponse,
    HeartBeatCreate, HeartBeatUpdate, HeartBeatResponse,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse,
    ReportGenerationCreate, ReportGenerationUpdate, ReportGenerationResponse,
    ServerMonitoringCreate, ServerMonitoringResponse,
    OnlineUsersReportQuery, HistoryReportQuery, NewUsersReportQuery,
    TopUsersReportQuery, SystemLogQuery, BatchReportQuery
)
from app.core.exceptions import ValidationError, NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class UpsStatusService:
    """Service for UPS status management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UpsStatusRepository(db)
    
    async def create_ups_status(self, ups_data: UpsStatusCreate) -> UpsStatusResponse:
        """Create new UPS status record"""
        try:
            # Check if UPS with same name already exists
            existing = self.repository.get_by_name(ups_data.ups_name)
            if existing:
                raise ValidationError(f"UPS with name '{ups_data.ups_name}' already exists")
            
            ups_status = UpsStatus(**ups_data.dict())
            created = self.repository.create(ups_status)
            
            logger.info(f"Created UPS status record: {ups_data.ups_name}")
            return UpsStatusResponse.from_orm(created)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error creating UPS status: {e}")
            raise ValidationError("Failed to create UPS status record")
    
    async def get_ups_status(self, ups_id: int) -> UpsStatusResponse:
        """Get UPS status by ID"""
        ups_status = self.repository.get_by_id(ups_id)
        if not ups_status:
            raise NotFoundError(f"UPS status with ID {ups_id} not found")
        
        return UpsStatusResponse.from_orm(ups_status)
    
    async def update_ups_status(self, ups_id: int, update_data: UpsStatusUpdate) -> UpsStatusResponse:
        """Update UPS status"""
        ups_status = self.repository.get_by_id(ups_id)
        if not ups_status:
            raise NotFoundError(f"UPS status with ID {ups_id} not found")
        
        try:
            updated = self.repository.update(ups_status, update_data.dict(exclude_unset=True))
            logger.info(f"Updated UPS status: {ups_status.ups_name}")
            return UpsStatusResponse.from_orm(updated)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error updating UPS status: {e}")
            raise ValidationError("Failed to update UPS status")
    
    async def delete_ups_status(self, ups_id: int) -> bool:
        """Delete UPS status"""
        ups_status = self.repository.get_by_id(ups_id)
        if not ups_status:
            raise NotFoundError(f"UPS status with ID {ups_id} not found")
        
        try:
            self.repository.delete(ups_status)
            logger.info(f"Deleted UPS status: {ups_status.ups_name}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting UPS status: {e}")
            raise ValidationError("Failed to delete UPS status")
    
    async def get_all_ups_status(self, skip: int = 0, limit: int = 100) -> List[UpsStatusResponse]:
        """Get all UPS status records"""
        ups_statuses = self.repository.get_all(skip=skip, limit=limit)
        return [UpsStatusResponse.from_orm(ups) for ups in ups_statuses]
    
    async def get_ups_summary(self) -> Dict[str, Any]:
        """Get UPS status summary"""
        summary = self.repository.get_ups_status_summary()
        low_battery = self.repository.get_ups_with_low_battery()
        
        return {
            'status_summary': summary,
            'total_devices': sum(summary.values()),
            'low_battery_count': len(low_battery),
            'low_battery_devices': [ups.ups_name for ups in low_battery]
        }


class RaidStatusService:
    """Service for RAID status management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = RaidStatusRepository(db)
    
    async def create_raid_status(self, raid_data: RaidStatusCreate) -> RaidStatusResponse:
        """Create new RAID status record"""
        try:
            # Check if RAID with same array name already exists
            existing = self.repository.get_by_array_name(raid_data.array_name)
            if existing:
                raise ValidationError(f"RAID array '{raid_data.array_name}' already exists")
            
            raid_status = RaidStatus(**raid_data.dict())
            created = self.repository.create(raid_status)
            
            logger.info(f"Created RAID status record: {raid_data.array_name}")
            return RaidStatusResponse.from_orm(created)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error creating RAID status: {e}")
            raise ValidationError("Failed to create RAID status record")
    
    async def get_raid_status(self, raid_id: int) -> RaidStatusResponse:
        """Get RAID status by ID"""
        raid_status = self.repository.get_by_id(raid_id)
        if not raid_status:
            raise NotFoundError(f"RAID status with ID {raid_id} not found")
        
        return RaidStatusResponse.from_orm(raid_status)
    
    async def update_raid_status(self, raid_id: int, update_data: RaidStatusUpdate) -> RaidStatusResponse:
        """Update RAID status"""
        raid_status = self.repository.get_by_id(raid_id)
        if not raid_status:
            raise NotFoundError(f"RAID status with ID {raid_id} not found")
        
        try:
            updated = self.repository.update(raid_status, update_data.dict(exclude_unset=True))
            logger.info(f"Updated RAID status: {raid_status.array_name}")
            return RaidStatusResponse.from_orm(updated)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error updating RAID status: {e}")
            raise ValidationError("Failed to update RAID status")
    
    async def delete_raid_status(self, raid_id: int) -> bool:
        """Delete RAID status"""
        raid_status = self.repository.get_by_id(raid_id)
        if not raid_status:
            raise NotFoundError(f"RAID status with ID {raid_id} not found")
        
        try:
            self.repository.delete(raid_status)
            logger.info(f"Deleted RAID status: {raid_status.array_name}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting RAID status: {e}")
            raise ValidationError("Failed to delete RAID status")
    
    async def get_all_raid_status(self, skip: int = 0, limit: int = 100) -> List[RaidStatusResponse]:
        """Get all RAID status records"""
        raid_statuses = self.repository.get_all(skip=skip, limit=limit)
        return [RaidStatusResponse.from_orm(raid) for raid in raid_statuses]
    
    async def get_raid_summary(self) -> Dict[str, Any]:
        """Get RAID status summary"""
        summary = self.repository.get_raid_status_summary()
        degraded = self.repository.get_degraded_arrays()
        
        return {
            'status_summary': summary,
            'total_arrays': sum(summary.values()),
            'degraded_count': len(degraded),
            'degraded_arrays': [raid.array_name for raid in degraded]
        }


class HeartBeatService:
    """Service for HeartBeat monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = HeartBeatRepository(db)
    
    async def create_heartbeat(self, heartbeat_data: HeartBeatCreate) -> HeartBeatResponse:
        """Create new heartbeat record"""
        try:
            # Check if service already exists
            existing = self.repository.get_by_service(
                heartbeat_data.service_name,
                heartbeat_data.host_name
            )
            if existing:
                raise ValidationError(
                    f"Service '{heartbeat_data.service_name}' on host "
                    f"'{heartbeat_data.host_name}' already exists"
                )
            
            heartbeat = HeartBeat(**heartbeat_data.dict())
            created = self.repository.create(heartbeat)
            
            logger.info(
                f"Created heartbeat record: {heartbeat_data.service_name} "
                f"on {heartbeat_data.host_name}"
            )
            return HeartBeatResponse.from_orm(created)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error creating heartbeat: {e}")
            raise ValidationError("Failed to create heartbeat record")
    
    async def get_heartbeat(self, heartbeat_id: int) -> HeartBeatResponse:
        """Get heartbeat by ID"""
        heartbeat = self.repository.get_by_id(heartbeat_id)
        if not heartbeat:
            raise NotFoundError(f"Heartbeat with ID {heartbeat_id} not found")
        
        return HeartBeatResponse.from_orm(heartbeat)
    
    async def update_heartbeat(self, heartbeat_id: int, update_data: HeartBeatUpdate) -> HeartBeatResponse:
        """Update heartbeat"""
        heartbeat = self.repository.get_by_id(heartbeat_id)
        if not heartbeat:
            raise NotFoundError(f"Heartbeat with ID {heartbeat_id} not found")
        
        try:
            # Update last_heartbeat if status is being updated to online
            update_dict = update_data.dict(exclude_unset=True)
            if update_dict.get('status') == SystemStatus.ONLINE:
                update_dict['last_heartbeat'] = datetime.utcnow()
            
            updated = self.repository.update(heartbeat, update_dict)
            logger.info(f"Updated heartbeat: {heartbeat.service_name}")
            return HeartBeatResponse.from_orm(updated)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error updating heartbeat: {e}")
            raise ValidationError("Failed to update heartbeat")
    
    async def delete_heartbeat(self, heartbeat_id: int) -> bool:
        """Delete heartbeat"""
        heartbeat = self.repository.get_by_id(heartbeat_id)
        if not heartbeat:
            raise NotFoundError(f"Heartbeat with ID {heartbeat_id} not found")
        
        try:
            self.repository.delete(heartbeat)
            logger.info(f"Deleted heartbeat: {heartbeat.service_name}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting heartbeat: {e}")
            raise ValidationError("Failed to delete heartbeat")
    
    async def get_all_heartbeats(self, skip: int = 0, limit: int = 100) -> List[HeartBeatResponse]:
        """Get all heartbeat records"""
        heartbeats = self.repository.get_all(skip=skip, limit=limit)
        return [HeartBeatResponse.from_orm(hb) for hb in heartbeats]
    
    async def get_heartbeat_summary(self) -> Dict[str, Any]:
        """Get heartbeat status summary"""
        summary = self.repository.get_heartbeat_summary()
        offline_services = self.repository.get_offline_services()
        
        return {
            'status_summary': summary,
            'total_services': sum(summary.values()),
            'offline_count': len(offline_services),
            'offline_services': [
                f"{service.service_name} on {service.host_name}"
                for service in offline_services
            ]
        }


class ReportTemplateService:
    """Service for report template management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportTemplateRepository(db)
    
    async def create_template(self, template_data: ReportTemplateCreate) -> ReportTemplateResponse:
        """Create new report template"""
        try:
            # Check if template with same name already exists
            existing = self.repository.get_by_name(template_data.name)
            if existing:
                raise ValidationError(f"Template with name '{template_data.name}' already exists")
            
            template = ReportTemplate(**template_data.dict())
            created = self.repository.create(template)
            
            logger.info(f"Created report template: {template_data.name}")
            return ReportTemplateResponse.from_orm(created)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error creating template: {e}")
            raise ValidationError("Failed to create report template")
    
    async def get_template(self, template_id: int) -> ReportTemplateResponse:
        """Get template by ID"""
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundError(f"Template with ID {template_id} not found")
        
        return ReportTemplateResponse.from_orm(template)
    
    async def update_template(self, template_id: int, update_data: ReportTemplateUpdate) -> ReportTemplateResponse:
        """Update report template"""
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundError(f"Template with ID {template_id} not found")
        
        try:
            updated = self.repository.update(template, update_data.dict(exclude_unset=True))
            logger.info(f"Updated template: {template.name}")
            return ReportTemplateResponse.from_orm(updated)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error updating template: {e}")
            raise ValidationError("Failed to update template")
    
    async def delete_template(self, template_id: int) -> bool:
        """Delete report template"""
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundError(f"Template with ID {template_id} not found")
        
        try:
            self.repository.delete(template)
            logger.info(f"Deleted template: {template.name}")
            return True
        
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting template: {e}")
            raise ValidationError("Failed to delete template")
    
    async def get_all_templates(self, skip: int = 0, limit: int = 100) -> List[ReportTemplateResponse]:
        """Get all templates"""
        templates = self.repository.get_all(skip=skip, limit=limit)
        return [ReportTemplateResponse.from_orm(template) for template in templates]
    
    async def get_templates_by_type(self, report_type: ReportType) -> List[ReportTemplateResponse]:
        """Get templates by report type"""
        templates = self.repository.get_by_type(report_type)
        return [ReportTemplateResponse.from_orm(template) for template in templates]


class ReportGenerationService:
    """Service for report generation management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportGenerationRepository(db)
        self.reports_repository = ReportsRepository(db)
    
    async def create_report_generation(self, report_data: ReportGenerationCreate) -> ReportGenerationResponse:
        """Create new report generation request"""
        try:
            generation = ReportGeneration(**report_data.dict(), status="pending")
            created = self.repository.create(generation)
            
            # Start async report generation
            asyncio.create_task(self._generate_report(created.id))
            
            logger.info(f"Created report generation request: {report_data.report_name}")
            return ReportGenerationResponse.from_orm(created)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error creating report generation: {e}")
            raise ValidationError("Failed to create report generation request")
    
    async def get_report_generation(self, generation_id: int) -> ReportGenerationResponse:
        """Get report generation by ID"""
        generation = self.repository.get_by_id(generation_id)
        if not generation:
            raise NotFoundError(f"Report generation with ID {generation_id} not found")
        
        return ReportGenerationResponse.from_orm(generation)
    
    async def get_user_reports(self, username: str) -> List[ReportGenerationResponse]:
        """Get user's report generations"""
        reports = self.repository.get_user_reports(username)
        return [ReportGenerationResponse.from_orm(report) for report in reports]
    
    async def get_pending_reports(self) -> List[ReportGenerationResponse]:
        """Get pending report generations"""
        reports = self.repository.get_pending_reports()
        return [ReportGenerationResponse.from_orm(report) for report in reports]
    
    async def _generate_report(self, generation_id: int):
        """Generate report asynchronously"""
        try:
            generation = self.repository.get_by_id(generation_id)
            if not generation:
                return
            
            # Update status to running
            self.repository.update(generation, {
                'status': 'running',
                'started_at': datetime.utcnow(),
                'progress': 0
            })
            
            # Generate report based on type
            if generation.report_type == ReportType.ONLINE_USERS:
                data = await self._generate_online_users_report(generation)
            elif generation.report_type == ReportType.HISTORY:
                data = await self._generate_history_report(generation)
            elif generation.report_type == ReportType.NEW_USERS:
                data = await self._generate_new_users_report(generation)
            elif generation.report_type == ReportType.TOP_USERS:
                data = await self._generate_top_users_report(generation)
            elif generation.report_type == ReportType.SYSTEM_LOGS:
                data = await self._generate_system_logs_report(generation)
            else:
                raise ValidationError(f"Unsupported report type: {generation.report_type}")
            
            # Save report data (could save to file or database)
            file_path = f"/tmp/reports/{generation.id}_{generation.report_name}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, default=str, indent=2)
            
            # Update completion status
            self.repository.update(generation, {
                'status': 'completed',
                'progress': 100,
                'result_count': len(data) if isinstance(data, list) else 1,
                'file_path': file_path,
                'completed_at': datetime.utcnow()
            })
            
            logger.info(f"Completed report generation: {generation.report_name}")
            
        except Exception as e:
            logger.error(f"Error generating report {generation_id}: {e}")
            self.repository.update(generation, {
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.utcnow()
            })
    
    async def _generate_online_users_report(self, generation: ReportGeneration) -> List[Dict[str, Any]]:
        """Generate online users report"""
        params = generation.parameters or {}
        return self.reports_repository.get_online_users(
            nas_ip=params.get('nas_ip'),
            username=params.get('username'),
            session_timeout_min=params.get('session_timeout_min')
        )
    
    async def _generate_history_report(self, generation: ReportGeneration) -> List[Dict[str, Any]]:
        """Generate history report"""
        params = generation.parameters or {}
        return self.reports_repository.get_history_report(
            username=params.get('username'),
            nas_ip=params.get('nas_ip'),
            start_date=generation.date_range_start,
            end_date=generation.date_range_end,
            session_time_min=params.get('session_time_min')
        )
    
    async def _generate_new_users_report(self, generation: ReportGeneration) -> List[Dict[str, Any]]:
        """Generate new users report"""
        params = generation.parameters or {}
        return self.reports_repository.get_new_users_report(
            start_date=generation.date_range_start,
            end_date=generation.date_range_end,
            group_name=params.get('group_name')
        )
    
    async def _generate_top_users_report(self, generation: ReportGeneration) -> List[Dict[str, Any]]:
        """Generate top users report"""
        params = generation.parameters or {}
        return self.reports_repository.get_top_users_report(
            start_date=generation.date_range_start,
            end_date=generation.date_range_end,
            limit=params.get('limit', 10),
            order_by=params.get('order_by', 'total_traffic')
        )
    
    async def _generate_system_logs_report(self, generation: ReportGeneration) -> List[Dict[str, Any]]:
        """Generate system logs report"""
        params = generation.parameters or {}
        return self.reports_repository.get_system_logs_report(
            log_level=params.get('log_level'),
            logger_name=params.get('logger_name'),
            username=params.get('username'),
            start_date=generation.date_range_start,
            end_date=generation.date_range_end,
            search_text=params.get('search_text')
        )


class ReportsService:
    """Main service for report generation and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportsRepository(db)
    
    async def get_online_users_report(self, query: OnlineUsersReportQuery) -> List[Dict[str, Any]]:
        """Generate online users report"""
        return self.repository.get_online_users(
            nas_ip=query.nas_ip,
            username=query.username,
            session_timeout_min=query.session_timeout_min
        )
    
    async def get_history_report(self, query: HistoryReportQuery) -> List[Dict[str, Any]]:
        """Generate history report"""
        return self.repository.get_history_report(
            username=query.username,
            nas_ip=query.nas_ip,
            start_date=query.start_date,
            end_date=query.end_date,
            session_time_min=query.session_time_min
        )
    
    async def get_last_connect_report(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Generate last connect report"""
        return self.repository.get_last_connect_report(limit=limit)
    
    async def get_new_users_report(self, query: NewUsersReportQuery) -> List[Dict[str, Any]]:
        """Generate new users report"""
        return self.repository.get_new_users_report(
            start_date=query.start_date,
            end_date=query.end_date,
            group_name=query.group_name
        )
    
    async def get_top_users_report(self, query: TopUsersReportQuery) -> List[Dict[str, Any]]:
        """Generate top users report"""
        return self.repository.get_top_users_report(
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit,
            order_by=query.order_by
        )
    
    async def get_system_logs_report(self, query: SystemLogQuery) -> List[Dict[str, Any]]:
        """Generate system logs report"""
        return self.repository.get_system_logs_report(
            log_level=query.log_level,
            logger_name=query.logger_name,
            username=query.username,
            start_date=query.start_date,
            end_date=query.end_date,
            search_text=query.search_text
        )
    
    async def get_batch_report(self, query: BatchReportQuery) -> List[Dict[str, Any]]:
        """Generate batch operations report"""
        return self.repository.get_batch_report(
            batch_name=query.batch_name,
            start_date=query.start_date,
            end_date=query.end_date
        )
    
    async def get_system_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive system status report"""
        return self.repository.get_system_status_report()
    
    async def get_reports_dashboard(self) -> Dict[str, Any]:
        """Get reports dashboard summary"""
        try:
            # Get various statistics
            online_users = len(await self.get_online_users_report(OnlineUsersReportQuery()))
            
            # Get recent activity
            recent_history = await self.get_history_report(HistoryReportQuery(
                start_date=datetime.utcnow() - timedelta(days=1)
            ))
            
            # Get system status
            system_status = await self.get_system_status_report()
            
            return {
                'online_users_count': online_users,
                'daily_sessions': len(recent_history),
                'system_health': {
                    'servers_monitored': len(system_status.get('server_status', [])),
                    'services_monitored': len(system_status.get('service_status', [])),
                    'ups_devices': len(system_status.get('ups_status', [])),
                    'raid_arrays': len(system_status.get('raid_status', []))
                },
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating reports dashboard: {e}")
            return {
                'online_users_count': 0,
                'daily_sessions': 0,
                'system_health': {},
                'error': str(e),
                'generated_at': datetime.utcnow()
            }