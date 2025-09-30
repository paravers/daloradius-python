"""
Billing and Payment Pydantic Schemas

This module contains Pydantic models for billing, payments, invoices,
and rate management validation and serialization.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status options"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    """Invoice status options"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Payment method options"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    OTHER = "other"


class BillingType(str, Enum):
    """Billing type options"""
    PREPAID = "prepaid"
    POSTPAID = "postpaid"
    UNLIMITED = "unlimited"


class RateType(str, Enum):
    """Rate calculation types"""
    FIXED = "fixed"
    TIME_BASED = "time_based"
    DATA_BASED = "data_based"
    COMBINED = "combined"


# Billing Plan schemas
class BillPlanBase(BaseModel):
    """Base billing plan schema"""
    plan_name: str = Field(..., max_length=128, description="Plan name")
    plan_id: str = Field(..., max_length=64,
                         description="Unique plan identifier")
    description: Optional[str] = Field(None, description="Plan description")
    plan_cost: Decimal = Field(..., ge=0, description="Plan cost")
    plan_setup_cost: Decimal = Field(0, ge=0, description="Setup cost")
    plan_type: BillingType = Field(..., description="Billing type")
    plan_tax: Decimal = Field(0, ge=0, le=100, description="Tax percentage")
    currency: str = Field("USD", max_length=3, description="Currency code")

    # Time and data limits
    max_all_session_time: Optional[int] = Field(
        None, ge=0, description="Max total session time in seconds")
    max_daily_session_time: Optional[int] = Field(
        None, ge=0, description="Max daily session time in seconds")
    max_weekly_session_time: Optional[int] = Field(
        None, ge=0, description="Max weekly session time in seconds")
    max_monthly_session_time: Optional[int] = Field(
        None, ge=0, description="Max monthly session time in seconds")

    max_all_session_traffic: Optional[int] = Field(
        None, ge=0, description="Max total traffic in MB")
    max_daily_session_traffic: Optional[int] = Field(
        None, ge=0, description="Max daily traffic in MB")
    max_weekly_session_traffic: Optional[int] = Field(
        None, ge=0, description="Max weekly traffic in MB")
    max_monthly_session_traffic: Optional[int] = Field(
        None, ge=0, description="Max monthly traffic in MB")

    # Session settings
    simultaneous_use: int = Field(
        1, ge=1, description="Simultaneous sessions allowed")
    session_timeout: Optional[int] = Field(
        None, ge=0, description="Session timeout in seconds")
    idle_timeout: Optional[int] = Field(
        None, ge=0, description="Idle timeout in seconds")

    # Network settings
    download_limit: Optional[int] = Field(
        None, ge=0, description="Download speed limit in Kbps")
    upload_limit: Optional[int] = Field(
        None, ge=0, description="Upload speed limit in Kbps")

    # Plan validity
    plan_active: bool = Field(True, description="Is plan active")
    plan_creation_date: Optional[datetime] = None
    plan_creation_by: Optional[str] = Field(None, max_length=128)

    @validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError('Currency must be 3 characters (ISO 4217)')
        return v.upper()


class BillPlanCreate(BillPlanBase):
    """Schema for creating billing plan"""
    pass


class BillPlanUpdate(BaseModel):
    """Schema for updating billing plan"""
    plan_name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    plan_cost: Optional[Decimal] = Field(None, ge=0)
    plan_setup_cost: Optional[Decimal] = Field(None, ge=0)
    plan_type: Optional[BillingType] = None
    plan_tax: Optional[Decimal] = Field(None, ge=0, le=100)
    max_all_session_time: Optional[int] = Field(None, ge=0)
    max_daily_session_time: Optional[int] = Field(None, ge=0)
    max_weekly_session_time: Optional[int] = Field(None, ge=0)
    max_monthly_session_time: Optional[int] = Field(None, ge=0)
    max_all_session_traffic: Optional[int] = Field(None, ge=0)
    max_daily_session_traffic: Optional[int] = Field(None, ge=0)
    max_weekly_session_traffic: Optional[int] = Field(None, ge=0)
    max_monthly_session_traffic: Optional[int] = Field(None, ge=0)
    simultaneous_use: Optional[int] = Field(None, ge=1)
    session_timeout: Optional[int] = Field(None, ge=0)
    idle_timeout: Optional[int] = Field(None, ge=0)
    download_limit: Optional[int] = Field(None, ge=0)
    upload_limit: Optional[int] = Field(None, ge=0)
    plan_active: Optional[bool] = None


class BillPlanResponse(BillPlanBase):
    """Schema for billing plan responses"""
    id: int

    class Config:
        from_attributes = True


# Rate schemas
class BillRateBase(BaseModel):
    """Base billing rate schema"""
    rate_name: str = Field(..., max_length=128, description="Rate name")
    rate_type: RateType = Field(..., description="Rate type")
    rate_cost: Decimal = Field(..., ge=0, description="Rate cost per unit")
    currency: str = Field("USD", max_length=3, description="Currency code")

    # Time-based rates
    rate_per_minute: Optional[Decimal] = Field(
        None, ge=0, description="Cost per minute")
    rate_per_hour: Optional[Decimal] = Field(
        None, ge=0, description="Cost per hour")

    # Data-based rates
    rate_per_mb: Optional[Decimal] = Field(
        None, ge=0, description="Cost per MB")
    rate_per_gb: Optional[Decimal] = Field(
        None, ge=0, description="Cost per GB")

    # Rate validity
    rate_effective_date: Optional[date] = Field(
        None, description="Rate effective date")
    rate_expiry_date: Optional[date] = Field(
        None, description="Rate expiry date")
    is_active: bool = Field(True, description="Is rate active")


class BillRateCreate(BillRateBase):
    """Schema for creating billing rate"""
    pass


class BillRateUpdate(BaseModel):
    """Schema for updating billing rate"""
    rate_name: Optional[str] = Field(None, max_length=128)
    rate_cost: Optional[Decimal] = Field(None, ge=0)
    rate_per_minute: Optional[Decimal] = Field(None, ge=0)
    rate_per_hour: Optional[Decimal] = Field(None, ge=0)
    rate_per_mb: Optional[Decimal] = Field(None, ge=0)
    rate_per_gb: Optional[Decimal] = Field(None, ge=0)
    rate_effective_date: Optional[date] = None
    rate_expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class BillRateResponse(BillRateBase):
    """Schema for billing rate responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Payment Type schemas
class PaymentTypeBase(BaseModel):
    """Base payment type schema"""
    type_name: str = Field(..., max_length=128,
                           description="Payment type name")
    type_description: Optional[str] = Field(
        None, description="Payment type description")
    is_active: bool = Field(True, description="Is payment type active")


class PaymentTypeCreate(PaymentTypeBase):
    """Schema for creating payment type"""
    pass


class PaymentTypeResponse(PaymentTypeBase):
    """Schema for payment type responses"""
    id: int

    class Config:
        from_attributes = True


# Payment schemas
class PaymentBase(BaseModel):
    """Base payment schema"""
    username: str = Field(..., max_length=64, description="Username")
    payment_amount: Decimal = Field(..., ge=0, description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    payment_status: PaymentStatus = Field(
        PaymentStatus.PENDING, description="Payment status")
    currency: str = Field("USD", max_length=3, description="Currency code")

    # Payment details
    payment_date: Optional[datetime] = None
    payment_notes: Optional[str] = Field(None, description="Payment notes")
    transaction_id: Optional[str] = Field(
        None, max_length=128, description="External transaction ID")

    # Invoice association
    invoice_id: Optional[int] = Field(
        None, description="Associated invoice ID")


class PaymentCreate(PaymentBase):
    """Schema for creating payment"""
    pass


class PaymentUpdate(BaseModel):
    """Schema for updating payment"""
    payment_status: Optional[PaymentStatus] = None
    payment_date: Optional[datetime] = None
    payment_notes: Optional[str] = None
    transaction_id: Optional[str] = Field(None, max_length=128)


class PaymentResponse(PaymentBase):
    """Schema for payment responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


# Invoice schemas
class InvoiceBase(BaseModel):
    """Base invoice schema"""
    username: str = Field(..., max_length=64, description="Username")
    invoice_date: date = Field(..., description="Invoice date")
    due_date: Optional[date] = Field(None, description="Due date")
    invoice_status: InvoiceStatus = Field(
        InvoiceStatus.DRAFT, description="Invoice status")

    # Amounts
    subtotal: Decimal = Field(..., ge=0, description="Subtotal amount")
    tax_amount: Decimal = Field(0, ge=0, description="Tax amount")
    discount_amount: Decimal = Field(0, ge=0, description="Discount amount")
    total_amount: Decimal = Field(..., ge=0, description="Total amount")
    paid_amount: Decimal = Field(0, ge=0, description="Amount paid")

    currency: str = Field("USD", max_length=3, description="Currency code")
    invoice_notes: Optional[str] = Field(None, description="Invoice notes")


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoice"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    due_date: Optional[date] = None
    invoice_status: Optional[InvoiceStatus] = None
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    invoice_notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses"""
    id: int
    invoice_number: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if not self.due_date:
            return False
        return date.today() > self.due_date and self.balance_due > 0

    class Config:
        from_attributes = True


# Invoice Line Item schemas
class InvoiceLineItemBase(BaseModel):
    """Base invoice line item schema"""
    description: str = Field(..., max_length=255,
                             description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    discount_percentage: Decimal = Field(
        0, ge=0, le=100, description="Discount percentage")

    @property
    def line_total(self) -> Decimal:
        """Calculate line total"""
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percentage / 100)
        return subtotal - discount


class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema for creating invoice line item"""
    invoice_id: int = Field(..., description="Invoice ID")


class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Schema for invoice line item responses"""
    id: int
    invoice_id: int

    class Config:
        from_attributes = True


# User billing info schemas
class UserBillingInfoBase(BaseModel):
    """Base user billing info schema"""
    username: str = Field(..., max_length=64, description="Username")
    plan_name: Optional[str] = Field(
        None, max_length=128, description="Current plan")

    # Billing cycle
    billing_cycle_start: Optional[date] = Field(
        None, description="Billing cycle start")
    billing_cycle_end: Optional[date] = Field(
        None, description="Billing cycle end")

    # Account balance
    account_balance: Decimal = Field(0, description="Account balance")
    credit_limit: Decimal = Field(0, ge=0, description="Credit limit")

    # Status
    billing_status: str = Field(
        "active", max_length=32, description="Billing status")
    auto_renew: bool = Field(False, description="Auto-renew subscription")

    # Contact info
    billing_email: Optional[str] = Field(
        None, max_length=255, description="Billing email")
    billing_phone: Optional[str] = Field(
        None, max_length=32, description="Billing phone")

    # Address
    billing_address: Optional[str] = Field(
        None, max_length=255, description="Billing address")
    billing_city: Optional[str] = Field(
        None, max_length=100, description="Billing city")
    billing_state: Optional[str] = Field(
        None, max_length=100, description="Billing state")
    billing_zip: Optional[str] = Field(
        None, max_length=20, description="Billing ZIP")
    billing_country: Optional[str] = Field(
        None, max_length=100, description="Billing country")


class UserBillingInfoCreate(UserBillingInfoBase):
    """Schema for creating user billing info"""
    pass


class UserBillingInfoUpdate(BaseModel):
    """Schema for updating user billing info"""
    plan_name: Optional[str] = Field(None, max_length=128)
    billing_cycle_start: Optional[date] = None
    billing_cycle_end: Optional[date] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    billing_status: Optional[str] = Field(None, max_length=32)
    auto_renew: Optional[bool] = None
    billing_email: Optional[str] = Field(None, max_length=255)
    billing_phone: Optional[str] = Field(None, max_length=32)
    billing_address: Optional[str] = Field(None, max_length=255)
    billing_city: Optional[str] = Field(None, max_length=100)
    billing_state: Optional[str] = Field(None, max_length=100)
    billing_zip: Optional[str] = Field(None, max_length=20)
    billing_country: Optional[str] = Field(None, max_length=100)


class UserBillingInfoResponse(UserBillingInfoBase):
    """Schema for user billing info responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    @property
    def available_credit(self) -> Decimal:
        """Calculate available credit"""
        return self.credit_limit + self.account_balance

    class Config:
        from_attributes = True


# Reporting schemas
class BillingReport(BaseModel):
    """Billing report schema"""
    report_date: date
    total_revenue: Decimal = 0
    total_payments: Decimal = 0
    total_outstanding: Decimal = 0
    total_invoices: int = 0
    paid_invoices: int = 0
    overdue_invoices: int = 0
    active_subscribers: int = 0
    currency: str = "USD"


class PaymentSummary(BaseModel):
    """Payment summary schema"""
    period_start: date
    period_end: date
    total_payments: Decimal = 0
    payment_count: int = 0
    average_payment: Decimal = 0
    payment_methods: Dict[str, Decimal] = {}
    currency: str = "USD"


class UserBillingSummary(BaseModel):
    """User billing summary schema"""
    username: str
    current_plan: Optional[str] = None
    account_balance: Decimal = 0
    total_payments: Decimal = 0
    total_invoices: Decimal = 0
    outstanding_amount: Decimal = 0
    last_payment_date: Optional[date] = None
    next_billing_date: Optional[date] = None


# Batch operations
class BatchInvoiceGeneration(BaseModel):
    """Schema for batch invoice generation"""
    usernames: List[str] = Field(..., description="List of usernames")
    invoice_date: date = Field(..., description="Invoice date")
    due_days: int = Field(
        30, ge=1, description="Due date in days from invoice date")
    include_usage: bool = Field(True, description="Include usage charges")


class BulkPaymentProcessing(BaseModel):
    """Schema for bulk payment processing"""
    payments: List[PaymentCreate] = Field(..., max_items=100)
    auto_apply_to_invoices: bool = Field(
        True, description="Auto-apply to outstanding invoices")


# =====================================================================
# API-compatible schemas for existing billing models
# =====================================================================

# Billing Plan schemas matching the database model
class BillingPlanBase(BaseModel):
    """Base schema for BillingPlan model"""
    planName: Optional[str] = Field(
        None, max_length=128, description="Plan name")
    planId: Optional[str] = Field(
        None, max_length=128, description="Plan identifier")
    planType: Optional[str] = Field(
        None, max_length=128, description="Plan type")
    planTimeBank: Optional[str] = Field(
        None, max_length=128, description="Time bank")
    planTimeType: Optional[str] = Field(
        None, max_length=128, description="Time type")
    planTimeRefillCost: Optional[str] = Field(
        None, max_length=128, description="Time refill cost")
    planBandwidthUp: Optional[str] = Field(
        None, max_length=128, description="Upload bandwidth")
    planBandwidthDown: Optional[str] = Field(
        None, max_length=128, description="Download bandwidth")
    planTrafficTotal: Optional[str] = Field(
        None, max_length=128, description="Total traffic")
    planTrafficUp: Optional[str] = Field(
        None, max_length=128, description="Upload traffic")
    planTrafficDown: Optional[str] = Field(
        None, max_length=128, description="Download traffic")
    planTrafficRefillCost: Optional[str] = Field(
        None, max_length=128, description="Traffic refill cost")
    planRecurring: Optional[str] = Field(
        None, max_length=128, description="Recurring")
    planRecurringPeriod: Optional[str] = Field(
        None, max_length=128, description="Recurring period")
    planRecurringBillingSchedule: Optional[str] = Field(
        None, max_length=128, description="Billing schedule")
    planCost: Optional[str] = Field(
        None, max_length=128, description="Plan cost")
    planSetupCost: Optional[str] = Field(
        None, max_length=128, description="Setup cost")
    planTax: Optional[str] = Field(None, max_length=128, description="Tax")
    planCurrency: Optional[str] = Field(
        None, max_length=128, description="Currency")
    planGroup: Optional[str] = Field(
        None, max_length=128, description="Plan group")
    planActive: Optional[bool] = Field(None, description="Is plan active")


class BillingPlanCreate(BillingPlanBase):
    """Schema for creating billing plans"""
    planName: str = Field(..., description="Plan name is required")


class BillingPlanUpdate(BaseModel):
    """Schema for updating billing plans"""
    planName: Optional[str] = Field(None, max_length=128)
    planId: Optional[str] = Field(None, max_length=128)
    planType: Optional[str] = Field(None, max_length=128)
    planTimeBank: Optional[str] = Field(None, max_length=128)
    planTimeType: Optional[str] = Field(None, max_length=128)
    planTimeRefillCost: Optional[str] = Field(None, max_length=128)
    planBandwidthUp: Optional[str] = Field(None, max_length=128)
    planBandwidthDown: Optional[str] = Field(None, max_length=128)
    planTrafficTotal: Optional[str] = Field(None, max_length=128)
    planTrafficUp: Optional[str] = Field(None, max_length=128)
    planTrafficDown: Optional[str] = Field(None, max_length=128)
    planTrafficRefillCost: Optional[str] = Field(None, max_length=128)
    planRecurring: Optional[str] = Field(None, max_length=128)
    planRecurringPeriod: Optional[str] = Field(None, max_length=128)
    planRecurringBillingSchedule: Optional[str] = Field(None, max_length=128)
    planCost: Optional[str] = Field(None, max_length=128)
    planSetupCost: Optional[str] = Field(None, max_length=128)
    planTax: Optional[str] = Field(None, max_length=128)
    planCurrency: Optional[str] = Field(None, max_length=128)
    planGroup: Optional[str] = Field(None, max_length=128)
    planActive: Optional[bool] = Field(None)


class BillingPlanResponse(BillingPlanBase):
    """Schema for billing plan responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# Billing History schemas
class BillingHistoryBase(BaseModel):
    """Base schema for BillingHistory model"""
    username: Optional[str] = Field(
        None, max_length=128, description="Username")
    planId: Optional[int] = Field(None, description="Plan ID")
    billAmount: Optional[str] = Field(
        None, max_length=200, description="Bill amount")
    billAction: Optional[str] = Field(
        None, max_length=128, description="Bill action")
    billPerformer: Optional[str] = Field(
        None, max_length=200, description="Bill performer")
    billReason: Optional[str] = Field(
        None, max_length=200, description="Bill reason")
    paymentmethod: Optional[str] = Field(
        None, max_length=200, description="Payment method")
    cash: Optional[str] = Field(
        None, max_length=200, description="Cash amount")
    creditcardname: Optional[str] = Field(
        None, max_length=200, description="Credit card name")
    creditcardnumber: Optional[str] = Field(
        None, max_length=200, description="Credit card number")
    creditcardverification: Optional[str] = Field(
        None, max_length=200, description="Credit card verification")
    creditcardtype: Optional[str] = Field(
        None, max_length=200, description="Credit card type")
    creditcardexp: Optional[str] = Field(
        None, max_length=200, description="Credit card expiration")


class BillingHistoryCreate(BillingHistoryBase):
    """Schema for creating billing history"""
    username: str = Field(..., description="Username is required")
    billAction: str = Field(..., description="Bill action is required")


class BillingHistoryResponse(BillingHistoryBase):
    """Schema for billing history responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None

    class Config:
        from_attributes = True


# Billing Rate schemas
class BillingRateBase(BaseModel):
    """Base schema for BillingRate model"""
    rateName: Optional[str] = Field(
        None, max_length=128, description="Rate name")
    rateType: Optional[str] = Field(
        None, max_length=128, description="Rate type")
    rateCost: Optional[int] = Field(None, description="Rate cost")


class BillingRateCreate(BillingRateBase):
    """Schema for creating billing rates"""
    rateName: str = Field(..., description="Rate name is required")
    rateType: str = Field(..., description="Rate type is required")
    rateCost: int = Field(..., description="Rate cost is required")


class BillingRateUpdate(BaseModel):
    """Schema for updating billing rates"""
    rateName: Optional[str] = Field(None, max_length=128)
    rateType: Optional[str] = Field(None, max_length=128)
    rateCost: Optional[int] = Field(None)


class BillingRateResponse(BillingRateBase):
    """Schema for billing rate responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# Merchant Transaction schemas
class MerchantTransactionBase(BaseModel):
    """Base schema for BillingMerchant model"""
    username: Optional[str] = Field(
        None, max_length=128, description="Username")
    password: Optional[str] = Field(
        None, max_length=128, description="Password")
    mac: Optional[str] = Field(None, max_length=200, description="MAC address")
    pin: Optional[str] = Field(None, max_length=200, description="PIN")
    txnId: Optional[str] = Field(
        None, max_length=200, description="Transaction ID")
    planName: Optional[str] = Field(
        None, max_length=128, description="Plan name")
    planId: Optional[int] = Field(None, description="Plan ID")
    quantity: Optional[str] = Field(
        None, max_length=200, description="Quantity")
    business_email: Optional[str] = Field(
        None, max_length=200, description="Business email")
    business_id: Optional[str] = Field(
        None, max_length=200, description="Business ID")
    txn_type: Optional[str] = Field(
        None, max_length=200, description="Transaction type")
    txn_id: Optional[str] = Field(
        None, max_length=200, description="Transaction ID")
    payment_type: Optional[str] = Field(
        None, max_length=200, description="Payment type")


class MerchantTransactionCreate(MerchantTransactionBase):
    """Schema for creating merchant transactions"""
    username: str = Field(..., description="Username is required")
    txnId: str = Field(..., description="Transaction ID is required")
    business_email: str = Field(..., description="Business email is required")
    business_id: str = Field(..., description="Business ID is required")


class MerchantTransactionResponse(MerchantTransactionBase):
    """Schema for merchant transaction responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================================
# Invoice Schemas
# =====================================================================

class InvoiceBase(BaseModel):
    """Base schema for invoices"""
    invoice_number: Optional[str] = Field(
        None, max_length=50, description="Invoice number")
    customer_id: Optional[str] = Field(
        None, max_length=128, description="Customer ID")
    customer_name: Optional[str] = Field(
        None, max_length=255, description="Customer name")
    customer_email: Optional[str] = Field(
        None, max_length=255, description="Customer email")
    customer_address: Optional[str] = Field(
        None, description="Customer address")
    subtotal: Optional[Decimal] = Field(
        Decimal('0.00'), description="Subtotal amount")
    tax_amount: Optional[Decimal] = Field(
        Decimal('0.00'), description="Tax amount")
    discount_amount: Optional[Decimal] = Field(
        Decimal('0.00'), description="Discount amount")
    total_amount: Optional[Decimal] = Field(
        Decimal('0.00'), description="Total amount")
    currency: Optional[str] = Field(
        "CNY", max_length=3, description="Currency code")
    status: Optional[InvoiceStatus] = Field(
        InvoiceStatus.DRAFT, description="Invoice status")
    issue_date: Optional[date] = Field(None, description="Issue date")
    due_date: Optional[date] = Field(None, description="Due date")
    paid_date: Optional[date] = Field(None, description="Paid date")
    description: Optional[str] = Field(None, description="Invoice description")
    notes: Optional[str] = Field(None, description="Invoice notes")
    terms_conditions: Optional[str] = Field(
        None, description="Terms and conditions")


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoices"""
    customer_id: str = Field(..., description="Customer ID is required")
    customer_name: str = Field(..., description="Customer name is required")
    due_date: date = Field(..., description="Due date is required")


class InvoiceUpdate(InvoiceBase):
    """Schema for updating invoices"""
    pass


class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================================
# Payment Schemas
# =====================================================================

class PaymentBase(BaseModel):
    """Base schema for payments"""
    payment_number: Optional[str] = Field(
        None, max_length=50, description="Payment number")
    customer_id: Optional[str] = Field(
        None, max_length=128, description="Customer ID")
    invoice_id: Optional[int] = Field(None, description="Invoice ID")
    amount: Optional[Decimal] = Field(
        Decimal('0.00'), description="Payment amount")
    currency: Optional[str] = Field(
        "CNY", max_length=3, description="Currency code")
    payment_method: Optional[str] = Field(
        None, max_length=50, description="Payment method")
    payment_date: Optional[datetime] = Field(None, description="Payment date")
    transaction_id: Optional[str] = Field(
        None, max_length=255, description="Transaction ID")
    reference_number: Optional[str] = Field(
        None, max_length=255, description="Reference number")
    gateway: Optional[str] = Field(
        None, max_length=100, description="Payment gateway")
    status: Optional[PaymentStatus] = Field(
        PaymentStatus.PENDING, description="Payment status")
    description: Optional[str] = Field(None, description="Payment description")
    notes: Optional[str] = Field(None, description="Payment notes")


class PaymentCreate(PaymentBase):
    """Schema for creating payments"""
    customer_id: str = Field(..., description="Customer ID is required")
    amount: Decimal = Field(..., gt=0,
                            description="Amount must be greater than 0")
    payment_method: str = Field(..., description="Payment method is required")


class PaymentUpdate(PaymentBase):
    """Schema for updating payments"""
    pass


class PaymentResponse(PaymentBase):
    """Schema for payment responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================================
# Refund Schemas
# =====================================================================

class RefundBase(BaseModel):
    """Base schema for refunds"""
    refund_number: Optional[str] = Field(
        None, max_length=50, description="Refund number")
    payment_id: Optional[int] = Field(None, description="Payment ID")
    customer_id: Optional[str] = Field(
        None, max_length=128, description="Customer ID")
    amount: Optional[Decimal] = Field(
        Decimal('0.00'), description="Refund amount")
    currency: Optional[str] = Field(
        "CNY", max_length=3, description="Currency code")
    refund_date: Optional[datetime] = Field(None, description="Refund date")
    reason: Optional[str] = Field(
        None, max_length=255, description="Refund reason")
    status: Optional[str] = Field("pending", description="Refund status")
    transaction_id: Optional[str] = Field(
        None, max_length=255, description="Transaction ID")
    gateway: Optional[str] = Field(
        None, max_length=100, description="Payment gateway")
    notes: Optional[str] = Field(None, description="Refund notes")


class RefundCreate(RefundBase):
    """Schema for creating refunds"""
    payment_id: int = Field(..., description="Payment ID is required")
    customer_id: str = Field(..., description="Customer ID is required")
    amount: Decimal = Field(..., gt=0,
                            description="Amount must be greater than 0")
    reason: str = Field(..., description="Refund reason is required")


class RefundUpdate(RefundBase):
    """Schema for updating refunds"""
    pass


class RefundResponse(RefundBase):
    """Schema for refund responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================================
# Payment Type Schemas
# =====================================================================

class PaymentTypeBase(BaseModel):
    """Base schema for payment types"""
    name: Optional[str] = Field(
        None, max_length=100, description="Payment type name")
    display_name: Optional[str] = Field(
        None, max_length=100, description="Display name")
    code: Optional[str] = Field(
        None, max_length=20, description="Payment type code")
    is_active: Optional[bool] = Field(
        True, description="Is payment type active")
    is_online: Optional[bool] = Field(False, description="Is online payment")
    requires_gateway: Optional[bool] = Field(
        False, description="Requires payment gateway")
    gateway_name: Optional[str] = Field(
        None, max_length=100, description="Gateway name")
    gateway_config: Optional[str] = Field(
        None, description="Gateway configuration (JSON)")
    fixed_fee: Optional[Decimal] = Field(
        Decimal('0.00'), description="Fixed fee")
    percentage_fee: Optional[Decimal] = Field(
        Decimal('0.00'), description="Percentage fee")
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum amount")
    description: Optional[str] = Field(
        None, description="Payment type description")
    icon: Optional[str] = Field(
        None, max_length=100, description="Payment type icon")
    sort_order: Optional[int] = Field(0, description="Sort order")


class PaymentTypeCreate(PaymentTypeBase):
    """Schema for creating payment types"""
    name: str = Field(..., description="Payment type name is required")
    display_name: str = Field(..., description="Display name is required")
    code: str = Field(..., description="Payment type code is required")


class PaymentTypeUpdate(PaymentTypeBase):
    """Schema for updating payment types"""
    pass


class PaymentTypeResponse(PaymentTypeBase):
    """Schema for payment type responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================================
# POS Schemas
# =====================================================================

class POSBase(BaseModel):
    """Base schema for POS terminals"""
    name: Optional[str] = Field(
        None, max_length=100, description="Terminal name")
    serial_number: Optional[str] = Field(
        None, max_length=100, description="Serial number")
    model: Optional[str] = Field(
        None, max_length=100, description="Terminal model")
    manufacturer: Optional[str] = Field(
        None, max_length=100, description="Manufacturer")
    location_id: Optional[str] = Field(
        None, max_length=50, description="Location ID")
    location_name: Optional[str] = Field(
        None, max_length=255, description="Location name")
    assigned_user: Optional[str] = Field(
        None, max_length=128, description="Assigned user")
    ip_address: Optional[str] = Field(
        None, max_length=45, description="IP address")
    mac_address: Optional[str] = Field(
        None, max_length=17, description="MAC address")
    network_config: Optional[str] = Field(
        None, description="Network configuration (JSON)")
    status: Optional[str] = Field("active", description="Terminal status")
    last_heartbeat: Optional[datetime] = Field(
        None, description="Last heartbeat")
    last_transaction: Optional[datetime] = Field(
        None, description="Last transaction")
    supports_contactless: Optional[bool] = Field(
        False, description="Supports contactless payments")
    supports_chip: Optional[bool] = Field(
        False, description="Supports chip cards")
    supports_pin: Optional[bool] = Field(
        False, description="Supports PIN entry")
    supports_receipt_print: Optional[bool] = Field(
        False, description="Supports receipt printing")
    terminal_config: Optional[str] = Field(
        None, description="Terminal configuration (JSON)")
    firmware_version: Optional[str] = Field(
        None, max_length=50, description="Firmware version")
    description: Optional[str] = Field(
        None, description="Terminal description")
    notes: Optional[str] = Field(None, description="Terminal notes")


class POSCreate(POSBase):
    """Schema for creating POS terminals"""
    name: str = Field(..., description="Terminal name is required")
    serial_number: str = Field(..., description="Serial number is required")


class POSUpdate(POSBase):
    """Schema for updating POS terminals"""
    pass


class POSResponse(POSBase):
    """Schema for POS terminal responses"""
    id: int
    creationdate: Optional[datetime] = None
    creationby: Optional[str] = None
    updatedate: Optional[datetime] = None
    updateby: Optional[str] = None

    class Config:
        from_attributes = True


# Paginated response schema
class PaginatedResponse(BaseModel):
    """Generic paginated response schema"""
    data: List[Any] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
