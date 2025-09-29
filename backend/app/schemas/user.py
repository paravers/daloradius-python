"""
User Management Pydantic Schemas

This module contains Pydantic models for request/response validation
and serialization in the user management API endpoints.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED" 
    EXPIRED = "EXPIRED"


class AuthType(str, Enum):
    """Authentication types"""
    LOCAL = "LOCAL"
    LDAP = "LDAP"
    RADIUS = "RADIUS"
    SQL = "SQL"


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=1, max_length=64, description="Unique username")
    email: Optional[EmailStr] = Field(None, description="User email address")
    first_name: Optional[str] = Field(None, max_length=200, description="First name")
    last_name: Optional[str] = Field(None, max_length=200, description="Last name")
    department: Optional[str] = Field(None, max_length=200, description="Department")
    company: Optional[str] = Field(None, max_length=200, description="Company")
    work_phone: Optional[str] = Field(None, max_length=200, description="Work phone")
    home_phone: Optional[str] = Field(None, max_length=200, description="Home phone")
    mobile_phone: Optional[str] = Field(None, max_length=200, description="Mobile phone")
    address: Optional[str] = Field(None, max_length=200, description="Address")
    city: Optional[str] = Field(None, max_length=200, description="City")
    state: Optional[str] = Field(None, max_length=200, description="State/Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    zip_code: Optional[str] = Field(None, max_length=200, description="ZIP/Postal code")
    notes: Optional[str] = Field(None, description="User notes")

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').replace('.', '').replace('@', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscore, hyphen, dot, and @')
        return v


# Request schemas
class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6, description="User password")
    auth_type: AuthType = Field(AuthType.LOCAL, description="Authentication type")
    is_active: bool = Field(True, description="Is user active")
    status: UserStatus = Field(UserStatus.ACTIVE, description="User status")
    mac_address: Optional[str] = Field(None, max_length=17, description="MAC address")
    pin_code: Optional[str] = Field(None, max_length=32, description="PIN code")
    enable_portal_login: bool = Field(False, description="Enable portal login")
    portal_login_password: Optional[str] = Field(None, max_length=128, description="Portal password")
    change_user_info: bool = Field(False, description="Allow user to change info")

    @validator('mac_address')
    def validate_mac_address(cls, v):
        if v:
            import re
            if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', v):
                raise ValueError('Invalid MAC address format')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=200)
    last_name: Optional[str] = Field(None, max_length=200)
    department: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    work_phone: Optional[str] = Field(None, max_length=200)
    home_phone: Optional[str] = Field(None, max_length=200)
    mobile_phone: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[UserStatus] = None
    mac_address: Optional[str] = Field(None, max_length=17)
    pin_code: Optional[str] = Field(None, max_length=32)
    enable_portal_login: Optional[bool] = None
    portal_login_password: Optional[str] = Field(None, max_length=128)
    change_user_info: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")


# Response schemas
class UserResponse(UserBase):
    """Schema for user API responses"""
    id: int
    auth_type: AuthType
    is_active: bool
    status: UserStatus
    mac_address: Optional[str] = None
    pin_code: Optional[str] = None
    enable_portal_login: bool
    change_user_info: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list API responses"""
    users: List[UserResponse]
    total: int
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    pages: int

    class Config:
        from_attributes = True


# Group schemas
class GroupBase(BaseModel):
    """Base group schema"""
    groupname: str = Field(..., min_length=1, max_length=64, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    priority: int = Field(1, ge=0, description="Group priority")
    is_active: bool = Field(True, description="Is group active")


class GroupCreate(GroupBase):
    """Schema for creating a new group"""
    pass


class GroupUpdate(BaseModel):
    """Schema for updating a group"""
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class GroupResponse(GroupBase):
    """Schema for group API responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


# User-Group association schemas
class UserGroupBase(BaseModel):
    """Base user-group association schema"""
    username: str = Field(..., max_length=64)
    groupname: str = Field(..., max_length=64)
    priority: int = Field(1, ge=0)


class UserGroupCreate(UserGroupBase):
    """Schema for creating user-group association"""
    pass


class UserGroupResponse(UserGroupBase):
    """Schema for user-group association responses"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserGroupUpdate(BaseModel):
    """Schema for updating user-group association"""
    groupname: Optional[str] = Field(None, max_length=64)
    priority: Optional[int] = Field(None, ge=0)


class UserGroupListResponse(BaseModel):
    """Schema for user group list responses"""
    groups: List[str] = Field(..., description="List of group names")
    total: int = Field(..., description="Total number of groups")


class UserGroupStatisticsResponse(BaseModel):
    """Schema for user group statistics responses"""
    total_associations: int = Field(..., description="Total user-group associations")
    total_groups: int = Field(..., description="Total number of groups")
    total_users: int = Field(..., description="Total users with groups")
    top_groups: List[Dict[str, Any]] = Field(..., description="Groups with most users")


class UserGroupDetailResponse(BaseModel):
    """Schema for detailed user group response"""
    id: int
    groupname: str
    priority: int
    member_count: int
    joined_at: datetime


class BatchUserGroupOperation(BaseModel):
    """Schema for batch user group operations"""
    usernames: List[str] = Field(..., description="List of usernames")
    groupname: str = Field(..., max_length=64, description="Group name")
    priority: int = Field(1, ge=0, description="Priority for new associations")


class BatchUserGroupResult(BaseModel):
    """Schema for batch operation results"""
    groupname: str
    requested: int
    added: Optional[int] = None
    removed: Optional[int] = None
    failed: int
    errors: List[str]


class GroupWithUserCount(BaseModel):
    """Schema for group with user count"""
    groupname: str
    user_count: int


class UserGroupSearchParams(BaseModel):
    """Schema for user group search parameters"""
    username_pattern: Optional[str] = None
    groupname_pattern: Optional[str] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


# Operator schemas
class OperatorBase(BaseModel):
    """Base operator schema"""
    username: str = Field(..., min_length=1, max_length=64)
    fullname: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=200)
    is_active: bool = Field(True)


class OperatorCreate(OperatorBase):
    """Schema for creating a new operator"""
    password: str = Field(..., min_length=6)
    permissions: Optional[str] = Field(None, description="JSON permissions")


class OperatorUpdate(BaseModel):
    """Schema for updating an operator"""
    fullname: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    permissions: Optional[str] = None


class OperatorResponse(OperatorBase):
    """Schema for operator API responses"""
    id: int
    last_login: Optional[datetime] = None
    permissions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Common response schemas
class MessageResponse(BaseModel):
    """Standard message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Standard error response"""
    message: str
    success: bool = False
    details: Optional[dict] = None


# Batch operation schemas
class BatchUserCreate(BaseModel):
    """Schema for batch user creation"""
    count: int = Field(..., ge=1, le=1000, description="Number of users to create")
    username_prefix: str = Field(..., min_length=1, max_length=32, description="Username prefix")
    password_length: int = Field(8, ge=6, le=32, description="Password length")
    group: Optional[str] = Field(None, max_length=64, description="Default group")
    
    # User info template
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    email_domain: Optional[str] = Field(None, description="Email domain for generated emails")


class BatchOperationResult(BaseModel):
    """Schema for batch operation results"""
    success_count: int = 0
    error_count: int = 0
    total_count: int = 0
    errors: List[str] = []
    created_users: List[str] = []