"""
RADIUS Profile Models

This module contains SQLAlchemy models for RADIUS profile management.
A profile is a logical grouping of RADIUS attributes that can be applied
to users or groups, backed by radgroupcheck and radgroupreply tables.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    Index, UniqueConstraint, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class RadiusProfile(BaseModel):
    """
    RADIUS Profile - logical grouping of attributes
    This is a virtual model that represents a profile as a collection
    of group check and reply attributes with the same groupname.
    """
    __tablename__ = "radius_profiles"

    profile_name = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Profile name (maps to groupname in radgroupcheck/radgroupreply)"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Profile description"
    )

    # Status and metadata
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is profile active"
    )

    # Usage tracking
    usage_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times this profile is used"
    )

    # Indexes
    __table_args__ = (
        Index('idx_radius_profiles_name', 'profile_name'),
        Index('idx_radius_profiles_active', 'is_active'),
    )

    def __repr__(self):
        return f"<RadiusProfile(id={self.id}, profile_name='{self.profile_name}')>"


class ProfileUsage(BaseModel):
    """
    Profile usage tracking - which users/groups use which profiles
    """
    __tablename__ = "profile_usage"

    profile_id = Column(
        Integer,
        ForeignKey("radius_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Profile ID"
    )

    entity_type = Column(
        String(10),
        nullable=False,
        comment="Entity type: 'user' or 'group'"
    )

    entity_name = Column(
        String(64),
        nullable=False,
        index=True,
        comment="Username or groupname"
    )

    priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Application priority"
    )

    # Relationships
    profile = relationship("RadiusProfile", back_populates="usages")

    # Indexes
    __table_args__ = (
        Index('idx_profile_usage_profile', 'profile_id'),
        Index('idx_profile_usage_entity', 'entity_type', 'entity_name'),
        UniqueConstraint('profile_id', 'entity_type',
                         'entity_name', name='uq_profile_usage'),
    )

    def __repr__(self):
        return f"<ProfileUsage(profile_id={self.profile_id}, entity_type='{self.entity_type}', entity_name='{self.entity_name}')>"


# Add relationship back to RadiusProfile
RadiusProfile.usages = relationship(
    "ProfileUsage", back_populates="profile", cascade="all, delete-orphan")


# Export models
__all__ = [
    "RadiusProfile",
    "ProfileUsage"
]
