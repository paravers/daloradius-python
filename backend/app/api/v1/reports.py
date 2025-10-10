"""
Reports API Routes

This module contains the API endpoints for the reporting system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.exceptions import ValidationError, NotFoundError
from app.services.reports import (
    UpsStatusService, RaidStatusService, HeartBeatService,
    ReportTemplateService, ReportGenerationService, ReportsService
)
from app.schemas.reports import (
    UpsStatusCreate, UpsStatusUpdate, UpsStatusResponse, UpsStatusListResponse,
    RaidStatusCreate, RaidStatusUpdate, RaidStatusResponse, RaidStatusListResponse,
    HeartBeatCreate, HeartBeatUpdate, HeartBeatResponse, HeartBeatListResponse,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse, ReportTemplateListResponse,
    ReportGenerationCreate, ReportGenerationResponse, ReportGenerationListResponse,
    OnlineUsersReportQuery, HistoryReportQuery, NewUsersReportQuery,
    TopUsersReportQuery, SystemLogQuery, BatchReportQuery,
    SystemStatusReport, ReportType
)

router = APIRouter()


# =============================================================================
# UPS Status Endpoints
# =============================================================================

@router.post("/ups-status", response_model=UpsStatusResponse)
async def create_ups_status(
    ups_data: UpsStatusCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new UPS status record"""
    try:
        service = UpsStatusService(db)
        return await service.create_ups_status(ups_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ups-status/{ups_id}", response_model=UpsStatusResponse)
async def get_ups_status(
    ups_id: int = Path(..., description="UPS status ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get UPS status by ID"""
    try:
        service = UpsStatusService(db)
        return await service.get_ups_status(ups_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/ups-status/{ups_id}", response_model=UpsStatusResponse)
async def update_ups_status(
    ups_id: int = Path(..., description="UPS status ID"),
    update_data: UpsStatusUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update UPS status"""
    try:
        service = UpsStatusService(db)
        return await service.update_ups_status(ups_id, update_data)
    except (ValidationError, NotFoundError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/ups-status/{ups_id}")
async def delete_ups_status(
    ups_id: int = Path(..., description="UPS status ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete UPS status"""
    try:
        service = UpsStatusService(db)
        await service.delete_ups_status(ups_id)
        return {"message": "UPS status deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/ups-status", response_model=List[UpsStatusResponse])
async def list_ups_status(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all UPS status records"""
    service = UpsStatusService(db)
    return await service.get_all_ups_status(skip=skip, limit=limit)


@router.get("/ups-status/summary")
async def get_ups_summary(db: AsyncSession = Depends(get_db)):
    """Get UPS status summary"""
    service = UpsStatusService(db)
    return await service.get_ups_summary()


# =============================================================================
# RAID Status Endpoints
# =============================================================================

@router.post("/raid-status", response_model=RaidStatusResponse)
async def create_raid_status(
    raid_data: RaidStatusCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new RAID status record"""
    try:
        service = RaidStatusService(db)
        return await service.create_raid_status(raid_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/raid-status/{raid_id}", response_model=RaidStatusResponse)
async def get_raid_status(
    raid_id: int = Path(..., description="RAID status ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get RAID status by ID"""
    try:
        service = RaidStatusService(db)
        return await service.get_raid_status(raid_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/raid-status/{raid_id}", response_model=RaidStatusResponse)
async def update_raid_status(
    raid_id: int = Path(..., description="RAID status ID"),
    update_data: RaidStatusUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update RAID status"""
    try:
        service = RaidStatusService(db)
        return await service.update_raid_status(raid_id, update_data)
    except (ValidationError, NotFoundError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/raid-status/{raid_id}")
async def delete_raid_status(
    raid_id: int = Path(..., description="RAID status ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete RAID status"""
    try:
        service = RaidStatusService(db)
        await service.delete_raid_status(raid_id)
        return {"message": "RAID status deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/raid-status", response_model=List[RaidStatusResponse])
async def list_raid_status(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all RAID status records"""
    service = RaidStatusService(db)
    return await service.get_all_raid_status(skip=skip, limit=limit)


@router.get("/raid-status/summary")
async def get_raid_summary(db: AsyncSession = Depends(get_db)):
    """Get RAID status summary"""
    service = RaidStatusService(db)
    return await service.get_raid_summary()


# =============================================================================
# HeartBeat Endpoints
# =============================================================================

@router.post("/heartbeat", response_model=HeartBeatResponse)
async def create_heartbeat(
    heartbeat_data: HeartBeatCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new heartbeat record"""
    try:
        service = HeartBeatService(db)
        return await service.create_heartbeat(heartbeat_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/heartbeat/{heartbeat_id}", response_model=HeartBeatResponse)
async def get_heartbeat(
    heartbeat_id: int = Path(..., description="Heartbeat ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get heartbeat by ID"""
    try:
        service = HeartBeatService(db)
        return await service.get_heartbeat(heartbeat_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/heartbeat/{heartbeat_id}", response_model=HeartBeatResponse)
async def update_heartbeat(
    heartbeat_id: int = Path(..., description="Heartbeat ID"),
    update_data: HeartBeatUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update heartbeat"""
    try:
        service = HeartBeatService(db)
        return await service.update_heartbeat(heartbeat_id, update_data)
    except (ValidationError, NotFoundError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/heartbeat/{heartbeat_id}")
async def delete_heartbeat(
    heartbeat_id: int = Path(..., description="Heartbeat ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete heartbeat"""
    try:
        service = HeartBeatService(db)
        await service.delete_heartbeat(heartbeat_id)
        return {"message": "Heartbeat deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/heartbeat", response_model=List[HeartBeatResponse])
async def list_heartbeats(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all heartbeat records"""
    service = HeartBeatService(db)
    return await service.get_all_heartbeats(skip=skip, limit=limit)


@router.get("/heartbeat/summary")
async def get_heartbeat_summary(db: AsyncSession = Depends(get_db)):
    """Get heartbeat status summary"""
    service = HeartBeatService(db)
    return await service.get_heartbeat_summary()


# =============================================================================
# Report Template Endpoints
# =============================================================================

@router.post("/templates", response_model=ReportTemplateResponse)
async def create_report_template(
    template_data: ReportTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new report template"""
    try:
        service = ReportTemplateService(db)
        return await service.create_template(template_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: int = Path(..., description="Template ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get report template by ID"""
    try:
        service = ReportTemplateService(db)
        return await service.get_template(template_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(
    template_id: int = Path(..., description="Template ID"),
    update_data: ReportTemplateUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update report template"""
    try:
        service = ReportTemplateService(db)
        return await service.update_template(template_id, update_data)
    except (ValidationError, NotFoundError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 400
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_report_template(
    template_id: int = Path(..., description="Template ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete report template"""
    try:
        service = ReportTemplateService(db)
        await service.delete_template(template_id)
        return {"message": "Report template deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/templates", response_model=List[ReportTemplateResponse])
async def list_report_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    report_type: Optional[ReportType] = Query(
        None, description="Filter by report type"),
    db: AsyncSession = Depends(get_db)
):
    """List report templates"""
    service = ReportTemplateService(db)
    if report_type:
        return await service.get_templates_by_type(report_type)
    return await service.get_all_templates(skip=skip, limit=limit)


# =============================================================================
# Report Generation Endpoints
# =============================================================================

@router.post("/generate", response_model=ReportGenerationResponse)
async def create_report_generation(
    generation_data: ReportGenerationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new report generation request"""
    try:
        service = ReportGenerationService(db)
        return await service.create_report_generation(generation_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/generate/{generation_id}", response_model=ReportGenerationResponse)
async def get_report_generation(
    generation_id: int = Path(..., description="Generation ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get report generation by ID"""
    try:
        service = ReportGenerationService(db)
        return await service.get_report_generation(generation_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/generate/user/{username}", response_model=List[ReportGenerationResponse])
async def get_user_report_generations(
    username: str = Path(..., description="Username"),
    db: AsyncSession = Depends(get_db)
):
    """Get user's report generations"""
    service = ReportGenerationService(db)
    return await service.get_user_reports(username)


@router.get("/generate/pending", response_model=List[ReportGenerationResponse])
async def get_pending_reports(db: AsyncSession = Depends(get_db)):
    """Get pending report generations"""
    service = ReportGenerationService(db)
    return await service.get_pending_reports()


# =============================================================================
# Report Data Endpoints
# =============================================================================

@router.get("/data/online-users")
async def get_online_users_report(
    nas_ip: Optional[str] = Query(None, description="Filter by NAS IP"),
    username: Optional[str] = Query(None, description="Filter by username"),
    session_timeout_min: Optional[int] = Query(
        None, ge=1, description="Session timeout in minutes"),
    db: AsyncSession = Depends(get_db)
):
    """Get online users report"""
    service = ReportsService(db)
    query = OnlineUsersReportQuery(
        nas_ip=nas_ip,
        username=username,
        session_timeout_min=session_timeout_min
    )
    return await service.get_online_users_report(query)


@router.get("/data/history")
async def get_history_report(
    username: Optional[str] = Query(None, description="Filter by username"),
    nas_ip: Optional[str] = Query(None, description="Filter by NAS IP"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    session_time_min: Optional[int] = Query(
        None, ge=0, description="Minimum session time in minutes"),
    db: AsyncSession = Depends(get_db)
):
    """Get history report"""
    service = ReportsService(db)
    query = HistoryReportQuery(
        username=username,
        nas_ip=nas_ip,
        start_date=start_date,
        end_date=end_date,
        session_time_min=session_time_min
    )
    return await service.get_history_report(query)


@router.get("/data/last-connect")
async def get_last_connect_report(
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get last connect report"""
    service = ReportsService(db)
    return await service.get_last_connect_report(limit=limit)


@router.get("/data/new-users")
async def get_new_users_report(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    group_name: Optional[str] = Query(None, description="Filter by group"),
    db: AsyncSession = Depends(get_db)
):
    """Get new users report"""
    service = ReportsService(db)
    query = NewUsersReportQuery(
        start_date=start_date,
        end_date=end_date,
        group_name=group_name
    )
    return await service.get_new_users_report(query)


@router.get("/data/top-users")
async def get_top_users_report(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users"),
    order_by: str = Query(
        "total_traffic", regex="^(total_traffic|session_time|session_count)$", description="Order by field"),
    db: AsyncSession = Depends(get_db)
):
    """Get top users report"""
    service = ReportsService(db)
    query = TopUsersReportQuery(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order_by=order_by
    )
    return await service.get_top_users_report(query)


@router.get("/data/system-logs")
async def get_system_logs_report(
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    logger_name: Optional[str] = Query(
        None, description="Filter by logger name"),
    username: Optional[str] = Query(None, description="Filter by username"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    search_text: Optional[str] = Query(
        None, description="Search in log messages"),
    db: AsyncSession = Depends(get_db)
):
    """Get system logs report"""
    service = ReportsService(db)
    query = SystemLogQuery(
        log_level=log_level,
        logger_name=logger_name,
        username=username,
        start_date=start_date,
        end_date=end_date,
        search_text=search_text
    )
    return await service.get_system_logs_report(query)


@router.get("/data/batch")
async def get_batch_report(
    batch_name: Optional[str] = Query(
        None, description="Filter by batch name"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    """Get batch operations report"""
    service = ReportsService(db)
    query = BatchReportQuery(
        batch_name=batch_name,
        start_date=start_date,
        end_date=end_date
    )
    return await service.get_batch_report(query)


@router.get("/data/system-status")
async def get_system_status_report(db: AsyncSession = Depends(get_db)):
    """Get comprehensive system status report"""
    service = ReportsService(db)
    return await service.get_system_status_report()


@router.get("/dashboard")
async def get_reports_dashboard(db: AsyncSession = Depends(get_db)):
    """Get reports dashboard summary"""
    service = ReportsService(db)
    return await service.get_reports_dashboard()
