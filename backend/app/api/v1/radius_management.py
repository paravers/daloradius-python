"""
RADIUS Management API Routes

This module provides RESTful API endpoints for managing additional RADIUS features
including IP pools, profiles, realms, proxies, and hunt groups.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_db
from ...core.auth import get_current_user
from ...core.pagination import PaginationParams, PaginatedResponse
from ...models.user import User
from ...services.radius_management import (
    RadIpPoolService,
    RadiusProfileService,
    RealmService,
    ProxyService,
    HuntGroupService
)
from ...schemas.radius_management import (
    RadIpPoolCreate, RadIpPoolUpdate, RadIpPoolResponse,
    ProfileCreate, ProfileUpdate, ProfileResponse,
    RealmCreate, RealmUpdate, RealmResponse,
    ProxyCreate, ProxyUpdate, ProxyResponse,
    HuntGroupCreate, HuntGroupUpdate, HuntGroupResponse,
    IpPoolStatistics, ProfileStatistics, RealmStatistics,
    ProxyStatistics, HuntGroupStatistics,
    IpPoolListResponse, ProfileListResponse, RealmListResponse,
    ProxyListResponse, HuntGroupListResponse
)
from ...core.exceptions import ValidationError, NotFoundError, ConflictError

router = APIRouter()


# ===== IP Pool Management Routes =====

@router.get("/ip-pools", response_model=PaginatedResponse[RadIpPoolResponse])
async def list_ip_pool_entries(
    pagination: PaginationParams = Depends(),
    pool_name: Optional[str] = Query(None, description="Filter by pool name"),
    nas_ip: Optional[str] = Query(None, description="Filter by NAS IP"),
    status: Optional[str] = Query(None, description="Filter by status: available, assigned"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of IP pool entries"""
    try:
        service = RadIpPoolService(db)
        entries = await service.get_ip_pool_entries(
            skip=pagination.skip,
            limit=pagination.limit,
            pool_name=pool_name,
            nas_ip=nas_ip,
            status=status
        )
        
        # Get total count (simplified for now)
        total = len(entries) if len(entries) < pagination.limit else pagination.skip + len(entries) + 1
        
        return PaginatedResponse(
            items=entries,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list IP pool entries: {str(e)}"
        )


@router.post("/ip-pools", response_model=RadIpPoolResponse)
async def create_ip_pool_entry(
    data: RadIpPoolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new IP pool entry"""
    try:
        service = RadIpPoolService(db)
        return await service.create_ip_pool_entry(data)
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/ip-pools/{entry_id}", response_model=RadIpPoolResponse)
async def get_ip_pool_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific IP pool entry"""
    try:
        service = RadIpPoolService(db)
        return await service.get_ip_pool_entry(entry_id)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/ip-pools/{entry_id}", response_model=RadIpPoolResponse)
async def update_ip_pool_entry(
    entry_id: int,
    data: RadIpPoolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update IP pool entry"""
    try:
        service = RadIpPoolService(db)
        return await service.update_ip_pool_entry(entry_id, data)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/ip-pools/{entry_id}")
async def delete_ip_pool_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete IP pool entry"""
    try:
        service = RadIpPoolService(db)
        success = await service.delete_ip_pool_entry(entry_id)
        
        if success:
            return {"message": "IP pool entry deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete IP pool entry"
            )
            
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/ip-pools/assign")
async def assign_ip_to_user(
    pool_name: str = Query(..., description="Pool name"),
    username: str = Query(..., description="Username"),
    nas_ip: str = Query(..., description="NAS IP address"),
    duration_hours: Optional[int] = Query(None, description="Assignment duration in hours"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign available IP to user"""
    try:
        service = RadIpPoolService(db)
        result = await service.assign_ip_to_user(pool_name, username, nas_ip, duration_hours)
        
        if result:
            return {"message": "IP assigned successfully", "ip_entry": result}
        else:
            return {"message": "No available IP addresses in the specified pool"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign IP: {str(e)}"
        )


@router.post("/ip-pools/release/{ip_address}")
async def release_ip_from_user(
    ip_address: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Release IP address from user"""
    try:
        service = RadIpPoolService(db)
        success = await service.release_user_ip(ip_address)
        
        if success:
            return {"message": f"IP address {ip_address} released successfully"}
        else:
            return {"message": f"IP address {ip_address} not found or not assigned"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to release IP: {str(e)}"
        )


@router.get("/ip-pools/pools/list", response_model=IpPoolListResponse)
async def list_pool_names(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all pool names"""
    try:
        service = RadIpPoolService(db)
        pools = await service.get_pool_names()
        return IpPoolListResponse(pools=pools, total=len(pools))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pool names: {str(e)}"
        )


@router.get("/ip-pools/statistics", response_model=IpPoolStatistics)
async def get_ip_pool_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get IP pool usage statistics"""
    try:
        service = RadIpPoolService(db)
        return await service.get_statistics()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get IP pool statistics: {str(e)}"
        )


# ===== Profile Management Routes =====

@router.get("/profiles", response_model=PaginatedResponse[ProfileResponse])
async def list_profiles(
    pagination: PaginationParams = Depends(),
    include_attributes: bool = Query(False, description="Include attribute details"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of profiles"""
    try:
        service = RadiusProfileService(db)
        profiles = await service.get_profiles(
            skip=pagination.skip,
            limit=pagination.limit,
            include_attributes=include_attributes
        )
        
        total = len(profiles) if len(profiles) < pagination.limit else pagination.skip + len(profiles) + 1
        
        return PaginatedResponse(
            items=profiles,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}"
        )


@router.post("/profiles", response_model=ProfileResponse)
async def create_profile(
    data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new profile with attributes"""
    try:
        service = RadiusProfileService(db)
        return await service.create_profile(data)
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific profile with attributes"""
    try:
        service = RadiusProfileService(db)
        return await service.get_profile(profile_id)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/profiles/by-name/{profile_name}", response_model=ProfileResponse)
async def get_profile_by_name(
    profile_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get profile by name with attributes"""
    try:
        service = RadiusProfileService(db)
        return await service.get_profile_by_name(profile_name)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update profile basic information"""
    try:
        service = RadiusProfileService(db)
        return await service.update_profile(profile_id, data)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/profiles/duplicate", response_model=ProfileResponse)
async def duplicate_profile(
    source_profile: str = Query(..., description="Source profile name"),
    new_profile: str = Query(..., description="New profile name"),
    description: Optional[str] = Query(None, description="New profile description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate an existing profile"""
    try:
        service = RadiusProfileService(db)
        return await service.duplicate_profile(source_profile, new_profile, description)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete profile and all its attributes"""
    try:
        service = RadiusProfileService(db)
        success = await service.delete_profile(profile_id)
        
        if success:
            return {"message": "Profile deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )


@router.get("/profiles/names/list", response_model=ProfileListResponse)
async def list_profile_names(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all profile names"""
    try:
        service = RadiusProfileService(db)
        profiles = await service.get_profile_names()
        return ProfileListResponse(profiles=profiles, total=len(profiles))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile names: {str(e)}"
        )


# ===== Realm Management Routes =====

@router.get("/realms", response_model=PaginatedResponse[RealmResponse])
async def list_realms(
    pagination: PaginationParams = Depends(),
    active_only: bool = Query(False, description="Show only active realms"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of realms"""
    try:
        service = RealmService(db)
        realms = await service.get_realms(
            skip=pagination.skip,
            limit=pagination.limit,
            active_only=active_only
        )
        
        total = len(realms) if len(realms) < pagination.limit else pagination.skip + len(realms) + 1
        
        return PaginatedResponse(
            items=realms,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list realms: {str(e)}"
        )


@router.post("/realms", response_model=RealmResponse)
async def create_realm(
    data: RealmCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new realm"""
    try:
        service = RealmService(db)
        return await service.create_realm(data)
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/realms/{realm_id}", response_model=RealmResponse)
async def get_realm(
    realm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific realm"""
    try:
        service = RealmService(db)
        return await service.get_realm(realm_id)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/realms/by-name/{realmname}", response_model=RealmResponse)
async def get_realm_by_name(
    realmname: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get realm by name"""
    try:
        service = RealmService(db)
        return await service.get_realm_by_name(realmname)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/realms/{realm_id}", response_model=RealmResponse)
async def update_realm(
    realm_id: int,
    data: RealmUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update realm"""
    try:
        service = RealmService(db)
        return await service.update_realm(realm_id, data)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/realms/{realm_id}")
async def delete_realm(
    realm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete realm"""
    try:
        service = RealmService(db)
        success = await service.delete_realm(realm_id)
        
        if success:
            return {"message": "Realm deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete realm"
            )
            
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/realms/names/list", response_model=RealmListResponse)
async def list_realm_names(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all realm names"""
    try:
        service = RealmService(db)
        realms = await service.get_realm_names()
        return RealmListResponse(realms=realms, total=len(realms))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get realm names: {str(e)}"
        )


# ===== Proxy Management Routes =====

@router.get("/proxies", response_model=PaginatedResponse[ProxyResponse])
async def list_proxies(
    pagination: PaginationParams = Depends(),
    active_only: bool = Query(False, description="Show only active proxies"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of proxies"""
    try:
        service = ProxyService(db)
        proxies = await service.get_proxies(
            skip=pagination.skip,
            limit=pagination.limit,
            active_only=active_only
        )
        
        total = len(proxies) if len(proxies) < pagination.limit else pagination.skip + len(proxies) + 1
        
        return PaginatedResponse(
            items=proxies,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list proxies: {str(e)}"
        )


@router.post("/proxies", response_model=ProxyResponse)
async def create_proxy(
    data: ProxyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new proxy"""
    try:
        service = ProxyService(db)
        return await service.create_proxy(data)
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/proxies/{proxy_id}", response_model=ProxyResponse)
async def get_proxy(
    proxy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific proxy"""
    try:
        service = ProxyService(db)
        return await service.get_proxy(proxy_id)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/proxies/{proxy_id}", response_model=ProxyResponse)
async def update_proxy(
    proxy_id: int,
    data: ProxyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update proxy"""
    try:
        service = ProxyService(db)
        return await service.update_proxy(proxy_id, data)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/proxies/{proxy_id}")
async def delete_proxy(
    proxy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete proxy"""
    try:
        service = ProxyService(db)
        success = await service.delete_proxy(proxy_id)
        
        if success:
            return {"message": "Proxy deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete proxy"
            )
            
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/proxies/names/list", response_model=ProxyListResponse)
async def list_proxy_names(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all proxy names"""
    try:
        service = ProxyService(db)
        proxies = await service.get_proxy_names()
        return ProxyListResponse(proxies=proxies, total=len(proxies))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get proxy names: {str(e)}"
        )


# ===== Hunt Group Management Routes =====

@router.get("/hunt-groups", response_model=PaginatedResponse[HuntGroupResponse])
async def list_hunt_groups(
    pagination: PaginationParams = Depends(),
    groupname: Optional[str] = Query(None, description="Filter by group name"),
    nas_ip: Optional[str] = Query(None, description="Filter by NAS IP"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of hunt groups"""
    try:
        service = HuntGroupService(db)
        groups = await service.get_hunt_groups(
            skip=pagination.skip,
            limit=pagination.limit,
            groupname=groupname,
            nas_ip=nas_ip
        )
        
        total = len(groups) if len(groups) < pagination.limit else pagination.skip + len(groups) + 1
        
        return PaginatedResponse(
            items=groups,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list hunt groups: {str(e)}"
        )


@router.post("/hunt-groups", response_model=HuntGroupResponse)
async def create_hunt_group(
    data: HuntGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new hunt group"""
    try:
        service = HuntGroupService(db)
        return await service.create_hunt_group(data)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/hunt-groups/{group_id}", response_model=HuntGroupResponse)
async def get_hunt_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific hunt group"""
    try:
        service = HuntGroupService(db)
        return await service.get_hunt_group(group_id)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/hunt-groups/{group_id}", response_model=HuntGroupResponse)
async def update_hunt_group(
    group_id: int,
    data: HuntGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update hunt group"""
    try:
        service = HuntGroupService(db)
        return await service.update_hunt_group(group_id, data)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/hunt-groups/{group_id}")
async def delete_hunt_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete hunt group"""
    try:
        service = HuntGroupService(db)
        success = await service.delete_hunt_group(group_id)
        
        if success:
            return {"message": "Hunt group deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete hunt group"
            )
            
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/hunt-groups/groups/list", response_model=HuntGroupListResponse)
async def list_hunt_group_names(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all hunt group names"""
    try:
        service = HuntGroupService(db)
        groups = await service.get_group_names()
        return HuntGroupListResponse(groups=groups, total=len(groups))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hunt group names: {str(e)}"
        )


@router.get("/hunt-groups/groups/{groupname}/nas-ips")
async def get_nas_ips_for_hunt_group(
    groupname: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all NAS IPs for a hunt group"""
    try:
        service = HuntGroupService(db)
        nas_ips = await service.get_nas_ips_for_group(groupname)
        return {"groupname": groupname, "nas_ips": nas_ips, "total": len(nas_ips)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NAS IPs for hunt group: {str(e)}"
        )


@router.get("/hunt-groups/statistics", response_model=HuntGroupStatistics)
async def get_hunt_group_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hunt group statistics"""
    try:
        service = HuntGroupService(db)
        return await service.get_statistics()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hunt group statistics: {str(e)}"
        )


# Export the router
__all__ = ["router"]