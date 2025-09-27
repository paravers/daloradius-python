"""
RADIUS Group Management Models

This module contains SQLAlchemy models for RADIUS group management,
including group checks, replies, and post-authentication logging.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship

from .base import RadiusBaseModel


class RadGroupCheck(RadiusBaseModel):
    """
    RADIUS group check attributes
    Maps to radgroupcheck table
    """
    __tablename__ = "radgroupcheck"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(String(2), nullable=False, default='==')
    value = Column(String(253), nullable=False)


class RadGroupReply(RadiusBaseModel):
    """
    RADIUS group reply attributes
    Maps to radgroupreply table
    """
    __tablename__ = "radgroupreply"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String(64), nullable=False, index=True)
    attribute = Column(String(64), nullable=False)
    op = Column(String(2), nullable=False, default='=')
    value = Column(String(253), nullable=False)


class RadPostAuth(RadiusBaseModel):
    """
    RADIUS post-authentication log
    Maps to radpostauth table
    """
    __tablename__ = "radpostauth"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, index=True)
    pass_field = Column('pass', String(64), nullable=False)
    reply = Column(String(32), nullable=False)
    authdate = Column(DateTime(timezone=True), nullable=False, index=True)
    class_field = Column('class', String(64), nullable=True)


class NasReload(RadiusBaseModel):
    """
    NAS reload management
    Maps to nasreload table
    """
    __tablename__ = "nasreload"
    __table_args__ = {'extend_existing': True}
    
    nasipaddress = Column(INET, primary_key=True)
    reloadtime = Column(DateTime(timezone=True), nullable=False)


class RadIpPool(RadiusBaseModel):
    """
    RADIUS IP pool management
    Maps to radippool table
    """
    __tablename__ = "radippool"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_name = Column(String(30), nullable=False, index=True)
    framedipaddress = Column(INET, nullable=False, index=True)
    nasipaddress = Column(INET, nullable=False, index=True)
    calledstationid = Column(String(30), nullable=True)
    callingstationid = Column(String(30), nullable=True)
    expiry_time = Column(DateTime(timezone=True), nullable=True)
    username = Column(String(64), nullable=True)
    pool_key = Column(String(30), nullable=True)


# Export all models
__all__ = [
    "RadGroupCheck",
    "RadGroupReply", 
    "RadPostAuth",
    "NasReload",
    "RadIpPool"
]