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
    planRecurringBillingSchedule = Column(String(128), nullable=False, default='Fixed')
    
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
    
    __table_args__ = (
        Index('idx_billing_plans_active', 'planActive'),
    )
    session_timeout: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    idle_timeout: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Bandwidth limits (in Kbps)
    download_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    upload_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Plan status and metadata
    plan_active: Mapped[bool] = mapped_column(Boolean, default=True)
    plan_creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now())
    plan_creation_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class BillRate(Base):
    """Billing rates for different services"""
    __tablename__ = "billrates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Rate identification
    rate_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    rate_type: Mapped[str] = mapped_column(String(32), nullable=False)  # fixed, time_based, data_based, combined
    
    # Pricing
    rate_cost: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Time-based rates
    rate_per_minute: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    rate_per_hour: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    
    # Data-based rates
    rate_per_mb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    rate_per_gb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    
    # Rate validity
    rate_effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rate_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class PaymentType(Base):
    """Payment method types"""
    __tablename__ = "billpaymenttypes"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Payment type details
    type_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    type_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Payment(Base):
    """Payment records"""
    __tablename__ = "billpayments"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Payment details
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)  # cash, credit_card, bank_transfer, etc.
    payment_status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, completed, failed, refunded, cancelled
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Payment metadata
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    payment_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    
    # Associated invoice
    invoice_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("billinvoices.id"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Relationships
    invoice: Mapped[Optional["Invoice"]] = relationship("Invoice", back_populates="payments")


class Invoice(Base):
    """Invoice records"""
    __tablename__ = "billinvoices"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Invoice identification
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Invoice dates
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    invoice_status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, sent, paid, overdue, cancelled
    
    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    # Invoice metadata
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    invoice_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Relationships
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice")
    line_items: Mapped[List["InvoiceLineItem"]] = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    
    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount
    
    def __init__(self, **kwargs):
        # Generate invoice number if not provided
        if "invoice_number" not in kwargs:
            import uuid
            kwargs["invoice_number"] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().__init__(**kwargs)


class InvoiceLineItem(Base):
    """Invoice line items"""
    __tablename__ = "billinvoiceitems"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign key
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("billinvoices.id"), nullable=False)
    
    # Line item details
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="line_items")
    
    @property
    def line_total(self) -> Decimal:
        """Calculate line total"""
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percentage / 100)
        return subtotal - discount


class UserBillingHistory(Base):
    """User billing history and transactions"""
    __tablename__ = "billinghistory"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # User and transaction details
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)  # payment, charge, refund, adjustment
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Transaction metadata
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)  # Payment ID, Invoice ID, etc.
    balance_before: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)


class BillingPOS(Base):
    """Point of Sale transactions"""
    __tablename__ = "billpos"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # POS details
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_name: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Transaction details
    transaction_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    processed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class MerchantTransaction(Base):
    """Merchant payment gateway transactions"""
    __tablename__ = "billmerchant"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Transaction details
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Merchant details
    merchant_name: Mapped[str] = mapped_column(String(128), nullable=False)
    merchant_transaction_id: Mapped[str] = mapped_column(String(128), nullable=False)
    gateway_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Transaction status
    status: Mapped[str] = mapped_column(String(32), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)