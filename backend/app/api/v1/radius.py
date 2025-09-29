"""
RADIUS Attributes API Routes

This module provides RESTful API endpoints for managing RADIUS attributes,
including RadCheck (authentication) and RadReply (authorization) attributes.
"""

from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ...db.session import get_db
from ...repositories.radius import RadcheckRepository, RadreplyRepository
from ...schemas.radius import (
    RadcheckCreate, RadcheckUpdate, RadcheckResponse,
    RadreplyCreate, RadreplyUpdate, RadreplyResponse,
    RadgroupcheckCreate, RadgroupcheckResponse,
    RadgroupreplyCreate, RadgroupreplyResponse,
    GroupListResponse, GroupAttributesResponse, GroupStatisticsResponse,
    RadiusOperator
)
from ...core.pagination import PaginationParams, PaginatedResponse


router = APIRouter()


# ===== RadCheck (Authentication Attributes) Routes =====

@router.get("/radcheck", response_model=PaginatedResponse[RadcheckResponse])
async def list_radcheck_attributes(
    username: Optional[str] = Query(None, description="Filter by username"),
    attribute: Optional[str] = Query(None, description="Filter by attribute name"),
    search: Optional[str] = Query(None, description="Search in username or attribute"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of RadCheck attributes with filtering and pagination
    """
    repo = RadcheckRepository(db)
    
    # Build filters
    filters = {}
    if username:
        filters["username"] = username
    if attribute:
        filters["attribute"] = attribute
    
    # Apply search
    search_fields = ["username", "attribute", "value"] if search else None
    
    try:
        items, total = await repo.get_paginated(
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters,
            search_term=search,
            search_fields=search_fields,
            order_by="username"
        )
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve RadCheck attributes: {str(e)}"
        )


@router.get("/radcheck/{attribute_id}", response_model=RadcheckResponse)
async def get_radcheck_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific RadCheck attribute by ID
    """
    repo = RadcheckRepository(db)
    
    attribute = await repo.get(attribute_id)
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadCheck attribute not found"
        )
    
    return attribute


@router.post("/radcheck", response_model=RadcheckResponse)
async def create_radcheck_attribute(
    attribute_data: RadcheckCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new RadCheck attribute
    """
    repo = RadcheckRepository(db)
    
    try:
        # Check if attribute already exists for user
        existing = await repo.get_user_attribute(
            attribute_data.username, 
            attribute_data.attribute
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Attribute '{attribute_data.attribute}' already exists for user '{attribute_data.username}'"
            )
        
        attribute = await repo.create(attribute_data)
        return attribute
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create RadCheck attribute: {str(e)}"
        )


@router.put("/radcheck/{attribute_id}", response_model=RadcheckResponse)
async def update_radcheck_attribute(
    attribute_id: int,
    attribute_data: RadcheckUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing RadCheck attribute
    """
    repo = RadcheckRepository(db)
    
    existing = await repo.get(attribute_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadCheck attribute not found"
        )
    
    try:
        attribute = await repo.update(existing, attribute_data)
        return attribute
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update RadCheck attribute: {str(e)}"
        )


@router.delete("/radcheck/{attribute_id}")
async def delete_radcheck_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a RadCheck attribute
    """
    repo = RadcheckRepository(db)
    
    existing = await repo.get(attribute_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadCheck attribute not found"
        )
    
    try:
        await repo.delete(existing)
        return {"message": "RadCheck attribute deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete RadCheck attribute: {str(e)}"
        )


# ===== RadReply (Authorization Attributes) Routes =====

@router.get("/radreply", response_model=PaginatedResponse[RadreplyResponse])
async def list_radreply_attributes(
    username: Optional[str] = Query(None, description="Filter by username"),
    attribute: Optional[str] = Query(None, description="Filter by attribute name"),
    search: Optional[str] = Query(None, description="Search in username or attribute"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of RadReply attributes with filtering and pagination
    """
    repo = RadreplyRepository(db)
    
    # Build filters
    filters = {}
    if username:
        filters["username"] = username
    if attribute:
        filters["attribute"] = attribute
    
    # Apply search
    search_fields = ["username", "attribute", "value"] if search else None
    
    try:
        items, total = await repo.get_paginated(
            skip=pagination.skip,
            limit=pagination.limit,
            filters=filters,
            search_term=search,
            search_fields=search_fields,
            order_by="username"
        )
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve RadReply attributes: {str(e)}"
        )


@router.get("/radreply/{attribute_id}", response_model=RadreplyResponse)
async def get_radreply_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific RadReply attribute by ID
    """
    repo = RadreplyRepository(db)
    
    attribute = await repo.get(attribute_id)
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadReply attribute not found"
        )
    
    return attribute


@router.post("/radreply", response_model=RadreplyResponse)
async def create_radreply_attribute(
    attribute_data: RadreplyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new RadReply attribute
    """
    repo = RadreplyRepository(db)
    
    try:
        attribute = await repo.create(attribute_data)
        return attribute
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create RadReply attribute: {str(e)}"
        )


@router.put("/radreply/{attribute_id}", response_model=RadreplyResponse)
async def update_radreply_attribute(
    attribute_id: int,
    attribute_data: RadreplyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing RadReply attribute
    """
    repo = RadreplyRepository(db)
    
    existing = await repo.get(attribute_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadReply attribute not found"
        )
    
    try:
        attribute = await repo.update(existing, attribute_data)
        return attribute
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update RadReply attribute: {str(e)}"
        )


@router.delete("/radreply/{attribute_id}")
async def delete_radreply_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a RadReply attribute
    """
    repo = RadreplyRepository(db)
    
    existing = await repo.get(attribute_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadReply attribute not found"
        )
    
    try:
        await repo.delete(existing)
        return {"message": "RadReply attribute deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete RadReply attribute: {str(e)}"
        )


# ===== User-Specific Attribute Routes =====

@router.get("/users/{username}/attributes")
async def get_user_attributes(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all attributes (RadCheck + RadReply) for a specific user
    """
    radcheck_repo = RadcheckRepository(db)
    radreply_repo = RadreplyRepository(db)
    
    try:
        check_attributes = await radcheck_repo.get_user_attributes(username)
        reply_attributes = await radreply_repo.get_user_attributes(username)
        
        return {
            "username": username,
            "check_attributes": check_attributes,
            "reply_attributes": reply_attributes,
            "total_attributes": len(check_attributes) + len(reply_attributes)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user attributes: {str(e)}"
        )


@router.post("/users/{username}/password")
async def set_user_password(
    username: str,
    password_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Set or update user password in RadCheck
    """
    repo = RadcheckRepository(db)
    
    password = password_data.get("password")
    password_type = password_data.get("password_type", "Cleartext-Password")
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    try:
        attribute = await repo.set_user_password(username, password, password_type)
        return {
            "message": "Password updated successfully",
            "attribute": attribute
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set user password: {str(e)}"
        )


# ===== Utility Routes =====

@router.get("/attributes/operators", response_model=List[str])
async def get_radius_operators():
    """
    Get list of available RADIUS operators
    """
    return [op.value for op in RadiusOperator]


@router.get("/attributes/common-check")
async def get_common_check_attributes():
    """
    Get list of common RadCheck attribute names
    """
    return {
        "password_attributes": [
            "User-Password",
            "Cleartext-Password", 
            "Crypt-Password",
            "MD5-Password",
            "SHA-Password",
            "NT-Password",
            "LM-Password"
        ],
        "access_control": [
            "Auth-Type",
            "Simultaneous-Use",
            "Max-Daily-Session",
            "Max-Monthly-Session",
            "Expiration",
            "Access-Period",
            "Login-Time"
        ]
    }


@router.get("/attributes/common-reply")
async def get_common_reply_attributes():
    """
    Get list of common RadReply attribute names
    """
    return {
        "networking": [
            "Framed-IP-Address",
            "Framed-IP-Netmask", 
            "Framed-Protocol",
            "Framed-Route"
        ],
        "service_control": [
            "Service-Type",
            "Session-Timeout",
            "Idle-Timeout",
            "Acct-Interim-Interval",
            "Port-Limit"
        ],
        "other": [
            "Filter-Id",
            "Reply-Message",
            "Callback-Number"
        ]
    }


# ===== RADIUS Group Management Routes =====

@router.get("/radgroupcheck", response_model=PaginatedResponse[RadgroupcheckResponse])
async def list_group_check_attributes(
    groupname: Optional[str] = Query(None, description="Filter by group name"),
    attribute: Optional[str] = Query(None, description="Filter by attribute name"),
    search: Optional[str] = Query(None, description="Search in groupname or attribute"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of RadGroupCheck attributes with filtering and pagination
    """
    from ...repositories.radius import GroupCheckRepository
    
    repo = GroupCheckRepository(db)
    
    # Build filters
    filters = {}
    if groupname:
        filters["groupname"] = groupname
    if attribute:
        filters["attribute"] = attribute
    
    # Apply search
    search_fields = ["groupname", "attribute", "value"] if search else None
    
    # Get paginated results
    result = await repo.get_multi_paginated(
        filters=filters,
        search=search,
        search_fields=search_fields,
        page=pagination.page,
        size=pagination.size,
        order_by="groupname"
    )
    
    return result


@router.post("/radgroupcheck", response_model=RadgroupcheckResponse)
async def create_group_check_attribute(
    attribute_data: RadgroupcheckCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new RadGroupCheck attribute
    """
    from ...repositories.radius import GroupCheckRepository
    
    repo = GroupCheckRepository(db)
    
    try:
        attribute = await repo.create(attribute_data)
        return attribute
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group check attribute with this combination already exists"
        )


@router.get("/radgroupcheck/{attribute_id}", response_model=RadgroupcheckResponse)
async def get_group_check_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific RadGroupCheck attribute by ID
    """
    from ...repositories.radius import GroupCheckRepository
    
    repo = GroupCheckRepository(db)
    attribute = await repo.get(attribute_id)
    
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group check attribute not found"
        )
    
    return attribute


@router.put("/radgroupcheck/{attribute_id}", response_model=RadgroupcheckResponse)
async def update_group_check_attribute(
    attribute_id: int,
    attribute_data: RadgroupcheckCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a RadGroupCheck attribute
    """
    from ...repositories.radius import GroupCheckRepository
    
    repo = GroupCheckRepository(db)
    
    # Check if attribute exists
    existing_attribute = await repo.get(attribute_id)
    if not existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group check attribute not found"
        )
    
    # Update the attribute
    updated_attribute = await repo.update(attribute_id, attribute_data)
    return updated_attribute


@router.delete("/radgroupcheck/{attribute_id}")
async def delete_group_check_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a RadGroupCheck attribute
    """
    from ...repositories.radius import GroupCheckRepository
    
    repo = GroupCheckRepository(db)
    
    # Check if attribute exists
    existing_attribute = await repo.get(attribute_id)
    if not existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group check attribute not found"
        )
    
    await repo.delete(attribute_id)
    return {"message": "Group check attribute deleted successfully"}


@router.get("/radgroupreply", response_model=PaginatedResponse[RadgroupreplyResponse])
async def list_group_reply_attributes(
    groupname: Optional[str] = Query(None, description="Filter by group name"),
    attribute: Optional[str] = Query(None, description="Filter by attribute name"),
    search: Optional[str] = Query(None, description="Search in groupname or attribute"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of RadGroupReply attributes with filtering and pagination
    """
    from ...repositories.radius import GroupReplyRepository
    
    repo = GroupReplyRepository(db)
    
    # Build filters
    filters = {}
    if groupname:
        filters["groupname"] = groupname
    if attribute:
        filters["attribute"] = attribute
    
    # Apply search
    search_fields = ["groupname", "attribute", "value"] if search else None
    
    # Get paginated results
    result = await repo.get_multi_paginated(
        filters=filters,
        search=search,
        search_fields=search_fields,
        page=pagination.page,
        size=pagination.size,
        order_by="groupname"
    )
    
    return result


@router.post("/radgroupreply", response_model=RadgroupreplyResponse)
async def create_group_reply_attribute(
    attribute_data: RadgroupreplyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new RadGroupReply attribute
    """
    from ...repositories.radius import GroupReplyRepository
    
    repo = GroupReplyRepository(db)
    
    try:
        attribute = await repo.create(attribute_data)
        return attribute
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group reply attribute with this combination already exists"
        )


@router.get("/radgroupreply/{attribute_id}", response_model=RadgroupreplyResponse)
async def get_group_reply_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific RadGroupReply attribute by ID
    """
    from ...repositories.radius import GroupReplyRepository
    
    repo = GroupReplyRepository(db)
    attribute = await repo.get(attribute_id)
    
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group reply attribute not found"
        )
    
    return attribute


@router.put("/radgroupreply/{attribute_id}", response_model=RadgroupreplyResponse)
async def update_group_reply_attribute(
    attribute_id: int,
    attribute_data: RadgroupreplyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a RadGroupReply attribute
    """
    from ...repositories.radius import GroupReplyRepository
    
    repo = GroupReplyRepository(db)
    
    # Check if attribute exists
    existing_attribute = await repo.get(attribute_id)
    if not existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group reply attribute not found"
        )
    
    # Update the attribute
    updated_attribute = await repo.update(attribute_id, attribute_data)
    return updated_attribute


@router.delete("/radgroupreply/{attribute_id}")
async def delete_group_reply_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a RadGroupReply attribute
    """
    from ...repositories.radius import GroupReplyRepository
    
    repo = GroupReplyRepository(db)
    
    # Check if attribute exists
    existing_attribute = await repo.get(attribute_id)
    if not existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group reply attribute not found"
        )
    
    await repo.delete(attribute_id)
    return {"message": "Group reply attribute deleted successfully"}


# ===== Group Management Utility Routes =====

@router.get("/groups", response_model=GroupListResponse)
async def list_groups(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all RADIUS groups (from both check and reply tables)
    """
    from ...repositories.radius import GroupCheckRepository, GroupReplyRepository
    
    check_repo = GroupCheckRepository(db)
    reply_repo = GroupReplyRepository(db)
    
    # Get groups from both tables
    check_groups = await check_repo.get_groups_list()
    reply_groups = await reply_repo.get_groups_list()
    
    # Combine and deduplicate
    all_groups = sorted(list(set(check_groups + reply_groups)))
    
    return GroupListResponse(
        groups=all_groups,
        total=len(all_groups)
    )


@router.get("/groups/{groupname}/attributes", response_model=GroupAttributesResponse)
async def get_group_attributes(
    groupname: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all attributes (check and reply) for a specific group
    """
    from ...repositories.radius import GroupCheckRepository, GroupReplyRepository
    
    check_repo = GroupCheckRepository(db)
    reply_repo = GroupReplyRepository(db)
    
    # Get attributes from both tables
    check_attributes = await check_repo.get_group_attributes(groupname)
    reply_attributes = await reply_repo.get_group_attributes(groupname)
    
    return GroupAttributesResponse(
        groupname=groupname,
        check_attributes=check_attributes,
        reply_attributes=reply_attributes,
        total_attributes=len(check_attributes) + len(reply_attributes)
    )


@router.delete("/groups/{groupname}/attributes")
async def delete_group_all_attributes(
    groupname: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete all attributes (check and reply) for a specific group
    """
    from ...repositories.radius import GroupCheckRepository, GroupReplyRepository
    
    check_repo = GroupCheckRepository(db)
    reply_repo = GroupReplyRepository(db)
    
    # Delete from both tables
    check_count = await check_repo.delete_group_attributes(groupname)
    reply_count = await reply_repo.delete_group_attributes(groupname)
    
    total_deleted = check_count + reply_count
    
    return {
        "message": f"Deleted {total_deleted} attributes for group '{groupname}'",
        "check_attributes_deleted": check_count,
        "reply_attributes_deleted": reply_count
    }


@router.get("/groups/statistics", response_model=GroupStatisticsResponse)
async def get_group_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about RADIUS groups
    """
    from ...repositories.radius import GroupCheckRepository, GroupReplyRepository
    
    check_repo = GroupCheckRepository(db)
    reply_repo = GroupReplyRepository(db)
    
    # Get statistics from both tables
    check_stats = await check_repo.get_group_statistics()
    reply_stats = await reply_repo.get_group_statistics()
    
    # Get unique groups
    check_groups = await check_repo.get_groups_list()
    reply_groups = await reply_repo.get_groups_list()
    unique_groups = set(check_groups + reply_groups)
    
    return GroupStatisticsResponse(
        total_groups=len(unique_groups),
        total_check_attributes=check_stats['total_attributes'],
        total_reply_attributes=reply_stats['total_attributes'],
        groups_with_attributes=len(unique_groups)
    )