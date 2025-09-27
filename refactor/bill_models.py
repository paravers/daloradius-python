"""
daloRADIUS Billing Module Data Models

This module contains Pydantic models for all data structures used in the Billing functionality.
These models represent the data structures from the PHP files in app/operators/bill-*.php files.

Models follow SOLID principles:
- SRP: Each model has a single responsibility 
- OCP: Models are extensible through inheritance
- DIP: Models depend on abstractions (base classes)
- ISP: Interfaces are segregated by functionality
- LSP: Derived models can replace base models

Database Tables Covered:
- dalobillinginvoice: Invoice records
- dalobillinginvoiceitems: Invoice line items
- dalobillinginvoicestatus: Invoice status types
- dalobillinginvoicetype: Invoice type definitions
- dalopayments: Payment records
- dalopaymenttypes: Payment type definitions
- dalobillingplans: Billing plan definitions
- dalobillingrates: Rate definitions for billing
- dalouserbillinfo: User billing information
- dalobillingplansprofiles: Plan-profile associations
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from ipaddress import IPv4Address


class BaseBillModel(BaseModel):
    """Base model for all billing-related data structures"""
    
    class Config:
        # Enable ORM mode for database integration
        orm_mode = True
        # Use enum values instead of enum names
        use_enum_values = True
        # Allow population by field name or alias
        allow_population_by_field_name = True
        # Validate assignments
        validate_assignment = True


class SortOrder(str, Enum):
    """Sort order enumeration - follows ISP principle"""
    ASC = "asc"
    DESC = "desc"


class BillingStatus(str, Enum):
    """Billing status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class PlanTimeType(str, Enum):
    """Plan time type enumeration - from PHP validation"""
    ACCUMULATIVE = "Accumulative"
    TIME_TO_FINISH = "Time-To-Finish"


class PlanRecurringPeriod(str, Enum):
    """Plan recurring period enumeration - from PHP validation"""
    NEVER = "Never"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    SEMI_YEARLY = "Semi-Yearly"
    YEARLY = "Yearly"


class PlanRecurringBillingSchedule(str, Enum):
    """Plan recurring billing schedule enumeration - from PHP validation"""
    FIXED = "Fixed"
    ANNIVERSARY = "Anniversary"


class TimeUnit(str, Enum):
    """Time unit enumeration for rates - from PHP validation"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class BillAction(str, Enum):
    """Bill action enumeration for history - from PHP validation"""
    ANY = "Any"
    REFILL_SESSION_TIME = "Refill Session Time"
    REFILL_SESSION_TRAFFIC = "Refill Session Traffic"


class VendorType(str, Enum):
    """Merchant vendor types - from validation.php"""
    ANY = "Any"
    TWOCHECKOUT = "2Checkout"
    PAYPAL = "PayPal"


class PaymentStatus(str, Enum):
    """External payment status values - from validation.php"""
    ANY = "Any"
    COMPLETED = "Completed"
    DENIED = "Denied"
    EXPIRED = "Expired"
    FAILED = "Failed"
    IN_PROGRESS = "In-Progress"
    PENDING = "Pending"
    PROCESSED = "Processed"
    REFUNDED = "Refunded"
    REVERSED = "Reversed"
    CANCELED_REVERSAL = "Canceled-Reversal"
    VOIDED = "Voided"


# =====================================================================
# Core Invoice Models - SRP: Single responsibility per model
# =====================================================================

class InvoiceStatus(BaseBillModel):
    """Invoice status model - maps to dalobillinginvoicestatus table"""
    id: int = Field(..., description="Status ID")
    value: str = Field(..., description="Status name")
    
    
class InvoiceType(BaseBillModel):
    """Invoice type model - maps to dalobillinginvoicetype table"""
    id: int = Field(..., description="Type ID")
    value: str = Field(..., description="Type name")


class Invoice(BaseBillModel):
    """
    Core invoice model - maps to dalobillinginvoice table
    """
    id: Optional[int] = Field(None, description="Invoice ID")
    user_id: int = Field(..., description="User ID from dalouserbillinfo")
    date: date = Field(..., description="Invoice date")
    status_id: int = Field(..., description="Invoice status ID")
    type_id: int = Field(..., description="Invoice type ID")
    notes: Optional[str] = Field(None, description="Invoice notes")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        """Parse date from string if needed"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Invalid date format, expected YYYY-MM-DD')
        return v


class InvoiceItem(BaseBillModel):
    """
    Invoice item model - maps to dalobillinginvoiceitems table
    """
    id: Optional[int] = Field(None, description="Item ID")
    invoice_id: int = Field(..., description="Invoice ID")
    plan_id: int = Field(..., description="Plan ID")
    amount: Decimal = Field(..., description="Item amount")
    tax_amount: Decimal = Field(0, description="Tax amount")
    notes: Optional[str] = Field(None, description="Item notes")
    plan_name: Optional[str] = Field(None, alias="planName", description="Joined plan name from billing plans table")
    
    @validator('amount', 'tax_amount')
    def validate_amounts(cls, v):
        """Ensure amounts are non-negative"""
        if v < 0:
            raise ValueError('Amounts must be non-negative')
        return v


class InvoiceWithDetails(Invoice):
    """
    Extended invoice model with detailed information
    Follows OCP principle - extends base without modification
    Matches data structure from bill-invoice-edit.php SQL query
    """
    username: Optional[str] = Field(None, description="Username from dalouserbillinfo")
    contact_person: Optional[str] = Field(None, alias="contactperson", description="Contact person name")
    city: Optional[str] = Field(None, description="City from dalouserbillinfo")
    state: Optional[str] = Field(None, description="State from dalouserbillinfo")
    status_name: Optional[str] = Field(None, description="Status name from dalobillinginvoicestatus")
    type_name: Optional[str] = Field(None, description="Type name from dalobillinginvoicetype")
    total_billed: Decimal = Field(0, alias="totalbilled", description="Total billed amount")
    total_payed: Decimal = Field(0, alias="totalpayed", description="Total paid amount")
    balance: Decimal = Field(0, description="Outstanding balance")
    items: List[InvoiceItem] = Field(default_factory=list, description="Invoice items")
    
    @validator('balance', always=True)
    def calculate_balance(cls, v, values):
        """Calculate balance as total_billed - total_payed"""
        total_billed = values.get('total_billed', 0)
        total_payed = values.get('total_payed', 0)
        return total_billed - total_payed


# =====================================================================
# Payment Models - SRP: Single responsibility for payments
# =====================================================================

class PaymentType(BaseBillModel):
    """Payment type model - maps to dalopaymenttypes table"""
    id: int = Field(..., description="Payment type ID")
    value: str = Field(..., description="Payment type name")
    notes: Optional[str] = Field(None, description="Payment type notes")


class Payment(BaseBillModel):
    """
    Payment model - maps to dalopayments table
    Matches structure from bill-payments-new.php
    """
    id: Optional[int] = Field(None, description="Payment ID")
    invoice_id: int = Field(..., description="Invoice ID")
    amount: Decimal = Field(..., description="Payment amount")
    date: date = Field(..., description="Payment date")
    type_id: int = Field(..., description="Payment type ID")
    notes: Optional[str] = Field(None, description="Payment notes")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Ensure payment amount is positive"""
        if v <= 0:
            raise ValueError('Payment amount must be positive')
        return v
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        """Parse date from string if needed"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Invalid date format, expected YYYY-MM-DD')
        return v


class PaymentWithDetails(Payment):
    """
    Extended payment model with type information
    """
    type_name: Optional[str] = Field(None, description="Payment type name")
    invoice_date: Optional[date] = Field(None, description="Associated invoice date")
    username: Optional[str] = Field(None, description="Username from invoice")


# =====================================================================
# Billing Plans Models - SRP: Plan management
# =====================================================================

class BillingPlan(BaseBillModel):
    """
    Billing plan model - maps to dalobillingplans table
    Matches structure from bill-plans-new.php INSERT statement
    """
    id: Optional[int] = Field(None, description="Plan ID")
    plan_name: str = Field(..., alias="planName", description="Plan name")
    plan_id: Optional[str] = Field(None, alias="planId", description="Plan identifier")
    plan_type: Optional[str] = Field(None, alias="planType", description="Plan type")
    plan_time_type: PlanTimeType = Field(PlanTimeType.ACCUMULATIVE, alias="planTimeType", description="Time period type")
    plan_time_bank: Optional[str] = Field(None, alias="planTimeBank", description="Time allowance (stored as string)")
    plan_time_refill_cost: Optional[str] = Field(None, alias="planTimeRefillCost", description="Time refill cost (stored as string)")
    plan_bandwidth_up: Optional[str] = Field(None, alias="planBandwidthUp", description="Upload bandwidth limit (stored as string)")
    plan_bandwidth_down: Optional[str] = Field(None, alias="planBandwidthDown", description="Download bandwidth limit (stored as string)")
    plan_traffic_total: Optional[str] = Field(None, alias="planTrafficTotal", description="Total traffic allowance (stored as string)")
    plan_traffic_up: Optional[str] = Field(None, alias="planTrafficUp", description="Upload traffic allowance (stored as string)")
    plan_traffic_down: Optional[str] = Field(None, alias="planTrafficDown", description="Download traffic allowance (stored as string)")
    plan_traffic_refill_cost: Optional[str] = Field(None, alias="planTrafficRefillCost", description="Traffic refill cost (stored as string)")
    plan_recurring: bool = Field(True, alias="planRecurring", description="Is plan recurring")
    plan_recurring_period: PlanRecurringPeriod = Field(PlanRecurringPeriod.NEVER, alias="planRecurringPeriod", description="Recurring period")
    plan_recurring_billing_schedule: PlanRecurringBillingSchedule = Field(PlanRecurringBillingSchedule.FIXED, alias="planRecurringBillingSchedule", description="Billing schedule")
    plan_active: bool = Field(True, alias="planActive", description="Is plan active")
    plan_cost: Optional[str] = Field(None, alias="planCost", description="Plan cost (stored as string)")
    plan_setup_cost: Optional[str] = Field(None, alias="planSetupCost", description="Plan setup cost (stored as string)")
    plan_tax: Optional[str] = Field(None, alias="planTax", description="Plan tax (stored as string)")
    plan_currency: Optional[str] = Field(None, alias="planCurrency", description="Plan currency")
    plan_group: Optional[str] = Field(None, alias="planGroup", description="Plan group")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")
    
    @validator('plan_recurring', pre=True)
    def parse_plan_recurring(cls, v):
        """Parse plan_recurring from yes/no to boolean"""
        if isinstance(v, str):
            return v.lower() == 'yes'
        return v
    
    @validator('plan_active', pre=True) 
    def parse_plan_active(cls, v):
        """Parse plan_active from yes/no to boolean"""
        if isinstance(v, str):
            return v.lower() == 'yes'
        return v


# =====================================================================
# Rate Models - SRP: Rate management
# =====================================================================

class BillingRate(BaseBillModel):
    """
    Billing rate model - maps to dalobillingrates table
    Matches structure from bill-rates-new.php
    """
    id: Optional[int] = Field(None, description="Rate ID")
    rate_name: str = Field(..., alias="ratename", description="Rate name")
    rate_type: str = Field(..., alias="ratetype", description="Rate type (e.g., '1/minute')")
    rate_cost: int = Field(..., alias="ratecost", description="Rate cost (stored as integer)")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")
    
    @validator('rate_cost')
    def validate_rate_cost(cls, v):
        """Ensure rate cost is positive"""
        if v <= 0:
            raise ValueError('Rate cost must be positive')
        return v
    
    @validator('rate_type')
    def validate_rate_type(cls, v):
        """Validate rate type format (number/timeunit)"""
        import re
        if not re.match(r'^\d+/(second|minute|hour|day|week|month|year)$', v):
            raise ValueError('Rate type must be in format "number/timeunit"')
        return v


class RateTypeComponents(BaseBillModel):
    """
    Rate type components for creating new rates
    """
    rate_type_num: int = Field(..., alias="ratetypenum", description="Rate type number")
    rate_type_time: TimeUnit = Field(..., alias="ratetypetime", description="Rate type time unit")
    
    @validator('rate_type_num')
    def validate_rate_type_num(cls, v):
        """Ensure rate type number is positive"""
        if v <= 0:
            raise ValueError('Rate type number must be positive')
        return v


# =====================================================================
# User Billing Information Models - SRP: User billing data
# =====================================================================

class UserBillInfo(BaseBillModel):
    """
    User billing information model - maps to dalouserbillinfo table
    Complete structure from bill-pos-new.php INSERT statement
    """
    id: Optional[int] = Field(None, description="User billing ID")
    plan_name: Optional[str] = Field(None, alias="planname", description="Plan name")
    username: str = Field(..., description="Username")
    contact_person: Optional[str] = Field(None, alias="contactperson", description="Contact person name")
    company: Optional[str] = Field(None, description="Company name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country")
    zip: Optional[str] = Field(None, description="ZIP/Postal code")
    payment_method: Optional[str] = Field(None, alias="paymentmethod", description="Payment method")
    cash: Optional[str] = Field(None, description="Cash balance (stored as string)")
    creditcard_name: Optional[str] = Field(None, alias="creditcardname", description="Credit card holder name")
    creditcard_number: Optional[str] = Field(None, alias="creditcardnumber", description="Credit card number")
    creditcard_verification: Optional[str] = Field(None, alias="creditcardverification", description="Credit card CVV")
    creditcard_type: Optional[str] = Field(None, alias="creditcardtype", description="Credit card type")
    creditcard_exp: Optional[str] = Field(None, alias="creditcardexp", description="Credit card expiration")
    notes: Optional[str] = Field(None, description="Billing notes")
    change_userbillinfo: Optional[str] = Field(None, alias="changeuserbillinfo", description="Change billing info flag")
    lead: Optional[str] = Field(None, description="Lead information")
    coupon: Optional[str] = Field(None, description="Coupon code")
    ordertaker: Optional[str] = Field(None, description="Order taker")
    billstatus: Optional[str] = Field(None, description="Bill status")
    lastbill: Optional[str] = Field(None, description="Last bill date")
    nextbill: Optional[str] = Field(None, description="Next bill date")
    nextinvoicedue: Optional[str] = Field(None, description="Next invoice due date")
    billdue: Optional[str] = Field(None, description="Bill due flag")
    postalinvoice: Optional[str] = Field(None, description="Postal invoice flag")
    faxinvoice: Optional[str] = Field(None, description="Fax invoice flag")
    emailinvoice: Optional[str] = Field(None, description="Email invoice flag")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation"""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


# =====================================================================
# Point of Sale Models - SRP: POS functionality
# =====================================================================

class PointOfSaleInfo(BaseBillModel):
    """
    Point of Sale information combining user billing and plan data
    """
    username: str = Field(..., description="Username")
    plan_name: Optional[str] = Field(None, description="Current plan name")
    contact_person: Optional[str] = Field(None, description="Contact person")
    cash_balance: Optional[Decimal] = Field(None, description="Current cash balance")
    credit_balance: Optional[Decimal] = Field(None, description="Current credit balance")
    last_bill_date: Optional[date] = Field(None, description="Last billing date")
    next_bill_date: Optional[date] = Field(None, description="Next billing date")
    billing_enabled: bool = Field(True, description="Is billing enabled")
    active_invoices: int = Field(0, description="Number of active invoices")
    total_outstanding: Decimal = Field(0, description="Total outstanding amount")


# =====================================================================
# History and Merchant Models - SRP: Transaction history
# =====================================================================

class BillingHistory(BaseBillModel):
    """
    Billing history model - maps to dalobillinghistory table
    Based on bill-history-query.php analysis
    """
    id: Optional[int] = Field(None, description="History record ID")
    username: str = Field(..., description="Username")
    billaction: BillAction = Field(..., description="Billing action type")
    billdate: Optional[datetime] = Field(None, description="Billing date")
    amount: Optional[str] = Field(None, description="Amount involved (stored as string)")
    description: Optional[str] = Field(None, description="Event description")
    operator: Optional[str] = Field(None, description="Operator who performed the action")


class MerchantTransaction(BaseBillModel):
    """
    Merchant transaction model for external payment processing
    """
    id: Optional[int] = Field(None, description="Transaction ID")
    invoice_id: Optional[int] = Field(None, description="Associated invoice ID")
    username: str = Field(..., description="Username")
    transaction_id: str = Field(..., description="External transaction ID")
    merchant: str = Field(..., description="Merchant/Payment processor name")
    amount: Decimal = Field(..., description="Transaction amount")
    currency: str = Field("USD", description="Transaction currency")
    status: str = Field(..., description="Transaction status")
    transaction_date: datetime = Field(..., description="Transaction timestamp")
    notes: Optional[str] = Field(None, description="Transaction notes")
    payer_email: Optional[str] = Field(None, description="Payer email (for PayPal-like processors)")
    payment_status: Optional[str] = Field(None, description="Processor reported payment status")
    vendor_type: Optional[str] = Field(None, description="Vendor type (PayPal, 2Checkout, etc.)")

class Merchant(BaseBillModel):
    """Merchant record model - maps to dalobillingmerchant (inferred from bill-merchant-transactions.php)"""
    id: Optional[int] = Field(None, description="Merchant record ID")
    vendor_type: Optional[VendorType] = Field(None, description="Vendor type")
    payer_email: Optional[str] = Field(None, description="Payer email / account email")
    payment_status: Optional[PaymentStatus] = Field(None, description="Current payment status")
    payment_date: Optional[date] = Field(None, description="Payment date")
    amount: Optional[str] = Field(None, description="Amount as stored (string/raw)")
    currency: Optional[str] = Field(None, description="Currency code")
    payment_fee: Optional[str] = Field(None, description="Processor fee (raw)")
    payment_total: Optional[str] = Field(None, description="Payment total including fee (raw)")
    first_name: Optional[str] = Field(None, description="Payer first name")
    last_name: Optional[str] = Field(None, description="Payer last name")
    payer_address_country: Optional[str] = Field(None, description="Payer country")
    payer_address_city: Optional[str] = Field(None, description="Payer city")
    payer_address_state: Optional[str] = Field(None, description="Payer state")
    creation_date: Optional[datetime] = Field(None, alias="creationdate", description="Creation timestamp")
    creation_by: Optional[str] = Field(None, alias="creationby", description="Created by operator")
    update_date: Optional[datetime] = Field(None, alias="updatedate", description="Last update timestamp")
    update_by: Optional[str] = Field(None, alias="updateby", description="Last updated by operator")


# =====================================================================
# Query Parameter Models - ISP: Interface segregation by query type
# =====================================================================

class BaseQueryParams(BaseBillModel):
    """Base query parameters - follows ISP principle"""
    order_by: str = Field("id", description="Field to order by")
    order_type: SortOrder = Field(SortOrder.DESC, description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Records per page")


class InvoiceQueryParams(BaseQueryParams):
    """Invoice-specific query parameters"""
    user_id: Optional[int] = Field(None, description="User ID to filter by")
    username: Optional[str] = Field(None, description="Username to filter by")
    invoice_status_id: Optional[int] = Field(None, description="Invoice status to filter by")
    date_from: Optional[date] = Field(None, description="Start date filter")
    date_to: Optional[date] = Field(None, description="End date filter")


class PaymentQueryParams(BaseQueryParams):
    """Payment-specific query parameters"""
    invoice_id: Optional[int] = Field(None, description="Invoice ID to filter by")
    payment_type_id: Optional[int] = Field(None, description="Payment type to filter by")
    date_from: Optional[date] = Field(None, description="Start date filter")
    date_to: Optional[date] = Field(None, description="End date filter")


class PlanQueryParams(BaseQueryParams):
    """Plan-specific query parameters"""
    plan_active: Optional[bool] = Field(None, description="Filter by plan active status")
    plan_type: Optional[str] = Field(None, description="Plan type to filter by")


class RateQueryParams(BaseQueryParams):
    """Rate-specific query parameters"""
    rate_name: Optional[str] = Field(None, description="Rate name to filter by")


# =====================================================================
# Response Models - SRP: Single responsibility for different responses
# =====================================================================

class PaginationInfo(BaseBillModel):
    """Pagination information model"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Records per page")
    total_pages: int = Field(..., description="Total number of pages")
    total_records: int = Field(..., description="Total number of records")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class BaseListResponse(BaseBillModel):
    """Base response model for list endpoints"""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field("", description="Response message")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")


class InvoiceListResponse(BaseListResponse):
    """Response model for invoice lists"""
    invoices: List[InvoiceWithDetails] = Field([], description="List of invoices")


class PaymentListResponse(BaseListResponse):
    """Response model for payment lists"""
    payments: List[PaymentWithDetails] = Field([], description="List of payments")


class PlanListResponse(BaseListResponse):
    """Response model for plan lists"""
    plans: List[BillingPlan] = Field([], description="List of billing plans")


class RateListResponse(BaseListResponse):
    """Response model for rate lists"""
    rates: List[BillingRate] = Field([], description="List of billing rates")


# =====================================================================
# Operation Models - SRP: CRUD operations
# =====================================================================

class InvoiceCreateRequest(BaseBillModel):
    """Request model for creating invoices"""
    user_id: int = Field(..., description="User ID")
    invoice_type_id: int = Field(..., description="Invoice type ID")
    invoice_status_id: int = Field(1, description="Invoice status ID")
    invoice_date: date = Field(default_factory=date.today, description="Invoice date")
    invoice_notes: Optional[str] = Field(None, description="Invoice notes")
    items: List[Dict[str, Any]] = Field([], description="Invoice items data")


class PaymentCreateRequest(BaseBillModel):
    """Request model for creating payments"""
    payment_invoice_id: int = Field(..., description="Invoice ID")
    payment_type_id: int = Field(..., description="Payment type ID")
    payment_amount: Decimal = Field(..., description="Payment amount")
    payment_date: date = Field(default_factory=date.today, description="Payment date")
    payment_notes: Optional[str] = Field(None, description="Payment notes")


class PlanCreateRequest(BaseBillModel):
    """Request model for creating billing plans"""
    plan_name: str = Field(..., description="Plan name")
    plan_type: Optional[str] = Field(None, description="Plan type")
    plan_cost: Optional[Decimal] = Field(None, description="Plan cost")
    plan_active: bool = Field(True, description="Is plan active")
    # Include all other plan fields as needed


class RateCreateRequest(BaseBillModel):
    """Request model for creating rates"""
    rate_name: str = Field(..., description="Rate name")
    rate_type_num: int = Field(..., description="Rate type number")
    rate_type_time: TimeUnit = Field(..., description="Rate type time unit")
    rate_cost: Decimal = Field(..., description="Rate cost")


# =====================================================================
# Error Models - SRP: Dedicated error handling
# =====================================================================

class ValidationError(BaseBillModel):
    """Validation error model"""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")


class ErrorResponse(BaseBillModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    errors: Optional[List[ValidationError]] = Field(None, description="List of validation errors")
    error_code: Optional[str] = Field(None, description="Error code")


# =====================================================================
# Model Registry - DIP: Dependency inversion for model factory
# =====================================================================

class BillModelRegistry:
    """
    Registry for all billing models
    Follows DIP principle - provides abstraction for model creation
    """
    
    _models = {
        # Core models
        'invoice': Invoice,
        'invoice_with_details': InvoiceWithDetails,
        'invoice_item': InvoiceItem,
        'invoice_status': InvoiceStatus,
        'invoice_type': InvoiceType,
        'payment': Payment,
        'payment_with_details': PaymentWithDetails,
        'payment_type': PaymentType,
        'billing_plan': BillingPlan,
        'billing_rate': BillingRate,
        'rate_type_components': RateTypeComponents,
        'user_bill_info': UserBillInfo,
        'point_of_sale_info': PointOfSaleInfo,
        'billing_history': BillingHistory,
        'merchant_transaction': MerchantTransaction,
        
        # Query parameter models
        'invoice_query_params': InvoiceQueryParams,
        'payment_query_params': PaymentQueryParams,
        'plan_query_params': PlanQueryParams,
        'rate_query_params': RateQueryParams,
        
        # Response models
        'invoice_list_response': InvoiceListResponse,
        'payment_list_response': PaymentListResponse,
        'plan_list_response': PlanListResponse,
        'rate_list_response': RateListResponse,
        
        # Operation models
        'invoice_create_request': InvoiceCreateRequest,
        'payment_create_request': PaymentCreateRequest,
        'plan_create_request': PlanCreateRequest,
        'rate_create_request': RateCreateRequest,
        
        # Error models
        'error_response': ErrorResponse,
        'validation_error': ValidationError,
    }
    
    @classmethod
    def get_model(cls, model_name: str) -> BaseBillModel:
        """Get model class by name - follows DIP principle"""
        if model_name not in cls._models:
            raise ValueError(f"Unknown model: {model_name}")
        return cls._models[model_name]
    
    @classmethod
    def list_models(cls) -> List[str]:
        """List all available model names"""
        return list(cls._models.keys())
    
    @classmethod
    def register_model(cls, name: str, model_class: type):
        """Register a new model - follows OCP principle"""
        if not issubclass(model_class, BaseBillModel):
            raise ValueError("Model must inherit from BaseBillModel")
        cls._models[name] = model_class


# Export all models for easy importing
__all__ = [
    # Base classes
    'BaseBillModel',
    
    # Enums
    'SortOrder',
    'BillingStatus',
    'PlanTimeType',
    'PlanRecurringPeriod',
    'PlanRecurringBillingSchedule',
    'TimeUnit',
    
    # Core models
    'Invoice',
    'InvoiceWithDetails',
    'InvoiceItem',
    'InvoiceStatus',
    'InvoiceType',
    'Payment',
    'PaymentWithDetails',
    'PaymentType',
    'BillingPlan',
    'BillingRate',
    'RateTypeComponents',
    'UserBillInfo',
    'PointOfSaleInfo',
    'BillingHistory',
    'MerchantTransaction',
    
    # Query parameter models
    'BaseQueryParams',
    'InvoiceQueryParams',
    'PaymentQueryParams',
    'PlanQueryParams',
    'RateQueryParams',
    
    # Response models
    'PaginationInfo',
    'BaseListResponse',
    'InvoiceListResponse',
    'PaymentListResponse',
    'PlanListResponse',
    'RateListResponse',
    
    # Operation models
    'InvoiceCreateRequest',
    'PaymentCreateRequest',
    'PlanCreateRequest',
    'RateCreateRequest',
    
    # Error models
    'ValidationError',
    'ErrorResponse',
    
    # Registry
    'BillModelRegistry',
]