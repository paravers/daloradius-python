"""
User Management Repository Implementations

This module contains repository classes for user management operations
including users, operators, groups, and their relationships.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.exc import IntegrityError

from .base import BaseRepository
from ..models.user import User, UserInfo, UserGroup, Operator, UserBillingInfo
from ..schemas.user import (
    UserCreate, UserUpdate, GroupCreate, GroupUpdate, 
    OperatorCreate, OperatorUpdate, UserGroupCreate
)


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for user queries (simplified for initial implementation)"""
        # For now, return query without relationship loading
        # Will be enhanced when relationships are properly defined
        return query

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.get_by_field("username", username, load_relationships=True)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return await self.get_by_field("email", email, load_relationships=True)

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            User instance if authenticated, None otherwise
        """
        user = await self.get_by_username(username)
        if user and user.verify_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            await self.db.commit()
            return user
        return None

    async def create_with_info(
        self, 
        user_data: UserCreate,
        user_info_data: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create user with optional user info
        
        Args:
            user_data: User creation data
            user_info_data: Additional user info data
            
        Returns:
            Created user instance
        """
        # Create user
        user = await self.create(user_data)
        
        # Create user info if provided
        if user_info_data:
            user_info = UserInfo(
                username=user.username,
                **user_info_data
            )
            self.db.add(user_info)
            await self.db.commit()
            await self.db.refresh(user)
            
        return user

    async def update_password(self, user: User, new_password: str) -> User:
        """
        Update user password
        
        Args:
            user: User instance
            new_password: New plain text password
            
        Returns:
            Updated user instance
        """
        user.set_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_users_by_status(
        self, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get users by status"""
        filters = {"status": status}
        return await self.get_multi(
            skip=skip, 
            limit=limit, 
            filters=filters,
            load_relationships=True
        )

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users"""
        filters = {"is_active": True}
        return await self.get_multi(
            skip=skip, 
            limit=limit, 
            filters=filters,
            load_relationships=True
        )

    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """
        Search users across multiple fields
        
        Args:
            search_term: Text to search for
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Additional filters
            
        Returns:
            List of matching users
        """
        search_fields = [
            "username", "email", "first_name", "last_name", 
            "department", "company"
        ]
        return await self.search(
            search_term=search_term,
            search_fields=search_fields,
            skip=skip,
            limit=limit,
            filters=filters
        )

    async def get_users_by_group(
        self, 
        groupname: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """
        Get users belonging to a specific group
        
        Args:
            groupname: Group name
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users in the group
        """
        query = (
            select(User)
            .join(User.groups)
            .where(UserGroup.groupname == groupname)
            .offset(skip)
            .limit(limit)
        )
        
        query = self._add_relationship_loading(query)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_users_created_between(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users created within date range"""
        filters = {
            "created_at": {
                ">=": start_date,
                "<=": end_date
            }
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="created_at",
            order_desc=True
        )

    async def count_users_by_status(self) -> Dict[str, int]:
        """Get user count by status"""
        query = (
            select(User.status, func.count(User.id))
            .group_by(User.status)
        )
        
        result = await self.db.execute(query)
        return dict(result.all())

    async def get_recently_active_users(
        self,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users who logged in within the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filters = {
            "last_login": {">=": cutoff_date}
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="last_login",
            order_desc=True
        )


class UserGroupRepository(BaseRepository[UserGroup, UserGroupCreate, None]):
    """Repository for UserGroup model operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(UserGroup, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for user group queries"""
        return query

    async def get_by_groupname(self, groupname: str) -> Optional[UserGroup]:
        """Get group by name"""
        return await self.get_by_field("groupname", groupname)

    async def get_user_groups(self, username: str) -> List[UserGroup]:
        """Get all groups for a user"""
        filters = {"username": username}
        return await self.get_multi(filters=filters, order_by="priority")

    async def get_group_users(self, groupname: str) -> List[UserGroup]:
        """Get all users in a group"""
        filters = {"groupname": groupname}
        return await self.get_multi(filters=filters, order_by="priority")

    async def add_user_to_group(
        self, 
        username: str, 
        groupname: str, 
        priority: int = 1
    ) -> UserGroup:
        """Add user to group"""
        user_group_data = UserGroupCreate(
            username=username,
            groupname=groupname,
            priority=priority
        )
        return await self.create(user_group_data)

    async def remove_user_from_group(
        self, 
        username: str, 
        groupname: str
    ) -> bool:
        """Remove user from group"""
        query = select(UserGroup).where(
            and_(
                UserGroup.username == username,
                UserGroup.groupname == groupname
            )
        )
        result = await self.db.execute(query)
        user_group = result.scalar_one_or_none()
        
        if user_group:
            await self.delete(user_group.id)
            return True
        return False

    async def update_user_group_priority(
        self,
        username: str,
        groupname: str,
        priority: int
    ) -> Optional[UserGroup]:
        """Update user's priority in a group"""
        query = select(UserGroup).where(
            and_(
                UserGroup.username == username,
                UserGroup.groupname == groupname
            )
        )
        result = await self.db.execute(query)
        user_group = result.scalar_one_or_none()
        
        if user_group:
            user_group.priority = priority
            await self.db.commit()
            await self.db.refresh(user_group)
            
        return user_group

    async def get_groups_with_user_count(self) -> List[Dict[str, Any]]:
        """Get all groups with user count"""
        query = (
            select(
                UserGroup.groupname,
                func.count(UserGroup.username).label('user_count')
            )
            .group_by(UserGroup.groupname)
            .order_by(UserGroup.groupname)
        )
        
        result = await self.db.execute(query)
        return [
            {
                "groupname": row.groupname,
                "user_count": row.user_count
            }
            for row in result.all()
        ]


class OperatorRepository(BaseRepository[Operator, OperatorCreate, OperatorUpdate]):
    """Repository for Operator model operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Operator, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for operator queries"""
        return query

    async def get_by_username(self, username: str) -> Optional[Operator]:
        """Get operator by username"""
        return await self.get_by_field("username", username)

    async def authenticate(self, username: str, password: str) -> Optional[Operator]:
        """
        Authenticate operator with username and password
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Operator instance if authenticated, None otherwise
        """
        operator = await self.get_by_username(username)
        if operator and operator.verify_password(password):
            # Update last login
            operator.last_login = datetime.utcnow()
            await self.db.commit()
            return operator
        return None

    async def update_password(self, operator: Operator, new_password: str) -> Operator:
        """Update operator password"""
        operator.set_password(new_password)
        await self.db.commit()
        await self.db.refresh(operator)
        return operator

    async def get_active_operators(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Operator]:
        """Get active operators"""
        filters = {"is_active": True}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="username"
        )

    async def search_operators(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Operator]:
        """Search operators"""
        search_fields = ["username", "fullname", "email", "department"]
        return await self.search(
            search_term=search_term,
            search_fields=search_fields,
            skip=skip,
            limit=limit
        )

    async def update_permissions(
        self, 
        operator: Operator, 
        permissions: Dict[str, Any]
    ) -> Operator:
        """Update operator permissions"""
        import json
        operator.permissions = json.dumps(permissions)
        await self.db.commit()
        await self.db.refresh(operator)
        return operator

    async def get_operators_by_department(
        self,
        department: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Operator]:
        """Get operators by department"""
        filters = {"department": department}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="username"
        )


class UserBillingInfoRepository(BaseRepository[UserBillingInfo, None, None]):
    """Repository for UserBillingInfo model operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(UserBillingInfo, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for user billing info queries"""
        return query.options(
            joinedload(UserBillingInfo.user)
        )

    async def get_by_username(self, username: str) -> Optional[UserBillingInfo]:
        """Get billing info by username"""
        return await self.get_by_field("username", username, load_relationships=True)

    async def create_billing_info(
        self,
        username: str,
        billing_data: Dict[str, Any]
    ) -> UserBillingInfo:
        """Create billing info for user"""
        billing_info = UserBillingInfo(
            username=username,
            **billing_data
        )
        self.db.add(billing_info)
        await self.db.commit()
        await self.db.refresh(billing_info)
        return billing_info

    async def update_account_balance(
        self,
        username: str,
        amount: float,
        operation: str = "add"  # "add" or "subtract"
    ) -> Optional[UserBillingInfo]:
        """Update user account balance"""
        billing_info = await self.get_by_username(username)
        if not billing_info:
            return None
            
        if operation == "add":
            billing_info.account_balance += amount
        elif operation == "subtract":
            billing_info.account_balance -= amount
            
        await self.db.commit()
        await self.db.refresh(billing_info)
        return billing_info

    async def get_users_with_negative_balance(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserBillingInfo]:
        """Get users with negative account balance"""
        filters = {"account_balance": {"<": 0}}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="account_balance",
            load_relationships=True
        )

    async def get_users_by_plan(
        self,
        plan_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserBillingInfo]:
        """Get users by billing plan"""
        filters = {"plan_name": plan_name}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="username",
            load_relationships=True
        )

    async def get_expiring_subscriptions(
        self,
        days_ahead: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserBillingInfo]:
        """Get subscriptions expiring within N days"""
        from datetime import timedelta
        
        end_date = datetime.utcnow().date() + timedelta(days=days_ahead)
        filters = {
            "billing_cycle_end": {"<=": end_date},
            "billing_status": "active"
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="billing_cycle_end",
            load_relationships=True
        )