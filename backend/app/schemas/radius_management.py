"""
RADIUS Additional Management Schemas

This module contains Pydantic schemas for additional RADIUS management features
including IP pools, profiles, realms, proxies, and hunt groups.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from ipaddress import IPv4Address

# ===== IP Pool Schemas =====


class RadIpPoolBase(BaseModel):
    """Base IP Pool schema"""
    pool_name: str = Field(..., min_length=1, max_length=30,
                           description="IP pool name")
    framedipaddress: IPv4Address = Field(..., description="IP address")
    nasipaddress: IPv4Address = Field(..., description="NAS IP address")
    calledstationid: Optional[str] = Field(
        None, max_length=30, description="Called station ID")
    callingstationid: Optional[str] = Field(
        None, max_length=30, description="Calling station ID (MAC)")
    expiry_time: Optional[datetime] = Field(None, description="IP expiry time")
    username: Optional[str] = Field(
        None, max_length=64, description="Assigned username")
    pool_key: Optional[str] = Field(
        None, max_length=30, description="Pool key")


class RadIpPoolCreate(RadIpPoolBase):
    """Schema for creating IP pool entries"""
    pass


class RadIpPoolUpdate(BaseModel):
    """Schema for updating IP pool entries"""
    pool_name: Optional[str] = Field(None, min_length=1, max_length=30)
    framedipaddress: Optional[IPv4Address] = None
    nasipaddress: Optional[IPv4Address] = None
    calledstationid: Optional[str] = Field(None, max_length=30)
    callingstationid: Optional[str] = Field(None, max_length=30)
    expiry_time: Optional[datetime] = None
    username: Optional[str] = Field(None, max_length=64)
    pool_key: Optional[str] = Field(None, max_length=30)


class RadIpPoolResponse(RadIpPoolBase):
    """Schema for IP pool responses"""
    id: int = Field(..., description="IP pool entry ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ===== Profile Schemas =====

class RadiusAttribute(BaseModel):
    """Single RADIUS attribute"""
    attribute: str = Field(..., max_length=64, description="Attribute name")
    op: str = Field(..., max_length=2, description="Operator")
    value: str = Field(..., max_length=253, description="Attribute value")


class ProfileBase(BaseModel):
    """Base Profile schema"""
    profile_name: str = Field(..., min_length=1,
                              max_length=64, description="Profile name")
    description: Optional[str] = Field(
        None, max_length=255, description="Profile description")


class ProfileCreate(ProfileBase):
    """Schema for creating profiles"""
    check_attributes: List[RadiusAttribute] = Field(
        default_factory=list, description="Check attributes")
    reply_attributes: List[RadiusAttribute] = Field(
        default_factory=list, description="Reply attributes")


class ProfileUpdate(BaseModel):
    """Schema for updating profiles"""
    profile_name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=255)


class ProfileResponse(ProfileBase):
    """Schema for profile responses"""
    id: int = Field(..., description="Profile ID")
    check_attributes: List[RadiusAttribute] = Field(default_factory=list)
    reply_attributes: List[RadiusAttribute] = Field(default_factory=list)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ===== Realm Schemas =====

class RealmBase(BaseModel):
    """Base Realm schema"""
    realmname: str = Field(..., min_length=1,
                           max_length=64, description="Realm name")
    type: Optional[str] = Field(None, max_length=64, description="Realm type")
    authhost: Optional[str] = Field(
        None, max_length=128, description="Authentication host")
    accthost: Optional[str] = Field(
        None, max_length=128, description="Accounting host")
    secret: Optional[str] = Field(
        None, max_length=128, description="Shared secret")
    ldflag: Optional[str] = Field(None, max_length=64, description="Load flag")
    nostrip: bool = Field(default=False, description="No strip flag")
    hints: Optional[str] = Field(None, max_length=128, description="Hints")
    notrealm: Optional[str] = Field(
        None, max_length=128, description="No realm")


class RealmCreate(RealmBase):
    """Schema for creating realms"""
    pass


class RealmUpdate(BaseModel):
    """Schema for updating realms"""
    type: Optional[str] = Field(None, max_length=64)
    authhost: Optional[str] = Field(None, max_length=128)
    accthost: Optional[str] = Field(None, max_length=128)
    secret: Optional[str] = Field(None, max_length=128)
    ldflag: Optional[str] = Field(None, max_length=64)
    nostrip: Optional[bool] = None
    hints: Optional[str] = Field(None, max_length=128)
    notrealm: Optional[str] = Field(None, max_length=128)


class RealmResponse(RealmBase):
    """Schema for realm responses"""
    id: int = Field(..., description="Realm ID")
    is_active: bool = Field(..., description="Is realm active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ===== Proxy Schemas =====

class ProxyBase(BaseModel):
    """Base Proxy schema"""
    proxyname: str = Field(..., min_length=1,
                           max_length=128, description="Proxy name")
    retry_delay: Optional[int] = Field(
        None, ge=0, description="Retry delay in seconds")
    retry_count: Optional[int] = Field(
        None, ge=0, description="Number of retries")
    dead_time: Optional[int] = Field(
        None, ge=0, description="Dead time in seconds")
    default_fallback: bool = Field(
        default=False, description="Is default fallback")


class ProxyCreate(ProxyBase):
    """Schema for creating proxies"""
    pass


class ProxyUpdate(BaseModel):
    """Schema for updating proxies"""
    retry_delay: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)
    dead_time: Optional[int] = Field(None, ge=0)
    default_fallback: Optional[bool] = None


class ProxyResponse(ProxyBase):
    """Schema for proxy responses"""
    id: int = Field(..., description="Proxy ID")
    is_active: bool = Field(..., description="Is proxy active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ===== Hunt Group Schemas =====

class HuntGroupBase(BaseModel):
    """Base Hunt Group schema"""
    groupname: str = Field(..., min_length=1, max_length=64,
                           description="Hunt group name")
    nasipaddress: str = Field(..., max_length=15, description="NAS IP address")
    nasportid: Optional[str] = Field(
        None, max_length=15, description="NAS port ID")

    @validator('nasipaddress')
    def validate_nas_ip(cls, v):
        try:
            IPv4Address(v)
            return v
        except Exception:
            raise ValueError('Invalid IP address format')


class HuntGroupCreate(HuntGroupBase):
    """Schema for creating hunt groups"""
    pass


class HuntGroupUpdate(BaseModel):
    """Schema for updating hunt groups"""
    groupname: Optional[str] = Field(None, min_length=1, max_length=64)
    nasipaddress: Optional[str] = Field(None, max_length=15)
    nasportid: Optional[str] = Field(None, max_length=15)

    @validator('nasipaddress')
    def validate_nas_ip(cls, v):
        if v is not None:
            try:
                IPv4Address(v)
                return v
            except Exception:
                raise ValueError('Invalid IP address format')
        return v


class HuntGroupResponse(HuntGroupBase):
    """Schema for hunt group responses"""
    id: int = Field(..., description="Hunt group ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# ===== Statistics Schemas =====

class IpPoolStatistics(BaseModel):
    """IP Pool usage statistics"""
    total_pools: int = Field(..., description="Total number of pools")
    total_ips: int = Field(..., description="Total IP addresses")
    assigned_ips: int = Field(..., description="Assigned IP addresses")
    available_ips: int = Field(..., description="Available IP addresses")
    expired_ips: int = Field(..., description="Expired IP addresses")
    pools_by_nas: List[Dict[str, Any]] = Field(
        default_factory=list, description="Pools grouped by NAS")
    top_pools: List[Dict[str, Any]] = Field(
        default_factory=list, description="Most used pools")


class ProfileStatistics(BaseModel):
    """Profile usage statistics"""
    total_profiles: int = Field(..., description="Total number of profiles")
    active_profiles: int = Field(..., description="Active profiles")
    attributes_per_profile: Dict[str, int] = Field(
        default_factory=dict, description="Attributes per profile")


class RealmStatistics(BaseModel):
    """Realm statistics"""
    total_realms: int = Field(..., description="Total number of realms")
    active_realms: int = Field(..., description="Active realms")
    realms_by_type: Dict[str, int] = Field(
        default_factory=dict, description="Realms by type")


class ProxyStatistics(BaseModel):
    """Proxy statistics"""
    total_proxies: int = Field(..., description="Total number of proxies")
    active_proxies: int = Field(..., description="Active proxies")
    default_fallback_proxies: int = Field(...,
                                          description="Default fallback proxies")


class HuntGroupStatistics(BaseModel):
    """Hunt group statistics"""
    total_hunt_groups: int = Field(..., description="Total hunt groups")
    groups_by_nas: Dict[str, int] = Field(
        default_factory=dict, description="Groups by NAS")
    unique_nas_count: int = Field(..., description="Unique NAS count")


# ===== List Response Schemas =====

class IpPoolListResponse(BaseModel):
    """IP Pool list response"""
    pools: List[str] = Field(default_factory=list, description="Pool names")
    total: int = Field(..., description="Total count")


class ProfileListResponse(BaseModel):
    """Profile list response"""
    profiles: List[str] = Field(
        default_factory=list, description="Profile names")
    total: int = Field(..., description="Total count")


class RealmListResponse(BaseModel):
    """Realm list response"""
    realms: List[str] = Field(default_factory=list, description="Realm names")
    total: int = Field(..., description="Total count")


class ProxyListResponse(BaseModel):
    """Proxy list response"""
    proxies: List[str] = Field(default_factory=list, description="Proxy names")
    total: int = Field(..., description="Total count")


class HuntGroupListResponse(BaseModel):
    """Hunt group list response"""
    groups: List[str] = Field(default_factory=list,
                              description="Hunt group names")
    total: int = Field(..., description="Total count")


# Export all schemas
__all__ = [
    # IP Pool schemas
    "RadIpPoolBase",
    "RadIpPoolCreate",
    "RadIpPoolUpdate",
    "RadIpPoolResponse",

    # Profile schemas
    "RadiusAttribute",
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",

    # Realm schemas
    "RealmBase",
    "RealmCreate",
    "RealmUpdate",
    "RealmResponse",

    # Proxy schemas
    "ProxyBase",
    "ProxyCreate",
    "ProxyUpdate",
    "ProxyResponse",

    # Hunt Group schemas
    "HuntGroupBase",
    "HuntGroupCreate",
    "HuntGroupUpdate",
    "HuntGroupResponse",

    # Statistics schemas
    "IpPoolStatistics",
    "ProfileStatistics",
    "RealmStatistics",
    "ProxyStatistics",
    "HuntGroupStatistics",

    # List response schemas
    "IpPoolListResponse",
    "ProfileListResponse",
    "RealmListResponse",
    "ProxyListResponse",
    "HuntGroupListResponse",
]
