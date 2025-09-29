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