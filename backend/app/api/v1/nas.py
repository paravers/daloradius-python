"""
NAS API Routes

Complete NAS (Network Access Server) management endpoints with full CRUD operations,
monitoring, and connectivity testing.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging

from app.db.session import get_db
from app.repositories.radius import NasRepository
from app.schemas.radius import (
    NasResponse, NasCreate, NasUpdate, 
    NasListResponse, NasMonitoringResponse
)
from app.services.nas import NasService
from app.core.pagination import PaginationParams
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# NAS CRUD endpoints
@router.get("/", response_model=NasListResponse)
async def get_nas_devices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for nasname, shortname, description"),
    nas_type: Optional[str] = Query(None, description="Filter by NAS type"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    sort_by: Optional[str] = Query("shortname", description="Sort field"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of NAS devices with optional filtering and search"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        # Build filters
        filters = {}
        if nas_type:
            filters['type'] = nas_type
        if status:
            filters['is_active'] = status == 'active'
            
        nas_devices, total = await nas_service.get_nas_paginated(
            skip=skip,
            limit=limit, 
            search=search,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return NasListResponse(
            devices=nas_devices,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            pages=(total + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching NAS devices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NAS devices"
        )

@router.get("/{nas_id}", response_model=NasResponse)
async def get_nas_device(
    nas_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get NAS device by ID"""
    try:
        nas_repo = NasRepository(db)
        nas_device = await nas_repo.get_by_id(nas_id)
        
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
            
        return nas_device
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching NAS device {nas_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NAS device"
        )

@router.post("/", response_model=NasResponse, status_code=status.HTTP_201_CREATED)
async def create_nas_device(
    nas_data: NasCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new NAS device"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        # Check if NAS name already exists
        existing_nas = await nas_repo.get_by_name(nas_data.nasname)
        if existing_nas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NAS name already exists"
            )
            
        # Check if short name already exists
        if nas_data.shortname:
            existing_nas = await nas_repo.get_by_shortname(nas_data.shortname)
            if existing_nas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Short name already exists"
                )
        
        nas_device = await nas_service.create_nas(nas_data, created_by=current_user.username)
        return nas_device
        
    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NAS with this name already exists"
        )
    except Exception as e:
        logger.error(f"Error creating NAS device: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create NAS device"
        )

@router.put("/{nas_id}", response_model=NasResponse)
async def update_nas_device(
    nas_id: int,
    nas_data: NasUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update NAS device by ID"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        nas_device = await nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
            
        # Check short name uniqueness if being updated
        if nas_data.shortname and nas_data.shortname != nas_device.shortname:
            existing_nas = await nas_repo.get_by_shortname(nas_data.shortname)
            if existing_nas and existing_nas.id != nas_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Short name already exists"
                )
        
        updated_nas = await nas_service.update_nas(
            nas_id, nas_data, updated_by=current_user.username
        )
        return updated_nas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating NAS device {nas_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update NAS device"
        )

@router.delete("/{nas_id}")
async def delete_nas_device(
    nas_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete NAS device by ID"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        nas_device = await nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
        
        # Check if NAS has active sessions before deletion
        has_active_sessions = await nas_service.has_active_sessions(nas_id)
        if has_active_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete NAS device with active sessions"
            )
        
        success = await nas_repo.delete(nas_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete NAS device"
            )
            
        return {"message": "NAS device deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting NAS device {nas_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete NAS device"
        )

# NAS monitoring and status endpoints
@router.get("/{nas_id}/status")
async def get_nas_status(
    nas_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time status of NAS device"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        nas_device = await nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
        
        status_info = await nas_service.get_nas_status(nas_id)
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NAS status {nas_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get NAS status"
        )

@router.post("/{nas_id}/test-connection")
async def test_nas_connection(
    nas_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test connectivity to NAS device"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        nas_device = await nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
        
        connection_result = await nas_service.test_nas_connectivity(nas_id)
        return connection_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing NAS connection {nas_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test NAS connection"
        )

@router.get("/{nas_id}/sessions")
async def get_nas_active_sessions(
    nas_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active sessions for a specific NAS device"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        nas_device = await nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NAS device not found"
            )
        
        sessions = await nas_service.get_nas_active_sessions(nas_id, skip, limit)
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching NAS sessions {nas_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NAS sessions"
        )

# Batch operations
@router.delete("/batch")
async def batch_delete_nas(
    nas_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple NAS devices in batch"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        result = await nas_service.batch_delete_nas(nas_ids)
        return result
        
    except Exception as e:
        logger.error(f"Error in batch NAS deletion: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete NAS devices in batch"
        )

# Search and utility endpoints
@router.get("/search/{query}")
async def search_nas_devices(
    query: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search NAS devices by name, shortname, or description"""
    try:
        nas_repo = NasRepository(db)
        
        nas_devices = await nas_repo.search_nas(query, limit=limit)
        return nas_devices
        
    except Exception as e:
        logger.error(f"Error searching NAS devices with query '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search NAS devices"
        )

@router.get("/types/available")
async def get_available_nas_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available NAS types"""
    try:
        nas_types = [
            {"value": "cisco", "label": "Cisco"},
            {"value": "juniper", "label": "Juniper"},
            {"value": "mikrotik", "label": "MikroTik"},
            {"value": "ubiquiti", "label": "Ubiquiti"},
            {"value": "alcatel", "label": "Alcatel"},
            {"value": "other", "label": "Other"}
        ]
        return nas_types
        
    except Exception as e:
        logger.error(f"Error fetching NAS types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NAS types"
        )

# NAS statistics and monitoring
@router.get("/statistics/overview")
async def get_nas_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics for all NAS devices"""
    try:
        nas_repo = NasRepository(db)
        nas_service = NasService(nas_repo)
        
        statistics = await nas_service.get_nas_statistics()
        return statistics
        
    except Exception as e:
        logger.error(f"Error fetching NAS statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NAS statistics"
        )