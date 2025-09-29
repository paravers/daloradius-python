"""
RADIUS Management Service Layer

This module provides business logic for RADIUS management operations
including IP pools, profiles, realms, proxies, and hunt groups.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.radius_management import (
    RadIpPoolRepository,
    RadiusProfileRepository,
    RealmRepository,
    ProxyRepository,
    HuntGroupRepository
)
from ..schemas.radius_management import (
    RadIpPoolCreate, RadIpPoolUpdate, RadIpPoolResponse,
    ProfileCreate, ProfileUpdate, ProfileResponse,
    RealmCreate, RealmUpdate, RealmResponse,
    ProxyCreate, ProxyUpdate, ProxyResponse,
    HuntGroupCreate, HuntGroupUpdate, HuntGroupResponse,
    IpPoolStatistics, ProfileStatistics, RealmStatistics,
    ProxyStatistics, HuntGroupStatistics
)
from ..core.exceptions import ValidationError, NotFoundError, ConflictError


class RadIpPoolService:
    """Service for IP Pool management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RadIpPoolRepository(db)
    
    async def create_ip_pool_entry(self, data: RadIpPoolCreate) -> RadIpPoolResponse:
        """Create a new IP pool entry"""
        # Check if IP already exists
        existing = await self.repository.get_by_ip_address(str(data.framedipaddress))
        if existing:
            raise ConflictError(f"IP address {data.framedipaddress} already exists in pool")
        
        entry = await self.repository.create(data)
        return RadIpPoolResponse.from_orm(entry)
    
    async def get_ip_pool_entries(
        self,
        skip: int = 0,
        limit: int = 100,
        pool_name: Optional[str] = None,
        nas_ip: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[RadIpPoolResponse]:
        """Get IP pool entries with filtering"""
        if status == "available":
            entries = await self.repository.get_available_ips(pool_name, nas_ip)
        elif status == "assigned":
            entries = await self.repository.get_assigned_ips(pool_name, nas_ip)
        else:
            # Apply manual filtering
            filters = {}
            if pool_name:
                filters["pool_name"] = pool_name
            if nas_ip:
                filters["nasipaddress"] = nas_ip
                
            entries = await self.repository.get_multi(
                skip=skip,
                limit=limit,
                filters=filters
            )
        
        return [RadIpPoolResponse.from_orm(entry) for entry in entries]
    
    async def get_ip_pool_entry(self, entry_id: int) -> RadIpPoolResponse:
        """Get IP pool entry by ID"""
        entry = await self.repository.get(entry_id)
        if not entry:
            raise NotFoundError(f"IP pool entry with ID {entry_id} not found")
        return RadIpPoolResponse.from_orm(entry)
    
    async def update_ip_pool_entry(
        self,
        entry_id: int,
        data: RadIpPoolUpdate
    ) -> RadIpPoolResponse:
        """Update IP pool entry"""
        entry = await self.repository.get(entry_id)
        if not entry:
            raise NotFoundError(f"IP pool entry with ID {entry_id} not found")
        
        # Check IP conflicts if changing IP
        if data.framedipaddress and data.framedipaddress != entry.framedipaddress:
            existing = await self.repository.get_by_ip_address(str(data.framedipaddress))
            if existing and existing.id != entry_id:
                raise ConflictError(f"IP address {data.framedipaddress} already exists")
        
        updated_entry = await self.repository.update(entry_id, data)
        return RadIpPoolResponse.from_orm(updated_entry)
    
    async def delete_ip_pool_entry(self, entry_id: int) -> bool:
        """Delete IP pool entry"""
        entry = await self.repository.get(entry_id)
        if not entry:
            raise NotFoundError(f"IP pool entry with ID {entry_id} not found")
        
        return await self.repository.delete(entry_id)
    
    async def assign_ip_to_user(
        self,
        pool_name: str,
        username: str,
        nas_ip: str,
        duration_hours: Optional[int] = None
    ) -> Optional[RadIpPoolResponse]:
        """Assign an available IP to a user"""
        expiry_time = None
        if duration_hours:
            expiry_time = datetime.utcnow() + timedelta(hours=duration_hours)
        
        entry = await self.repository.assign_ip(pool_name, username, nas_ip, expiry_time)
        if entry:
            return RadIpPoolResponse.from_orm(entry)
        return None
    
    async def release_user_ip(self, ip_address: str) -> bool:
        """Release an IP address from a user"""
        return await self.repository.release_ip(ip_address)
    
    async def get_pool_names(self) -> List[str]:
        """Get all unique pool names"""
        return await self.repository.get_pool_names()
    
    async def get_statistics(self) -> IpPoolStatistics:
        """Get IP pool statistics"""
        stats = await self.repository.get_pool_statistics()
        return IpPoolStatistics(**stats)


class RadiusProfileService:
    """Service for RADIUS Profile management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RadiusProfileRepository(db)
    
    async def create_profile(self, data: ProfileCreate) -> ProfileResponse:
        """Create a new profile with attributes"""
        # Check if profile name already exists
        existing = await self.repository.get_by_name(data.profile_name)
        if existing:
            raise ConflictError(f"Profile '{data.profile_name}' already exists")
        
        # Validate attribute names
        self._validate_attributes(data.check_attributes + data.reply_attributes)
        
        profile = await self.repository.create_with_attributes(data)
        
        # Get attributes for response
        check_attrs, reply_attrs = await self.repository.get_profile_attributes(profile.profile_name)
        
        response = ProfileResponse.from_orm(profile)
        response.check_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in check_attrs
        ]
        response.reply_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in reply_attrs
        ]
        
        return response
    
    async def get_profiles(
        self,
        skip: int = 0,
        limit: int = 100,
        include_attributes: bool = False
    ) -> List[ProfileResponse]:
        """Get profiles with optional attributes"""
        profiles = await self.repository.get_multi(skip=skip, limit=limit)
        
        responses = []
        for profile in profiles:
            response = ProfileResponse.from_orm(profile)
            
            if include_attributes:
                check_attrs, reply_attrs = await self.repository.get_profile_attributes(profile.profile_name)
                response.check_attributes = [
                    {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
                    for attr in check_attrs
                ]
                response.reply_attributes = [
                    {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
                    for attr in reply_attrs
                ]
            
            responses.append(response)
        
        return responses
    
    async def get_profile(self, profile_id: int) -> ProfileResponse:
        """Get profile by ID with attributes"""
        profile = await self.repository.get(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with ID {profile_id} not found")
        
        check_attrs, reply_attrs = await self.repository.get_profile_attributes(profile.profile_name)
        
        response = ProfileResponse.from_orm(profile)
        response.check_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in check_attrs
        ]
        response.reply_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in reply_attrs
        ]
        
        return response
    
    async def get_profile_by_name(self, profile_name: str) -> ProfileResponse:
        """Get profile by name with attributes"""
        profile = await self.repository.get_by_name(profile_name)
        if not profile:
            raise NotFoundError(f"Profile '{profile_name}' not found")
        
        check_attrs, reply_attrs = await self.repository.get_profile_attributes(profile_name)
        
        response = ProfileResponse.from_orm(profile)
        response.check_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in check_attrs
        ]
        response.reply_attributes = [
            {"attribute": attr.attribute, "op": attr.op, "value": attr.value}
            for attr in reply_attrs
        ]
        
        return response
    
    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileResponse:
        """Update profile basic information"""
        profile = await self.repository.get(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with ID {profile_id} not found")
        
        updated_profile = await self.repository.update(profile_id, data)
        return ProfileResponse.from_orm(updated_profile)
    
    async def duplicate_profile(
        self,
        source_profile: str,
        new_profile: str,
        description: Optional[str] = None
    ) -> ProfileResponse:
        """Duplicate an existing profile"""
        # Check if new profile name already exists
        existing = await self.repository.get_by_name(new_profile)
        if existing:
            raise ConflictError(f"Profile '{new_profile}' already exists")
        
        duplicated = await self.repository.duplicate_profile(
            source_profile, new_profile, description
        )
        
        if not duplicated:
            raise NotFoundError(f"Source profile '{source_profile}' not found")
        
        return ProfileResponse.from_orm(duplicated)
    
    async def delete_profile(self, profile_id: int) -> bool:
        """Delete profile and all its attributes"""
        return await self.repository.delete_with_attributes(profile_id)
    
    async def get_profile_names(self) -> List[str]:
        """Get all profile names"""
        return await self.repository.get_profile_names()
    
    def _validate_attributes(self, attributes: List[Any]) -> None:
        """Validate RADIUS attributes"""
        for attr in attributes:
            if not attr.attribute or len(attr.attribute.strip()) == 0:
                raise ValidationError("Attribute name cannot be empty")
            
            if not attr.op or attr.op not in ['==', ':=', '+=', '!=', '>', '>=', '<', '<=', '=~', '!~']:
                raise ValidationError(f"Invalid operator '{attr.op}'")
            
            if not attr.value or len(attr.value.strip()) == 0:
                raise ValidationError("Attribute value cannot be empty")


class RealmService:
    """Service for Realm management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RealmRepository(db)
    
    async def create_realm(self, data: RealmCreate) -> RealmResponse:
        """Create a new realm"""
        # Check if realm name already exists
        existing = await self.repository.get_by_name(data.realmname)
        if existing:
            raise ConflictError(f"Realm '{data.realmname}' already exists")
        
        realm = await self.repository.create(data)
        return RealmResponse.from_orm(realm)
    
    async def get_realms(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[RealmResponse]:
        """Get realms with filtering"""
        if active_only:
            realms = await self.repository.get_active_realms()
        else:
            realms = await self.repository.get_multi(skip=skip, limit=limit)
        
        return [RealmResponse.from_orm(realm) for realm in realms]
    
    async def get_realm(self, realm_id: int) -> RealmResponse:
        """Get realm by ID"""
        realm = await self.repository.get(realm_id)
        if not realm:
            raise NotFoundError(f"Realm with ID {realm_id} not found")
        return RealmResponse.from_orm(realm)
    
    async def get_realm_by_name(self, realmname: str) -> RealmResponse:
        """Get realm by name"""
        realm = await self.repository.get_by_name(realmname)
        if not realm:
            raise NotFoundError(f"Realm '{realmname}' not found")
        return RealmResponse.from_orm(realm)
    
    async def update_realm(self, realm_id: int, data: RealmUpdate) -> RealmResponse:
        """Update realm"""
        realm = await self.repository.get(realm_id)
        if not realm:
            raise NotFoundError(f"Realm with ID {realm_id} not found")
        
        updated_realm = await self.repository.update(realm_id, data)
        return RealmResponse.from_orm(updated_realm)
    
    async def delete_realm(self, realm_id: int) -> bool:
        """Delete realm"""
        realm = await self.repository.get(realm_id)
        if not realm:
            raise NotFoundError(f"Realm with ID {realm_id} not found")
        
        return await self.repository.delete(realm_id)
    
    async def get_realm_names(self) -> List[str]:
        """Get all realm names"""
        return await self.repository.get_realm_names()


class ProxyService:
    """Service for Proxy management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProxyRepository(db)
    
    async def create_proxy(self, data: ProxyCreate) -> ProxyResponse:
        """Create a new proxy"""
        # Check if proxy name already exists
        existing = await self.repository.get_by_name(data.proxyname)
        if existing:
            raise ConflictError(f"Proxy '{data.proxyname}' already exists")
        
        proxy = await self.repository.create(data)
        return ProxyResponse.from_orm(proxy)
    
    async def get_proxies(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[ProxyResponse]:
        """Get proxies with filtering"""
        if active_only:
            proxies = await self.repository.get_active_proxies()
        else:
            proxies = await self.repository.get_multi(skip=skip, limit=limit)
        
        return [ProxyResponse.from_orm(proxy) for proxy in proxies]
    
    async def get_proxy(self, proxy_id: int) -> ProxyResponse:
        """Get proxy by ID"""
        proxy = await self.repository.get(proxy_id)
        if not proxy:
            raise NotFoundError(f"Proxy with ID {proxy_id} not found")
        return ProxyResponse.from_orm(proxy)
    
    async def get_proxy_by_name(self, proxyname: str) -> ProxyResponse:
        """Get proxy by name"""
        proxy = await self.repository.get_by_name(proxyname)
        if not proxy:
            raise NotFoundError(f"Proxy '{proxyname}' not found")
        return ProxyResponse.from_orm(proxy)
    
    async def update_proxy(self, proxy_id: int, data: ProxyUpdate) -> ProxyResponse:
        """Update proxy"""
        proxy = await self.repository.get(proxy_id)
        if not proxy:
            raise NotFoundError(f"Proxy with ID {proxy_id} not found")
        
        updated_proxy = await self.repository.update(proxy_id, data)
        return ProxyResponse.from_orm(updated_proxy)
    
    async def delete_proxy(self, proxy_id: int) -> bool:
        """Delete proxy"""
        proxy = await self.repository.get(proxy_id)
        if not proxy:
            raise NotFoundError(f"Proxy with ID {proxy_id} not found")
        
        return await self.repository.delete(proxy_id)
    
    async def get_proxy_names(self) -> List[str]:
        """Get all proxy names"""
        return await self.repository.get_proxy_names()


class HuntGroupService:
    """Service for Hunt Group management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = HuntGroupRepository(db)
    
    async def create_hunt_group(self, data: HuntGroupCreate) -> HuntGroupResponse:
        """Create a new hunt group entry"""
        hunt_group = await self.repository.create(data)
        return HuntGroupResponse.from_orm(hunt_group)
    
    async def get_hunt_groups(
        self,
        skip: int = 0,
        limit: int = 100,
        groupname: Optional[str] = None,
        nas_ip: Optional[str] = None
    ) -> List[HuntGroupResponse]:
        """Get hunt groups with filtering"""
        if groupname:
            groups = await self.repository.get_by_group_name(groupname)
        elif nas_ip:
            groups = await self.repository.get_by_nas_ip(nas_ip)
        else:
            groups = await self.repository.get_multi(skip=skip, limit=limit)
        
        return [HuntGroupResponse.from_orm(group) for group in groups]
    
    async def get_hunt_group(self, group_id: int) -> HuntGroupResponse:
        """Get hunt group by ID"""
        group = await self.repository.get(group_id)
        if not group:
            raise NotFoundError(f"Hunt group with ID {group_id} not found")
        return HuntGroupResponse.from_orm(group)
    
    async def update_hunt_group(self, group_id: int, data: HuntGroupUpdate) -> HuntGroupResponse:
        """Update hunt group"""
        group = await self.repository.get(group_id)
        if not group:
            raise NotFoundError(f"Hunt group with ID {group_id} not found")
        
        updated_group = await self.repository.update(group_id, data)
        return HuntGroupResponse.from_orm(updated_group)
    
    async def delete_hunt_group(self, group_id: int) -> bool:
        """Delete hunt group"""
        group = await self.repository.get(group_id)
        if not group:
            raise NotFoundError(f"Hunt group with ID {group_id} not found")
        
        return await self.repository.delete(group_id)
    
    async def get_group_names(self) -> List[str]:
        """Get all unique group names"""
        return await self.repository.get_group_names()
    
    async def get_nas_ips_for_group(self, groupname: str) -> List[str]:
        """Get all NAS IPs for a hunt group"""
        return await self.repository.get_nas_ips_for_group(groupname)
    
    async def get_statistics(self) -> HuntGroupStatistics:
        """Get hunt group statistics"""
        stats = await self.repository.get_hunt_group_statistics()
        return HuntGroupStatistics(**stats)


# Export all services
__all__ = [
    "RadIpPoolService",
    "RadiusProfileService", 
    "RealmService",
    "ProxyService",
    "HuntGroupService"
]