"""
System Configuration Service Layer

This module contains business logic for system configuration operations
including configuration management, mail settings, backup operations,
cron job management, and system messaging.
"""

import json
import asyncio
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .base import BaseService
from ..repositories.config import (
    SystemConfigRepository, MailSettingsRepository, BackupHistoryRepository,
    CronJobRepository, MessageRepository, SystemLogRepository
)
from ..models.system import (
    SystemConfig, MailSettings, BackupHistory, CronJob
)
from ..models.access_control import Message, MessageType
from ..schemas.config import (
    SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse,
    MailSettingsCreate, MailSettingsUpdate, MailSettingsResponse,
    MailTestRequest, MailTestResponse,
    BackupHistoryCreate, BackupHistoryUpdate, BackupHistoryResponse,
    CronJobCreate, CronJobUpdate, CronJobResponse,
    MessageCreate, MessageUpdate, MessageResponse,
    BulkConfigUpdateRequest, BulkConfigUpdateResponse,
    ConfigBackupRequest, ConfigBackupResponse,
    ConfigRestoreRequest, ConfigRestoreResponse,
    ConfigStatisticsResponse, BackupStatisticsResponse,
    SystemInfoResponse
)
from ..core.exceptions import (
    NotFoundError as NotFoundException, 
    ValidationError as ValidationException, 
    BusinessLogicError as ConflictException, 
    DaloRadiusException as ServiceException
)
from ..core.security import get_password_hash


# Placeholder encryption functions - these should be implemented properly
def encrypt_value(value: str) -> str:
    """Encrypt sensitive configuration values"""
    # This is a placeholder - implement proper encryption
    return value

def decrypt_value(value: str) -> str:
    """Decrypt sensitive configuration values"""
    # This is a placeholder - implement proper decryption
    return value


class SystemConfigService(BaseService):
    """Service for system configuration management"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.config_repo = SystemConfigRepository(db_session)

    async def get_all_configs(
        self, 
        category: Optional[str] = None,
        include_system: bool = True,
        include_encrypted: bool = False
    ) -> List[SystemConfigResponse]:
        """Get all system configurations with optional filtering"""
        if category:
            configs = await self.config_repo.get_by_category(category)
        else:
            configs = await self.config_repo.get_all()
        
        # Apply filters
        filtered_configs = []
        for config in configs:
            if not include_system and config.is_system:
                continue
            if not include_encrypted and config.is_encrypted:
                continue
            filtered_configs.append(config)
        
        return [SystemConfigResponse.from_orm(config) for config in filtered_configs]

    async def get_config_by_key(self, config_key: str) -> SystemConfigResponse:
        """Get configuration by key"""
        config = await self.config_repo.get_by_key(config_key)
        if not config:
            raise NotFoundException(f"Configuration with key '{config_key}' not found")
        
        return SystemConfigResponse.from_orm(config)

    async def get_configs_by_category(self, category: str) -> List[SystemConfigResponse]:
        """Get configurations by category"""
        configs = await self.config_repo.get_by_category(category)
        return [SystemConfigResponse.from_orm(config) for config in configs]

    async def create_config(self, config_data: SystemConfigCreate) -> SystemConfigResponse:
        """Create new configuration"""
        # Check if config key already exists
        existing = await self.config_repo.get_by_key(config_data.config_key)
        if existing:
            raise ConflictException(f"Configuration with key '{config_data.config_key}' already exists")
        
        # Encrypt value if needed
        if config_data.is_encrypted and config_data.config_value:
            config_data.config_value = encrypt_value(config_data.config_value)
        
        config = await self.config_repo.create(config_data)
        return SystemConfigResponse.from_orm(config)

    async def update_config(
        self, 
        config_key: str, 
        config_data: SystemConfigUpdate
    ) -> SystemConfigResponse:
        """Update configuration"""
        config = await self.config_repo.get_by_key(config_key)
        if not config:
            raise NotFoundException(f"Configuration with key '{config_key}' not found")
        
        # Encrypt value if needed
        if config.is_encrypted and config_data.config_value:
            config_data.config_value = encrypt_value(config_data.config_value)
        
        updated_config = await self.config_repo.update(config.id, config_data)
        return SystemConfigResponse.from_orm(updated_config)

    async def delete_config(self, config_key: str) -> bool:
        """Delete configuration"""
        config = await self.config_repo.get_by_key(config_key)
        if not config:
            raise NotFoundException(f"Configuration with key '{config_key}' not found")
        
        if config.is_system:
            raise ValidationException("System configurations cannot be deleted")
        
        return await self.config_repo.delete(config.id)

    async def bulk_update_configs(
        self, 
        request: BulkConfigUpdateRequest
    ) -> BulkConfigUpdateResponse:
        """Bulk update multiple configurations"""
        updated_configs = []
        failed_updates = []
        
        for config_key, config_value in request.updates.items():
            try:
                config = await self.config_repo.get_by_key(config_key)
                if config:
                    # Encrypt if needed
                    if config.is_encrypted:
                        config_value = encrypt_value(config_value)
                    
                    config.config_value = config_value
                    config.updated_by = request.updated_by
                    config.updated_at = datetime.utcnow()
                    updated_configs.append(config)
                else:
                    failed_updates.append({
                        "key": config_key,
                        "error": "Configuration not found"
                    })
            except Exception as e:
                failed_updates.append({
                    "key": config_key,
                    "error": str(e)
                })
        
        # Commit all successful updates
        if updated_configs:
            await self.db.commit()
            for config in updated_configs:
                await self.db.refresh(config)
        
        return BulkConfigUpdateResponse(
            updated_configs=[SystemConfigResponse.from_orm(c) for c in updated_configs],
            failed_updates=failed_updates,
            success_count=len(updated_configs),
            error_count=len(failed_updates)
        )

    async def get_config_value(self, config_key: str, decrypt: bool = True) -> Optional[str]:
        """Get configuration value with optional decryption"""
        config = await self.config_repo.get_by_key(config_key)
        if not config or not config.config_value:
            return None
        
        if config.is_encrypted and decrypt:
            return decrypt_value(config.config_value)
        
        return config.config_value

    async def set_config_value(
        self, 
        config_key: str, 
        value: str, 
        updated_by: Optional[str] = None
    ) -> SystemConfigResponse:
        """Set configuration value"""
        config = await self.config_repo.get_by_key(config_key)
        if not config:
            raise NotFoundException(f"Configuration with key '{config_key}' not found")
        
        if config.is_encrypted:
            value = encrypt_value(value)
        
        config.config_value = value
        config.updated_by = updated_by
        config.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(config)
        
        return SystemConfigResponse.from_orm(config)

    async def get_statistics(self) -> ConfigStatisticsResponse:
        """Get configuration statistics"""
        all_configs = await self.config_repo.get_all()
        
        system_configs = [c for c in all_configs if c.is_system]
        user_configs = [c for c in all_configs if not c.is_system]
        encrypted_configs = [c for c in all_configs if c.is_encrypted]
        
        # Count by category
        categories = {}
        for config in all_configs:
            if config.category not in categories:
                categories[config.category] = 0
            categories[config.category] += 1
        
        category_list = [
            {"name": name, "count": count} 
            for name, count in categories.items()
        ]
        
        # Recent updates (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_updates = len([
            c for c in all_configs 
            if c.updated_at >= recent_date
        ])
        
        return ConfigStatisticsResponse(
            total_configs=len(all_configs),
            system_configs=len(system_configs),
            user_configs=len(user_configs),
            encrypted_configs=len(encrypted_configs),
            categories=category_list,
            recent_updates=recent_updates
        )


class MailService(BaseService):
    """Service for mail configuration and operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.mail_repo = MailSettingsRepository(db_session)

    async def get_all_settings(self) -> List[MailSettingsResponse]:
        """Get all mail settings"""
        settings_list = await self.mail_repo.get_all()
        return [MailSettingsResponse.from_orm(settings) for settings in settings_list]

    async def get_default_settings(self) -> Optional[MailSettingsResponse]:
        """Get default mail settings"""
        settings = await self.mail_repo.get_default_settings()
        return MailSettingsResponse.from_orm(settings) if settings else None

    async def create_settings(self, settings_data: MailSettingsCreate) -> MailSettingsResponse:
        """Create new mail settings"""
        # Encrypt password
        settings_data.smtp_password = encrypt_value(settings_data.smtp_password)
        
        settings = await self.mail_repo.create(settings_data)
        return MailSettingsResponse.from_orm(settings)

    async def update_settings(
        self, 
        settings_id: int, 
        settings_data: MailSettingsUpdate
    ) -> MailSettingsResponse:
        """Update mail settings"""
        settings = await self.mail_repo.get(settings_id)
        if not settings:
            raise NotFoundException(f"Mail settings with ID {settings_id} not found")
        
        # Encrypt password if provided
        if settings_data.smtp_password:
            settings_data.smtp_password = encrypt_value(settings_data.smtp_password)
        
        updated_settings = await self.mail_repo.update(settings_id, settings_data)
        return MailSettingsResponse.from_orm(updated_settings)

    async def delete_settings(self, settings_id: int) -> bool:
        """Delete mail settings"""
        settings = await self.mail_repo.get(settings_id)
        if not settings:
            raise NotFoundException(f"Mail settings with ID {settings_id} not found")
        
        if settings.is_default:
            raise ValidationException("Cannot delete default mail settings")
        
        return await self.mail_repo.delete(settings_id)

    async def set_default_settings(self, settings_id: int) -> MailSettingsResponse:
        """Set mail settings as default"""
        settings = await self.mail_repo.set_default(settings_id)
        return MailSettingsResponse.from_orm(settings)

    async def test_mail_settings(
        self, 
        test_request: MailTestRequest
    ) -> MailTestResponse:
        """Test mail settings by sending a test email"""
        # Get mail settings
        if test_request.mail_settings_id:
            settings = await self.mail_repo.get(test_request.mail_settings_id)
        else:
            settings = await self.mail_repo.get_default_settings()
        
        if not settings:
            raise NotFoundException("No mail settings found")
        
        try:
            # TODO: Implement actual SMTP test
            # This is a placeholder for the actual email sending logic
            success = await self._send_test_email(settings, test_request)
            
            return MailTestResponse(
                success=success,
                message="Test email sent successfully" if success else "Test email failed",
                tested_at=datetime.utcnow(),
                details={"recipient": test_request.recipient}
            )
            
        except Exception as e:
            return MailTestResponse(
                success=False,
                message=f"Mail test failed: {str(e)}",
                tested_at=datetime.utcnow(),
                details={"error": str(e)}
            )

    async def _send_test_email(
        self, 
        settings: MailSettings, 
        test_request: MailTestRequest
    ) -> bool:
        """Send test email (placeholder implementation)"""
        # This would contain actual SMTP logic
        # For now, just simulate success
        await asyncio.sleep(0.1)  # Simulate network delay
        return True


class BackupService(BaseService):
    """Service for backup management operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.backup_repo = BackupHistoryRepository(db_session)

    async def get_all_backups(self) -> List[BackupHistoryResponse]:
        """Get all backup records"""
        backups = await self.backup_repo.get_all()
        return [BackupHistoryResponse.from_orm(backup) for backup in backups]

    async def get_recent_backups(self, days: int = 30) -> List[BackupHistoryResponse]:
        """Get recent backup records"""
        backups = await self.backup_repo.get_recent_backups(days)
        return [BackupHistoryResponse.from_orm(backup) for backup in backups]

    async def create_backup(self, backup_data: BackupHistoryCreate) -> BackupHistoryResponse:
        """Create new backup record"""
        backup = await self.backup_repo.create(backup_data)
        return BackupHistoryResponse.from_orm(backup)

    async def update_backup_status(
        self, 
        backup_id: int, 
        backup_data: BackupHistoryUpdate
    ) -> BackupHistoryResponse:
        """Update backup status"""
        backup = await self.backup_repo.get(backup_id)
        if not backup:
            raise NotFoundException(f"Backup with ID {backup_id} not found")
        
        updated_backup = await self.backup_repo.update(backup_id, backup_data)
        return BackupHistoryResponse.from_orm(updated_backup)

    async def delete_backup(self, backup_id: int) -> bool:
        """Delete backup record"""
        backup = await self.backup_repo.get(backup_id)
        if not backup:
            raise NotFoundException(f"Backup with ID {backup_id} not found")
        
        return await self.backup_repo.delete(backup_id)

    async def cleanup_old_backups(self, keep_days: int = 90) -> Dict[str, int]:
        """Clean up old backup records"""
        deleted_count = await self.backup_repo.cleanup_old_backups(keep_days)
        return {"deleted_count": deleted_count}

    async def get_backup_statistics(self) -> BackupStatisticsResponse:
        """Get backup statistics"""
        stats = await self.backup_repo.get_backup_statistics()
        
        # Get latest backup
        recent_backups = await self.backup_repo.get_recent_backups(days=1)
        latest_backup = recent_backups[0] if recent_backups else None
        
        return BackupStatisticsResponse(
            total_backups=stats["total_backups"],
            successful_backups=stats["successful_backups"],
            recent_backups=stats["recent_backups"],
            success_rate=stats["success_rate"],
            latest_backup=BackupHistoryResponse.from_orm(latest_backup) if latest_backup else None
        )


class CronJobService(BaseService):
    """Service for cron job management"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.cron_repo = CronJobRepository(db_session)

    async def get_all_jobs(self) -> List[CronJobResponse]:
        """Get all cron jobs"""
        jobs = await self.cron_repo.get_all()
        return [CronJobResponse.from_orm(job) for job in jobs]

    async def get_active_jobs(self) -> List[CronJobResponse]:
        """Get active cron jobs"""
        jobs = await self.cron_repo.get_active_jobs()
        return [CronJobResponse.from_orm(job) for job in jobs]

    async def get_job_by_name(self, name: str) -> CronJobResponse:
        """Get cron job by name"""
        job = await self.cron_repo.get_by_name(name)
        if not job:
            raise NotFoundException(f"Cron job with name '{name}' not found")
        
        return CronJobResponse.from_orm(job)

    async def create_job(self, job_data: CronJobCreate) -> CronJobResponse:
        """Create new cron job"""
        # Check if job name already exists
        existing = await self.cron_repo.get_by_name(job_data.name)
        if existing:
            raise ConflictException(f"Cron job with name '{job_data.name}' already exists")
        
        job = await self.cron_repo.create(job_data)
        return CronJobResponse.from_orm(job)

    async def update_job(self, job_id: int, job_data: CronJobUpdate) -> CronJobResponse:
        """Update cron job"""
        job = await self.cron_repo.get(job_id)
        if not job:
            raise NotFoundException(f"Cron job with ID {job_id} not found")
        
        updated_job = await self.cron_repo.update(job_id, job_data)
        return CronJobResponse.from_orm(updated_job)

    async def delete_job(self, job_id: int) -> bool:
        """Delete cron job"""
        job = await self.cron_repo.get(job_id)
        if not job:
            raise NotFoundException(f"Cron job with ID {job_id} not found")
        
        return await self.cron_repo.delete(job_id)

    async def toggle_job(self, job_id: int) -> CronJobResponse:
        """Toggle cron job enabled/disabled status"""
        job = await self.cron_repo.get(job_id)
        if not job:
            raise NotFoundException(f"Cron job with ID {job_id} not found")
        
        job.is_enabled = not job.is_enabled
        await self.db.commit()
        await self.db.refresh(job)
        
        return CronJobResponse.from_orm(job)

    async def update_job_status(
        self, 
        job_id: int, 
        status: str, 
        output: Optional[str] = None
    ) -> CronJobResponse:
        """Update job execution status"""
        job = await self.cron_repo.update_job_status(job_id, status, output)
        if not job:
            raise NotFoundException(f"Cron job with ID {job_id} not found")
        
        return CronJobResponse.from_orm(job)


class MessageService(BaseService):
    """Service for system message management"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.message_repo = MessageRepository(db_session)

    async def get_all_messages(self) -> List[MessageResponse]:
        """Get all system messages"""
        messages = await self.message_repo.get_all()
        return [MessageResponse.from_orm(message) for message in messages]

    async def get_messages_by_type(self, message_type: MessageType) -> List[MessageResponse]:
        """Get messages by type"""
        messages = await self.message_repo.get_by_type(message_type)
        return [MessageResponse.from_orm(message) for message in messages]

    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create new system message"""
        message = await self.message_repo.create(message_data)
        return MessageResponse.from_orm(message)

    async def update_message(
        self, 
        message_id: int, 
        message_data: MessageUpdate
    ) -> MessageResponse:
        """Update system message"""
        message = await self.message_repo.get(message_id)
        if not message:
            raise NotFoundException(f"Message with ID {message_id} not found")
        
        updated_message = await self.message_repo.update(message_id, message_data)
        return MessageResponse.from_orm(updated_message)

    async def delete_message(self, message_id: int) -> bool:
        """Delete system message"""
        message = await self.message_repo.get(message_id)
        if not message:
            raise NotFoundException(f"Message with ID {message_id} not found")
        
        return await self.message_repo.delete(message_id)

    async def get_recent_messages(self, days: int = 7) -> List[MessageResponse]:
        """Get recent messages"""
        messages = await self.message_repo.get_recent_messages(days)
        return [MessageResponse.from_orm(message) for message in messages]


class SystemInfoService(BaseService):
    """Service for system information and health checks"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.config_repo = SystemConfigRepository(db_session)
        self.mail_repo = MailSettingsRepository(db_session)
        self.backup_repo = BackupHistoryRepository(db_session)
        self.cron_repo = CronJobRepository(db_session)

    async def get_system_info(self) -> SystemInfoResponse:
        """Get comprehensive system information"""
        # Get basic system info
        version = await self._get_system_version()
        uptime = await self._get_system_uptime()
        
        # Check component statuses
        database_status = await self._check_database_status()
        mail_status = await self._check_mail_status()
        backup_status = await self._check_backup_status()
        
        # Get active cron jobs count
        active_jobs = await self.cron_repo.get_active_jobs()
        
        return SystemInfoResponse(
            version=version,
            uptime=uptime,
            database_status=database_status,
            mail_status=mail_status,
            backup_status=backup_status,
            active_cron_jobs=len(active_jobs)
        )

    async def _get_system_version(self) -> str:
        """Get system version"""
        # This could read from a version file or configuration
        return "2.0.0"

    async def _get_system_uptime(self) -> str:
        """Get system uptime"""
        # This would calculate actual uptime
        return "24h 30m"

    async def _check_database_status(self) -> str:
        """Check database connectivity status"""
        try:
            # Simple query to test database
            await self.config_repo.get_multi(limit=1)
            return "healthy"
        except Exception:
            return "error"

    async def _check_mail_status(self) -> str:
        """Check mail configuration status"""
        try:
            default_settings = await self.mail_repo.get_default_settings()
            return "configured" if default_settings else "not_configured"
        except Exception:
            return "error"

    async def _check_backup_status(self) -> str:
        """Check backup status"""
        try:
            recent_backups = await self.backup_repo.get_recent_backups(days=7)
            successful_backups = [b for b in recent_backups if b.status == "completed"]
            
            if not recent_backups:
                return "no_recent_backups"
            elif len(successful_backups) == len(recent_backups):
                return "healthy"
            else:
                return "partial_failures"
        except Exception:
            return "error"