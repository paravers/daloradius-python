"""
Users API Routes

Complete user management endpoints with full CRUD operations,
search, pagination, and batch operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging
import io
import pandas as pd

from app.db.session import get_db
from app.repositories.user import UserRepository, UserGroupRepository
from app.schemas.user import (
    UserResponse, UserCreate, UserUpdate, UserListResponse,
    GroupResponse, GroupCreate, GroupUpdate,
    UserGroupResponse, UserGroupCreate,
    BatchUserCreate, BatchOperationResult, UserPasswordUpdate
)
from app.services.user import UserService
from app.core.pagination import PaginationParams, paginate
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# User CRUD endpoints


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of users to return"),
    search: Optional[str] = Query(
        None, description="Search term for username, email, name"),
    status: Optional[str] = Query(None, description="Filter by user status"),
    auth_type: Optional[str] = Query(
        None, description="Filter by authentication type"),
    sort_by: Optional[str] = Query("username", description="Sort field"),
    sort_order: Optional[str] = Query(
        "asc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of users with optional filtering and search"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if auth_type:
            filters['auth_type'] = auth_type

        users, total = await user_service.get_users_paginated(
            skip=skip,
            limit=limit,
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return UserListResponse(
            users=users,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            pages=(total + limit - 1) // limit
        )

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    try:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        # Check if username exists
        existing_user = await user_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email exists
        if user_data.email:
            existing_user = await user_repo.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        user = await user_service.create_user(user_data, created_by=current_user.username)
        return user

    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user by ID"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            existing_user = await user_repo.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        updated_user = await user_service.update_user(
            user_id, user_data, updated_by=current_user.username
        )
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user by ID"""
    try:
        user_repo = UserRepository(db)

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        success = await user_repo.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

# Quick user creation


@router.post("/quick", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_quick(
    username: str,
    password: str,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick user creation with minimal required fields"""
    try:
        user_data = UserCreate(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        # Check if username exists
        existing_user = await user_repo.get_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        user = await user_service.create_user(user_data, created_by=current_user.username)
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating quick user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

# Batch operations


@router.post("/batch", response_model=BatchOperationResult)
async def batch_create_users(
    batch_data: BatchUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple users in batch"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        result = await user_service.create_users_batch(
            batch_data, created_by=current_user.username
        )
        return result

    except Exception as e:
        logger.error(f"Error in batch user creation: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create users in batch"
        )


@router.post("/import", response_model=BatchOperationResult)
async def import_users(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import users from CSV/Excel file"""
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or Excel format"
            )

        content = await file.read()

        # Parse file based on type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        result = await user_service.import_users_from_dataframe(
            df, created_by=current_user.username
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing users: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import users: {str(e)}"
        )


@router.delete("/batch")
async def batch_delete_users(
    user_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple users in batch"""
    try:
        # Prevent self-deletion
        if current_user.id in user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        user_repo = UserRepository(db)

        deleted_count = 0
        for user_id in user_ids:
            success = await user_repo.delete(user_id)
            if success:
                deleted_count += 1

        return {
            "message": f"Successfully deleted {deleted_count} users",
            "deleted_count": deleted_count,
            "total_requested": len(user_ids)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch user deletion: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete users in batch"
        )

# Password management


@router.put("/{user_id}/password")
async def change_user_password(
    user_id: int,
    password_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        # Only allow self password change or admin
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change this user's password"
            )

        await user_service.change_password(
            user_id,
            password_data.current_password,
            password_data.new_password
        )

        return {"message": "Password updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

# Online user monitoring


@router.get("/online/active", response_model=List[dict])
async def get_online_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of currently online users"""
    try:
        user_repo = UserRepository(db)
        user_service = UserService(user_repo)

        online_users = await user_service.get_online_users()
        return online_users

    except Exception as e:
        logger.error(f"Error fetching online users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch online users"
        )

# User search


@router.get("/search/{query}")
async def search_users(
    query: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search users by username, email, or name"""
    try:
        user_repo = UserRepository(db)

        users = await user_repo.search_users(query, limit)
        return users

    except Exception as e:
        logger.error(f"Error searching users with query '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )

# User groups management


@router.get("/{user_id}/groups", response_model=List[UserGroupResponse])
async def get_user_groups(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get groups for a specific user"""
    try:
        user_repo = UserRepository(db)
        group_repo = UserGroupRepository(db)

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        groups = await group_repo.get_user_groups(user.username)
        return groups

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching groups for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user groups"
        )


@router.post("/{user_id}/groups", response_model=UserGroupResponse)
async def add_user_to_group(
    user_id: int,
    group_data: UserGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add user to a group"""
    try:
        user_repo = UserRepository(db)
        group_repo = UserGroupRepository(db)

        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update username in group data to match user
        group_data.username = user.username

        group_association = await group_repo.create(group_data)
        return group_association

    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )
    except Exception as e:
        logger.error(f"Error adding user {user_id} to group: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add user to group"
        )
