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


# Export all models
__all__ = [
    "BillingPlan",
    "BillingHistory",
    "BillingMerchant", 
    "BillingRate",
    "BillingPlanProfile"
]