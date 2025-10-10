"""
Accounting API Module

This module provides REST API endpoints for accounting/session statistics
and reporting functionality.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError
from app.models import User
from app.repositories.accounting import (
    AccountingRepository,
    UserTrafficSummaryRepository,
    NasTrafficSummaryRepository
)
from app.services.accounting import (
    AccountingService,
    UserTrafficSummaryService,
    NasTrafficSummaryService
)
from app.schemas.accounting import (
    RadAcctResponse, AccountingQuery, AccountingQueryFilters,
    PaginatedAccountingResponse, AccountingOverview,
    HourlyTrafficReport,
    NasUsageReport, CustomQueryResult, MaintenanceResult,
    PaginatedTopUsersResponse, UserTrafficSummaryResponse,
    NasTrafficSummaryResponse, AccountingTimeRangeEnum,
    CustomQueryRequest, MaintenanceRequest
)
from sqlalchemy.orm import Session

router = APIRouter()


def get_accounting_service(db: Session = Depends(get_db)) -> AccountingService:
    """Get accounting service instance"""
    repository = AccountingRepository(db)
    return AccountingService(repository)


def get_user_traffic_summary_service(db: Session = Depends(get_db)) -> UserTrafficSummaryService:
    """Get user traffic summary service instance"""
    repository = UserTrafficSummaryRepository(db)
    return UserTrafficSummaryService(repository)


def get_nas_traffic_summary_service(db: Session = Depends(get_db)) -> NasTrafficSummaryService:
    """Get NAS traffic summary service instance"""
    repository = NasTrafficSummaryRepository(db)
    return NasTrafficSummaryService(repository)


# =====================================================================
# Session Management Endpoints
# =====================================================================

@router.get("/sessions", response_model=PaginatedAccountingResponse)
async def get_accounting_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_field: Optional[str] = Query(
        "acctstarttime", description="Sort field"),
    sort_order: Optional[str] = Query(
        "desc", regex="^(asc|desc)$", description="Sort order"),
    # Filters
    username: Optional[str] = Query(None, description="Filter by username"),
    groupname: Optional[str] = Query(None, description="Filter by group name"),
    nasipaddress: Optional[str] = Query(
        None, description="Filter by NAS IP address"),
    framedipaddress: Optional[str] = Query(
        None, description="Filter by framed IP address"),
    callingstationid: Optional[str] = Query(
        None, description="Filter by calling station ID"),
    servicetype: Optional[str] = Query(
        None, description="Filter by service type"),
    time_range: Optional[AccountingTimeRangeEnum] = Query(
        None, description="Predefined time range"),
    start_date: Optional[datetime] = Query(
        None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    active_only: Optional[bool] = Query(
        None, description="Show only active sessions"),
    # Current user dependency
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get paginated accounting sessions with filtering"""
    try:
        # Build query filters
        filters = AccountingQueryFilters(
            username=username,
            groupname=groupname,
            nasipaddress=nasipaddress,
            framedipaddress=framedipaddress,
            callingstationid=callingstationid,
            servicetype=servicetype,
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            active_only=active_only
        )

        # Create query
        query = AccountingQuery(
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_order=sort_order,
            filters=filters
        )

        # Get sessions
        return await service.get_accounting_sessions(query)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/{session_id}", response_model=RadAcctResponse)
async def get_session_by_id(
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get accounting session by ID"""
    try:
        return await service.get_session_by_id(session_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/active", response_model=PaginatedAccountingResponse)
async def get_active_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    nas_ip: Optional[str] = Query(None, description="Filter by NAS IP"),
    username: Optional[str] = Query(None, description="Filter by username"),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get active sessions"""
    try:
        return await service.get_active_sessions(
            page=page,
            page_size=page_size,
            nas_ip=nas_ip,
            username=username
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/user/{username}", response_model=PaginatedAccountingResponse)
async def get_user_sessions(
    username: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get sessions for a specific user"""
    try:
        return await service.get_user_sessions(
            username=username,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================================
# Statistics and Overview Endpoints
# =====================================================================

@router.get("/overview", response_model=AccountingOverview)
async def get_accounting_overview(
    time_range: Optional[AccountingTimeRangeEnum] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    # Filters
    username: Optional[str] = Query(None),
    groupname: Optional[str] = Query(None),
    nasipaddress: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get comprehensive accounting overview"""
    try:
        filters = None
        if username or groupname or nasipaddress:
            filters = AccountingQueryFilters(
                username=username,
                groupname=groupname,
                nasipaddress=nasipaddress
            )

        return await service.get_accounting_overview(
            time_range=time_range,
            date_from=date_from,
            date_to=date_to,
            filters=filters
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================================
# Reports Endpoints
# =====================================================================

@router.get("/reports/top-users", response_model=PaginatedTopUsersResponse)
async def get_top_users_report(
    limit: int = Query(10, ge=1, le=100, description="Number of top users"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get top users by traffic consumption"""
    try:
        return await service.get_top_users_report(
            limit=limit,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/reports/hourly-traffic", response_model=List[HourlyTrafficReport])
async def get_hourly_traffic_report(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get hourly traffic distribution report"""
    try:
        return await service.get_hourly_traffic_report(
            date_from=date_from,
            date_to=date_to
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/reports/nas-usage", response_model=List[NasUsageReport])
async def get_nas_usage_report(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get NAS usage statistics report"""
    try:
        return await service.get_nas_usage_report(
            date_from=date_from,
            date_to=date_to
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================================
# Custom Queries and Maintenance
# =====================================================================

@router.post("/custom-query", response_model=CustomQueryResult)
async def execute_custom_query(
    request: CustomQueryRequest,
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Execute custom accounting query"""
    try:
        return await service.execute_custom_query(
            query_sql=request.query_sql,
            parameters=request.parameters,
            limit=request.limit
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/maintenance/cleanup", response_model=MaintenanceResult)
async def cleanup_old_sessions(
    request: MaintenanceRequest,
    current_user: User = Depends(get_current_user),
    service: AccountingService = Depends(get_accounting_service)
):
    """Clean up old accounting sessions"""
    try:
        return await service.cleanup_old_sessions(
            days_old=request.days_old,
            dry_run=request.dry_run
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================================
# Traffic Summary Endpoints
# =====================================================================

@router.get("/traffic-summary/user/{username}", response_model=List[UserTrafficSummaryResponse])
async def get_user_traffic_summary(
    username: str,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: UserTrafficSummaryService = Depends(
        get_user_traffic_summary_service)
):
    """Get traffic summary for a user"""
    try:
        return await service.get_user_traffic_summary(
            username=username,
            date_from=date_from.date() if date_from else None,
            date_to=date_to.date() if date_to else None
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/traffic-summary/nas/{nasipaddress}", response_model=List[NasTrafficSummaryResponse])
async def get_nas_traffic_summary(
    nasipaddress: str,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    service: NasTrafficSummaryService = Depends(
        get_nas_traffic_summary_service)
):
    """Get traffic summary for a NAS"""
    try:
        return await service.get_nas_traffic_summary(
            nasipaddress=nasipaddress,
            date_from=date_from.date() if date_from else None,
            date_to=date_to.date() if date_to else None
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =====================================================================
# Health Check
# =====================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for accounting module"""
    return JSONResponse(
        content={
            "status": "healthy",
            "module": "accounting",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Export router
__all__ = ["router"]
