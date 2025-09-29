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
    BillingRate, BillingPlanProfile
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
                query = query.filter(BillingPlan.planName.ilike(f"%{name_filter}%"))
            
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
            logger.error(f"Error fetching billing plan by name {plan_name}: {str(e)}")
            raise DatabaseError(f"Failed to fetch billing plan by name: {str(e)}")
    
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
            raise DatabaseError(f"Failed to fetch active billing plans: {str(e)}")
    
    async def get_plan_statistics(self) -> Dict[str, Any]:
        """Get billing plan statistics"""
        try:
            total_plans = self.session.query(BillingPlan).count()
            active_plans = self.session.query(BillingPlan).filter(BillingPlan.planActive == True).count()
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
                query = query.filter(BillingHistory.username.ilike(f"%{username_filter}%"))
            
            if plan_id_filter:
                query = query.filter(BillingHistory.planId == plan_id_filter)
            
            if start_date:
                query = query.filter(BillingHistory.creationdate >= start_date)
            
            if end_date:
                query = query.filter(BillingHistory.creationdate <= end_date)
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            sort_column = getattr(BillingHistory, sort_field, BillingHistory.id)
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
            logger.error(f"Error fetching billing history {history_id}: {str(e)}")
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
            logger.error(f"Error fetching billing history for user {username}: {str(e)}")
            raise DatabaseError(f"Failed to fetch user billing history: {str(e)}")
    
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
            logger.error(f"Error fetching user statistics for {username}: {str(e)}")
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
                query = query.filter(BillingRate.rateName.ilike(f"%{name_filter}%"))
            
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
                query = query.filter(BillingMerchant.username.ilike(f"%{username_filter}%"))
            
            if business_id_filter:
                query = query.filter(BillingMerchant.business_id == business_id_filter)
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            sort_column = getattr(BillingMerchant, sort_field, BillingMerchant.id)
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
            raise DatabaseError(f"Failed to fetch merchant transactions: {str(e)}")
    
    async def get_by_id(self, merchant_id: int) -> Optional[BillingMerchant]:
        """Get merchant transaction by ID"""
        try:
            return self.session.query(BillingMerchant).filter(BillingMerchant.id == merchant_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching merchant transaction {merchant_id}: {str(e)}")
            raise DatabaseError(f"Failed to fetch merchant transaction: {str(e)}")
    
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
            raise DatabaseError(f"Failed to create merchant transaction: {str(e)}")