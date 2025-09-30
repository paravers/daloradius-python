"""
Billing Service Module

This module provides business logic for billing-related operations,
implementing the service layer pattern for clean architecture.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal

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
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError
from app.core.logging import logger


class BillingPlanService:
    """Service for billing plan operations"""

    def __init__(self, repository: BillingPlanRepository):
        self.repository = repository

    async def get_plans(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        active_only: bool = False,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated billing plans with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            plans, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                name_filter=name_filter,
                type_filter=type_filter,
                active_only=active_only,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            plan_responses = [self._to_response_model(plan) for plan in plans]

            return PaginatedResponse(
                data=plan_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )

        except Exception as e:
            logger.error(f"Error getting billing plans: {str(e)}")
            raise

    async def get_plan_by_id(self, plan_id: int) -> BillingPlanResponse:
        """Get a billing plan by ID"""
        try:
            plan = await self.repository.get_by_id(plan_id)
            if not plan:
                raise NotFoundError(
                    f"Billing plan with ID {plan_id} not found")

            return self._to_response_model(plan)

        except Exception as e:
            logger.error(f"Error getting billing plan {plan_id}: {str(e)}")
            raise

    async def create_plan(self, plan_data: BillingPlanCreate) -> BillingPlanResponse:
        """Create a new billing plan"""
        try:
            # Validate plan name is unique
            existing_plan = await self.repository.get_by_name(plan_data.planName)
            if existing_plan:
                raise ValidationError(
                    f"Plan with name '{plan_data.planName}' already exists")

            # Validate business rules
            self._validate_plan_data(plan_data.dict())

            # Prepare data for creation
            plan_dict = plan_data.dict()
            plan_dict['creationdate'] = datetime.utcnow()
            # TODO: Get from current user context
            plan_dict['creationby'] = 'system'
            plan_dict['updatedate'] = datetime.utcnow()
            plan_dict['updateby'] = 'system'

            # Create plan
            plan = await self.repository.create(plan_dict)

            logger.info(
                f"Created billing plan: {plan.planName} (ID: {plan.id})")
            return self._to_response_model(plan)

        except Exception as e:
            logger.error(f"Error creating billing plan: {str(e)}")
            raise

    async def update_plan(self, plan_id: int, plan_data: BillingPlanUpdate) -> BillingPlanResponse:
        """Update an existing billing plan"""
        try:
            # Check if plan exists
            existing_plan = await self.repository.get_by_id(plan_id)
            if not existing_plan:
                raise NotFoundError(
                    f"Billing plan with ID {plan_id} not found")

            # Validate name uniqueness if changed
            if plan_data.planName and plan_data.planName != existing_plan.planName:
                name_check = await self.repository.get_by_name(plan_data.planName)
                if name_check and name_check.id != plan_id:
                    raise ValidationError(
                        f"Plan with name '{plan_data.planName}' already exists")

            # Prepare update data
            update_dict = {k: v for k, v in plan_data.dict().items()
                           if v is not None}
            # TODO: Get from current user context
            update_dict['updateby'] = 'system'

            # Validate business rules
            if update_dict:
                self._validate_plan_data(update_dict)

            # Update plan
            updated_plan = await self.repository.update(plan_id, update_dict)

            logger.info(
                f"Updated billing plan: {updated_plan.planName} (ID: {plan_id})")
            return self._to_response_model(updated_plan)

        except Exception as e:
            logger.error(f"Error updating billing plan {plan_id}: {str(e)}")
            raise

    async def delete_plan(self, plan_id: int) -> bool:
        """Delete a billing plan"""
        try:
            # Check if plan exists
            plan = await self.repository.get_by_id(plan_id)
            if not plan:
                raise NotFoundError(
                    f"Billing plan with ID {plan_id} not found")

            # Check if plan is in use (business rule)
            # TODO: Check if plan has active subscriptions or history

            # Delete plan
            success = await self.repository.delete(plan_id)

            if success:
                logger.info(
                    f"Deleted billing plan: {plan.planName} (ID: {plan_id})")

            return success

        except Exception as e:
            logger.error(f"Error deleting billing plan {plan_id}: {str(e)}")
            raise

    async def get_active_plans(self) -> List[BillingPlanResponse]:
        """Get all active billing plans"""
        try:
            plans = await self.repository.get_active_plans()
            return [self._to_response_model(plan) for plan in plans]
        except Exception as e:
            logger.error(f"Error getting active billing plans: {str(e)}")
            raise

    async def get_plan_statistics(self) -> Dict[str, Any]:
        """Get billing plan statistics"""
        try:
            stats = await self.repository.get_plan_statistics()

            # Add additional calculated metrics
            stats['utilization_rate'] = (
                (stats['active_plans'] / stats['total_plans'] * 100)
                if stats['total_plans'] > 0 else 0
            )

            return stats
        except Exception as e:
            logger.error(f"Error getting plan statistics: {str(e)}")
            raise

    def _validate_plan_data(self, plan_data: Dict[str, Any]) -> None:
        """Validate billing plan data according to business rules"""
        # Validate time bank format
        if 'planTimeBank' in plan_data and plan_data['planTimeBank']:
            try:
                # Time should be in format like "30:00:00" for 30 hours
                time_parts = str(plan_data['planTimeBank']).split(':')
                if len(time_parts) != 3:
                    raise ValidationError(
                        "Time bank must be in HH:MM:SS format")

                hours, minutes, seconds = map(int, time_parts)
                if minutes >= 60 or seconds >= 60:
                    raise ValidationError("Invalid time format in time bank")

            except (ValueError, AttributeError):
                raise ValidationError("Invalid time bank format")

        # Validate bandwidth values
        for bandwidth_field in ['planBandwidthUp', 'planBandwidthDown']:
            if bandwidth_field in plan_data and plan_data[bandwidth_field]:
                try:
                    bandwidth_value = str(plan_data[bandwidth_field])
                    # Should be numeric or end with unit (Kbps, Mbps, etc.)
                    if not (bandwidth_value.isdigit() or
                            any(bandwidth_value.lower().endswith(unit)
                                for unit in ['kbps', 'mbps', 'gbps'])):
                        raise ValidationError(
                            f"Invalid bandwidth format: {bandwidth_field}")
                except (ValueError, AttributeError):
                    raise ValidationError(
                        f"Invalid bandwidth value: {bandwidth_field}")

        # Validate traffic values
        for traffic_field in ['planTrafficTotal', 'planTrafficUp', 'planTrafficDown']:
            if traffic_field in plan_data and plan_data[traffic_field]:
                try:
                    traffic_value = str(plan_data[traffic_field])
                    # Should be numeric or end with unit (MB, GB, TB)
                    if not (traffic_value.isdigit() or
                            any(traffic_value.lower().endswith(unit)
                                for unit in ['mb', 'gb', 'tb', 'kb'])):
                        raise ValidationError(
                            f"Invalid traffic format: {traffic_field}")
                except (ValueError, AttributeError):
                    raise ValidationError(
                        f"Invalid traffic value: {traffic_field}")

    def _to_response_model(self, plan) -> BillingPlanResponse:
        """Convert database model to response model"""
        return BillingPlanResponse(
            id=plan.id,
            planName=plan.planName or "",
            planId=plan.planId or "",
            planType=plan.planType or "",
            planTimeBank=plan.planTimeBank or "",
            planTimeType=plan.planTimeType or "",
            planTimeRefillCost=plan.planTimeRefillCost or "",
            planBandwidthUp=plan.planBandwidthUp or "",
            planBandwidthDown=plan.planBandwidthDown or "",
            planTrafficTotal=plan.planTrafficTotal or "",
            planTrafficUp=plan.planTrafficUp or "",
            planTrafficDown=plan.planTrafficDown or "",
            planTrafficRefillCost=plan.planTrafficRefillCost or "",
            planRecurring=plan.planRecurring or "",
            planRecurringPeriod=plan.planRecurringPeriod or "",
            planRecurringBillingSchedule=plan.planRecurringBillingSchedule or "",
            planCost=plan.planCost or "",
            planSetupCost=plan.planSetupCost or "",
            planTax=plan.planTax or "",
            planCurrency=plan.planCurrency or "",
            planGroup=plan.planGroup or "",
            planActive=plan.planActive or False,
            creationdate=plan.creationdate,
            creationby=plan.creationby or "",
            updatedate=plan.updatedate,
            updateby=plan.updateby or ""
        )


class BillingHistoryService:
    """Service for billing history operations"""

    def __init__(self, repository: BillingHistoryRepository):
        self.repository = repository

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 10,
        username_filter: Optional[str] = None,
        plan_id_filter: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_field: str = "id",
        sort_order: str = "desc"
    ) -> PaginatedResponse:
        """Get paginated billing history with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Validate date range
            if start_date and end_date and start_date > end_date:
                raise ValidationError("Start date cannot be after end date")

            history, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                username_filter=username_filter,
                plan_id_filter=plan_id_filter,
                start_date=start_date,
                end_date=end_date,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            history_responses = [self._to_response_model(
                record) for record in history]

            return PaginatedResponse(
                data=history_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )

        except Exception as e:
            logger.error(f"Error getting billing history: {str(e)}")
            raise

    async def get_user_history(self, username: str, limit: int = 50) -> List[BillingHistoryResponse]:
        """Get billing history for a specific user"""
        try:
            if limit > 100:
                limit = 100  # Cap the limit

            history = await self.repository.get_by_username(username, limit)
            return [self._to_response_model(record) for record in history]

        except Exception as e:
            logger.error(
                f"Error getting user billing history for {username}: {str(e)}")
            raise

    async def create_history_record(self, history_data: BillingHistoryCreate) -> BillingHistoryResponse:
        """Create a new billing history record"""
        try:
            # Prepare data for creation
            history_dict = history_data.dict()
            history_dict['creationdate'] = datetime.utcnow()
            # TODO: Get from current user context
            history_dict['creationby'] = 'system'

            # Create history record
            history = await self.repository.create(history_dict)

            logger.info(
                f"Created billing history record for user: {history.username} (ID: {history.id})")
            return self._to_response_model(history)

        except Exception as e:
            logger.error(f"Error creating billing history record: {str(e)}")
            raise

    async def get_user_statistics(self, username: str) -> Dict[str, Any]:
        """Get billing statistics for a specific user"""
        try:
            stats = await self.repository.get_user_statistics(username)

            # Add additional calculated metrics
            avg_payment = (
                stats['total_amount'] / stats['payment_count']
                if stats['payment_count'] > 0 else 0
            )

            return {
                **stats,
                'average_payment': avg_payment
            }

        except Exception as e:
            logger.error(
                f"Error getting user statistics for {username}: {str(e)}")
            raise

    def _to_response_model(self, history) -> BillingHistoryResponse:
        """Convert database model to response model"""
        return BillingHistoryResponse(
            id=history.id,
            username=history.username or "",
            planId=history.planId,
            billAmount=history.billAmount or "",
            billAction=history.billAction or "",
            billPerformer=history.billPerformer or "",
            billReason=history.billReason or "",
            paymentmethod=history.paymentmethod or "",
            cash=history.cash or "",
            creditcardname=history.creditcardname or "",
            creditcardnumber=history.creditcardnumber or "",
            creditcardverification=history.creditcardverification or "",
            creditcardtype=history.creditcardtype or "",
            creditcardexp=history.creditcardexp or "",
            creationdate=history.creationdate,
            creationby=history.creationby or ""
        )


class BillingRateService:
    """Service for billing rate operations"""

    def __init__(self, repository: BillingRateRepository):
        self.repository = repository

    async def get_rates(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated billing rates with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            rates, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                name_filter=name_filter,
                type_filter=type_filter,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            rate_responses = [self._to_response_model(rate) for rate in rates]

            return PaginatedResponse(
                data=rate_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )

        except Exception as e:
            logger.error(f"Error getting billing rates: {str(e)}")
            raise

    async def create_rate(self, rate_data: BillingRateCreate) -> BillingRateResponse:
        """Create a new billing rate"""
        try:
            # Validate rate data
            self._validate_rate_data(rate_data.dict())

            # Prepare data for creation
            rate_dict = rate_data.dict()
            rate_dict['creationdate'] = datetime.utcnow()
            # TODO: Get from current user context
            rate_dict['creationby'] = 'system'
            rate_dict['updatedate'] = datetime.utcnow()
            rate_dict['updateby'] = 'system'

            # Create rate
            rate = await self.repository.create(rate_dict)

            logger.info(
                f"Created billing rate: {rate.rateName} (ID: {rate.id})")
            return self._to_response_model(rate)

        except Exception as e:
            logger.error(f"Error creating billing rate: {str(e)}")
            raise

    async def update_rate(self, rate_id: int, rate_data: BillingRateUpdate) -> BillingRateResponse:
        """Update an existing billing rate"""
        try:
            # Check if rate exists
            existing_rate = await self.repository.get_by_id(rate_id)
            if not existing_rate:
                raise NotFoundError(
                    f"Billing rate with ID {rate_id} not found")

            # Prepare update data
            update_dict = {k: v for k, v in rate_data.dict().items()
                           if v is not None}
            # TODO: Get from current user context
            update_dict['updateby'] = 'system'

            # Validate business rules
            if update_dict:
                self._validate_rate_data(update_dict)

            # Update rate
            updated_rate = await self.repository.update(rate_id, update_dict)

            logger.info(
                f"Updated billing rate: {updated_rate.rateName} (ID: {rate_id})")
            return self._to_response_model(updated_rate)

        except Exception as e:
            logger.error(f"Error updating billing rate {rate_id}: {str(e)}")
            raise

    async def delete_rate(self, rate_id: int) -> bool:
        """Delete a billing rate"""
        try:
            # Check if rate exists
            rate = await self.repository.get_by_id(rate_id)
            if not rate:
                raise NotFoundError(
                    f"Billing rate with ID {rate_id} not found")

            # Delete rate
            success = await self.repository.delete(rate_id)

            if success:
                logger.info(
                    f"Deleted billing rate: {rate.rateName} (ID: {rate_id})")

            return success

        except Exception as e:
            logger.error(f"Error deleting billing rate {rate_id}: {str(e)}")
            raise

    def _validate_rate_data(self, rate_data: Dict[str, Any]) -> None:
        """Validate billing rate data according to business rules"""
        # Validate rate cost is non-negative
        if 'rateCost' in rate_data:
            try:
                cost = int(rate_data['rateCost'])
                if cost < 0:
                    raise ValidationError("Rate cost cannot be negative")
            except (ValueError, TypeError):
                raise ValidationError("Rate cost must be a valid number")

    def _to_response_model(self, rate) -> BillingRateResponse:
        """Convert database model to response model"""
        return BillingRateResponse(
            id=rate.id,
            rateName=rate.rateName or "",
            rateType=rate.rateType or "",
            rateCost=rate.rateCost or 0,
            creationdate=rate.creationdate,
            creationby=rate.creationby or "",
            updatedate=rate.updatedate,
            updateby=rate.updateby or ""
        )


class BillingMerchantService:
    """Service for billing merchant operations"""

    def __init__(self, repository: BillingMerchantRepository):
        self.repository = repository

    async def get_transactions(
        self,
        page: int = 1,
        page_size: int = 10,
        username_filter: Optional[str] = None,
        business_id_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "desc"
    ) -> PaginatedResponse:
        """Get paginated merchant transactions with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            merchants, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                username_filter=username_filter,
                business_id_filter=business_id_filter,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            merchant_responses = [self._to_response_model(
                merchant) for merchant in merchants]

            return PaginatedResponse(
                data=merchant_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )

        except Exception as e:
            logger.error(f"Error getting merchant transactions: {str(e)}")
            raise

    async def create_transaction(self, transaction_data: MerchantTransactionCreate) -> MerchantTransactionResponse:
        """Create a new merchant transaction"""
        try:
            # Validate transaction data
            self._validate_transaction_data(transaction_data.dict())

            # Prepare data for creation
            transaction_dict = transaction_data.dict()
            transaction_dict['creationdate'] = datetime.utcnow()
            # TODO: Get from current user context
            transaction_dict['creationby'] = 'system'

            # Create transaction
            transaction = await self.repository.create(transaction_dict)

            logger.info(
                f"Created merchant transaction for user: {transaction.username} (ID: {transaction.id})")
            return self._to_response_model(transaction)

        except Exception as e:
            logger.error(f"Error creating merchant transaction: {str(e)}")
            raise

    def _validate_transaction_data(self, transaction_data: Dict[str, Any]) -> None:
        """Validate merchant transaction data according to business rules"""
        # Validate required fields
        required_fields = ['username', 'planId',
                           'txnId', 'business_email', 'business_id']
        for field in required_fields:
            if field not in transaction_data or not transaction_data[field]:
                raise ValidationError(
                    f"Required field '{field}' is missing or empty")

        # Validate email format
        if 'business_email' in transaction_data:
            email = transaction_data['business_email']
            if '@' not in email or '.' not in email:
                raise ValidationError("Invalid email format")

    def _to_response_model(self, merchant) -> MerchantTransactionResponse:
        """Convert database model to response model"""
        return MerchantTransactionResponse(
            id=merchant.id,
            username=merchant.username or "",
            planId=merchant.planId or 0,
            txnId=merchant.txnId or "",
            planName=merchant.planName or "",
            quantity=merchant.quantity or "",
            business_email=merchant.business_email or "",
            business_id=merchant.business_id or "",
            txn_type=merchant.txn_type or "",
            txn_id=merchant.txn_id or "",
            payment_type=merchant.payment_type or "",
            creationdate=merchant.creationdate,
            creationby=merchant.creationby or ""
        )


# =====================================================================
# Invoice Service
# =====================================================================

class InvoiceService:
    """Service for invoice operations"""

    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    async def get_invoices(
        self,
        page: int = 1,
        page_size: int = 10,
        customer_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated invoices with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get invoices from repository
            invoices, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                customer_filter=customer_filter,
                status_filter=status_filter,
                date_from=date_from,
                date_to=date_to,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            invoice_responses = [self._to_response_model(
                invoice) for invoice in invoices]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                data=invoice_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_invoices: {str(e)}")
            raise BusinessLogicError(f"Failed to get invoices: {str(e)}")

    async def get_invoice(self, invoice_id: int) -> InvoiceResponse:
        """Get invoice by ID"""
        try:
            invoice = await self.repository.get_by_id(invoice_id)
            if not invoice:
                raise NotFoundError(f"Invoice with ID {invoice_id} not found")

            return self._to_response_model(invoice)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_invoice: {str(e)}")
            raise BusinessLogicError(f"Failed to get invoice: {str(e)}")

    async def create_invoice(self, invoice_data: InvoiceCreate) -> InvoiceResponse:
        """Create a new invoice"""
        try:
            # Validate business rules
            self._validate_invoice_data(invoice_data.model_dump())

            # Generate invoice number if not provided
            invoice_dict = invoice_data.model_dump(exclude_unset=True)
            if not invoice_dict.get('invoice_number'):
                invoice_dict['invoice_number'] = await self._generate_invoice_number()

            # Set creation metadata
            invoice_dict['creationdate'] = datetime.utcnow()
            # Should come from auth context
            invoice_dict['creationby'] = 'system'

            # Create invoice
            invoice = await self.repository.create(invoice_dict)

            logger.info(f"Invoice created with ID: {invoice.id}")
            return self._to_response_model(invoice)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in create_invoice: {str(e)}")
            raise BusinessLogicError(f"Failed to create invoice: {str(e)}")

    async def update_invoice(self, invoice_id: int, invoice_data: InvoiceUpdate) -> InvoiceResponse:
        """Update an existing invoice"""
        try:
            # Check if invoice exists
            existing_invoice = await self.repository.get_by_id(invoice_id)
            if not existing_invoice:
                raise NotFoundError(f"Invoice with ID {invoice_id} not found")

            # Validate business rules
            update_data = invoice_data.model_dump(exclude_unset=True)
            if update_data:
                self._validate_invoice_data(update_data)

            # Set update metadata
            update_data['updatedate'] = datetime.utcnow()
            update_data['updateby'] = 'system'  # Should come from auth context

            # Update invoice
            invoice = await self.repository.update(invoice_id, update_data)

            logger.info(f"Invoice updated: {invoice_id}")
            return self._to_response_model(invoice)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in update_invoice: {str(e)}")
            raise BusinessLogicError(f"Failed to update invoice: {str(e)}")

    async def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        try:
            # Check if invoice exists
            existing_invoice = await self.repository.get_by_id(invoice_id)
            if not existing_invoice:
                raise NotFoundError(f"Invoice with ID {invoice_id} not found")

            # Business rule: Can't delete paid invoices
            if existing_invoice.status == 'paid':
                raise ValidationError("Cannot delete a paid invoice")

            # Delete invoice
            result = await self.repository.delete(invoice_id)

            if result:
                logger.info(f"Invoice deleted: {invoice_id}")

            return result

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in delete_invoice: {str(e)}")
            raise BusinessLogicError(f"Failed to delete invoice: {str(e)}")

    async def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INV-{timestamp}"

    def _validate_invoice_data(self, invoice_data: Dict[str, Any]) -> None:
        """Validate invoice data according to business rules"""
        # Validate amounts
        if 'total_amount' in invoice_data and invoice_data['total_amount'] < 0:
            raise ValidationError("Total amount cannot be negative")

        # Validate dates
        if 'issue_date' in invoice_data and 'due_date' in invoice_data:
            if invoice_data['due_date'] < invoice_data['issue_date']:
                raise ValidationError("Due date cannot be before issue date")

    def _to_response_model(self, invoice) -> InvoiceResponse:
        """Convert database model to response model"""
        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=invoice.customer_name,
            customer_email=invoice.customer_email,
            customer_address=invoice.customer_address,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            currency=invoice.currency,
            status=invoice.status,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            paid_date=invoice.paid_date,
            description=invoice.description,
            notes=invoice.notes,
            terms_conditions=invoice.terms_conditions,
            creationdate=invoice.creationdate,
            creationby=invoice.creationby,
            updatedate=invoice.updatedate,
            updateby=invoice.updateby
        )


# =====================================================================
# Payment Service
# =====================================================================

class PaymentService:
    """Service for payment operations"""

    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    async def get_payments(
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
    ) -> PaginatedResponse:
        """Get paginated payments with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get payments from repository
            payments, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                customer_filter=customer_filter,
                payment_method_filter=payment_method_filter,
                status_filter=status_filter,
                date_from=date_from,
                date_to=date_to,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            payment_responses = [self._to_response_model(
                payment) for payment in payments]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                data=payment_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_payments: {str(e)}")
            raise BusinessLogicError(f"Failed to get payments: {str(e)}")

    async def get_payment(self, payment_id: int) -> PaymentResponse:
        """Get payment by ID"""
        try:
            payment = await self.repository.get_by_id(payment_id)
            if not payment:
                raise NotFoundError(f"Payment with ID {payment_id} not found")

            return self._to_response_model(payment)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_payment: {str(e)}")
            raise BusinessLogicError(f"Failed to get payment: {str(e)}")

    async def create_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """Create a new payment"""
        try:
            # Validate business rules
            self._validate_payment_data(payment_data.model_dump())

            # Generate payment number if not provided
            payment_dict = payment_data.model_dump(exclude_unset=True)
            if not payment_dict.get('payment_number'):
                payment_dict['payment_number'] = await self._generate_payment_number()

            # Set payment date if not provided
            if not payment_dict.get('payment_date'):
                payment_dict['payment_date'] = datetime.utcnow()

            # Set creation metadata
            payment_dict['creationdate'] = datetime.utcnow()
            # Should come from auth context
            payment_dict['creationby'] = 'system'

            # Create payment
            payment = await self.repository.create(payment_dict)

            logger.info(f"Payment created with ID: {payment.id}")
            return self._to_response_model(payment)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in create_payment: {str(e)}")
            raise BusinessLogicError(f"Failed to create payment: {str(e)}")

    async def update_payment(self, payment_id: int, payment_data: PaymentUpdate) -> PaymentResponse:
        """Update an existing payment"""
        try:
            # Check if payment exists
            existing_payment = await self.repository.get_by_id(payment_id)
            if not existing_payment:
                raise NotFoundError(f"Payment with ID {payment_id} not found")

            # Validate business rules
            update_data = payment_data.model_dump(exclude_unset=True)
            if update_data:
                self._validate_payment_data(update_data)

            # Set update metadata
            update_data['updatedate'] = datetime.utcnow()
            update_data['updateby'] = 'system'  # Should come from auth context

            # Update payment
            payment = await self.repository.update(payment_id, update_data)

            logger.info(f"Payment updated: {payment_id}")
            return self._to_response_model(payment)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in update_payment: {str(e)}")
            raise BusinessLogicError(f"Failed to update payment: {str(e)}")

    async def delete_payment(self, payment_id: int) -> bool:
        """Delete a payment"""
        try:
            # Check if payment exists
            existing_payment = await self.repository.get_by_id(payment_id)
            if not existing_payment:
                raise NotFoundError(f"Payment with ID {payment_id} not found")

            # Business rule: Can't delete successful payments
            if existing_payment.status == 'success':
                raise ValidationError("Cannot delete a successful payment")

            # Delete payment
            result = await self.repository.delete(payment_id)

            if result:
                logger.info(f"Payment deleted: {payment_id}")

            return result

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in delete_payment: {str(e)}")
            raise BusinessLogicError(f"Failed to delete payment: {str(e)}")

    async def _generate_payment_number(self) -> str:
        """Generate a unique payment number"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PAY-{timestamp}"

    def _validate_payment_data(self, payment_data: Dict[str, Any]) -> None:
        """Validate payment data according to business rules"""
        # Validate amount
        if 'amount' in payment_data and payment_data['amount'] <= 0:
            raise ValidationError("Payment amount must be greater than 0")

    def _to_response_model(self, payment) -> PaymentResponse:
        """Convert database model to response model"""
        return PaymentResponse(
            id=payment.id,
            payment_number=payment.payment_number,
            customer_id=payment.customer_id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            payment_date=payment.payment_date,
            transaction_id=payment.transaction_id,
            reference_number=payment.reference_number,
            gateway=payment.gateway,
            status=payment.status,
            description=payment.description,
            notes=payment.notes,
            creationdate=payment.creationdate,
            creationby=payment.creationby,
            updatedate=payment.updatedate,
            updateby=payment.updateby
        )


# =====================================================================
# Refund Service
# =====================================================================

class RefundService:
    """Service for refund operations"""

    def __init__(self, repository: RefundRepository):
        self.repository = repository

    async def get_refunds(
        self,
        page: int = 1,
        page_size: int = 10,
        customer_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        payment_id_filter: Optional[int] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated refunds with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get refunds from repository
            refunds, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                customer_filter=customer_filter,
                status_filter=status_filter,
                payment_id_filter=payment_id_filter,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            refund_responses = [self._to_response_model(
                refund) for refund in refunds]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                data=refund_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_refunds: {str(e)}")
            raise BusinessLogicError(f"Failed to get refunds: {str(e)}")

    async def get_refund(self, refund_id: int) -> RefundResponse:
        """Get refund by ID"""
        try:
            refund = await self.repository.get_by_id(refund_id)
            if not refund:
                raise NotFoundError(f"Refund with ID {refund_id} not found")

            return self._to_response_model(refund)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_refund: {str(e)}")
            raise BusinessLogicError(f"Failed to get refund: {str(e)}")

    async def create_refund(self, refund_data: RefundCreate) -> RefundResponse:
        """Create a new refund"""
        try:
            # Validate business rules
            await self._validate_refund_data(refund_data.model_dump())

            # Generate refund number if not provided
            refund_dict = refund_data.model_dump(exclude_unset=True)
            if not refund_dict.get('refund_number'):
                refund_dict['refund_number'] = await self._generate_refund_number()

            # Set refund date if not provided
            if not refund_dict.get('refund_date'):
                refund_dict['refund_date'] = datetime.utcnow()

            # Set creation metadata
            refund_dict['creationdate'] = datetime.utcnow()
            # Should come from auth context
            refund_dict['creationby'] = 'system'

            # Create refund
            refund = await self.repository.create(refund_dict)

            logger.info(f"Refund created with ID: {refund.id}")
            return self._to_response_model(refund)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in create_refund: {str(e)}")
            raise BusinessLogicError(f"Failed to create refund: {str(e)}")

    async def update_refund(self, refund_id: int, refund_data: RefundUpdate) -> RefundResponse:
        """Update an existing refund"""
        try:
            # Check if refund exists
            existing_refund = await self.repository.get_by_id(refund_id)
            if not existing_refund:
                raise NotFoundError(f"Refund with ID {refund_id} not found")

            # Validate business rules
            update_data = refund_data.model_dump(exclude_unset=True)
            if update_data:
                await self._validate_refund_data(update_data)

            # Set update metadata
            update_data['updatedate'] = datetime.utcnow()
            update_data['updateby'] = 'system'  # Should come from auth context

            # Update refund
            refund = await self.repository.update(refund_id, update_data)

            logger.info(f"Refund updated: {refund_id}")
            return self._to_response_model(refund)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in update_refund: {str(e)}")
            raise BusinessLogicError(f"Failed to update refund: {str(e)}")

    async def delete_refund(self, refund_id: int) -> bool:
        """Delete a refund"""
        try:
            # Check if refund exists
            existing_refund = await self.repository.get_by_id(refund_id)
            if not existing_refund:
                raise NotFoundError(f"Refund with ID {refund_id} not found")

            # Business rule: Can't delete processed refunds
            if existing_refund.status == 'processed':
                raise ValidationError("Cannot delete a processed refund")

            # Delete refund
            result = await self.repository.delete(refund_id)

            if result:
                logger.info(f"Refund deleted: {refund_id}")

            return result

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in delete_refund: {str(e)}")
            raise BusinessLogicError(f"Failed to delete refund: {str(e)}")

    async def _generate_refund_number(self) -> str:
        """Generate a unique refund number"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"REF-{timestamp}"

    async def _validate_refund_data(self, refund_data: Dict[str, Any]) -> None:
        """Validate refund data according to business rules"""
        # Validate amount
        if 'amount' in refund_data and refund_data['amount'] <= 0:
            raise ValidationError("Refund amount must be greater than 0")

        # Validate payment exists and has sufficient amount
        if 'payment_id' in refund_data:
            # This would need to check against the actual payment
            # For now, we'll just validate the ID exists
            pass

    def _to_response_model(self, refund) -> RefundResponse:
        """Convert database model to response model"""
        return RefundResponse(
            id=refund.id,
            refund_number=refund.refund_number,
            payment_id=refund.payment_id,
            customer_id=refund.customer_id,
            amount=refund.amount,
            currency=refund.currency,
            refund_date=refund.refund_date,
            reason=refund.reason,
            status=refund.status,
            transaction_id=refund.transaction_id,
            gateway=refund.gateway,
            notes=refund.notes,
            creationdate=refund.creationdate,
            creationby=refund.creationby,
            updatedate=refund.updatedate,
            updateby=refund.updateby
        )


# =====================================================================
# Payment Type Service
# =====================================================================

class PaymentTypeService:
    """Service for payment type operations"""

    def __init__(self, repository: PaymentTypeRepository):
        self.repository = repository

    async def get_payment_types(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        active_only: bool = False,
        sort_field: str = "sort_order",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated payment types with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get payment types from repository
            payment_types, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                name_filter=name_filter,
                active_only=active_only,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            payment_type_responses = [self._to_response_model(
                payment_type) for payment_type in payment_types]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                data=payment_type_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_payment_types: {str(e)}")
            raise BusinessLogicError(f"Failed to get payment types: {str(e)}")

    async def get_payment_type(self, payment_type_id: int) -> PaymentTypeResponse:
        """Get payment type by ID"""
        try:
            payment_type = await self.repository.get_by_id(payment_type_id)
            if not payment_type:
                raise NotFoundError(
                    f"Payment type with ID {payment_type_id} not found")

            return self._to_response_model(payment_type)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_payment_type: {str(e)}")
            raise BusinessLogicError(f"Failed to get payment type: {str(e)}")

    async def create_payment_type(self, payment_type_data: PaymentTypeCreate) -> PaymentTypeResponse:
        """Create a new payment type"""
        try:
            # Validate business rules
            self._validate_payment_type_data(payment_type_data.model_dump())

            # Check code uniqueness
            existing = await self.repository.get_by_code(payment_type_data.code)
            if existing:
                raise ValidationError(
                    f"Payment type with code '{payment_type_data.code}' already exists")

            # Set creation metadata
            payment_type_dict = payment_type_data.model_dump(
                exclude_unset=True)
            payment_type_dict['creationdate'] = datetime.utcnow()
            # Should come from auth context
            payment_type_dict['creationby'] = 'system'

            # Create payment type
            payment_type = await self.repository.create(payment_type_dict)

            logger.info(f"Payment type created with ID: {payment_type.id}")
            return self._to_response_model(payment_type)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in create_payment_type: {str(e)}")
            raise BusinessLogicError(
                f"Failed to create payment type: {str(e)}")

    async def update_payment_type(self, payment_type_id: int, payment_type_data: PaymentTypeUpdate) -> PaymentTypeResponse:
        """Update an existing payment type"""
        try:
            # Check if payment type exists
            existing_payment_type = await self.repository.get_by_id(payment_type_id)
            if not existing_payment_type:
                raise NotFoundError(
                    f"Payment type with ID {payment_type_id} not found")

            # Validate business rules
            update_data = payment_type_data.model_dump(exclude_unset=True)
            if update_data:
                self._validate_payment_type_data(update_data)

            # Check code uniqueness if code is being updated
            if 'code' in update_data and update_data['code'] != existing_payment_type.code:
                existing = await self.repository.get_by_code(update_data['code'])
                if existing:
                    raise ValidationError(
                        f"Payment type with code '{update_data['code']}' already exists")

            # Set update metadata
            update_data['updatedate'] = datetime.utcnow()
            update_data['updateby'] = 'system'  # Should come from auth context

            # Update payment type
            payment_type = await self.repository.update(payment_type_id, update_data)

            logger.info(f"Payment type updated: {payment_type_id}")
            return self._to_response_model(payment_type)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in update_payment_type: {str(e)}")
            raise BusinessLogicError(
                f"Failed to update payment type: {str(e)}")

    async def delete_payment_type(self, payment_type_id: int) -> bool:
        """Delete a payment type"""
        try:
            # Check if payment type exists
            existing_payment_type = await self.repository.get_by_id(payment_type_id)
            if not existing_payment_type:
                raise NotFoundError(
                    f"Payment type with ID {payment_type_id} not found")

            # Delete payment type
            result = await self.repository.delete(payment_type_id)

            if result:
                logger.info(f"Payment type deleted: {payment_type_id}")

            return result

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_payment_type: {str(e)}")
            raise BusinessLogicError(
                f"Failed to delete payment type: {str(e)}")

    def _validate_payment_type_data(self, payment_type_data: Dict[str, Any]) -> None:
        """Validate payment type data according to business rules"""
        # Validate fees
        if 'percentage_fee' in payment_type_data and payment_type_data['percentage_fee'] < 0:
            raise ValidationError("Percentage fee cannot be negative")

        if 'fixed_fee' in payment_type_data and payment_type_data['fixed_fee'] < 0:
            raise ValidationError("Fixed fee cannot be negative")

    def _to_response_model(self, payment_type) -> PaymentTypeResponse:
        """Convert database model to response model"""
        return PaymentTypeResponse(
            id=payment_type.id,
            name=payment_type.name,
            display_name=payment_type.display_name,
            code=payment_type.code,
            is_active=payment_type.is_active,
            is_online=payment_type.is_online,
            requires_gateway=payment_type.requires_gateway,
            gateway_name=payment_type.gateway_name,
            gateway_config=payment_type.gateway_config,
            fixed_fee=payment_type.fixed_fee,
            percentage_fee=payment_type.percentage_fee,
            min_amount=payment_type.min_amount,
            max_amount=payment_type.max_amount,
            description=payment_type.description,
            icon=payment_type.icon,
            sort_order=payment_type.sort_order,
            creationdate=payment_type.creationdate,
            creationby=payment_type.creationby,
            updatedate=payment_type.updatedate,
            updateby=payment_type.updateby
        )


# =====================================================================
# POS Service
# =====================================================================

class POSService:
    """Service for POS terminal operations"""

    def __init__(self, repository: POSRepository):
        self.repository = repository

    async def get_terminals(
        self,
        page: int = 1,
        page_size: int = 10,
        name_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        sort_field: str = "id",
        sort_order: str = "asc"
    ) -> PaginatedResponse:
        """Get paginated POS terminals with filtering"""
        try:
            # Validate pagination parameters
            if page < 1:
                raise ValidationError("Page must be greater than 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("Page size must be between 1 and 100")

            # Get terminals from repository
            terminals, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                name_filter=name_filter,
                location_filter=location_filter,
                status_filter=status_filter,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Convert to response models
            terminal_responses = [self._to_response_model(
                terminal) for terminal in terminals]

            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size

            return PaginatedResponse(
                data=terminal_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Error in get_terminals: {str(e)}")
            raise BusinessLogicError(f"Failed to get terminals: {str(e)}")

    async def get_terminal(self, pos_id: int) -> POSResponse:
        """Get POS terminal by ID"""
        try:
            terminal = await self.repository.get_by_id(pos_id)
            if not terminal:
                raise NotFoundError(f"POS terminal with ID {pos_id} not found")

            return self._to_response_model(terminal)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in get_terminal: {str(e)}")
            raise BusinessLogicError(f"Failed to get terminal: {str(e)}")

    async def create_terminal(self, pos_data: POSCreate) -> POSResponse:
        """Create a new POS terminal"""
        try:
            # Validate business rules
            self._validate_pos_data(pos_data.model_dump())

            # Check serial number uniqueness
            existing = await self.repository.get_by_serial_number(pos_data.serial_number)
            if existing:
                raise ValidationError(
                    f"POS terminal with serial number '{pos_data.serial_number}' already exists")

            # Set creation metadata
            pos_dict = pos_data.model_dump(exclude_unset=True)
            pos_dict['creationdate'] = datetime.utcnow()
            pos_dict['creationby'] = 'system'  # Should come from auth context
            pos_dict['last_heartbeat'] = datetime.utcnow()

            # Create terminal
            terminal = await self.repository.create(pos_dict)

            logger.info(f"POS terminal created with ID: {terminal.id}")
            return self._to_response_model(terminal)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error in create_terminal: {str(e)}")
            raise BusinessLogicError(f"Failed to create terminal: {str(e)}")

    async def update_terminal(self, pos_id: int, pos_data: POSUpdate) -> POSResponse:
        """Update an existing POS terminal"""
        try:
            # Check if terminal exists
            existing_terminal = await self.repository.get_by_id(pos_id)
            if not existing_terminal:
                raise NotFoundError(f"POS terminal with ID {pos_id} not found")

            # Validate business rules
            update_data = pos_data.model_dump(exclude_unset=True)
            if update_data:
                self._validate_pos_data(update_data)

            # Check serial number uniqueness if serial number is being updated
            if 'serial_number' in update_data and update_data['serial_number'] != existing_terminal.serial_number:
                existing = await self.repository.get_by_serial_number(update_data['serial_number'])
                if existing:
                    raise ValidationError(
                        f"POS terminal with serial number '{update_data['serial_number']}' already exists")

            # Set update metadata
            update_data['updatedate'] = datetime.utcnow()
            update_data['updateby'] = 'system'  # Should come from auth context

            # Update terminal
            terminal = await self.repository.update(pos_id, update_data)

            logger.info(f"POS terminal updated: {pos_id}")
            return self._to_response_model(terminal)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error in update_terminal: {str(e)}")
            raise BusinessLogicError(f"Failed to update terminal: {str(e)}")

    async def delete_terminal(self, pos_id: int) -> bool:
        """Delete a POS terminal"""
        try:
            # Check if terminal exists
            existing_terminal = await self.repository.get_by_id(pos_id)
            if not existing_terminal:
                raise NotFoundError(f"POS terminal with ID {pos_id} not found")

            # Delete terminal
            result = await self.repository.delete(pos_id)

            if result:
                logger.info(f"POS terminal deleted: {pos_id}")

            return result

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error in delete_terminal: {str(e)}")
            raise BusinessLogicError(f"Failed to delete terminal: {str(e)}")

    def _validate_pos_data(self, pos_data: Dict[str, Any]) -> None:
        """Validate POS terminal data according to business rules"""
        # Validate IP address format if provided
        if 'ip_address' in pos_data and pos_data['ip_address']:
            import ipaddress
            try:
                ipaddress.ip_address(pos_data['ip_address'])
            except ValueError:
                raise ValidationError("Invalid IP address format")

        # Validate MAC address format if provided
        if 'mac_address' in pos_data and pos_data['mac_address']:
            import re
            mac_pattern = re.compile(
                r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
            if not mac_pattern.match(pos_data['mac_address']):
                raise ValidationError("Invalid MAC address format")

    def _to_response_model(self, terminal) -> POSResponse:
        """Convert database model to response model"""
        return POSResponse(
            id=terminal.id,
            name=terminal.name,
            serial_number=terminal.serial_number,
            model=terminal.model,
            manufacturer=terminal.manufacturer,
            location_id=terminal.location_id,
            location_name=terminal.location_name,
            assigned_user=terminal.assigned_user,
            ip_address=terminal.ip_address,
            mac_address=terminal.mac_address,
            network_config=terminal.network_config,
            status=terminal.status,
            last_heartbeat=terminal.last_heartbeat,
            last_transaction=terminal.last_transaction,
            supports_contactless=terminal.supports_contactless,
            supports_chip=terminal.supports_chip,
            supports_pin=terminal.supports_pin,
            supports_receipt_print=terminal.supports_receipt_print,
            terminal_config=terminal.terminal_config,
            firmware_version=terminal.firmware_version,
            description=terminal.description,
            notes=terminal.notes,
            creationdate=terminal.creationdate,
            creationby=terminal.creationby,
            updatedate=terminal.updatedate,
            updateby=terminal.updateby
        )
