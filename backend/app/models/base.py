"""
Base Model Classes

This module provides base model classes with common fields and functionality
that all other models can inherit from.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, Integer, DateTime, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """
    Mixin for models that need created_at and updated_at timestamps
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )


class AuditMixin:
    """
    Mixin for models that need audit fields (who created/updated)
    """
    created_by = Column(
        String(64),
        nullable=True,
        comment="Username who created this record"
    )
    updated_by = Column(
        String(64),
        nullable=True,
        comment="Username who last updated this record"
    )


class SoftDeleteMixin:
    """
    Mixin for models that support soft delete
    """
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag"
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )
    deleted_by = Column(
        String(64),
        nullable=True,
        comment="Username who deleted this record"
    )


class BaseModel(Base, TimestampMixin, AuditMixin):
    """
    Base model class with common fields and functionality
    All models should inherit from this class
    """
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Primary key"
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name
        Convert CamelCase to snake_case
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model instance from dictionary
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """
        String representation of the model
        """
        return f"<{self.__class__.__name__}(id={self.id})>"


class RadiusBaseModel(BaseModel):
    """
    Base model for RADIUS-related tables
    These tables typically don't need audit fields as they're managed by RADIUS server
    """
    __abstract__ = True
    
    # Override to remove audit fields for RADIUS tables
    created_by = None
    updated_by = None


class LegacyBaseModel(Base):
    """
    Base model for legacy tables that need to maintain compatibility
    with existing daloRADIUS PHP schema
    """
    __abstract__ = True
    
    # Legacy tables use different timestamp field names
    creationdate = Column(
        DateTime,
        server_default=func.now(),
        nullable=True,
        comment="Legacy creation date field"
    )
    creationby = Column(
        String(128),
        nullable=True,
        comment="Legacy creation by field"
    )
    updatedate = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="Legacy update date field"
    )
    updateby = Column(
        String(128),
        nullable=True,
        comment="Legacy update by field"
    )