"""
Billing System Models

This module contains SQLAlchemy models for the billing system,
including plans, history, merchant transactions, and rates.
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Text, Numeric,
    Boolean, ForeignKey, Index
)
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, LegacyBaseModel


class BillingPlan(BaseModel):
    """
    Billing plans
    Maps to billing_plans table
    """
    __tablename__ = "billing_plans"
    __table_args__ = (
        Index('idx_billing_plans_active', 'planActive'),
        {'extend_existing': True}
    )

    # Plan identification
    planName = Column(String(128), nullable=True, index=True)
    planId = Column(String(128), nullable=True)
    planType = Column(String(128), nullable=True)

    # Time-based settings
    planTimeBank = Column(String(128), nullable=True)
    planTimeType = Column(String(128), nullable=True)
    planTimeRefillCost = Column(String(128), nullable=True)

    # Bandwidth settings
    planBandwidthUp = Column(String(128), nullable=True)
    planBandwidthDown = Column(String(128), nullable=True)

    # Traffic settings
    planTrafficTotal = Column(String(128), nullable=True)
    planTrafficUp = Column(String(128), nullable=True)
    planTrafficDown = Column(String(128), nullable=True)
    planTrafficRefillCost = Column(String(128), nullable=True)

    # Recurring billing
    planRecurring = Column(String(128), nullable=True)
    planRecurringPeriod = Column(String(128), nullable=True)
    planRecurringBillingSchedule = Column(
        String(128), nullable=False, default='Fixed')

    # Pricing
    planCost = Column(String(128), nullable=True)
    planSetupCost = Column(String(128), nullable=True)
    planTax = Column(String(128), nullable=True)
    planCurrency = Column(String(128), nullable=True)

    # Group and status
    planGroup = Column(String(128), nullable=True)
    planActive = Column(String(32), nullable=False, default='yes')

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False)
    updateby = Column(String(128), nullable=True)

    # Table args moved to class declaration


class BillingHistory(BaseModel):
    """
    Billing transaction history
    Maps to billing_history table
    """
    __tablename__ = "billing_history"
    __table_args__ = {'extend_existing': True}

    username = Column(String(128), nullable=True, index=True)
    planId = Column(Integer, nullable=True, index=True)
    billAmount = Column(String(200), nullable=True)
    billAction = Column(String(128), nullable=False, default='Unavailable')
    billPerformer = Column(String(200), nullable=True)
    billReason = Column(String(200), nullable=True)

    # Payment details
    paymentmethod = Column(String(200), nullable=True)
    cash = Column(String(200), nullable=True)
    creditcardname = Column(String(200), nullable=True)
    creditcardnumber = Column(String(200), nullable=True)
    creditcardverification = Column(String(200), nullable=True)
    creditcardtype = Column(String(200), nullable=True)
    creditcardexp = Column(String(200), nullable=True)

    # Discounts and promotions
    coupon = Column(String(200), nullable=True)
    discount = Column(String(200), nullable=True)
    notes = Column(String(200), nullable=True)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False)
    updateby = Column(String(128), nullable=True)


class BillingMerchant(BaseModel):
    """
    Merchant transaction details
    Maps to billing_merchant table
    """
    __tablename__ = "billing_merchant"
    __table_args__ = {'extend_existing': True}

    # User credentials
    username = Column(String(128), nullable=False, index=True)
    password = Column(String(128), nullable=False)
    mac = Column(String(200), nullable=False)
    pin = Column(String(200), nullable=False)

    # Transaction details
    txnId = Column(String(200), nullable=False, index=True)
    planName = Column(String(128), nullable=False)
    planId = Column(Integer, nullable=False)
    quantity = Column(String(200), nullable=False)

    # Business details
    business_email = Column(String(200), nullable=False)
    business_id = Column(String(200), nullable=False)
    txn_type = Column(String(200), nullable=False)
    txn_id = Column(String(200), nullable=False)

    # Payment details
    payment_type = Column(String(200), nullable=False)
    payment_tax = Column(String(200), nullable=False)
    payment_cost = Column(String(200), nullable=False)
    payment_fee = Column(String(200), nullable=False)
    payment_total = Column(String(200), nullable=False)
    payment_currency = Column(String(200), nullable=False)

    # Payer information
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    payer_email = Column(String(200), nullable=False)

    # Address information
    payer_address_name = Column(String(200), nullable=False)
    payer_address_street = Column(String(200), nullable=False)
    payer_address_country = Column(String(200), nullable=False)
    payer_address_country_code = Column(String(200), nullable=False)
    payer_address_city = Column(String(200), nullable=False)
    payer_address_state = Column(String(200), nullable=False)
    payer_address_zip = Column(String(200), nullable=False)

    # Payment status
    payment_date = Column(DateTime, nullable=False)
    payment_status = Column(String(200), nullable=False)
    pending_reason = Column(String(200), nullable=False)
    reason_code = Column(String(200), nullable=False)
    receipt_ID = Column(String(200), nullable=False)
    payment_address_status = Column(String(200), nullable=False)
    vendor_type = Column(String(200), nullable=False)
    payer_status = Column(String(200), nullable=False)


class BillingRate(BaseModel):
    """
    Billing rates
    Maps to billing_rates table
    """
    __tablename__ = "billing_rates"
    __table_args__ = {'extend_existing': True}

    rateName = Column(String(128), nullable=False, index=True)
    rateType = Column(String(128), nullable=False)
    rateCost = Column(Integer, nullable=False, default=0)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False)
    updateby = Column(String(128), nullable=True)


class BillingPlanProfile(BaseModel):
    """
    Billing plan profiles mapping
    Maps to billing_plans_profiles table
    """
    __tablename__ = "billing_plans_profiles"
    __table_args__ = {'extend_existing': True}

    plan_name = Column(String(128), nullable=False)
    profile_name = Column(String(256), nullable=True)


class Invoice(BaseModel):
    """
    Invoice model for billing system
    Maps to invoices table
    """
    __tablename__ = "invoices"
    __table_args__ = (
        Index('idx_invoices_number', 'invoice_number'),
        Index('idx_invoices_customer', 'customer_id'),
        Index('idx_invoices_status', 'status'),
        Index('idx_invoices_due_date', 'due_date'),
        {'extend_existing': True}
    )

    # Invoice identification
    invoice_number = Column(String(50), unique=True,
                            nullable=False, index=True)
    customer_id = Column(String(128), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    customer_address = Column(Text, nullable=True)

    # Financial details
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default='CNY')

    # Status and dates
    # draft, sent, paid, overdue, cancelled
    status = Column(String(50), nullable=False, default='draft')
    issue_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)

    # Description and notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False, default=datetime.utcnow)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False, default=datetime.utcnow)
    updateby = Column(String(128), nullable=True)


class Payment(BaseModel):
    """
    Payment model for billing system  
    Maps to payments table
    """
    __tablename__ = "payments"
    __table_args__ = (
        Index('idx_payments_customer', 'customer_id'),
        Index('idx_payments_invoice', 'invoice_id'),
        Index('idx_payments_status', 'status'),
        Index('idx_payments_date', 'payment_date'),
        {'extend_existing': True}
    )

    # Payment identification
    payment_number = Column(String(50), unique=True,
                            nullable=False, index=True)
    customer_id = Column(String(128), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='CNY')
    # cash, card, bank_transfer, alipay, wechat, etc.
    payment_method = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Transaction details
    transaction_id = Column(String(255), nullable=True)
    reference_number = Column(String(255), nullable=True)
    gateway = Column(String(100), nullable=True)  # Payment gateway used

    # Status tracking
    # pending, completed, failed, refunded
    status = Column(String(50), nullable=False, default='pending')

    # Additional information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False, default=datetime.utcnow)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False, default=datetime.utcnow)
    updateby = Column(String(128), nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")


class Refund(BaseModel):
    """
    Refund model for billing system
    Maps to refunds table
    """
    __tablename__ = "refunds"
    __table_args__ = (
        Index('idx_refunds_payment', 'payment_id'),
        Index('idx_refunds_customer', 'customer_id'),
        Index('idx_refunds_status', 'status'),
        Index('idx_refunds_date', 'refund_date'),
        {'extend_existing': True}
    )

    # Refund identification
    refund_number = Column(String(50), unique=True, nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    customer_id = Column(String(128), nullable=False, index=True)

    # Refund details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='CNY')
    refund_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Refund reason and status
    reason = Column(String(255), nullable=False)
    # pending, processed, failed
    status = Column(String(50), nullable=False, default='pending')

    # Transaction details
    transaction_id = Column(String(255), nullable=True)
    gateway = Column(String(100), nullable=True)

    # Additional information
    notes = Column(Text, nullable=True)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False, default=datetime.utcnow)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False, default=datetime.utcnow)
    updateby = Column(String(128), nullable=True)

    # Relationships
    payment = relationship("Payment", back_populates="refunds")


class PaymentType(BaseModel):
    """
    Payment types configuration
    Maps to payment_types table
    """
    __tablename__ = "payment_types"
    __table_args__ = (
        Index('idx_payment_types_name', 'name'),
        Index('idx_payment_types_active', 'is_active'),
        {'extend_existing': True}
    )

    # Type identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)

    # Configuration
    is_active = Column(Boolean, nullable=False, default=True)
    is_online = Column(Boolean, nullable=False, default=False)
    requires_gateway = Column(Boolean, nullable=False, default=False)

    # Gateway settings
    gateway_name = Column(String(100), nullable=True)
    gateway_config = Column(Text, nullable=True)  # JSON configuration

    # Fees and limits
    fixed_fee = Column(Numeric(10, 2), nullable=False, default=0)
    # 0.0000 to 1.0000 (0% to 100%)
    percentage_fee = Column(Numeric(5, 4), nullable=False, default=0)
    min_amount = Column(Numeric(10, 2), nullable=True)
    max_amount = Column(Numeric(10, 2), nullable=True)

    # Display and sorting
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False, default=datetime.utcnow)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False, default=datetime.utcnow)
    updateby = Column(String(128), nullable=True)


class POS(BaseModel):
    """
    POS (Point of Sale) terminals management
    Maps to pos_terminals table
    """
    __tablename__ = "pos_terminals"
    __table_args__ = (
        Index('idx_pos_serial', 'serial_number'),
        Index('idx_pos_location', 'location_id'),
        Index('idx_pos_status', 'status'),
        {'extend_existing': True}
    )

    # Terminal identification
    name = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True,
                           nullable=False, index=True)
    model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)

    # Location and assignment
    location_id = Column(String(50), nullable=True, index=True)
    location_name = Column(String(255), nullable=True)
    assigned_user = Column(String(128), nullable=True)

    # Network configuration
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(17), nullable=True)
    network_config = Column(Text, nullable=True)  # JSON configuration

    # Status and health
    # active, inactive, maintenance, error
    status = Column(String(50), nullable=False, default='active')
    last_heartbeat = Column(DateTime, nullable=True)
    last_transaction = Column(DateTime, nullable=True)

    # Capabilities and features
    supports_contactless = Column(Boolean, nullable=False, default=False)
    supports_chip = Column(Boolean, nullable=False, default=False)
    supports_pin = Column(Boolean, nullable=False, default=False)
    supports_receipt_print = Column(Boolean, nullable=False, default=False)

    # Configuration and settings
    terminal_config = Column(Text, nullable=True)  # JSON configuration
    firmware_version = Column(String(50), nullable=True)

    # Additional information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Legacy timestamp fields
    creationdate = Column(DateTime, nullable=False, default=datetime.utcnow)
    creationby = Column(String(128), nullable=True)
    updatedate = Column(DateTime, nullable=False, default=datetime.utcnow)
    updateby = Column(String(128), nullable=True)


# Update relationships
# Add to Invoice model
Invoice.payments = relationship("Payment", back_populates="invoice")

# Add to Payment model
Payment.refunds = relationship("Refund", back_populates="payment")


# Export all models
__all__ = [
    "BillingPlan",
    "BillingHistory",
    "BillingMerchant",
    "BillingRate",
    "BillingPlanProfile",
    "Invoice",
    "Payment",
    "Refund",
    "PaymentType",
    "POS"
]
