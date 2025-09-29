"""
User Group Management API Routes

This module provides RESTful API endpoints for managing user group associations,
including user-group relationships, group statistics, and batch operations.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_db
from ...repositories.user import UserRepository, UserGroupRepository
from ...schemas.user import (
    UserGroupCreate, UserGroupUpdate, UserGroupResponse,
    UserGroupListResponse, UserGroupStatisticsResponse,
    UserGroupDetailResponse, BatchUserGroupOperation, 
    BatchUserGroupResult, GroupWithUserCount,
    UserGroupSearchParams
)
from ...models.user import UserGroup
from ...core.pagination import PaginationParams, PaginatedResponse
from ...core.auth import get_current_user
from ...models.user import User


router = APIRouter()


# ===== User Group Association Management =====

@router.get("/user-groups", response_model=PaginatedResponse[UserGroupResponse])
async def list_user_groups(
    username: Optional[str] = Query(None, description="Filter by username"),
    groupname: Optional[str] = Query(None, description="Filter by groupname"),
    search: Optional[str] = Query(None, description="Search in username or groupname"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of user group associations with filtering
    """
    repo = UserGroupRepository(db)
    
    # Build filters
    filters = {}
    if username:
        filters["username"] = username
    if groupname:
        filters["groupname"] = groupname
    
    # Apply search
    search_fields = ["username", "groupname"] if search else None
    
    # Get paginated results
    result = await repo.get_multi_paginated(
        filters=filters,
        search=search,
        search_fields=search_fields,
        page=pagination.page,
        size=pagination.size,
        order_by="username"
    )
    
    return result


@router.post("/user-groups", response_model=UserGroupResponse)
async def create_user_group_association(
    association_data: UserGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user-group association
    """
    repo = UserGroupRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = await user_repo.get_by_username(association_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{association_data.username}' not found"
        )
    
    try:
        association = await repo.create(association_data)
        return association
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{association_data.username}' is already in group '{association_data.groupname}'"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user-group association"
        )


@router.get("/user-groups/{association_id}", response_model=UserGroupResponse)
async def get_user_group_association(
    association_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user-group association by ID
    """
    repo = UserGroupRepository(db)
    association = await repo.get(association_id)
    
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User-group association not found"
        )
    
    return association


@router.put("/user-groups/{association_id}", response_model=UserGroupResponse)
async def update_user_group_association(
    association_id: int,
    association_data: UserGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user-group association (e.g., change priority or group)
    """
    repo = UserGroupRepository(db)
    
    # Check if association exists
    existing_association = await repo.get(association_id)
    if not existing_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User-group association not found"
        )
    
    try:
        updated_association = await repo.update(association_id, association_data)
        return updated_association
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already in the target group"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user-group association"
        )


@router.delete("/user-groups/{association_id}")
async def delete_user_group_association(
    association_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user-group association
    """
    repo = UserGroupRepository(db)
    
    # Check if association exists
    existing_association = await repo.get(association_id)
    if not existing_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User-group association not found"
        )
    
    await repo.delete(association_id)
    return {"message": "User-group association deleted successfully"}


# ===== User-Specific Group Management =====

@router.get("/users/{username}/groups", response_model=List[UserGroupDetailResponse])
async def get_user_groups(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all groups for a specific user with details
    """
    repo = UserGroupRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    groups_with_details = await repo.get_user_groups_with_details(username)
    return [
        UserGroupDetailResponse(**group_detail)
        for group_detail in groups_with_details
    ]


@router.post("/users/{username}/groups", response_model=UserGroupResponse)
async def add_user_to_group(
    username: str,
    group_data: UserGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a user to a group
    """
    repo = UserGroupRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    # Override username in group_data to match URL parameter
    group_data.username = username
    
    try:
        association = await repo.add_user_to_group(
            username, 
            group_data.groupname, 
            group_data.priority
        )
        return association
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{username}' is already in group '{group_data.groupname}'"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add user to group"
        )


@router.delete("/users/{username}/groups/{groupname}")
async def remove_user_from_group(
    username: str,
    groupname: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a user from a group
    """
    repo = UserGroupRepository(db)
    
    success = await repo.remove_user_from_group(username, groupname)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' is not in group '{groupname}'"
        )
    
    return {"message": f"User '{username}' removed from group '{groupname}' successfully"}


# ===== Group-Specific User Management =====

@router.get("/groups", response_model=UserGroupListResponse)
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all groups
    """
    repo = UserGroupRepository(db)
    groups = await repo.get_all_groups()
    
    return UserGroupListResponse(
        groups=groups,
        total=len(groups)
    )


@router.get("/groups/{groupname}/users", response_model=List[UserGroupResponse])
async def get_group_users(
    groupname: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users in a specific group
    """
    repo = UserGroupRepository(db)
    users = await repo.get_group_users(groupname)
    
    return users


@router.get("/groups/statistics", response_model=UserGroupStatisticsResponse)
async def get_user_group_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive user group statistics
    """
    repo = UserGroupRepository(db)
    stats = await repo.get_user_group_statistics()
    
    return UserGroupStatisticsResponse(**stats)


@router.get("/groups/counts", response_model=List[GroupWithUserCount])
async def get_groups_with_user_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all groups with their user counts
    """
    repo = UserGroupRepository(db)
    groups_with_counts = await repo.get_groups_with_user_count()
    
    return [
        GroupWithUserCount(**group_data)
        for group_data in groups_with_counts
    ]


# ===== Batch Operations =====

@router.post("/groups/{groupname}/users/batch-add", response_model=BatchUserGroupResult)
async def batch_add_users_to_group(
    groupname: str,
    operation_data: BatchUserGroupOperation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Batch add multiple users to a group
    """
    repo = UserGroupRepository(db)
    
    # Override groupname to match URL parameter
    operation_data.groupname = groupname
    
    result = await repo.batch_add_users_to_group(
        operation_data.usernames,
        groupname,
        operation_data.priority
    )
    
    return BatchUserGroupResult(**result)


@router.post("/groups/{groupname}/users/batch-remove", response_model=BatchUserGroupResult)
async def batch_remove_users_from_group(
    groupname: str,
    operation_data: BatchUserGroupOperation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Batch remove multiple users from a group
    """
    repo = UserGroupRepository(db)
    
    result = await repo.batch_remove_users_from_group(
        operation_data.usernames,
        groupname
    )
    
    return BatchUserGroupResult(**result)


# ===== Search and Utility Operations =====

@router.get("/user-groups/search", response_model=List[UserGroupResponse])
async def search_user_groups(
    username_pattern: Optional[str] = Query(None, description="Username search pattern"),
    groupname_pattern: Optional[str] = Query(None, description="Group name search pattern"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search user group associations with patterns
    """
    repo = UserGroupRepository(db)
    
    associations = await repo.search_user_groups(
        username_pattern=username_pattern,
        groupname_pattern=groupname_pattern,
        skip=skip,
        limit=limit
    )
    
    return associations


@router.put("/users/{username}/groups/{groupname}/priority")
async def update_user_group_priority(
    username: str,
    groupname: str,
    priority: int = Query(..., ge=0, description="New priority value"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user's priority in a specific group
    """
    repo = UserGroupRepository(db)
    
    updated_association = await repo.update_user_group_priority(
        username, groupname, priority
    )
    
    if not updated_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' is not in group '{groupname}'"
        )
    
    return {
        "message": f"Priority updated for user '{username}' in group '{groupname}'",
        "new_priority": priority
    }