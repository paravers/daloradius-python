"""
NAS (Network Access Server) Models

This module contains SQLAlchemy models for NAS management,
including NAS devices, realms, proxies, and IP pools.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import INET
import enum

from .base import BaseModel


class NasType(enum.Enum):
    """NAS device types"""
    CISCO = "cisco"
    JUNIPER = "juniper"
    MIKROTIK = "mikrotik"
    UBIQUITI = "ubiquiti"
    ALCATEL = "alcatel"
    OTHER = "other"


class Nas(BaseModel):
    """
    Network Access Server (NAS) devices
    Maps to nas table
    """
    __tablename__ = "nas"

    # NAS identification
    nasname = Column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="NAS hostname or IP address"
    )
    shortname = Column(
        String(32),
        nullable=True,
        comment="Short name for NAS"
    )
    type = Column(
        String(30),
        nullable=True,
        comment="NAS type/vendor"
    )

    # Connection settings
    ports = Column(
        Integer,
        nullable=True,
        comment="Number of ports"
    )
    secret = Column(
        String(60),
        nullable=False,
        comment="RADIUS shared secret"
    )
    server = Column(
        String(64),
        nullable=True,
        comment="Virtual server name"
    )
    community = Column(
        String(50),
        nullable=True,
        comment="SNMP community string"
    )

    # Additional information
    description = Column(
        Text,
        nullable=True,
        comment="NAS description"
    )

    # Status and monitoring
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is NAS active"
    )
    last_seen = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last seen timestamp"
    )

    # Performance metrics
    total_requests = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total RADIUS requests"
    )
    successful_requests = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Successful RADIUS requests"
    )

    # Indexes
    __table_args__ = (
        Index('idx_nas_nasname', 'nasname'),
        Index('idx_nas_active', 'is_active'),
        Index('idx_nas_type', 'type'),
    )


class Realm(BaseModel):
    """
    RADIUS realms for routing authentication requests
    Maps to dalorealms table
    """
    __tablename__ = "dalorealms"

    realmname = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Realm name"
    )
    type = Column(
        String(64),
        nullable=True,
        comment="Realm type"
    )
    authhost = Column(
        String(128),
        nullable=True,
        comment="Authentication host"
    )
    accthost = Column(
        String(128),
        nullable=True,
        comment="Accounting host"
    )
    secret = Column(
        String(128),
        nullable=True,
        comment="Shared secret"
    )

    # FreeRADIUS specific settings
    ldflag = Column(String(64), nullable=True)
    nostrip = Column(Boolean, default=False, nullable=False)
    hints = Column(String(128), nullable=True)
    notrealm = Column(String(128), nullable=True)

    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is realm active"
    )


class Proxy(BaseModel):
    """
    RADIUS proxy configuration
    Maps to daloproxys table
    """
    __tablename__ = "daloproxys"

    proxyname = Column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="Proxy name"
    )

    # Proxy settings
    retry_delay = Column(
        Integer,
        nullable=True,
        comment="Retry delay in seconds"
    )
    retry_count = Column(
        Integer,
        nullable=True,
        comment="Number of retries"
    )
    dead_time = Column(
        Integer,
        nullable=True,
        comment="Dead time in seconds"
    )
    default_fallback = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Is default fallback"
    )

    # Status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is proxy active"
    )


class IpPool(BaseModel):
    """
    IP address pools for dynamic IP assignment
    Maps to radippool table
    """
    __tablename__ = "radippool"

    pool_name = Column(
        String(30),
        nullable=False,
        index=True,
        comment="Pool name"
    )
    framedipaddress = Column(
        INET,
        nullable=False,
        index=True,
        comment="IP address"
    )
    nasipaddress = Column(
        String(16),
        default='',
        nullable=False,
        comment="NAS IP address"
    )
    pool_key = Column(
        String(30),
        default='',
        nullable=False,
        comment="Pool key"
    )

    # Assignment tracking
    callingstationid = Column(
        String(30),
        default='',
        nullable=False,
        comment="Calling station ID (MAC)"
    )
    username = Column(
        String(64),
        default='',
        nullable=False,
        index=True,
        comment="Assigned username"
    )

    # Status and timing
    expiry_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="IP lease expiry time"
    )
    is_allocated = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Is IP allocated"
    )

    # Indexes
    __table_args__ = (
        Index('idx_ippool_pool_name', 'pool_name'),
        Index('idx_ippool_framedip', 'framedipaddress'),
        Index('idx_ippool_username', 'username'),
        Index('idx_ippool_pool_allocated', 'pool_name', 'is_allocated'),
        UniqueConstraint('framedipaddress', 'pool_name', name='uq_ip_pool'),
    )


class NasGroup(BaseModel):
    """
    NAS groups for organizing NAS devices
    """
    __tablename__ = "nas_groups"

    group_name = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Group name"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Group description"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is group active"
    )


class NasGroupMember(BaseModel):
    """
    NAS group membership
    """
    __tablename__ = "nas_group_members"

    group_id = Column(Integer, nullable=False, index=True)
    nas_id = Column(Integer, nullable=False, index=True)
    priority = Column(Integer, default=1, nullable=False)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('group_id', 'nas_id', name='uq_nas_group_member'),
    )


class NasMonitoring(BaseModel):
    """
    NAS monitoring and health check results
    """
    __tablename__ = "nas_monitoring"

    nas_id = Column(Integer, nullable=False, index=True)
    check_time = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Check timestamp"
    )

    # Connectivity checks
    ping_success = Column(Boolean, nullable=True)
    ping_latency_ms = Column(Integer, nullable=True)

    # RADIUS checks
    radius_auth_success = Column(Boolean, nullable=True)
    radius_acct_success = Column(Boolean, nullable=True)
    radius_response_time_ms = Column(Integer, nullable=True)

    # SNMP checks
    snmp_success = Column(Boolean, nullable=True)
    cpu_usage_percent = Column(Integer, nullable=True)
    memory_usage_percent = Column(Integer, nullable=True)
    uptime_seconds = Column(Integer, nullable=True)

    # Session counts
    active_sessions = Column(Integer, nullable=True)
    total_ports = Column(Integer, nullable=True)

    # Error details
    error_message = Column(Text, nullable=True)

    # Overall status
    status = Column(
        String(20),
        nullable=False,
        default='unknown',
        comment="Overall status: healthy, warning, critical, unknown"
    )

    # Indexes
    __table_args__ = (
        Index('idx_nas_monitoring_nas_time', 'nas_id', 'check_time'),
        Index('idx_nas_monitoring_status', 'status'),
    )


# Export all models
__all__ = [
    "Nas",
    "Realm",
    "Proxy",
    "IpPool",
    "NasGroup",
    "NasGroupMember",
    "NasMonitoring",
    "NasType",
]
