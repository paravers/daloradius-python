"""
RADIUS Management Repository Implementations

This module contains repository classes for additional RADIUS management operations
including IP pools, profiles, realms, proxies, and hunt groups.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, and_, or_, func, text, desc, asc
from sqlalchemy.exc import IntegrityError
from ipaddress import IPv4Address

from .base import BaseRepository
from ..models.radius_groups import RadIpPool
from ..models.radius_profile import RadiusProfile, ProfileUsage
from ..models.nas import Realm, Proxy
from ..models.radius import RadHuntGroup, GroupCheck, GroupReply
from ..schemas.radius_management import (
    RadIpPoolCreate, RadIpPoolUpdate,
    ProfileCreate, ProfileUpdate,
    RealmCreate, RealmUpdate,
    ProxyCreate, ProxyUpdate,
    HuntGroupCreate, HuntGroupUpdate
)


class RadIpPoolRepository(BaseRepository[RadIpPool, RadIpPoolCreate, RadIpPoolUpdate]):
    """Repository for RADIUS IP Pool management"""
    
    async def get_by_pool_name(self, pool_name: str) -> Optional[RadIpPool]:
        """Get IP pool entries by pool name"""
        query = select(RadIpPool).where(RadIpPool.pool_name == pool_name)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_ip_address(self, ip_address: str) -> Optional[RadIpPool]:
        """Get IP pool entry by IP address"""
        query = select(RadIpPool).where(RadIpPool.framedipaddress == ip_address)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_available_ips(
        self,
        pool_name: Optional[str] = None,
        nas_ip: Optional[str] = None
    ) -> List[RadIpPool]:
        """Get available IP addresses"""
        query = select(RadIpPool).where(
            or_(
                RadIpPool.username.is_(None),
                RadIpPool.username == '',
                and_(
                    RadIpPool.expiry_time.isnot(None),
                    RadIpPool.expiry_time < datetime.utcnow()
                )
            )
        )
        
        if pool_name:
            query = query.where(RadIpPool.pool_name == pool_name)
        if nas_ip:
            query = query.where(RadIpPool.nasipaddress == nas_ip)
            
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_assigned_ips(
        self,
        pool_name: Optional[str] = None,
        nas_ip: Optional[str] = None
    ) -> List[RadIpPool]:
        """Get assigned IP addresses"""
        query = select(RadIpPool).where(
            and_(
                RadIpPool.username.isnot(None),
                RadIpPool.username != '',
                or_(
                    RadIpPool.expiry_time.is_(None),
                    RadIpPool.expiry_time > datetime.utcnow()
                )
            )
        )
        
        if pool_name:
            query = query.where(RadIpPool.pool_name == pool_name)
        if nas_ip:
            query = query.where(RadIpPool.nasipaddress == nas_ip)
            
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def assign_ip(
        self,
        pool_name: str,
        username: str,
        nas_ip: str,
        expiry_time: Optional[datetime] = None
    ) -> Optional[RadIpPool]:
        """Assign an available IP to a user"""
        available_ips = await self.get_available_ips(pool_name=pool_name, nas_ip=nas_ip)
        
        if not available_ips:
            return None
            
        ip_entry = available_ips[0]
        ip_entry.username = username
        ip_entry.expiry_time = expiry_time
        ip_entry.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return ip_entry
    
    async def release_ip(self, ip_address: str) -> bool:
        """Release an IP address"""
        ip_entry = await self.get_by_ip_address(ip_address)
        if ip_entry:
            ip_entry.username = None
            ip_entry.expiry_time = None
            ip_entry.callingstationid = None
            ip_entry.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False
    
    async def get_pool_names(self) -> List[str]:
        """Get all unique pool names"""
        query = select(RadIpPool.pool_name).distinct().order_by(RadIpPool.pool_name)
        result = await self.db.execute(query)
        return [name for name, in result.all()]
    
    async def get_pool_statistics(self) -> Dict[str, Any]:
        """Get IP pool statistics"""
        # Total IPs
        total_query = select(func.count(RadIpPool.id))
        total_result = await self.db.execute(total_query)
        total_ips = total_result.scalar()
        
        # Assigned IPs
        assigned_query = select(func.count(RadIpPool.id)).where(
            and_(
                RadIpPool.username.isnot(None),
                RadIpPool.username != ''
            )
        )
        assigned_result = await self.db.execute(assigned_query)
        assigned_ips = assigned_result.scalar()
        
        # Expired IPs
        expired_query = select(func.count(RadIpPool.id)).where(
            and_(
                RadIpPool.expiry_time.isnot(None),
                RadIpPool.expiry_time < datetime.utcnow()
            )
        )
        expired_result = await self.db.execute(expired_query)
        expired_ips = expired_result.scalar()
        
        # Pools by NAS
        pools_by_nas_query = select(
            RadIpPool.nasipaddress,
            func.count(RadIpPool.id).label('ip_count')
        ).group_by(RadIpPool.nasipaddress)
        pools_by_nas_result = await self.db.execute(pools_by_nas_query)
        pools_by_nas = [
            {"nas_ip": row.nasipaddress, "ip_count": row.ip_count}
            for row in pools_by_nas_result.all()
        ]
        
        return {
            "total_ips": total_ips,
            "assigned_ips": assigned_ips,
            "available_ips": total_ips - assigned_ips,
            "expired_ips": expired_ips,
            "pools_by_nas": pools_by_nas
        }


class RadiusProfileRepository(BaseRepository[RadiusProfile, ProfileCreate, ProfileUpdate]):
    """Repository for RADIUS Profile management"""
    
    async def get_by_name(self, profile_name: str) -> Optional[RadiusProfile]:
        """Get profile by name"""
        query = select(RadiusProfile).where(RadiusProfile.profile_name == profile_name)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_profile_attributes(self, profile_name: str) -> Tuple[List[GroupCheck], List[GroupReply]]:
        """Get all attributes for a profile"""
        # Get check attributes
        check_query = select(GroupCheck).where(GroupCheck.groupname == profile_name)
        check_result = await self.db.execute(check_query)
        check_attributes = check_result.scalars().all()
        
        # Get reply attributes  
        reply_query = select(GroupReply).where(GroupReply.groupname == profile_name)
        reply_result = await self.db.execute(reply_query)
        reply_attributes = reply_result.scalars().all()
        
        return check_attributes, reply_attributes
    
    async def create_with_attributes(
        self,
        profile_data: ProfileCreate
    ) -> RadiusProfile:
        """Create profile with attributes"""
        # Create profile
        profile = RadiusProfile(
            profile_name=profile_data.profile_name,
            description=profile_data.description
        )
        self.db.add(profile)
        await self.db.flush()
        
        # Add check attributes
        for attr in profile_data.check_attributes:
            check_attr = GroupCheck(
                groupname=profile_data.profile_name,
                attribute=attr.attribute,
                op=attr.op,
                value=attr.value
            )
            self.db.add(check_attr)
        
        # Add reply attributes
        for attr in profile_data.reply_attributes:
            reply_attr = GroupReply(
                groupname=profile_data.profile_name,
                attribute=attr.attribute,
                op=attr.op,
                value=attr.value
            )
            self.db.add(reply_attr)
        
        await self.db.commit()
        return profile
    
    async def duplicate_profile(
        self,
        source_profile: str,
        new_profile: str,
        description: Optional[str] = None
    ) -> Optional[RadiusProfile]:
        """Duplicate an existing profile"""
        # Check if source exists
        source = await self.get_by_name(source_profile)
        if not source:
            return None
        
        # Get source attributes
        check_attrs, reply_attrs = await self.get_profile_attributes(source_profile)
        
        # Create new profile
        new_prof = RadiusProfile(
            profile_name=new_profile,
            description=description or f"Copy of {source_profile}"
        )
        self.db.add(new_prof)
        await self.db.flush()
        
        # Copy check attributes
        for attr in check_attrs:
            new_check = GroupCheck(
                groupname=new_profile,
                attribute=attr.attribute,
                op=attr.op,
                value=attr.value
            )
            self.db.add(new_check)
        
        # Copy reply attributes
        for attr in reply_attrs:
            new_reply = GroupReply(
                groupname=new_profile,
                attribute=attr.attribute,
                op=attr.op,
                value=attr.value
            )
            self.db.add(new_reply)
        
        await self.db.commit()
        return new_prof
    
    async def delete_with_attributes(self, profile_id: int) -> bool:
        """Delete profile and all its attributes"""
        profile = await self.get(profile_id)
        if not profile:
            return False
        
        profile_name = profile.profile_name
        
        # Delete check attributes
        check_delete = select(GroupCheck).where(GroupCheck.groupname == profile_name)
        check_result = await self.db.execute(check_delete)
        for attr in check_result.scalars().all():
            await self.db.delete(attr)
        
        # Delete reply attributes
        reply_delete = select(GroupReply).where(GroupReply.groupname == profile_name)
        reply_result = await self.db.execute(reply_delete)
        for attr in reply_result.scalars().all():
            await self.db.delete(attr)
        
        # Delete profile
        await self.db.delete(profile)
        await self.db.commit()
        return True
    
    async def get_profile_names(self) -> List[str]:
        """Get all profile names"""
        query = select(RadiusProfile.profile_name).order_by(RadiusProfile.profile_name)
        result = await self.db.execute(query)
        return [name for name, in result.all()]


class RealmRepository(BaseRepository[Realm, RealmCreate, RealmUpdate]):
    """Repository for RADIUS Realm management"""
    
    async def get_by_name(self, realmname: str) -> Optional[Realm]:
        """Get realm by name"""
        query = select(Realm).where(Realm.realmname == realmname)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_active_realms(self) -> List[Realm]:
        """Get all active realms"""
        query = select(Realm).where(Realm.is_active == True).order_by(Realm.realmname)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_realm_names(self) -> List[str]:
        """Get all realm names"""
        query = select(Realm.realmname).order_by(Realm.realmname)
        result = await self.db.execute(query)
        return [name for name, in result.all()]


class ProxyRepository(BaseRepository[Proxy, ProxyCreate, ProxyUpdate]):
    """Repository for RADIUS Proxy management"""
    
    async def get_by_name(self, proxyname: str) -> Optional[Proxy]:
        """Get proxy by name"""
        query = select(Proxy).where(Proxy.proxyname == proxyname)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_active_proxies(self) -> List[Proxy]:
        """Get all active proxies"""
        query = select(Proxy).where(Proxy.is_active == True).order_by(Proxy.proxyname)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_default_fallback_proxies(self) -> List[Proxy]:
        """Get default fallback proxies"""
        query = select(Proxy).where(
            and_(
                Proxy.is_active == True,
                Proxy.default_fallback == True
            )
        ).order_by(Proxy.proxyname)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_proxy_names(self) -> List[str]:
        """Get all proxy names"""
        query = select(Proxy.proxyname).order_by(Proxy.proxyname)
        result = await self.db.execute(query)
        return [name for name, in result.all()]


class HuntGroupRepository(BaseRepository[RadHuntGroup, HuntGroupCreate, HuntGroupUpdate]):
    """Repository for RADIUS Hunt Group management"""
    
    async def get_by_group_name(self, groupname: str) -> List[RadHuntGroup]:
        """Get hunt group entries by group name"""
        query = select(RadHuntGroup).where(RadHuntGroup.groupname == groupname)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_nas_ip(self, nas_ip: str) -> List[RadHuntGroup]:
        """Get hunt group entries by NAS IP"""
        query = select(RadHuntGroup).where(RadHuntGroup.nasipaddress == nas_ip)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_group_names(self) -> List[str]:
        """Get all unique group names"""
        query = select(RadHuntGroup.groupname).distinct().order_by(RadHuntGroup.groupname)
        result = await self.db.execute(query)
        return [name for name, in result.all()]
    
    async def get_nas_ips_for_group(self, groupname: str) -> List[str]:
        """Get all NAS IPs for a hunt group"""
        query = select(RadHuntGroup.nasipaddress).where(
            RadHuntGroup.groupname == groupname
        ).distinct().order_by(RadHuntGroup.nasipaddress)
        result = await self.db.execute(query)
        return [ip for ip, in result.all()]
    
    async def get_hunt_group_statistics(self) -> Dict[str, Any]:
        """Get hunt group statistics"""
        # Total groups
        total_query = select(func.count(RadHuntGroup.id))
        total_result = await self.db.execute(total_query)
        total_groups = total_result.scalar()
        
        # Unique group names
        unique_groups_query = select(func.count(func.distinct(RadHuntGroup.groupname)))
        unique_groups_result = await self.db.execute(unique_groups_query)
        unique_groups = unique_groups_result.scalar()
        
        # Unique NAS IPs
        unique_nas_query = select(func.count(func.distinct(RadHuntGroup.nasipaddress)))
        unique_nas_result = await self.db.execute(unique_nas_query)
        unique_nas = unique_nas_result.scalar()
        
        # Groups by NAS
        groups_by_nas_query = select(
            RadHuntGroup.nasipaddress,
            func.count(func.distinct(RadHuntGroup.groupname)).label('group_count')
        ).group_by(RadHuntGroup.nasipaddress)
        groups_by_nas_result = await self.db.execute(groups_by_nas_query)
        groups_by_nas = {
            row.nasipaddress: row.group_count
            for row in groups_by_nas_result.all()
        }
        
        return {
            "total_hunt_groups": total_groups,
            "unique_group_names": unique_groups,
            "unique_nas_count": unique_nas,
            "groups_by_nas": groups_by_nas
        }


# Export all repositories
__all__ = [
    "RadIpPoolRepository",
    "RadiusProfileRepository",
    "RealmRepository",
    "ProxyRepository",
    "HuntGroupRepository"
]