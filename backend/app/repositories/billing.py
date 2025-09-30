"""
Billing Repository Module

This module provides data access layer for billing-related operations,
following the repository pattern to abstract database operations.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import desc, asc, and_, or_, func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.models.billing import (
    BillingPlan, BillingHistory, BillingMerchant,
    BillingRate, BillingPlanProfile, Invoice, Payment,
    Refund, PaymentType, POS
)
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import logger


class BillingPlanRepository:
    """Repository for billing plan operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        active_only: bool = False,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[BillingPlan], int]:
        """Get all billing plans with filtering and pagination"""
        try:
            # Base query
            query = self.session.query(BillingPlan)

            # Apply filters
            if name_filter:
                query = query.filter(
                    BillingPlan.planName.ilike(f"%{name_filter}%"))

            if type_filter:
                query = query.filter(BillingPlan.planType == type_filter)

            if active_only:
                query = query.filter(BillingPlan.planActive == True)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(BillingPlan, sort_field, BillingPlan.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            plans = query.offset(offset).limit(page_size).all()

            return plans, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching billing plans: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing plans: {str(e)}")

    async def get_by_id(self, plan_id: int) -> Optional[BillingPlan]:
        """Get a billing plan by ID"""
        try:
            return self.session.query(BillingPlan).filter(BillingPlan.id == plan_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching billing plan {plan_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing plan: {str(e)}")

    async def get_by_name(self, plan_name: str) -> Optional[BillingPlan]:
        """Get a billing plan by name"""
        try:
            return self.session.query(BillingPlan).filter(BillingPlan.planName == plan_name).first()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching billing plan by name {plan_name}: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch billing plan by name: {str(e)}")

    async def create(self, plan_data: Dict[str, Any]) -> BillingPlan:
        """Create a new billing plan"""
        try:
            plan = BillingPlan(**plan_data)
            self.session.add(plan)
            self.session.flush()  # Get the ID before commit
            return plan
        except SQLAlchemyError as e:
            logger.error(f"Error creating billing plan: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create billing plan: {str(e)}")

    async def update(self, plan_id: int, update_data: Dict[str, Any]) -> Optional[BillingPlan]:
        """Update an existing billing plan"""
        try:
            plan = await self.get_by_id(plan_id)
            if not plan:
                return None

            for key, value in update_data.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)

            # Update timestamp
            plan.updatedate = datetime.utcnow()

            self.session.flush()
            return plan

        except SQLAlchemyError as e:
            logger.error(f"Error updating billing plan {plan_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update billing plan: {str(e)}")

    async def delete(self, plan_id: int) -> bool:
        """Delete a billing plan"""
        try:
            plan = await self.get_by_id(plan_id)
            if not plan:
                return False

            self.session.delete(plan)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting billing plan {plan_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete billing plan: {str(e)}")

    async def get_active_plans(self) -> List[BillingPlan]:
        """Get all active billing plans"""
        try:
            return self.session.query(BillingPlan).filter(BillingPlan.planActive == True).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching active billing plans: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch active billing plans: {str(e)}")

    async def get_plan_statistics(self) -> Dict[str, Any]:
        """Get billing plan statistics"""
        try:
            total_plans = self.session.query(BillingPlan).count()
            active_plans = self.session.query(BillingPlan).filter(
                BillingPlan.planActive == True).count()
            inactive_plans = total_plans - active_plans

            # Get plans by type
            type_stats = self.session.query(
                BillingPlan.planType,
                func.count(BillingPlan.id).label('count')
            ).group_by(BillingPlan.planType).all()

            return {
                "total_plans": total_plans,
                "active_plans": active_plans,
                "inactive_plans": inactive_plans,
                "by_type": [{"type": stat[0], "count": stat[1]} for stat in type_stats]
            }
        except SQLAlchemyError as e:
            logger.error(f"Error fetching plan statistics: {str(e)}")
            raise DatabaseError(f"Failed to fetch plan statistics: {str(e)}")


class BillingHistoryRepository:
    """Repository for billing history operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        username_filter: Optional[str] = None,
        plan_id_filter: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_field: str = "id",
        sort_order: str = "desc"
    ) -> tuple[List[BillingHistory], int]:
        """Get billing history with filtering and pagination"""
        try:
            query = self.session.query(BillingHistory)

            # Apply filters
            if username_filter:
                query = query.filter(
                    BillingHistory.username.ilike(f"%{username_filter}%"))

            if plan_id_filter:
                query = query.filter(BillingHistory.planId == plan_id_filter)

            if start_date:
                query = query.filter(BillingHistory.creationdate >= start_date)

            if end_date:
                query = query.filter(BillingHistory.creationdate <= end_date)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(
                BillingHistory, sort_field, BillingHistory.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            history = query.offset(offset).limit(page_size).all()

            return history, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching billing history: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing history: {str(e)}")

    async def get_by_id(self, history_id: int) -> Optional[BillingHistory]:
        """Get billing history by ID"""
        try:
            return self.session.query(BillingHistory).filter(BillingHistory.id == history_id).first()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching billing history {history_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing history: {str(e)}")

    async def get_by_username(self, username: str, limit: int = 50) -> List[BillingHistory]:
        """Get billing history for a specific user"""
        try:
            return (self.session.query(BillingHistory)
                    .filter(BillingHistory.username == username)
                    .order_by(desc(BillingHistory.creationdate))
                    .limit(limit)
                    .all())
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching billing history for user {username}: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch user billing history: {str(e)}")

    async def create(self, history_data: Dict[str, Any]) -> BillingHistory:
        """Create a new billing history record"""
        try:
            history = BillingHistory(**history_data)
            self.session.add(history)
            self.session.flush()
            return history
        except SQLAlchemyError as e:
            logger.error(f"Error creating billing history: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create billing history: {str(e)}")

    async def get_user_statistics(self, username: str) -> Dict[str, Any]:
        """Get billing statistics for a specific user"""
        try:
            total_records = (self.session.query(BillingHistory)
                             .filter(BillingHistory.username == username)
                             .count())

            # Get payment statistics
            payment_stats = (self.session.query(
                func.count(BillingHistory.id).label('count'),
                func.sum(BillingHistory.billAmount).label('total_amount')
            ).filter(BillingHistory.username == username).first())

            return {
                "total_records": total_records,
                "payment_count": payment_stats.count if payment_stats else 0,
                "total_amount": float(payment_stats.total_amount or 0)
            }
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching user statistics for {username}: {str(e)}")
            raise DatabaseError(f"Failed to fetch user statistics: {str(e)}")


class BillingRateRepository:
    """Repository for billing rate operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[BillingRate], int]:
        """Get all billing rates with filtering and pagination"""
        try:
            query = self.session.query(BillingRate)

            # Apply filters
            if name_filter:
                query = query.filter(
                    BillingRate.rateName.ilike(f"%{name_filter}%"))

            if type_filter:
                query = query.filter(BillingRate.rateType == type_filter)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(BillingRate, sort_field, BillingRate.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            rates = query.offset(offset).limit(page_size).all()

            return rates, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching billing rates: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing rates: {str(e)}")

    async def get_by_id(self, rate_id: int) -> Optional[BillingRate]:
        """Get a billing rate by ID"""
        try:
            return self.session.query(BillingRate).filter(BillingRate.id == rate_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching billing rate {rate_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing rate: {str(e)}")

    async def create(self, rate_data: Dict[str, Any]) -> BillingRate:
        """Create a new billing rate"""
        try:
            rate = BillingRate(**rate_data)
            self.session.add(rate)
            self.session.flush()
            return rate
        except SQLAlchemyError as e:
            logger.error(f"Error creating billing rate: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create billing rate: {str(e)}")

    async def update(self, rate_id: int, update_data: Dict[str, Any]) -> Optional[BillingRate]:
        """Update an existing billing rate"""
        try:
            rate = await self.get_by_id(rate_id)
            if not rate:
                return None

            for key, value in update_data.items():
                if hasattr(rate, key):
                    setattr(rate, key, value)

            # Update timestamp
            rate.updatedate = datetime.utcnow()

            self.session.flush()
            return rate

        except SQLAlchemyError as e:
            logger.error(f"Error updating billing rate {rate_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update billing rate: {str(e)}")

    async def delete(self, rate_id: int) -> bool:
        """Delete a billing rate"""
        try:
            rate = await self.get_by_id(rate_id)
            if not rate:
                return False

            self.session.delete(rate)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting billing rate {rate_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete billing rate: {str(e)}")


class BillingMerchantRepository:
    """Repository for billing merchant operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        username_filter: Optional[str] = None,
        business_id_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "desc"
    ) -> tuple[List[BillingMerchant], int]:
        """Get all merchant transactions with filtering and pagination"""
        try:
            query = self.session.query(BillingMerchant)

            # Apply filters
            if username_filter:
                query = query.filter(
                    BillingMerchant.username.ilike(f"%{username_filter}%"))

            if business_id_filter:
                query = query.filter(
                    BillingMerchant.business_id == business_id_filter)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(
                BillingMerchant, sort_field, BillingMerchant.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            merchants = query.offset(offset).limit(page_size).all()

            return merchants, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching merchant transactions: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch merchant transactions: {str(e)}")

    async def get_by_id(self, merchant_id: int) -> Optional[BillingMerchant]:
        """Get merchant transaction by ID"""
        try:
            return self.session.query(BillingMerchant).filter(BillingMerchant.id == merchant_id).first()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching merchant transaction {merchant_id}: {str(e)}")
            raise DatabaseError(
                f"Failed to fetch merchant transaction: {str(e)}")

    async def create(self, merchant_data: Dict[str, Any]) -> BillingMerchant:
        """Create a new merchant transaction"""
        try:
            merchant = BillingMerchant(**merchant_data)
            self.session.add(merchant)
            self.session.flush()
            return merchant
        except SQLAlchemyError as e:
            logger.error(f"Error creating merchant transaction: {str(e)}")
            self.session.rollback()
            raise DatabaseError(
                f"Failed to create merchant transaction: {str(e)}")

    async def update(self, merchant_id: int, merchant_data: Dict[str, Any]) -> Optional[BillingMerchant]:
        """Update an existing merchant transaction"""
        try:
            merchant = await self.get_by_id(merchant_id)
            if not merchant:
                return None

            for key, value in merchant_data.items():
                if hasattr(merchant, key):
                    setattr(merchant, key, value)

            self.session.flush()
            return merchant

        except SQLAlchemyError as e:
            logger.error(
                f"Error updating merchant transaction {merchant_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(
                f"Failed to update merchant transaction: {str(e)}")

    async def delete(self, merchant_id: int) -> bool:
        """Delete a merchant transaction"""
        try:
            merchant = await self.get_by_id(merchant_id)
            if not merchant:
                return False

            self.session.delete(merchant)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(
                f"Error deleting merchant transaction {merchant_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(
                f"Failed to delete merchant transaction: {str(e)}")


# =====================================================================
# Invoice Repository
# =====================================================================

class InvoiceRepository:
    """Repository for invoice operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        customer_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[Invoice], int]:
        """Get all invoices with filtering and pagination"""
        try:
            query = self.session.query(Invoice)

            # Apply filters
            if customer_filter:
                query = query.filter(
                    or_(
                        Invoice.customer_name.ilike(f"%{customer_filter}%"),
                        Invoice.customer_id.ilike(f"%{customer_filter}%")
                    )
                )

            if status_filter:
                query = query.filter(Invoice.status == status_filter)

            if date_from:
                query = query.filter(Invoice.issue_date >= date_from)

            if date_to:
                query = query.filter(Invoice.issue_date <= date_to)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(Invoice, sort_field, Invoice.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            invoices = query.offset(offset).limit(page_size).all()

            return invoices, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoices: {str(e)}")
            raise DatabaseError(f"Failed to fetch invoices: {str(e)}")

    async def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        try:
            return self.session.query(Invoice).filter(Invoice.id == invoice_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoice {invoice_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch invoice: {str(e)}")

    async def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        try:
            return self.session.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoice {invoice_number}: {str(e)}")
            raise DatabaseError(f"Failed to fetch invoice: {str(e)}")

    async def create(self, invoice_data: Dict[str, Any]) -> Invoice:
        """Create a new invoice"""
        try:
            invoice = Invoice(**invoice_data)
            self.session.add(invoice)
            self.session.flush()
            return invoice
        except SQLAlchemyError as e:
            logger.error(f"Error creating invoice: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create invoice: {str(e)}")

    async def update(self, invoice_id: int, invoice_data: Dict[str, Any]) -> Optional[Invoice]:
        """Update an existing invoice"""
        try:
            invoice = await self.get_by_id(invoice_id)
            if not invoice:
                return None

            for key, value in invoice_data.items():
                if hasattr(invoice, key):
                    setattr(invoice, key, value)

            self.session.flush()
            return invoice

        except SQLAlchemyError as e:
            logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update invoice: {str(e)}")

    async def delete(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        try:
            invoice = await self.get_by_id(invoice_id)
            if not invoice:
                return False

            self.session.delete(invoice)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting invoice {invoice_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete invoice: {str(e)}")


# =====================================================================
# Payment Repository
# =====================================================================

class PaymentRepository:
    """Repository for payment operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        customer_filter: Optional[str] = None,
        payment_method_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[Payment], int]:
        """Get all payments with filtering and pagination"""
        try:
            query = self.session.query(Payment)

            # Apply filters
            if customer_filter:
                query = query.filter(
                    Payment.customer_id.ilike(f"%{customer_filter}%"))

            if payment_method_filter:
                query = query.filter(
                    Payment.payment_method == payment_method_filter)

            if status_filter:
                query = query.filter(Payment.status == status_filter)

            if date_from:
                query = query.filter(Payment.payment_date >= date_from)

            if date_to:
                query = query.filter(Payment.payment_date <= date_to)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(Payment, sort_field, Payment.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            payments = query.offset(offset).limit(page_size).all()

            return payments, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching payments: {str(e)}")
            raise DatabaseError(f"Failed to fetch payments: {str(e)}")

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        try:
            return self.session.query(Payment).filter(Payment.id == payment_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching payment {payment_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch payment: {str(e)}")

    async def get_by_customer(self, customer_id: str) -> List[Payment]:
        """Get payments by customer ID"""
        try:
            return self.session.query(Payment).filter(Payment.customer_id == customer_id).all()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching payments for customer {customer_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch payments: {str(e)}")

    async def create(self, payment_data: Dict[str, Any]) -> Payment:
        """Create a new payment"""
        try:
            payment = Payment(**payment_data)
            self.session.add(payment)
            self.session.flush()
            return payment
        except SQLAlchemyError as e:
            logger.error(f"Error creating payment: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create payment: {str(e)}")

    async def update(self, payment_id: int, payment_data: Dict[str, Any]) -> Optional[Payment]:
        """Update an existing payment"""
        try:
            payment = await self.get_by_id(payment_id)
            if not payment:
                return None

            for key, value in payment_data.items():
                if hasattr(payment, key):
                    setattr(payment, key, value)

            self.session.flush()
            return payment

        except SQLAlchemyError as e:
            logger.error(f"Error updating payment {payment_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update payment: {str(e)}")

    async def delete(self, payment_id: int) -> bool:
        """Delete a payment"""
        try:
            payment = await self.get_by_id(payment_id)
            if not payment:
                return False

            self.session.delete(payment)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting payment {payment_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete payment: {str(e)}")


# =====================================================================
# Refund Repository
# =====================================================================

class RefundRepository:
    """Repository for refund operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        customer_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        payment_id_filter: Optional[int] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[Refund], int]:
        """Get all refunds with filtering and pagination"""
        try:
            query = self.session.query(Refund)

            # Apply filters
            if customer_filter:
                query = query.filter(
                    Refund.customer_id.ilike(f"%{customer_filter}%"))

            if status_filter:
                query = query.filter(Refund.status == status_filter)

            if payment_id_filter:
                query = query.filter(Refund.payment_id == payment_id_filter)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(Refund, sort_field, Refund.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            refunds = query.offset(offset).limit(page_size).all()

            return refunds, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching refunds: {str(e)}")
            raise DatabaseError(f"Failed to fetch refunds: {str(e)}")

    async def get_by_id(self, refund_id: int) -> Optional[Refund]:
        """Get refund by ID"""
        try:
            return self.session.query(Refund).filter(Refund.id == refund_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching refund {refund_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch refund: {str(e)}")

    async def get_by_payment(self, payment_id: int) -> List[Refund]:
        """Get refunds by payment ID"""
        try:
            return self.session.query(Refund).filter(Refund.payment_id == payment_id).all()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching refunds for payment {payment_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch refunds: {str(e)}")

    async def create(self, refund_data: Dict[str, Any]) -> Refund:
        """Create a new refund"""
        try:
            refund = Refund(**refund_data)
            self.session.add(refund)
            self.session.flush()
            return refund
        except SQLAlchemyError as e:
            logger.error(f"Error creating refund: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create refund: {str(e)}")

    async def update(self, refund_id: int, refund_data: Dict[str, Any]) -> Optional[Refund]:
        """Update an existing refund"""
        try:
            refund = await self.get_by_id(refund_id)
            if not refund:
                return None

            for key, value in refund_data.items():
                if hasattr(refund, key):
                    setattr(refund, key, value)

            self.session.flush()
            return refund

        except SQLAlchemyError as e:
            logger.error(f"Error updating refund {refund_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update refund: {str(e)}")

    async def delete(self, refund_id: int) -> bool:
        """Delete a refund"""
        try:
            refund = await self.get_by_id(refund_id)
            if not refund:
                return False

            self.session.delete(refund)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting refund {refund_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete refund: {str(e)}")


# =====================================================================
# Payment Type Repository
# =====================================================================

class PaymentTypeRepository:
    """Repository for payment type operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        active_only: bool = False,
        sort_field: str = "sort_order",
        sort_order: str = "asc"
    ) -> tuple[List[PaymentType], int]:
        """Get all payment types with filtering and pagination"""
        try:
            query = self.session.query(PaymentType)

            # Apply filters
            if name_filter:
                query = query.filter(
                    or_(
                        PaymentType.name.ilike(f"%{name_filter}%"),
                        PaymentType.display_name.ilike(f"%{name_filter}%")
                    )
                )

            if active_only:
                query = query.filter(PaymentType.is_active == True)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(PaymentType, sort_field,
                                  PaymentType.sort_order)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            payment_types = query.offset(offset).limit(page_size).all()

            return payment_types, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching payment types: {str(e)}")
            raise DatabaseError(f"Failed to fetch payment types: {str(e)}")

    async def get_by_id(self, payment_type_id: int) -> Optional[PaymentType]:
        """Get payment type by ID"""
        try:
            return self.session.query(PaymentType).filter(PaymentType.id == payment_type_id).first()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching payment type {payment_type_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch payment type: {str(e)}")

    async def get_by_code(self, code: str) -> Optional[PaymentType]:
        """Get payment type by code"""
        try:
            return self.session.query(PaymentType).filter(PaymentType.code == code).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching payment type {code}: {str(e)}")
            raise DatabaseError(f"Failed to fetch payment type: {str(e)}")

    async def create(self, payment_type_data: Dict[str, Any]) -> PaymentType:
        """Create a new payment type"""
        try:
            payment_type = PaymentType(**payment_type_data)
            self.session.add(payment_type)
            self.session.flush()
            return payment_type
        except SQLAlchemyError as e:
            logger.error(f"Error creating payment type: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create payment type: {str(e)}")

    async def update(self, payment_type_id: int, payment_type_data: Dict[str, Any]) -> Optional[PaymentType]:
        """Update an existing payment type"""
        try:
            payment_type = await self.get_by_id(payment_type_id)
            if not payment_type:
                return None

            for key, value in payment_type_data.items():
                if hasattr(payment_type, key):
                    setattr(payment_type, key, value)

            self.session.flush()
            return payment_type

        except SQLAlchemyError as e:
            logger.error(
                f"Error updating payment type {payment_type_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update payment type: {str(e)}")

    async def delete(self, payment_type_id: int) -> bool:
        """Delete a payment type"""
        try:
            payment_type = await self.get_by_id(payment_type_id)
            if not payment_type:
                return False

            self.session.delete(payment_type)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(
                f"Error deleting payment type {payment_type_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete payment type: {str(e)}")


# =====================================================================
# POS Repository
# =====================================================================

class POSRepository:
    """Repository for POS terminal operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> tuple[List[POS], int]:
        """Get all POS terminals with filtering and pagination"""
        try:
            query = self.session.query(POS)

            # Apply filters
            if name_filter:
                query = query.filter(
                    or_(
                        POS.name.ilike(f"%{name_filter}%"),
                        POS.serial_number.ilike(f"%{name_filter}%")
                    )
                )

            if location_filter:
                query = query.filter(
                    or_(
                        POS.location_id.ilike(f"%{location_filter}%"),
                        POS.location_name.ilike(f"%{location_filter}%")
                    )
                )

            if status_filter:
                query = query.filter(POS.status == status_filter)

            # Get total count
            total = query.count()

            # Apply sorting
            sort_column = getattr(POS, sort_field, POS.id)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (page - 1) * page_size
            pos_terminals = query.offset(offset).limit(page_size).all()

            return pos_terminals, total

        except SQLAlchemyError as e:
            logger.error(f"Error fetching POS terminals: {str(e)}")
            raise DatabaseError(f"Failed to fetch POS terminals: {str(e)}")

    async def get_by_id(self, pos_id: int) -> Optional[POS]:
        """Get POS terminal by ID"""
        try:
            return self.session.query(POS).filter(POS.id == pos_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching POS terminal {pos_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch POS terminal: {str(e)}")

    async def get_by_serial_number(self, serial_number: str) -> Optional[POS]:
        """Get POS terminal by serial number"""
        try:
            return self.session.query(POS).filter(POS.serial_number == serial_number).first()
        except SQLAlchemyError as e:
            logger.error(
                f"Error fetching POS terminal {serial_number}: {str(e)}")
            raise DatabaseError(f"Failed to fetch POS terminal: {str(e)}")

    async def create(self, pos_data: Dict[str, Any]) -> POS:
        """Create a new POS terminal"""
        try:
            pos = POS(**pos_data)
            self.session.add(pos)
            self.session.flush()
            return pos
        except SQLAlchemyError as e:
            logger.error(f"Error creating POS terminal: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to create POS terminal: {str(e)}")

    async def update(self, pos_id: int, pos_data: Dict[str, Any]) -> Optional[POS]:
        """Update an existing POS terminal"""
        try:
            pos = await self.get_by_id(pos_id)
            if not pos:
                return None

            for key, value in pos_data.items():
                if hasattr(pos, key):
                    setattr(pos, key, value)

            self.session.flush()
            return pos

        except SQLAlchemyError as e:
            logger.error(f"Error updating POS terminal {pos_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to update POS terminal: {str(e)}")

    async def delete(self, pos_id: int) -> bool:
        """Delete a POS terminal"""
        try:
            pos = await self.get_by_id(pos_id)
            if not pos:
                return False

            self.session.delete(pos)
            self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error deleting POS terminal {pos_id}: {str(e)}")
            self.session.rollback()
            raise DatabaseError(f"Failed to delete POS terminal: {str(e)}")
