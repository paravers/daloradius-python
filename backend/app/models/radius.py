"""
RADIUS Protocol Models

This module contains SQLAlchemy models for RADIUS protocol-related tables,
including radcheck, radreply, radgroupcheck, radgroupreply, and radpostauth.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum

from .base import RadiusBaseModel, BaseModel


class AttributeOperator(enum.Enum):
    """RADIUS attribute operators"""
    EQUAL = "="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    REGEX_MATCH = "=~"
    REGEX_NOT_MATCH = "!~"
    APPEND = "+="
    SET = ":="


class TerminateCause(enum.Enum):
    """RADIUS session termination causes"""
    UNKNOWN = "Unknown"
    USER_REQUEST = "User-Request"
    LOST_CARRIER = "Lost-Carrier"
    LOST_SERVICE = "Lost-Service"
    IDLE_TIMEOUT = "Idle-Timeout"
    SESSION_TIMEOUT = "Session-Timeout"
    ADMIN_RESET = "Admin-Reset"
    ADMIN_REBOOT = "Admin-Reboot"
    PORT_ERROR = "Port-Error"
    NAS_ERROR = "NAS-Error"
    NAS_REQUEST = "NAS-Request"
    NAS_REBOOT = "NAS-Reboot"
    PORT_UNNEEDED = "Port-Unneeded"
    PORT_PREEMPTED = "Port-Preempted"
    PORT_SUSPENDED = "Port-Suspended"
    SERVICE_UNAVAILABLE = "Service-Unavailable"
    CALLBACK = "Callback"
    USER_ERROR = "User-Error"
    HOST_REQUEST = "Host-Request"


class RadCheck(RadiusBaseModel):
    """
    RADIUS check attributes (authentication)
    Maps to radcheck table
    """
    __tablename__ = "radcheck"

    username = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(Enum(AttributeOperator),
                default=AttributeOperator.EQUAL, nullable=False)
    value = Column(String(253), nullable=False)

    # Relationships
    user = relationship("User", back_populates="rad_checks")

    # Indexes for performance
    __table_args__ = (
        Index('idx_radcheck_username', 'username'),
        Index('idx_radcheck_username_attribute', 'username', 'attribute'),
    )


class RadReply(RadiusBaseModel):
    """
    RADIUS reply attributes (authorization)
    Maps to radreply table
    """
    __tablename__ = "radreply"

    username = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(Enum(AttributeOperator),
                default=AttributeOperator.EQUAL, nullable=False)
    value = Column(String(253), nullable=False)

    # Relationships
    user = relationship("User", back_populates="rad_replies")

    # Indexes for performance
    __table_args__ = (
        Index('idx_radreply_username', 'username'),
        Index('idx_radreply_username_attribute', 'username', 'attribute'),
    )


class GroupCheck(RadiusBaseModel):
    """RADIUS group check attributes (canonical definition)

    NOTE: Consolidated duplicate definition (previously also in radius_groups.py).
    Aligns with Alembic migration 003 schema which uses a simple String(2)
    operator column rather than an Enum. We keep business enum elsewhere
    (AttributeOperator) for validation at service layer instead of DDL.
    """
    __tablename__ = "radgroupcheck"

    groupname = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    # Stored as raw two-char operator per legacy schema (==, =, :=, += ...)
    op = Column(String(2), nullable=False, default='==')
    value = Column(String(253), nullable=False)

    # Relationship placeholder (optional backref)
    group = relationship("Group", back_populates="group_checks",
                         uselist=False, viewonly=True, foreign_keys=[])  # type: ignore

    __table_args__ = (
        Index('idx_radgroupcheck_groupname', 'groupname'),
        Index('idx_radgroupcheck_groupname_attribute', 'groupname', 'attribute'),
        {'extend_existing': True}
    )


class GroupReply(RadiusBaseModel):
    """RADIUS group reply attributes (canonical definition)

    See notes in GroupCheck about consolidation & schema alignment.
    """
    __tablename__ = "radgroupreply"

    groupname = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(String(2), nullable=False, default='=')
    value = Column(String(253), nullable=False)

    group = relationship("Group", back_populates="group_replies",
                         uselist=False, viewonly=True, foreign_keys=[])  # type: ignore

    __table_args__ = (
        Index('idx_radgroupreply_groupname', 'groupname'),
        Index('idx_radgroupreply_groupname_attribute', 'groupname', 'attribute'),
        {'extend_existing': True}
    )


class RadPostAuth(RadiusBaseModel):
    """RADIUS post-authentication log (canonical definition)

    Consolidated with legacy version. Matches migration 003 that uses columns:
    id, username, pass, reply, authdate, class.
    Additional NAS columns from earlier experimental model removed to avoid
    schema drift; can be reintroduced via a new migration if required.
    """
    __tablename__ = "radpostauth"

    username = Column(String(64), nullable=False, index=True)
    pass_field = Column('pass', String(64), nullable=False)
    reply = Column(String(32), nullable=False)
    authdate = Column(DateTime(timezone=True), nullable=False,
                      server_default='NOW()', index=True)
    class_field = Column('class', String(64), nullable=True)

    __table_args__ = (
        Index('idx_radpostauth_username', 'username'),
        Index('idx_radpostauth_authdate', 'authdate'),
        {'extend_existing': True}
    )


class RadHuntGroup(RadiusBaseModel):
    """
    RADIUS hunt groups
    Maps to radhuntgroup table
    """
    __tablename__ = "radhuntgroup"

    groupname = Column(String(64), nullable=False, index=True)
    nasipaddress = Column(String(15), nullable=False)
    nasportid = Column(String(15), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_radhuntgroup_groupname', 'groupname'),
        Index('idx_radhuntgroup_nasip', 'nasipaddress'),
    )


class RadUserGroup(RadiusBaseModel):
    """
    RADIUS user group assignments
    This is the legacy table, new system uses UserGroup model
    """
    __tablename__ = "radusergroup_legacy"

    username = Column(String(64), nullable=False, index=True)
    groupname = Column(String(64), nullable=False, index=True)
    priority = Column(Integer, default=1, nullable=False)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('username', 'groupname', name='uq_legacy_user_group'),
    )


class RadiusDictionary(BaseModel):
    """
    RADIUS dictionary attributes
    Maps to dalodictionary table
    """
    __tablename__ = "dalodictionary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(64), nullable=True)
    attribute = Column(String(64), nullable=False, index=True)
    value = Column(String(64), nullable=True)
    format = Column(String(64), nullable=True)
    vendor = Column(String(64), nullable=False, index=True)
    recommended_op = Column(String(4), nullable=True)
    recommended_table = Column(String(32), nullable=True)
    recommended_helper = Column(String(64), nullable=True)
    recommended_tooltip = Column(Text, nullable=True)

    # Index for lookups
    __table_args__ = (
        Index('idx_dictionary_attribute_vendor', 'attribute', 'vendor'),
    )


class RadAttribute(BaseModel):
    """
    Custom RADIUS attributes for users
    This is a helper model for managing user attributes
    """
    __tablename__ = "rad_attributes"

    username = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(Enum(AttributeOperator),
                default=AttributeOperator.EQUAL, nullable=False)
    value = Column(String(253), nullable=False)
    attribute_type = Column(String(10), nullable=False)  # 'check' or 'reply'
    description = Column(Text, nullable=True)
    is_active = Column(String(3), default='yes', nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_rad_attributes_username', 'username'),
        Index('idx_rad_attributes_type', 'attribute_type'),
        Index('idx_rad_attributes_username_type',
              'username', 'attribute_type'),
    )


# Export all models
__all__ = [
    "RadCheck",
    "RadReply",
    "GroupCheck",
    "GroupReply",
    "RadPostAuth",
    "RadHuntGroup",
    "RadUserGroup",
    "RadiusDictionary",
    "RadAttribute",
    "AttributeOperator",
    "TerminateCause",
]
