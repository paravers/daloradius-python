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
    BillingMerchantRepository,
    InvoiceRepository,
    PaymentRepository,
    RefundRepository,
    PaymentTypeRepository,
    POSRepository
)
from app.services.billing import (
    BillingPlanService,
    BillingHistoryService,
    BillingRateService,
    BillingMerchantService,
    InvoiceService,
    PaymentService,
    RefundService,
    PaymentTypeService,
    POSService
)
from app.schemas.billing import (
    BillingPlanCreate, BillingPlanUpdate, BillingPlanResponse,
    BillingHistoryCreate, BillingHistoryResponse,
    BillingRateCreate, BillingRateUpdate, BillingRateResponse,
    MerchantTransactionCreate, MerchantTransactionResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    RefundCreate, RefundUpdate, RefundResponse,
    PaymentTypeCreate, PaymentTypeUpdate, PaymentTypeResponse,
    POSCreate, POSUpdate, POSResponse,
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


def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    repository = InvoiceRepository(db)
    return InvoiceService(repository)


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    repository = PaymentRepository(db)
    return PaymentService(repository)


def get_refund_service(db: Session = Depends(get_db)) -> RefundService:
    repository = RefundRepository(db)
    return RefundService(repository)


def get_payment_type_service(db: Session = Depends(get_db)) -> PaymentTypeService:
    repository = PaymentTypeRepository(db)
    return PaymentTypeService(repository)


def get_pos_service(db: Session = Depends(get_db)) -> POSService:
    repository = POSRepository(db)
    return POSService(repository)


# =====================================================================
# Billing Plans API Endpoints
# =====================================================================

@router.get("/plans", response_model=PaginatedResponse, summary="Get billing plans")
async def get_billing_plans(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(None, description="Filter by plan name"),
    type_filter: Optional[str] = Query(
        None, alias="type", description="Filter by plan type"),
    active_only: bool = Query(False, description="Show only active plans"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
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
            raise HTTPException(
                status_code=404, detail="Billing plan not found")
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
    sort_order: str = Query("desc", regex="^(asc|desc)$",
                            description="Sort order"),
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
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of records"),
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
    type_filter: Optional[str] = Query(
        None, alias="type", description="Filter by rate type"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
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
            raise HTTPException(
                status_code=404, detail="Billing rate not found")
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
    business_id: Optional[str] = Query(
        None, description="Filter by business ID"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$",
                            description="Sort order"),
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
# Invoice API Endpoints
# =====================================================================

@router.get("/invoices", response_model=PaginatedResponse, summary="Get invoices")
async def get_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    customer: Optional[str] = Query(
        None, description="Filter by customer name or ID"),
    status: Optional[str] = Query(
        None, description="Filter by invoice status"),
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of invoices with optional filtering"""
    try:
        return await service.get_invoices(
            page=page,
            page_size=page_size,
            customer_filter=customer,
            status_filter=status,
            date_from=date_from,
            date_to=date_to,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse, summary="Get invoice by ID")
async def get_invoice(
    invoice_id: int = Path(..., description="Invoice ID"),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific invoice by ID"""
    try:
        return await service.get_invoice(invoice_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices", response_model=InvoiceResponse, status_code=201, summary="Create invoice")
async def create_invoice(
    invoice_data: InvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new invoice"""
    try:
        return await service.create_invoice(invoice_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse, summary="Update invoice")
async def update_invoice(
    invoice_id: int = Path(..., description="Invoice ID"),
    invoice_data: InvoiceUpdate = None,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing invoice"""
    try:
        return await service.update_invoice(invoice_id, invoice_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/invoices/{invoice_id}", summary="Delete invoice")
async def delete_invoice(
    invoice_id: int = Path(..., description="Invoice ID"),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete an invoice"""
    try:
        result = await service.delete_invoice(invoice_id)
        if result:
            return {"message": f"Invoice {invoice_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Invoice not found")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Payment API Endpoints
# =====================================================================

@router.get("/payments", response_model=PaginatedResponse, summary="Get payments")
async def get_payments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    customer: Optional[str] = Query(None, description="Filter by customer ID"),
    payment_method: Optional[str] = Query(
        None, description="Filter by payment method"),
    status: Optional[str] = Query(
        None, description="Filter by payment status"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
    service: PaymentService = Depends(get_payment_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of payments with optional filtering"""
    try:
        return await service.get_payments(
            page=page,
            page_size=page_size,
            customer_filter=customer,
            payment_method_filter=payment_method,
            status_filter=status,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments/{payment_id}", response_model=PaymentResponse, summary="Get payment by ID")
async def get_payment(
    payment_id: int = Path(..., description="Payment ID"),
    service: PaymentService = Depends(get_payment_service),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific payment by ID"""
    try:
        return await service.get_payment(payment_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments", response_model=PaymentResponse, status_code=201, summary="Create payment")
async def create_payment(
    payment_data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new payment"""
    try:
        return await service.create_payment(payment_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/payments/{payment_id}", response_model=PaymentResponse, summary="Update payment")
async def update_payment(
    payment_id: int = Path(..., description="Payment ID"),
    payment_data: PaymentUpdate = None,
    service: PaymentService = Depends(get_payment_service),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing payment"""
    try:
        return await service.update_payment(payment_id, payment_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Refund API Endpoints
# =====================================================================

@router.get("/refunds", response_model=PaginatedResponse, summary="Get refunds")
async def get_refunds(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    customer: Optional[str] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by refund status"),
    payment_id: Optional[int] = Query(
        None, description="Filter by payment ID"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
    service: RefundService = Depends(get_refund_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of refunds with optional filtering"""
    try:
        return await service.get_refunds(
            page=page,
            page_size=page_size,
            customer_filter=customer,
            status_filter=status,
            payment_id_filter=payment_id,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refunds", response_model=RefundResponse, status_code=201, summary="Create refund")
async def create_refund(
    refund_data: RefundCreate,
    service: RefundService = Depends(get_refund_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new refund"""
    try:
        return await service.create_refund(refund_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# Payment Type API Endpoints
# =====================================================================

@router.get("/payment-types", response_model=PaginatedResponse, summary="Get payment types")
async def get_payment_types(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(
        None, description="Filter by payment type name"),
    active_only: bool = Query(
        False, description="Show only active payment types"),
    sort_field: str = Query("sort_order", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
    service: PaymentTypeService = Depends(get_payment_type_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of payment types with optional filtering"""
    try:
        return await service.get_payment_types(
            page=page,
            page_size=page_size,
            name_filter=name,
            active_only=active_only,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment-types", response_model=PaymentTypeResponse, status_code=201, summary="Create payment type")
async def create_payment_type(
    payment_type_data: PaymentTypeCreate,
    service: PaymentTypeService = Depends(get_payment_type_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new payment type"""
    try:
        return await service.create_payment_type(payment_type_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# POS Terminal API Endpoints
# =====================================================================

@router.get("/pos-terminals", response_model=PaginatedResponse, summary="Get POS terminals")
async def get_pos_terminals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    name: Optional[str] = Query(
        None, description="Filter by terminal name or serial"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(
        None, description="Filter by terminal status"),
    sort_field: str = Query("id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$",
                            description="Sort order"),
    service: POSService = Depends(get_pos_service),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of POS terminals with optional filtering"""
    try:
        return await service.get_terminals(
            page=page,
            page_size=page_size,
            name_filter=name,
            location_filter=location,
            status_filter=status,
            sort_field=sort_field,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pos-terminals", response_model=POSResponse, status_code=201, summary="Create POS terminal")
async def create_pos_terminal(
    pos_data: POSCreate,
    service: POSService = Depends(get_pos_service),
    current_user: dict = Depends(get_current_user)
):
    """Create a new POS terminal"""
    try:
        return await service.create_terminal(pos_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
