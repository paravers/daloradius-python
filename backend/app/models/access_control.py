"""
Access Control and System Configuration Models

This module contains SQLAlchemy models for access control,
dictionary management, and system messages.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean,
    ForeignKey, Enum, SmallInteger
)
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class MessageType(enum.Enum):
    """Message types"""
    LOGIN = "login"
    SUPPORT = "support" 
    DASHBOARD = "dashboard"


class OperatorAcl(BaseModel):
    """
    Operator access control list
    Maps to operators_acl table
    """
    __tablename__ = "operators_acl"
    
    operator_id = Column(Integer, ForeignKey('operators.id', ondelete='CASCADE'), nullable=False, index=True)
    file = Column(String(128), nullable=False, index=True)
    access = Column(SmallInteger, nullable=False, default=0)
    
    # Relationship to operator
    operator = relationship("Operator", back_populates="acl_entries")
    
    __table_args__ = (
        {'extend_existing': True}
    )


class OperatorAclFile(BaseModel):
    """
    Available ACL files configuration
    Maps to operators_acl_files table
    """
    __tablename__ = "operators_acl_files"
    __table_args__ = {'extend_existing': True}
    
    file = Column(String(128), nullable=False, unique=True)
    category = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)


class Dictionary(BaseModel):
    """
    RADIUS attribute dictionary
    Maps to dictionary table
    """
    __tablename__ = "dictionary"
    __table_args__ = {'extend_existing': True}
    
    Type = Column(String(30), nullable=True, index=True)
    Attribute = Column(String(64), nullable=True, index=True)
    Value = Column(String(64), nullable=True)
    Format = Column(String(20), nullable=True)
    Vendor = Column(String(32), nullable=True, index=True)
    RecommendedOP = Column(String(32), nullable=True)
    RecommendedTable = Column(String(32), nullable=True)
    RecommendedHelper = Column(String(32), nullable=True)
    RecommendedTooltip = Column(String(512), nullable=True)


class Message(BaseModel):
    """
    System messages for different contexts
    Maps to messages table
    """
    __tablename__ = "messages"
    __table_args__ = {'extend_existing': True}
    
    type = Column(Enum(MessageType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_on = Column(DateTime(timezone=True), nullable=False, index=True)
    created_by = Column(String(32), nullable=True)
    modified_on = Column(DateTime(timezone=True), nullable=True)
    modified_by = Column(String(32), nullable=True)


# Export all models
__all__ = [
    "OperatorAcl",
    "OperatorAclFile",
    "Dictionary",
    "Message",
    "MessageType"
]