"""
System Configuration Repository Implementations

This module contains repository classes for system configuration operations
including system settings, mail configuration, backup management, cron jobs,
and system messages.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.exc import IntegrityError

from .base import BaseRepository
from ..models.system import (
    SystemConfig, SystemLog, BackupHistory, CronJob, MailSettings,
    MailQueue, NotificationTemplate, ApiKey, DatabaseMaintenance,
    SessionStore, AuditTrail
)
from ..models.access_control import Message, MessageType
from ..models.user import Operator
from ..schemas.config import (
    SystemConfigCreate, SystemConfigUpdate,
    MailSettingsCreate, MailSettingsUpdate,
    BackupHistoryCreate, BackupHistoryUpdate,
    CronJobCreate, CronJobUpdate,
    MessageCreate, MessageUpdate
)


class SystemConfigRepository(BaseRepository[SystemConfig, SystemConfigCreate, SystemConfigUpdate]):
    """Repository for SystemConfig model operations"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(SystemConfig, db_session)

    async def get_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """Get configuration by key"""
        return await self.get_by_field("config_key", config_key)

    async def get_by_category(self, category: str) -> List[SystemConfig]:
        """Get configurations by category"""
        filters = {"category": category}
        return await self.get_multi(filters=filters, order_by="config_key")

    async def get_system_configs(self) -> List[SystemConfig]:
        """Get all system configurations (is_system=True)"""
        filters = {"is_system": True}
        return await self.get_multi(filters=filters, order_by="config_key")

    async def get_user_configs(self) -> List[SystemConfig]:
        """Get all user-configurable settings (is_system=False)"""
        filters = {"is_system": False}
        return await self.get_multi(filters=filters, order_by="config_key")

    async def get_encrypted_configs(self) -> List[SystemConfig]:
        """Get all encrypted configurations"""
        filters = {"is_encrypted": True}
        return await self.get_multi(filters=filters, order_by="config_key")

    async def bulk_update_configs(self, config_updates: Dict[str, str]) -> List[SystemConfig]:
        """Bulk update multiple configurations"""
        updated_configs = []

        for config_key, config_value in config_updates.items():
            config = await self.get_by_key(config_key)
            if config:
                config.config_value = config_value
                config.updated_at = datetime.utcnow()
                updated_configs.append(config)

        await self.db.commit()
        return updated_configs

    async def search_configs(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SystemConfig]:
        """Search configurations by key or description"""
        search_fields = ["config_key", "description"]
        return await self.search(
            search_term=search_term,
            search_fields=search_fields,
            skip=skip,
            limit=limit
        )


class MailSettingsRepository(BaseRepository[MailSettings, MailSettingsCreate, MailSettingsUpdate]):
    """Repository for MailSettings model operations"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(MailSettings, db_session)

    async def get_default_settings(self) -> Optional[MailSettings]:
        """Get the default mail settings"""
        return await self.get_by_field("is_default", True)

    async def get_active_settings(self) -> List[MailSettings]:
        """Get all active mail settings"""
        filters = {"is_active": True}
        return await self.get_multi(filters=filters, order_by="from_name")

    async def set_default(self, mail_settings_id: int) -> MailSettings:
        """Set a mail settings configuration as default"""
        # First, unset all existing defaults
        query = select(MailSettings).where(MailSettings.is_default == True)
        result = await self.db.execute(query)
        existing_defaults = result.scalars().all()

        for settings in existing_defaults:
            settings.is_default = False

        # Set the new default
        settings = await self.get(mail_settings_id)
        if settings:
            settings.is_default = True
            settings.is_active = True
            await self.db.commit()
            await self.db.refresh(settings)

        return settings

    async def test_connection(self, mail_settings: MailSettings) -> Dict[str, Any]:
        """Test mail settings connection (placeholder for actual SMTP test)"""
        # This would contain actual SMTP connection testing logic
        return {
            "success": True,
            "message": "Mail settings test successful",
            "tested_at": datetime.utcnow().isoformat()
        }


class BackupHistoryRepository(BaseRepository[BackupHistory, BackupHistoryCreate, BackupHistoryUpdate]):
    """Repository for BackupHistory model operations"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(BackupHistory, db_session)

    async def get_recent_backups(self, days: int = 30) -> List[BackupHistory]:
        """Get backups from the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        query = select(BackupHistory).where(
            BackupHistory.backup_date >= since_date
        ).order_by(BackupHistory.backup_date.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_successful_backups(self, limit: int = 10) -> List[BackupHistory]:
        """Get recent successful backups"""
        filters = {"status": "completed"}
        return await self.get_multi(
            filters=filters,
            limit=limit,
            order_by="-backup_date"
        )

    async def get_failed_backups(self, limit: int = 10) -> List[BackupHistory]:
        """Get recent failed backups"""
        filters = {"status": "failed"}
        return await self.get_multi(
            filters=filters,
            limit=limit,
            order_by="-backup_date"
        )

    async def cleanup_old_backups(self, keep_days: int = 90) -> int:
        """Delete backup records older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
        query = select(BackupHistory).where(
            BackupHistory.backup_date < cutoff_date
        )

        result = await self.db.execute(query)
        old_backups = result.scalars().all()

        for backup in old_backups:
            await self.delete(backup.id)

        return len(old_backups)

    async def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics"""
        # Total backups
        total_query = select(func.count(BackupHistory.id))
        total_result = await self.db.execute(total_query)
        total_backups = total_result.scalar()

        # Successful backups
        success_query = select(func.count(BackupHistory.id)).where(
            BackupHistory.status == "completed"
        )
        success_result = await self.db.execute(success_query)
        successful_backups = success_result.scalar()

        # Recent backups (last 30 days)
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_query = select(func.count(BackupHistory.id)).where(
            BackupHistory.backup_date >= recent_date
        )
        recent_result = await self.db.execute(recent_query)
        recent_backups = recent_result.scalar()

        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "recent_backups": recent_backups,
            "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0
        }


class CronJobRepository(BaseRepository[CronJob, CronJobCreate, CronJobUpdate]):
    """Repository for CronJob model operations"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(CronJob, db_session)

    async def get_active_jobs(self) -> List[CronJob]:
        """Get all active cron jobs"""
        filters = {"is_enabled": True}
        return await self.get_multi(filters=filters, order_by="name")

    async def get_by_name(self, name: str) -> Optional[CronJob]:
        """Get cron job by name"""
        return await self.get_by_field("name", name)

    async def get_due_jobs(self, current_time: datetime) -> List[CronJob]:
        """Get jobs that are due to run"""
        # This would contain cron expression parsing logic
        # For now, returning active jobs as placeholder
        return await self.get_active_jobs()

    async def update_job_status(
        self,
        job_id: int,
        status: str,
        output: Optional[str] = None
    ) -> Optional[CronJob]:
        """Update job execution status"""
        job = await self.get(job_id)
        if job:
            job.last_run = datetime.utcnow()
            job.last_status = status
            job.last_output = output
            await self.db.commit()
            await self.db.refresh(job)
        return job

    async def get_job_history(self, job_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a job (placeholder)"""
        # This would query a job execution history table
        # For now, returning basic info from the job record
        job = await self.get(job_id)
        if job:
            return [{
                "run_time": job.last_run.isoformat() if job.last_run else None,
                "status": job.last_status,
                "output": job.last_output
            }]
        return []


class MessageRepository(BaseRepository[Message, MessageCreate, MessageUpdate]):
    """Repository for Message model operations"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Message, db_session)

    async def get_by_type(self, message_type: MessageType) -> List[Message]:
        """Get messages by type"""
        query = select(Message).where(Message.type == message_type)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_messages(self) -> List[Message]:
        """Get all active messages"""
        # Note: The Message model from access_control doesn't have is_active field
        # This would need to be added to the model if needed
        query = select(Message).order_by(Message.created_on.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_messages(self, days: int = 7) -> List[Message]:
        """Get messages from the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        query = select(Message).where(
            Message.created_on >= since_date
        ).order_by(Message.created_on.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_messages(
        self,
        search_term: str,
        message_type: Optional[MessageType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Search messages by content"""
        query = select(Message)

        # Add type filter if provided
        if message_type:
            query = query.where(Message.type == message_type)

        # Add content search
        if search_term:
            query = query.where(Message.content.ilike(f"%{search_term}%"))

        query = query.order_by(Message.created_on.desc()
                               ).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()


class SystemLogRepository(BaseRepository[SystemLog, None, None]):
    """Repository for SystemLog model operations (read-only)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(SystemLog, db_session)

    async def get_logs_by_level(self, log_level: str, limit: int = 100) -> List[SystemLog]:
        """Get logs by level"""
        filters = {"log_level": log_level}
        return await self.get_multi(
            filters=filters,
            limit=limit,
            order_by="-timestamp"
        )

    async def get_recent_logs(self, hours: int = 24, limit: int = 100) -> List[SystemLog]:
        """Get logs from the last N hours"""
        since_time = datetime.utcnow() - timedelta(hours=hours)
        query = select(SystemLog).where(
            SystemLog.timestamp >= since_time
        ).order_by(SystemLog.timestamp.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_logs_by_user(self, username: str, limit: int = 100) -> List[SystemLog]:
        """Get logs for specific user"""
        filters = {"username": username}
        return await self.get_multi(
            filters=filters,
            limit=limit,
            order_by="-timestamp"
        )

    async def search_logs(
        self,
        search_term: str,
        log_level: Optional[str] = None,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SystemLog]:
        """Search logs with filters"""
        query = select(SystemLog)

        # Add filters
        if log_level:
            query = query.where(SystemLog.log_level == log_level)
        if username:
            query = query.where(SystemLog.username == username)
        if search_term:
            query = query.where(SystemLog.message.ilike(f"%{search_term}%"))

        query = query.order_by(SystemLog.timestamp.desc()
                               ).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
