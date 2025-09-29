"""
User Service Layer

Business logic for user management operations including
authentication, validation, and complex user operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import secrets
import string
import pandas as pd
import logging
import hashlib

from app.repositories.user import UserRepository
from app.models.user import User, UserInfo
from app.models.radius import RadAcct
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    BatchUserCreate, BatchOperationResult
)
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user management business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    async def create_user(
        self, 
        user_data: UserCreate, 
        created_by: Optional[str] = None
    ) -> UserResponse:
        """
        Create a new user with full validation and info creation
        
        Args:
            user_data: User creation data
            created_by: Username who created the user
            
        Returns:
            Created user response
        """
        # Hash the password
        user_data.password = get_password_hash(user_data.password)
        
        # Create user with additional fields
        user_dict = user_data.dict()
        user_dict['created_by'] = created_by
        user_dict['password_hash'] = user_dict.pop('password')
        
        # Create the user
        user = await self.user_repo.create(UserCreate(**user_dict))
        
        # Create corresponding UserInfo record for legacy compatibility
        user_info_data = {
            'username': user.username,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'email': user.email,
            'department': user.department,
            'company': user.company,
            'workphone': user.work_phone,
            'homephone': user.home_phone,
            'mobilephone': user.mobile_phone,
            'address': user.address,
            'city': user.city,
            'state': user.state,
            'country': user.country,
            'zip': user.zip,
            'creationdate': datetime.utcnow(),
            'creationby': created_by,
            'enableportallogin': 1 if user.enable_portal_login else 0,
            'changeuserinfo': 1 if user.change_user_info else 0
        }
        
        # Create UserInfo record
        user_info = UserInfo(**user_info_data)
        self.user_repo.db.add(user_info)
        await self.user_repo.db.commit()
        
        return UserResponse.from_orm(user)
    
    async def update_user(
        self, 
        user_id: int, 
        user_data: UserUpdate,
        updated_by: Optional[str] = None
    ) -> UserResponse:
        """
        Update user with validation and info sync
        
        Args:
            user_id: User ID to update
            user_data: Update data
            updated_by: Username who updated the user
            
        Returns:
            Updated user response
        """
        # Add audit fields
        update_dict = user_data.dict(exclude_unset=True)
        update_dict['updated_by'] = updated_by
        
        # Update user
        user = await self.user_repo.update(user_id, UserUpdate(**update_dict))
        
        # Sync with UserInfo table for legacy compatibility
        await self._sync_user_info(user)
        
        return UserResponse.from_orm(user)
    
    async def get_users_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "username",
        sort_order: str = "asc"
    ) -> Tuple[List[UserResponse], int]:
        """
        Get paginated users with search and filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term
            filters: Additional filters
            sort_by: Sort field
            sort_order: Sort direction
            
        Returns:
            Tuple of (users list, total count)
        """
        users, total = await self.user_repo.get_paginated(
            skip=skip,
            limit=limit,
            search_fields=['username', 'email', 'first_name', 'last_name'] if search else None,
            search_term=search,
            filters=filters or {},
            order_by=sort_by,
            order_desc=sort_order == "desc"
        )
        
        user_responses = [UserResponse.from_orm(user) for user in users]
        return user_responses, total
    
    async def change_password(
        self, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password with validation
        
        Args:
            user_id: User ID
            current_password: Current password for validation
            new_password: New password to set
            
        Returns:
            Success status
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Update password
        new_hash = get_password_hash(new_password)
        await self.user_repo.update(user_id, UserUpdate(
            password_hash=new_hash,
            password_changed_at=datetime.utcnow()
        ))
        
        return True
    
    async def create_users_batch(
        self, 
        batch_data: BatchUserCreate,
        created_by: Optional[str] = None
    ) -> BatchOperationResult:
        """
        Create multiple users in batch
        
        Args:
            batch_data: Batch creation parameters
            created_by: Username who created the batch
            
        Returns:
            Batch operation result
        """
        result = BatchOperationResult(total_count=batch_data.count)
        
        try:
            for i in range(batch_data.count):
                username = f"{batch_data.username_prefix}{i+1:03d}"
                password = self._generate_password(batch_data.password_length)
                
                # Generate email if domain provided
                email = None
                if batch_data.email_domain:
                    email = f"{username}@{batch_data.email_domain}"
                
                user_data = UserCreate(
                    username=username,
                    password=password,
                    email=email,
                    first_name=batch_data.first_name,
                    last_name=batch_data.last_name,
                    department=batch_data.department,
                    company=batch_data.company
                )
                
                try:
                    # Check if user already exists
                    existing = await self.user_repo.get_by_username(username)
                    if existing:
                        result.errors.append(f"User {username} already exists")
                        result.error_count += 1
                        continue
                    
                    await self.create_user(user_data, created_by)
                    result.created_users.append(username)
                    result.success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating user {username}: {str(e)}")
                    result.errors.append(f"Failed to create {username}: {str(e)}")
                    result.error_count += 1
                    
        except Exception as e:
            logger.error(f"Batch user creation failed: {str(e)}")
            result.errors.append(f"Batch operation failed: {str(e)}")
            
        return result
    
    async def import_users_from_dataframe(
        self, 
        df: pd.DataFrame,
        created_by: Optional[str] = None
    ) -> BatchOperationResult:
        """
        Import users from pandas DataFrame
        
        Args:
            df: DataFrame with user data
            created_by: Username who imported the users
            
        Returns:
            Import operation result
        """
        result = BatchOperationResult(total_count=len(df))
        
        # Required columns mapping
        required_columns = {
            'username': ['username', 'user', 'login'],
            'password': ['password', 'pass', 'pwd'],
        }
        
        optional_columns = {
            'email': ['email', 'mail'],
            'first_name': ['first_name', 'firstname', 'fname'],
            'last_name': ['last_name', 'lastname', 'lname'],
            'department': ['department', 'dept'],
            'company': ['company', 'organization', 'org'],
            'work_phone': ['work_phone', 'workphone', 'phone'],
            'mobile_phone': ['mobile_phone', 'mobile', 'cell']
        }
        
        # Find column mappings
        column_map = {}
        
        # Find required columns
        for field, possible_names in required_columns.items():
            found = False
            for col in df.columns:
                if col.lower() in possible_names:
                    column_map[field] = col
                    found = True
                    break
            if not found:
                result.errors.append(f"Required column '{field}' not found")
                result.error_count = len(df)
                return result
        
        # Find optional columns
        for field, possible_names in optional_columns.items():
            for col in df.columns:
                if col.lower() in possible_names:
                    column_map[field] = col
                    break
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Extract user data
                user_dict = {}
                for field, col_name in column_map.items():
                    value = row.get(col_name)
                    if pd.notna(value) and str(value).strip():
                        user_dict[field] = str(value).strip()
                
                # Validate required fields
                if not user_dict.get('username') or not user_dict.get('password'):
                    result.errors.append(f"Row {index + 1}: Missing username or password")
                    result.error_count += 1
                    continue
                
                # Check if user already exists
                existing = await self.user_repo.get_by_username(user_dict['username'])
                if existing:
                    result.errors.append(f"Row {index + 1}: User {user_dict['username']} already exists")
                    result.error_count += 1
                    continue
                
                # Create user
                user_data = UserCreate(**user_dict)
                await self.create_user(user_data, created_by)
                
                result.created_users.append(user_dict['username'])
                result.success_count += 1
                
            except Exception as e:
                logger.error(f"Error importing row {index + 1}: {str(e)}")
                result.errors.append(f"Row {index + 1}: {str(e)}")
                result.error_count += 1
        
        return result
    
    async def get_online_users(self) -> List[Dict[str, Any]]:
        """
        Get currently online users from RadAcct table
        
        Returns:
            List of online user information
        """
        # Query for active sessions (no AcctStopTime)
        query = select(RadAcct).where(RadAcct.acctstoptime.is_(None))
        
        result = await self.user_repo.db.execute(query)
        active_sessions = result.scalars().all()
        
        online_users = []
        for session in active_sessions:
            user_info = {
                'username': session.username,
                'nas_ip_address': session.nasipaddress,
                'session_id': session.acctsessionid,
                'start_time': session.acctstarttime,
                'input_bytes': session.acctinputoctets or 0,
                'output_bytes': session.acctoutputoctets or 0,
                'session_time': session.acctsessiontime or 0,
                'framed_ip': session.framedipaddress,
                'calling_station': session.callingstationid
            }
            online_users.append(user_info)
        
        return online_users
    
    async def _sync_user_info(self, user: User) -> None:
        """
        Sync user data with UserInfo table for legacy compatibility
        
        Args:
            user: User model instance
        """
        # Find existing UserInfo record
        query = select(UserInfo).where(UserInfo.username == user.username)
        result = await self.user_repo.db.execute(query)
        user_info = result.scalar_one_or_none()
        
        if user_info:
            # Update existing record
            user_info.firstname = user.first_name
            user_info.lastname = user.last_name
            user_info.email = user.email
            user_info.department = user.department
            user_info.company = user.company
            user_info.workphone = user.work_phone
            user_info.homephone = user.home_phone
            user_info.mobilephone = user.mobile_phone
            user_info.address = user.address
            user_info.city = user.city
            user_info.state = user.state
            user_info.country = user.country
            user_info.zip = user.zip
            user_info.updatedate = datetime.utcnow()
            user_info.enableportallogin = 1 if user.enable_portal_login else 0
            user_info.changeuserinfo = 1 if user.change_user_info else 0
        else:
            # Create new UserInfo record
            user_info = UserInfo(
                username=user.username,
                firstname=user.first_name,
                lastname=user.last_name,
                email=user.email,
                department=user.department,
                company=user.company,
                workphone=user.work_phone,
                homephone=user.home_phone,
                mobilephone=user.mobile_phone,
                address=user.address,
                city=user.city,
                state=user.state,
                country=user.country,
                zip=user.zip,
                creationdate=datetime.utcnow(),
                enableportallogin=1 if user.enable_portal_login else 0,
                changeuserinfo=1 if user.change_user_info else 0
            )
            self.user_repo.db.add(user_info)
        
        await self.user_repo.db.commit()
    
    def _generate_password(self, length: int = 8) -> str:
        """
        Generate random password
        
        Args:
            length: Password length
            
        Returns:
            Generated password
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))