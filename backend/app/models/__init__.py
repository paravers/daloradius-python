"""
Models package initialization

This module imports all SQLAlchemy models to ensure they are registered
with the SQLAlchemy metadata and available for use throughout the application.
"""

# Import base classes first
from .base import BaseModel, LegacyBaseModel, RadiusBaseModel

# Import core models
from .user import User, UserInfo, UserGroup, Operator, UserBillingInfo
from .radius import RadCheck, RadReply, RadUserGroup
from .nas import Nas  
from .accounting import RadAcct
from .system import BackupHistory

# Import new models
from .radius_groups import RadGroupCheck, RadGroupReply, RadPostAuth, NasReload, RadIpPool
from .radius_profile import RadiusProfile, ProfileUsage
from .nas import Realm, Proxy
from .radius import RadHuntGroup
from .billing import BillingPlan, BillingHistory, BillingMerchant, BillingRate, BillingPlanProfile
from .access_control import OperatorAcl, OperatorAclFile, Dictionary, Message, MessageType

# Export all models
__all__ = [
    # Base classes
    "BaseModel",
    "LegacyBaseModel", 
    "RadiusBaseModel",
    
    # Core models
    "User",
    "UserInfo",
    "UserGroup", 
    "UserBillingInfo",
    "Operator",
    "RadCheck",
    "RadReply", 
    "RadUserGroup",
    "Nas",
    "RadAcct",
    "BackupHistory",
    
    # RADIUS Group Management
    "RadGroupCheck",
    "RadGroupReply",
    "RadPostAuth", 
    "NasReload",
    "RadIpPool",
    
    # RADIUS Management
    "RadiusProfile",
    "ProfileUsage",
    "Realm",
    "Proxy",
    "RadHuntGroup",
    
    # Billing System
    "BillingPlan",
    "BillingHistory",
    "BillingMerchant",
    "BillingRate",
    "BillingPlanProfile",
    
    # Access Control
    "OperatorAcl",
    "OperatorAclFile",
    "Dictionary",
    "Message",
    "MessageType"
]