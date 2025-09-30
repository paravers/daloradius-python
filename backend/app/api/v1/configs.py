"""
System Configuration API Endpoints

This module provides FastAPI router endpoints for system configuration
management including configurations, mail settings, backup operations,
cron jobs, and system messages.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_db
from ...core.security import get_current_user
from ...models.user import Operator
from ...models.access_control import MessageType
from ...services.config import (
    SystemConfigService, MailService, BackupService, 
    CronJobService, MessageService, SystemInfoService
)
from ...schemas.config import (
    SystemConfigResponse, SystemConfigCreate, SystemConfigUpdate,
    MailSettingsResponse, MailSettingsCreate, MailSettingsUpdate,
    MailTestRequest, MailTestResponse,
    BackupHistoryResponse, BackupHistoryCreate, BackupHistoryUpdate,
    CronJobResponse, CronJobCreate, CronJobUpdate,
    MessageResponse, MessageCreate, MessageUpdate,
    BulkConfigUpdateRequest, BulkConfigUpdateResponse,
    ConfigBackupRequest, ConfigBackupResponse,
    ConfigRestoreRequest, ConfigRestoreResponse,
    ConfigSearchParams, ConfigSearchResponse,
    ConfigStatisticsResponse, BackupStatisticsResponse,
    SystemInfoResponse, ConfigErrorResponse
)
from ...core.exceptions import (
    NotFoundError as NotFoundException, 
    ValidationError as ValidationException,
    BusinessLogicError as ConflictException, 
    DaloRadiusException as ServiceException
)

router = APIRouter()


# System Configuration Endpoints
@router.get("/configs", response_model=List[SystemConfigResponse])
async def get_all_configs(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_system: bool = Query(True, description="Include system configurations"),
    include_encrypted: bool = Query(False, description="Include encrypted configurations"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get all system configurations with optional filtering"""
    service = SystemConfigService(db)
    return await service.get_all_configs(
        category=category,
        include_system=include_system,
        include_encrypted=include_encrypted
    )


@router.get("/configs/search", response_model=ConfigSearchResponse)
async def search_configs(
    search_params: ConfigSearchParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Search configurations with advanced filtering"""
    service = SystemConfigService(db)
    
    if search_params.category:
        configs = await service.get_configs_by_category(search_params.category)
    else:
        configs = await service.get_all_configs(
            include_system=search_params.is_system,
            include_encrypted=search_params.is_encrypted
        )
    
    # Apply search filter if provided
    if search_params.search_term:
        search_term_lower = search_params.search_term.lower()
        configs = [
            config for config in configs
            if (search_term_lower in config.config_key.lower() or
                (config.description and search_term_lower in config.description.lower()))
        ]
    
    # Apply pagination
    total_count = len(configs)
    start_idx = search_params.skip
    end_idx = start_idx + search_params.limit
    paginated_configs = configs[start_idx:end_idx]
    
    return ConfigSearchResponse(
        configs=paginated_configs,
        total_count=total_count,
        page_info={
            "skip": search_params.skip,
            "limit": search_params.limit,
            "has_more": end_idx < total_count
        }
    )


@router.get("/configs/statistics", response_model=ConfigStatisticsResponse)
async def get_config_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get configuration statistics"""
    service = SystemConfigService(db)
    return await service.get_statistics()


@router.get("/configs/category/{category}", response_model=List[SystemConfigResponse])
async def get_configs_by_category(
    category: str = Path(..., description="Configuration category"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get configurations by category"""
    service = SystemConfigService(db)
    return await service.get_configs_by_category(category)


@router.get("/configs/key/{config_key}", response_model=SystemConfigResponse)
async def get_config_by_key(
    config_key: str = Path(..., description="Configuration key"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get configuration by key"""
    service = SystemConfigService(db)
    return await service.get_config_by_key(config_key)


@router.post("/configs", response_model=SystemConfigResponse)
async def create_config(
    config_data: SystemConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create new configuration"""
    config_data.updated_by = current_user.username
    service = SystemConfigService(db)
    return await service.create_config(config_data)


@router.put("/configs/key/{config_key}", response_model=SystemConfigResponse)
async def update_config(
    config_key: str = Path(..., description="Configuration key"),
    config_data: SystemConfigUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update configuration by key"""
    config_data.updated_by = current_user.username
    service = SystemConfigService(db)
    return await service.update_config(config_key, config_data)


@router.delete("/configs/key/{config_key}")
async def delete_config(
    config_key: str = Path(..., description="Configuration key"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Delete configuration by key"""
    service = SystemConfigService(db)
    success = await service.delete_config(config_key)
    return {"success": success, "message": f"Configuration '{config_key}' deleted"}


@router.post("/configs/bulk-update", response_model=BulkConfigUpdateResponse)
async def bulk_update_configs(
    request: BulkConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Bulk update multiple configurations"""
    request.updated_by = current_user.username
    service = SystemConfigService(db)
    return await service.bulk_update_configs(request)


@router.get("/configs/value/{config_key}")
async def get_config_value(
    config_key: str = Path(..., description="Configuration key"),
    decrypt: bool = Query(True, description="Decrypt encrypted values"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get configuration value"""
    service = SystemConfigService(db)
    value = await service.get_config_value(config_key, decrypt=decrypt)
    return {"config_key": config_key, "value": value}


@router.post("/configs/value/{config_key}")
async def set_config_value(
    config_key: str = Path(..., description="Configuration key"),
    value: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Set configuration value"""
    service = SystemConfigService(db)
    config = await service.set_config_value(
        config_key, 
        value, 
        updated_by=current_user.username
    )
    return {"success": True, "config": config}


# Mail Settings Endpoints
@router.get("/mail", response_model=List[MailSettingsResponse])
async def get_all_mail_settings(
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get all mail settings"""
    service = MailService(db)
    return await service.get_all_settings()


@router.get("/mail/default", response_model=Optional[MailSettingsResponse])
async def get_default_mail_settings(
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get default mail settings"""
    service = MailService(db)
    return await service.get_default_settings()


@router.post("/mail", response_model=MailSettingsResponse)
async def create_mail_settings(
    settings_data: MailSettingsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create new mail settings"""
    settings_data.updated_by = current_user.username
    service = MailService(db)
    return await service.create_settings(settings_data)


@router.put("/mail/{settings_id}", response_model=MailSettingsResponse)
async def update_mail_settings(
    settings_id: int = Path(..., description="Mail settings ID"),
    settings_data: MailSettingsUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update mail settings"""
    settings_data.updated_by = current_user.username
    service = MailService(db)
    return await service.update_settings(settings_id, settings_data)


@router.delete("/mail/{settings_id}")
async def delete_mail_settings(
    settings_id: int = Path(..., description="Mail settings ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Delete mail settings"""
    service = MailService(db)
    success = await service.delete_settings(settings_id)
    return {"success": success, "message": f"Mail settings {settings_id} deleted"}


@router.post("/mail/{settings_id}/set-default", response_model=MailSettingsResponse)
async def set_default_mail_settings(
    settings_id: int = Path(..., description="Mail settings ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Set mail settings as default"""
    service = MailService(db)
    return await service.set_default_settings(settings_id)


@router.post("/mail/test", response_model=MailTestResponse)
async def test_mail_settings(
    test_request: MailTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Test mail settings by sending a test email"""
    service = MailService(db)
    return await service.test_mail_settings(test_request)


# Backup Management Endpoints
@router.get("/backups", response_model=List[BackupHistoryResponse])
async def get_all_backups(
    days: int = Query(30, description="Get backups from last N days"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get backup history"""
    service = BackupService(db)
    if days > 0:
        return await service.get_recent_backups(days)
    else:
        return await service.get_all_backups()


@router.get("/backups/statistics", response_model=BackupStatisticsResponse)
async def get_backup_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get backup statistics"""
    service = BackupService(db)
    return await service.get_backup_statistics()


@router.post("/backups", response_model=BackupHistoryResponse)
async def create_backup(
    backup_data: BackupHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create new backup record"""
    backup_data.created_by = current_user.username
    service = BackupService(db)
    return await service.create_backup(backup_data)


@router.put("/backups/{backup_id}", response_model=BackupHistoryResponse)
async def update_backup_status(
    backup_id: int = Path(..., description="Backup ID"),
    backup_data: BackupHistoryUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update backup status"""
    service = BackupService(db)
    return await service.update_backup_status(backup_id, backup_data)


@router.delete("/backups/{backup_id}")
async def delete_backup(
    backup_id: int = Path(..., description="Backup ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Delete backup record"""
    service = BackupService(db)
    success = await service.delete_backup(backup_id)
    return {"success": success, "message": f"Backup {backup_id} deleted"}


@router.post("/backups/cleanup")
async def cleanup_old_backups(
    keep_days: int = Body(90, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Clean up old backup records"""
    service = BackupService(db)
    result = await service.cleanup_old_backups(keep_days)
    return {"success": True, "deleted_count": result["deleted_count"]}


# Cron Job Management Endpoints
@router.get("/cron-jobs", response_model=List[CronJobResponse])
async def get_all_cron_jobs(
    active_only: bool = Query(False, description="Return only active jobs"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get all cron jobs"""
    service = CronJobService(db)
    if active_only:
        return await service.get_active_jobs()
    else:
        return await service.get_all_jobs()


@router.get("/cron-jobs/name/{name}", response_model=CronJobResponse)
async def get_cron_job_by_name(
    name: str = Path(..., description="Job name"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get cron job by name"""
    service = CronJobService(db)
    return await service.get_job_by_name(name)


@router.post("/cron-jobs", response_model=CronJobResponse)
async def create_cron_job(
    job_data: CronJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create new cron job"""
    job_data.created_by = current_user.username
    service = CronJobService(db)
    return await service.create_job(job_data)


@router.put("/cron-jobs/{job_id}", response_model=CronJobResponse)
async def update_cron_job(
    job_id: int = Path(..., description="Job ID"),
    job_data: CronJobUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update cron job"""
    service = CronJobService(db)
    return await service.update_job(job_id, job_data)


@router.delete("/cron-jobs/{job_id}")
async def delete_cron_job(
    job_id: int = Path(..., description="Job ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Delete cron job"""
    service = CronJobService(db)
    success = await service.delete_job(job_id)
    return {"success": success, "message": f"Cron job {job_id} deleted"}


@router.post("/cron-jobs/{job_id}/toggle", response_model=CronJobResponse)
async def toggle_cron_job(
    job_id: int = Path(..., description="Job ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Toggle cron job enabled/disabled status"""
    service = CronJobService(db)
    return await service.toggle_job(job_id)


@router.post("/cron-jobs/{job_id}/status")
async def update_cron_job_status(
    job_id: int = Path(..., description="Job ID"),
    status: str = Body(..., embed=True),
    output: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update cron job execution status"""
    service = CronJobService(db)
    job = await service.update_job_status(job_id, status, output)
    return {"success": True, "job": job}


# System Messages Endpoints
@router.get("/messages", response_model=List[MessageResponse])
async def get_all_messages(
    message_type: Optional[MessageType] = Query(None, description="Filter by message type"),
    recent_days: Optional[int] = Query(None, description="Get messages from last N days"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get system messages"""
    service = MessageService(db)
    
    if recent_days:
        return await service.get_recent_messages(recent_days)
    elif message_type:
        return await service.get_messages_by_type(message_type)
    else:
        return await service.get_all_messages()


@router.get("/messages/type/{message_type}", response_model=List[MessageResponse])
async def get_messages_by_type(
    message_type: MessageType = Path(..., description="Message type"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get messages by type"""
    service = MessageService(db)
    return await service.get_messages_by_type(message_type)


@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create new system message"""
    message_data.created_by = current_user.username
    service = MessageService(db)
    return await service.create_message(message_data)


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int = Path(..., description="Message ID"),
    message_data: MessageUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Update system message"""
    message_data.modified_by = current_user.username
    service = MessageService(db)
    return await service.update_message(message_id, message_data)


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int = Path(..., description="Message ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Delete system message"""
    service = MessageService(db)
    success = await service.delete_message(message_id)
    return {"success": success, "message": f"Message {message_id} deleted"}


# System Information Endpoints
@router.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info(
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Get comprehensive system information"""
    service = SystemInfoService(db)
    return await service.get_system_info()


# Configuration backup/restore endpoints
@router.post("/configs/backup", response_model=ConfigBackupResponse)
async def create_config_backup(
    request: ConfigBackupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Create configuration backup"""
    # This would implement actual backup logic
    # For now, returning a placeholder response
    return ConfigBackupResponse(
        backup_id=1,
        name=request.name,
        description=request.description,
        config_count=100,
        created_at=datetime.utcnow(),
        created_by=current_user.username
    )


@router.post("/configs/restore", response_model=ConfigRestoreResponse)
async def restore_config_backup(
    request: ConfigRestoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Operator = Depends(get_current_user)
):
    """Restore configuration from backup"""
    # This would implement actual restore logic
    # For now, returning a placeholder response
    return ConfigRestoreResponse(
        restored_configs=[],
        skipped_configs=[],
        success_count=0,
        skip_count=0
    )


# Error handlers
@router.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=ConfigErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


@router.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content=ConfigErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


@router.exception_handler(ConflictException)
async def conflict_exception_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content=ConfigErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


@router.exception_handler(ServiceException)
async def service_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ConfigErrorResponse(
            error=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )