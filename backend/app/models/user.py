"""
User Management Models

This module contains SQLAlchemy models for user management,
including user profiles, authentication, and authorization.
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean, 
    ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import BaseModel, LegacyBaseModel


class UserStatus(enum.Enum):
    """User account status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class AuthType(enum.Enum):
    """Authentication types"""
    LOCAL = "LOCAL"
    LDAP = "LDAP"
    RADIUS = "RADIUS"
    SQL = "SQL"


class PasswordType(enum.Enum):
    """Password types for RADIUS"""
    CLEARTEXT = "Cleartext-Password"
    CRYPT = "Crypt-Password"
    MD5 = "MD5-Password"
    SHA = "SHA-Password"
    NT = "NT-Password"
    LM = "LM-Password"


class User(BaseModel):
    """
    Main user model combining userinfo and authentication data
    This is the primary user table for the new system
    """
    __tablename__ = "users"
    
    # Basic user information
    username = Column(
        String(64), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Unique username"
    )
    email = Column(
        String(255), 
        unique=True, 
        nullable=True, 
        index=True,
        comment="User email address"
    )
    password_hash = Column(
        String(255), 
        nullable=True,
        comment="Hashed password for local authentication"
    )
    
    # Authentication settings
    auth_type = Column(
        Enum(AuthType),
        default=AuthType.LOCAL,
        nullable=False,
        comment="Authentication type"
    )
    is_active = Column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Is user account active"
    )
    status = Column(
        Enum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
        comment="User account status"
    )
    
    # Profile information
    first_name = Column(String(200), nullable=True, comment="First name")
    last_name = Column(String(200), nullable=True, comment="Last name")
    department = Column(String(200), nullable=True, comment="Department")
    company = Column(String(200), nullable=True, comment="Company")
    
    # Contact information
    work_phone = Column(String(200), nullable=True, comment="Work phone")
    home_phone = Column(String(200), nullable=True, comment="Home phone")
    mobile_phone = Column(String(200), nullable=True, comment="Mobile phone")
    
    # Address information
    address = Column(String(200), nullable=True, comment="Street address")
    city = Column(String(200), nullable=True, comment="City")
    state = Column(String(200), nullable=True, comment="State/Province")
    country = Column(String(100), nullable=True, comment="Country")
    zip_code = Column(String(200), nullable=True, comment="ZIP/Postal code")
    
    # Additional fields
    notes = Column(Text, nullable=True, comment="User notes")
    mac_address = Column(String(17), nullable=True, comment="MAC address")
    pin_code = Column(String(32), nullable=True, comment="PIN code")
    
    # Portal settings
    portal_login_password = Column(
        String(128), 
        nullable=True,
        comment="Portal login password"
    )
    enable_portal_login = Column(
        Boolean, 
        default=False,
        comment="Enable portal login"
    )
    change_user_info = Column(
        Boolean, 
        default=False,
        comment="Allow user to change info"
    )
    
    # Timestamps
    last_login = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Last login timestamp"
    )
    password_changed_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Password last changed"
    )
    
    # Relationships (simplified for initial implementation)
    # user_info will be accessed via separate query
    
    def set_password(self, password: str) -> None:
        """Set user password (hashed)"""
        import bcrypt
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.password_hash = hashed.decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        if not self.password_hash:
            return False
        import bcrypt
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def __init__(self, **kwargs):
        # Handle password during initialization
        if 'password' in kwargs:
            password = kwargs.pop('password')
            super().__init__(**kwargs)
            self.set_password(password)
        else:
            super().__init__(**kwargs)
    
    # Index for common queries
    __table_args__ = (
        Index('idx_users_username_active', 'username', 'is_active'),
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_status', 'status'),
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username


class UserInfo(LegacyBaseModel):
    """
    Legacy user info table for compatibility with existing daloRADIUS
    This maps to the existing 'userinfo' table
    """
    __tablename__ = "userinfo"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, index=True)
    firstname = Column(String(200), nullable=True)
    lastname = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    workphone = Column(String(200), nullable=True)
    homephone = Column(String(200), nullable=True)
    mobilephone = Column(String(200), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    country = Column(String(100), nullable=True)
    zip = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    changeuserinfo = Column(Integer, default=0)
    portalloginpassword = Column(String(128), nullable=True)
    enableportallogin = Column(Integer, default=0)


class UserBillingInfo(LegacyBaseModel):
    """
    User billing information
    Maps to existing dalouserbillinfo table
    """
    __tablename__ = "dalouserbillinfo"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(64), nullable=False, index=True)
    planname = Column(String(128), nullable=True)
    
    # Contact information
    contactperson = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(200), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    country = Column(String(200), nullable=True)
    zip = Column(String(200), nullable=True)
    
    # Payment information
    paymentmethod = Column(String(200), nullable=True)
    cash = Column(String(200), nullable=True)
    creditcardname = Column(String(200), nullable=True)
    creditcardnumber = Column(String(200), nullable=True)
    creditcardverification = Column(String(200), nullable=True)
    creditcardtype = Column(String(200), nullable=True)
    creditcardexp = Column(String(200), nullable=True)
    
    # Billing details
    lead = Column(String(200), nullable=True)
    coupon = Column(String(200), nullable=True)
    ordertaker = Column(String(200), nullable=True)
    billstatus = Column(String(200), nullable=True)
    lastbill = Column(Date, nullable=True)
    nextbill = Column(Date, nullable=True)
    nextinvoicedue = Column(Date, nullable=True)
    billdue = Column(Date, nullable=True)
    
    # Invoice preferences
    postalinvoice = Column(String(200), nullable=True)
    faxinvoice = Column(String(200), nullable=True)
    emailinvoice = Column(String(200), nullable=True)
    
    # Additional fields
    notes = Column(Text, nullable=True)
    changeuserbillinfo = Column(Integer, default=0)
    batch_id = Column(Integer, nullable=True)
    
    # Relationship (simplified for initial implementation)


class UserGroup(BaseModel):
    """
    User group membership
    Maps to radusergroup table
    """
    __tablename__ = "radusergroup"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(64), nullable=False, index=True)
    groupname = Column(String(64), nullable=False, index=True)
    priority = Column(Integer, default=1, nullable=False)
    
    # Relationships (simplified for initial implementation)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('username', 'groupname', name='uq_user_group'),
        Index('idx_user_group_username', 'username'),
        Index('idx_user_group_groupname', 'groupname'),
    )


class Group(BaseModel):
    """
    User groups for RBAC
    """
    __tablename__ = "radgroups"
    
    groupname = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships (simplified for initial implementation)


class BatchHistory(LegacyBaseModel):
    """
    Batch operation history
    Maps to existing batch_history table
    """
    __tablename__ = "batch_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_name = Column(String(128), nullable=False)
    batch_description = Column(Text, nullable=True)
    hotspot_id = Column(Integer, nullable=True)


class Operator(BaseModel):
    """
    System operators/administrators
    Maps to existing operators table
    """
    __tablename__ = "operators"
    
    username = Column(String(64), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fullname = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    department = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Additional fields from original operators table
    firstname = Column(String(32), nullable=True)
    lastname = Column(String(32), nullable=True)
    title = Column(String(32), nullable=True)
    company = Column(String(32), nullable=True)
    phone1 = Column(String(32), nullable=True)
    phone2 = Column(String(32), nullable=True)
    email1 = Column(String(32), nullable=True)
    email2 = Column(String(32), nullable=True)
    messenger1 = Column(String(32), nullable=True)
    messenger2 = Column(String(32), nullable=True)
    notes = Column(String(128), nullable=True)
    
    # Permissions and roles will be handled separately
    permissions = Column(Text, nullable=True, comment="JSON string of permissions")
    
    # Relationship to ACL entries
    acl_entries = relationship("OperatorAcl", back_populates="operator", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Set operator password (hashed)"""
        import bcrypt
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        self.password = hashed.decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify operator password"""
        if not self.password:
            return False
        import bcrypt
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def __init__(self, **kwargs):
        # Handle password during initialization
        if 'password' in kwargs:
            password = kwargs.pop('password')
            super().__init__(**kwargs)
            self.set_password(password)
        else:
            super().__init__(**kwargs)


# Export all models
__all__ = [
    "User",
    "UserInfo", 
    "UserBillingInfo",
    "UserGroup",
    "Group",
    "BatchHistory",
    "Operator",
    "UserStatus",
    "AuthType",
    "PasswordType",
]