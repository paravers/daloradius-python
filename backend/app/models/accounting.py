"""
Accounting Models

This module contains SQLAlchemy models for RADIUS accounting data,
including session records, traffic statistics, and usage tracking.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, BigInteger,
    Text, Index, func
)
from sqlalchemy.dialects.postgresql import INET
import enum

from .base import RadiusBaseModel


class SessionStatus(enum.Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    STOPPED = "stopped"
    EXPIRED = "expired"


class RadAcct(RadiusBaseModel):
    """
    RADIUS accounting records
    Maps to radacct table - this is the core accounting table
    """
    __tablename__ = "radacct"
    
    # Primary key - using radacctid as it's the standard
    radacctid = Column(Integer, primary_key=True, autoincrement=True)
    
    # User and session identification
    username = Column(String(64), nullable=False, index=True)
    realm = Column(String(64), nullable=True)
    acctsessionid = Column(String(64), nullable=False, index=True)
    acctuniqueid = Column(String(32), nullable=False, index=True)
    groupname = Column(String(64), nullable=True, index=True)
    
    # NAS identification
    nasipaddress = Column(INET, nullable=False, index=True)
    nasportid = Column(String(15), nullable=True)
    nasporttype = Column(String(32), nullable=True)
    nasidentifier = Column(String(64), nullable=True)
    
    # Connection details
    calledstationid = Column(String(50), nullable=True)
    callingstationid = Column(String(50), nullable=True, index=True)
    framedipaddress = Column(INET, nullable=True, index=True)
    framedipv6address = Column(String(45), nullable=True, index=True)
    framedipv6prefix = Column(String(45), nullable=True, index=True)
    framedinterfaceid = Column(String(44), nullable=True, index=True)
    delegatedipv6prefix = Column(String(45), nullable=True, index=True)
    framedprotocol = Column(String(32), nullable=True)
    
    # Service type and class
    servicetype = Column(String(32), nullable=True)
    class_attribute = Column("class", String(64), nullable=True)
    
    # Session timing
    acctstarttime = Column(
        DateTime(timezone=True), 
        nullable=True, 
        index=True,
        comment="Session start time"
    )
    acctstoptime = Column(
        DateTime(timezone=True), 
        nullable=True, 
        index=True,
        comment="Session stop time"
    )
    acctsessiontime = Column(
        Integer, 
        nullable=True,
        comment="Session duration in seconds"
    )
    acctinterval = Column(
        Integer,
        nullable=True,
        comment="Accounting update interval"
    )
    acctauthentic = Column(
        String(32),
        nullable=True,
        comment="Authentication method used"
    )
    
    # Traffic counters
    acctinputoctets = Column(
        BigInteger, 
        nullable=True, 
        default=0,
        comment="Input bytes"
    )
    acctoutputoctets = Column(
        BigInteger, 
        nullable=True, 
        default=0,
        comment="Output bytes"
    )
    acctinputpackets = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="Input packets"
    )
    acctoutputpackets = Column(
        Integer, 
        nullable=True, 
        default=0,
        comment="Output packets"
    )
    
    # Termination details
    acctterminatecause = Column(String(32), nullable=True)
    
    # Additional accounting data
    connectinfo_start = Column(String(50), nullable=True)
    connectinfo_stop = Column(String(50), nullable=True)
    
    # Indexes for performance optimization
    __table_args__ = (
        # Primary query indexes
        Index('idx_radacct_username', 'username'),
        Index('idx_radacct_nasipaddress', 'nasipaddress'),
        Index('idx_radacct_acctsessionid', 'acctsessionid'),
        Index('idx_radacct_acctuniqueid', 'acctuniqueid'),
        Index('idx_radacct_framedipaddress', 'framedipaddress'),
        Index('idx_radacct_callingstationid', 'callingstationid'),
        
        # Time-based indexes for reporting
        Index('idx_radacct_acctstarttime', 'acctstarttime'),
        Index('idx_radacct_acctstoptime', 'acctstoptime'),
        Index('idx_radacct_username_starttime', 'username', 'acctstarttime'),
        Index('idx_radacct_username_stoptime', 'username', 'acctstoptime'),
        
        # Composite indexes for common queries
        Index('idx_radacct_active_sessions', 'username', 'acctstarttime', 'acctstoptime'),
        Index('idx_radacct_nas_sessions', 'nasipaddress', 'acctstarttime'),
        
        # Unique constraint for session identification
        # Note: Using partial unique index for active sessions only
        Index('idx_radacct_unique_session', 
              'username', 'nasipaddress', 'acctsessionid',
              unique=True,
              postgresql_where=(Column('acctstoptime').is_(None))),
    )
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.acctstoptime is None
    
    @property
    def total_bytes(self) -> int:
        """Calculate total bytes transferred"""
        input_bytes = self.acctinputoctets or 0
        output_bytes = self.acctoutputoctets or 0
        return input_bytes + output_bytes
    
    @property
    def total_packets(self) -> int:
        """Calculate total packets transferred"""
        input_packets = self.acctinputpackets or 0
        output_packets = self.acctoutputpackets or 0
        return input_packets + output_packets


class RadAcctUpdate(RadiusBaseModel):
    """
    RADIUS accounting updates (interim updates)
    Maps to radacct table but for interim accounting records
    """
    __tablename__ = "radacct_updates"
    
    # References to main accounting record
    radacctid = Column(Integer, nullable=False, index=True)
    acctsessionid = Column(String(32), nullable=False, index=True)
    username = Column(String(64), nullable=False, index=True)
    
    # Update timestamp
    update_time = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        index=True
    )
    
    # Traffic counters at update time
    acctinputoctets = Column(BigInteger, nullable=True, default=0)
    acctoutputoctets = Column(BigInteger, nullable=True, default=0)
    acctinputpackets = Column(Integer, nullable=True, default=0)
    acctoutputpackets = Column(Integer, nullable=True, default=0)
    
    # Session time at update
    acctsessiontime = Column(Integer, nullable=True)
    
    # Connection info
    connectinfo = Column(String(50), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_radacct_updates_radacctid', 'radacctid'),
        Index('idx_radacct_updates_session', 'acctsessionid'),
        Index('idx_radacct_updates_username_time', 'username', 'update_time'),
    )


class UserTrafficSummary(RadiusBaseModel):
    """
    Materialized view or summary table for user traffic statistics
    This helps with performance for reporting queries
    """
    __tablename__ = "user_traffic_summary"
    
    username = Column(String(64), nullable=False, primary_key=True, index=True)
    summary_date = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    
    # Daily totals
    total_sessions = Column(Integer, nullable=False, default=0)
    total_session_time = Column(BigInteger, nullable=False, default=0)
    total_input_octets = Column(BigInteger, nullable=False, default=0)
    total_output_octets = Column(BigInteger, nullable=False, default=0)
    total_input_packets = Column(BigInteger, nullable=False, default=0)
    total_output_packets = Column(BigInteger, nullable=False, default=0)
    
    # Average values
    avg_session_time = Column(Integer, nullable=True)
    avg_throughput = Column(BigInteger, nullable=True)
    
    # Peak values
    peak_input_rate = Column(BigInteger, nullable=True)
    peak_output_rate = Column(BigInteger, nullable=True)
    
    # First and last session of the day
    first_session_start = Column(DateTime(timezone=True), nullable=True)
    last_session_stop = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_traffic_summary_date', 'summary_date'),
        Index('idx_traffic_summary_username_date', 'username', 'summary_date'),
    )


class NasTrafficSummary(RadiusBaseModel):
    """
    NAS traffic summary for monitoring NAS performance
    """
    __tablename__ = "nas_traffic_summary"
    
    nasipaddress = Column(INET, nullable=False, primary_key=True, index=True)
    summary_date = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    
    # Session statistics
    total_sessions = Column(Integer, nullable=False, default=0)
    active_sessions = Column(Integer, nullable=False, default=0)
    completed_sessions = Column(Integer, nullable=False, default=0)
    
    # Traffic statistics
    total_input_octets = Column(BigInteger, nullable=False, default=0)
    total_output_octets = Column(BigInteger, nullable=False, default=0)
    
    # Performance metrics
    avg_session_duration = Column(Integer, nullable=True)
    peak_concurrent_sessions = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_nas_summary_date', 'summary_date'),
        Index('idx_nas_summary_nas_date', 'nasipaddress', 'summary_date'),
    )


# Export all models
__all__ = [
    "RadAcct",
    "RadAcctUpdate", 
    "UserTrafficSummary",
    "NasTrafficSummary",
    "SessionStatus",
]