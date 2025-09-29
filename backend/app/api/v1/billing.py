"""
Billing API Routes

This module provides REST API endpoints for billing management,
including plans, history, rates, and merchant operations.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.billing import (
    BillingPlanRepository,
    BillingHistoryRepository,
    BillingRateRepository,
    BillingMerchantRepository
)
from app.services.billing import (
    BillingPlanService,
    BillingHistoryService,
    BillingRateService,
    BillingMerchantService
)
from app.schemas.billing import (
    BillingPlanCreate, BillingPlanUpdate, BillingPlanResponse,
    BillingHistoryCreate, BillingHistoryResponse,
    BillingRateCreate, BillingRateUpdate, BillingRateResponse,
    MerchantTransactionCreate, MerchantTransactionResponse,
    PaginatedResponse
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


# Dependency injection helpers
def get_billing_plan_service(db: Session = Depends(get_db)) -> BillingPlanService:
    repository = BillingPlanRepository(db)
    return BillingPlanService(repository)


def get_billing_history_service(db: Session = Depends(get_db)) -> BillingHistoryService:
    repository = BillingHistoryRepository(db)
    return BillingHistoryService(repository)


def get_billing_rate_service(db: Session = Depends(get_db)) -> BillingRateService:
    repository = BillingRateRepository(db)
    return BillingRateService(repository)


def get_billing_merchant_service(db: Session = Depends(get_db)) -> BillingMerchantService:
    repository = BillingMerchantRepository(db)
    return BillingMerchantService(repository)


# =====================================================================
# Billing Plans API Endpoints
# =====================================================================

@router.get("/plans", response_model=PaginatedResponse, summary="Get billing plans")
async def get_billing_plans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(None, description="Filter by plan name"),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by plan type"),
    active_only: bool = Query(False, description="Show only active plans"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of billing plans with optional filtering"""
    try:
        return await service.get_plans(
            page=page,
            page_size=page_size,
            name_filter=name,
            type_filter=type_filter,
            active_only=active_only,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/active", response_model=List[BillingPlanResponse], summary="Get active billing plans")
async def get_active_billing_plans(
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Get all active billing plans"""
    try:
        return await service.get_active_plans()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/statistics", response_model=Dict[str, Any], summary="Get billing plans statistics")
async def get_billing_plan_statistics(
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Get billing plan statistics"""
    try:
        return await service.get_plan_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}", response_model=BillingPlanResponse, summary="Get billing plan by ID")
async def get_billing_plan(
    plan_id: int = Path(..., description="Billing plan ID"),
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific billing plan by ID"""
    try:
        return await service.get_plan_by_id(plan_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plans", response_model=BillingPlanResponse, status_code=201, summary="Create billing plan")
async def create_billing_plan(
    plan_data: BillingPlanCreate,
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new billing plan"""
    try:
        return await service.create_plan(plan_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/plans/{plan_id}", response_model=BillingPlanResponse, summary="Update billing plan")
async def update_billing_plan(
    plan_id: int = Path(..., description="Billing plan ID"),
    plan_data: BillingPlanUpdate = ...,
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing billing plan"""
    try:
        return await service.update_plan(plan_id, plan_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plans/{plan_id}", status_code=204, summary="Delete billing plan")
async def delete_billing_plan(
    plan_id: int = Path(..., description="Billing plan ID"),
    service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete a billing plan"""
    try:
        success = await service.delete_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Billing plan not found")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Billing History API Endpoints
# =====================================================================

@router.get("/history", response_model=PaginatedResponse, summary="Get billing history")
async def get_billing_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    username: Optional[str] = Query(None, description="Filter by username"),
    plan_id: Optional[int] = Query(None, description="Filter by plan ID"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    service: BillingHistoryService = Depends(get_billing_history_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated billing history with optional filtering"""
    try:
        return await service.get_history(
            page=page,
            page_size=page_size,
            username_filter=username,
            plan_id_filter=plan_id,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/users/{username}", response_model=List[BillingHistoryResponse], summary="Get user billing history")
async def get_user_billing_history(
    username: str = Path(..., description="Username"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    service: BillingHistoryService = Depends(get_billing_history_service),
    current_user: dict = Depends(get_current_user)
):
    """Get billing history for a specific user"""
    try:
        return await service.get_user_history(username, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/users/{username}/statistics", response_model=Dict[str, Any], summary="Get user billing statistics")
async def get_user_billing_statistics(
    username: str = Path(..., description="Username"),
    service: BillingHistoryService = Depends(get_billing_history_service),
    current_user: dict = Depends(get_current_user)
):
    """Get billing statistics for a specific user"""
    try:
        return await service.get_user_statistics(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history", response_model=BillingHistoryResponse, status_code=201, summary="Create billing history record")
async def create_billing_history(
    history_data: BillingHistoryCreate,
    service: BillingHistoryService = Depends(get_billing_history_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new billing history record"""
    try:
        return await service.create_history_record(history_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Billing Rates API Endpoints
# =====================================================================

@router.get("/rates", response_model=PaginatedResponse, summary="Get billing rates")
async def get_billing_rates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(None, description="Filter by rate name"),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by rate type"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    service: BillingRateService = Depends(get_billing_rate_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of billing rates with optional filtering"""
    try:
        return await service.get_rates(
            page=page,
            page_size=page_size,
            name_filter=name,
            type_filter=type_filter,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rates", response_model=BillingRateResponse, status_code=201, summary="Create billing rate")
async def create_billing_rate(
    rate_data: BillingRateCreate,
    service: BillingRateService = Depends(get_billing_rate_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new billing rate"""
    try:
        return await service.create_rate(rate_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rates/{rate_id}", response_model=BillingRateResponse, summary="Update billing rate")
async def update_billing_rate(
    rate_id: int = Path(..., description="Billing rate ID"),
    rate_data: BillingRateUpdate = ...,
    service: BillingRateService = Depends(get_billing_rate_service),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing billing rate"""
    try:
        return await service.update_rate(rate_id, rate_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rates/{rate_id}", status_code=204, summary="Delete billing rate")
async def delete_billing_rate(
    rate_id: int = Path(..., description="Billing rate ID"),
    service: BillingRateService = Depends(get_billing_rate_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete a billing rate"""
    try:
        success = await service.delete_rate(rate_id)
        if not success:
            raise HTTPException(status_code=404, detail="Billing rate not found")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Merchant Transactions API Endpoints
# =====================================================================

@router.get("/merchants/transactions", response_model=PaginatedResponse, summary="Get merchant transactions")
async def get_merchant_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    username: Optional[str] = Query(None, description="Filter by username"),
    business_id: Optional[str] = Query(None, description="Filter by business ID"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    service: BillingMerchantService = Depends(get_billing_merchant_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of merchant transactions with optional filtering"""
    try:
        return await service.get_transactions(
            page=page,
            page_size=page_size,
            username_filter=username,
            business_id_filter=business_id,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merchants/transactions", response_model=MerchantTransactionResponse, status_code=201, summary="Create merchant transaction")
async def create_merchant_transaction(
    transaction_data: MerchantTransactionCreate,
    service: BillingMerchantService = Depends(get_billing_merchant_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new merchant transaction"""
    try:
        return await service.create_transaction(transaction_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# General Billing Statistics
# =====================================================================

@router.get("/statistics", response_model=Dict[str, Any], summary="Get overall billing statistics")
async def get_billing_statistics(
    plan_service: BillingPlanService = Depends(get_billing_plan_service),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive billing system statistics"""
    try:
        plan_stats = await plan_service.get_plan_statistics()
        
        return {
            "plans": plan_stats,
            "generated_at": "2024-01-01T00:00:00Z"  # Current timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Health Check
# =====================================================================

@router.get("/health", summary="Billing API health check")
async def billing_health_check():
    """Health check endpoint for billing API"""
    return {
        "status": "healthy",
        "service": "billing",
        "version": "1.0.0"
    }