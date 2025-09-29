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
    BillingMerchantRepository
)
from app.schemas.billing import (
    BillingPlanCreate, BillingPlanUpdate, BillingPlanResponse,
    BillingHistoryCreate, BillingHistoryResponse,
    BillingRateCreate, BillingRateUpdate, BillingRateResponse,
    MerchantTransactionCreate, MerchantTransactionResponse,
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
                raise NotFoundError(f"Billing plan with ID {plan_id} not found")
            
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
                raise ValidationError(f"Plan with name '{plan_data.planName}' already exists")
            
            # Validate business rules
            self._validate_plan_data(plan_data.dict())
            
            # Prepare data for creation
            plan_dict = plan_data.dict()
            plan_dict['creationdate'] = datetime.utcnow()
            plan_dict['creationby'] = 'system'  # TODO: Get from current user context
            plan_dict['updatedate'] = datetime.utcnow()
            plan_dict['updateby'] = 'system'
            
            # Create plan
            plan = await self.repository.create(plan_dict)
            
            logger.info(f"Created billing plan: {plan.planName} (ID: {plan.id})")
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
                raise NotFoundError(f"Billing plan with ID {plan_id} not found")
            
            # Validate name uniqueness if changed
            if plan_data.planName and plan_data.planName != existing_plan.planName:
                name_check = await self.repository.get_by_name(plan_data.planName)
                if name_check and name_check.id != plan_id:
                    raise ValidationError(f"Plan with name '{plan_data.planName}' already exists")
            
            # Prepare update data
            update_dict = {k: v for k, v in plan_data.dict().items() if v is not None}
            update_dict['updateby'] = 'system'  # TODO: Get from current user context
            
            # Validate business rules
            if update_dict:
                self._validate_plan_data(update_dict)
            
            # Update plan
            updated_plan = await self.repository.update(plan_id, update_dict)
            
            logger.info(f"Updated billing plan: {updated_plan.planName} (ID: {plan_id})")
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
                raise NotFoundError(f"Billing plan with ID {plan_id} not found")
            
            # Check if plan is in use (business rule)
            # TODO: Check if plan has active subscriptions or history
            
            # Delete plan
            success = await self.repository.delete(plan_id)
            
            if success:
                logger.info(f"Deleted billing plan: {plan.planName} (ID: {plan_id})")
            
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
                    raise ValidationError("Time bank must be in HH:MM:SS format")
                
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
                        raise ValidationError(f"Invalid bandwidth format: {bandwidth_field}")
                except (ValueError, AttributeError):
                    raise ValidationError(f"Invalid bandwidth value: {bandwidth_field}")
        
        # Validate traffic values
        for traffic_field in ['planTrafficTotal', 'planTrafficUp', 'planTrafficDown']:
            if traffic_field in plan_data and plan_data[traffic_field]:
                try:
                    traffic_value = str(plan_data[traffic_field])
                    # Should be numeric or end with unit (MB, GB, TB)
                    if not (traffic_value.isdigit() or 
                           any(traffic_value.lower().endswith(unit) 
                               for unit in ['mb', 'gb', 'tb', 'kb'])):
                        raise ValidationError(f"Invalid traffic format: {traffic_field}")
                except (ValueError, AttributeError):
                    raise ValidationError(f"Invalid traffic value: {traffic_field}")
    
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
            history_responses = [self._to_response_model(record) for record in history]
            
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
            logger.error(f"Error getting user billing history for {username}: {str(e)}")
            raise
    
    async def create_history_record(self, history_data: BillingHistoryCreate) -> BillingHistoryResponse:
        """Create a new billing history record"""
        try:
            # Prepare data for creation
            history_dict = history_data.dict()
            history_dict['creationdate'] = datetime.utcnow()
            history_dict['creationby'] = 'system'  # TODO: Get from current user context
            
            # Create history record
            history = await self.repository.create(history_dict)
            
            logger.info(f"Created billing history record for user: {history.username} (ID: {history.id})")
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
            logger.error(f"Error getting user statistics for {username}: {str(e)}")
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
            rate_dict['creationby'] = 'system'  # TODO: Get from current user context
            rate_dict['updatedate'] = datetime.utcnow()
            rate_dict['updateby'] = 'system'
            
            # Create rate
            rate = await self.repository.create(rate_dict)
            
            logger.info(f"Created billing rate: {rate.rateName} (ID: {rate.id})")
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
                raise NotFoundError(f"Billing rate with ID {rate_id} not found")
            
            # Prepare update data
            update_dict = {k: v for k, v in rate_data.dict().items() if v is not None}
            update_dict['updateby'] = 'system'  # TODO: Get from current user context
            
            # Validate business rules
            if update_dict:
                self._validate_rate_data(update_dict)
            
            # Update rate
            updated_rate = await self.repository.update(rate_id, update_dict)
            
            logger.info(f"Updated billing rate: {updated_rate.rateName} (ID: {rate_id})")
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
                raise NotFoundError(f"Billing rate with ID {rate_id} not found")
            
            # Delete rate
            success = await self.repository.delete(rate_id)
            
            if success:
                logger.info(f"Deleted billing rate: {rate.rateName} (ID: {rate_id})")
            
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
            merchant_responses = [self._to_response_model(merchant) for merchant in merchants]
            
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
            transaction_dict['creationby'] = 'system'  # TODO: Get from current user context
            
            # Create transaction
            transaction = await self.repository.create(transaction_dict)
            
            logger.info(f"Created merchant transaction for user: {transaction.username} (ID: {transaction.id})")
            return self._to_response_model(transaction)
            
        except Exception as e:
            logger.error(f"Error creating merchant transaction: {str(e)}")
            raise
    
    def _validate_transaction_data(self, transaction_data: Dict[str, Any]) -> None:
        """Validate merchant transaction data according to business rules"""
        # Validate required fields
        required_fields = ['username', 'planId', 'txnId', 'business_email', 'business_id']
        for field in required_fields:
            if field not in transaction_data or not transaction_data[field]:
                raise ValidationError(f"Required field '{field}' is missing or empty")
        
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