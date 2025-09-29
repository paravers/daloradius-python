"""
Hotspot Management API

REST API endpoints for hotspot management operations.
Provides CRUD operations and search functionality for WiFi hotspot management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.models.user import User
from app.services.hotspot import HotspotService
from app.schemas.hotspot import (
    HotspotCreate,
    HotspotUpdate,
    HotspotResponse,
    HotspotListResponse,
    HotspotSearchRequest,
    HotspotValidationRequest,
    HotspotValidationResponse,
    HotspotBulkDeleteRequest,
    HotspotBulkDeleteResponse,
    HotspotStatisticsResponse,
    HotspotOptionsResponse
)

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("/", response_model=HotspotListResponse)
async def get_hotspots(
    query: Optional[str] = Query(None, description="Search query"),
    type: Optional[str] = Query(None, description="Filter by hotspot type"),
    owner: Optional[str] = Query(None, description="Filter by owner"),
    company: Optional[str] = Query(None, description="Filter by company"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    order_by: str = Query("name", description="Order by field"),
    order_type: str = Query("asc", regex="^(asc|desc)$", description="Order direction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of hotspots with optional filtering and pagination.
    
    - **query**: General search term (searches name, mac, owner, company, address, manager)
    - **type**: Filter by hotspot type
    - **owner**: Filter by owner name
    - **company**: Filter by company name
    - **page**: Page number (starting from 1)
    - **per_page**: Number of items per page (1-100)
    - **order_by**: Field to order by (name, mac, owner, company, type, creationdate, updatedate)
    - **order_type**: Order direction (asc or desc)
    """
    try:
        service = HotspotService(db)
        hotspots, total = service.search_hotspots(
            query=query,
            hotspot_type=type,
            owner=owner,
            company=company,
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_type=order_type
        )
        
        # Calculate pagination info
        pages = (total + per_page - 1) // per_page
        
        return HotspotListResponse(
            hotspots=[HotspotResponse.from_orm(hotspot) for hotspot in hotspots],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving hotspots: {str(e)}"
        )


@router.post("/", response_model=HotspotResponse, status_code=status.HTTP_201_CREATED)
async def create_hotspot(
    hotspot_data: HotspotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new hotspot.
    
    - **name**: Hotspot name (required, unique)
    - **mac**: MAC address or IP address (required, unique)
    - **geocode**: Geographic coordinates or location code (optional)
    - **type**: Hotspot type or category (optional)
    - **owner**: Owner name (optional)
    - **email_owner**: Owner email address (optional)
    - **manager**: Manager name (optional)
    - **email_manager**: Manager email address (optional)
    - **address**: Physical address (optional)
    - **phone1**: Primary phone number (optional)
    - **phone2**: Secondary phone number (optional)
    - **company**: Company name (optional)
    - **companywebsite**: Company website URL (optional)
    - **companyemail**: Company email address (optional)
    - **companycontact**: Company contact person (optional)
    - **companyphone**: Company phone number (optional)
    """
    try:
        service = HotspotService(db)
        hotspot = service.create_hotspot(
            hotspot_data.dict(exclude_unset=True),
            created_by=current_user.username
        )
        return HotspotResponse.from_orm(hotspot)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating hotspot: {str(e)}"
        )


@router.get("/{hotspot_id}", response_model=HotspotResponse)
async def get_hotspot(
    hotspot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific hotspot by ID.
    
    - **hotspot_id**: The ID of the hotspot to retrieve
    """
    try:
        service = HotspotService(db)
        hotspot = service.get_hotspot(hotspot_id)
        return HotspotResponse.from_orm(hotspot)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving hotspot: {str(e)}"
        )


@router.put("/{hotspot_id}", response_model=HotspotResponse)
async def update_hotspot(
    hotspot_id: int,
    hotspot_data: HotspotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing hotspot.
    
    - **hotspot_id**: The ID of the hotspot to update
    - All fields are optional for updates
    """
    try:
        service = HotspotService(db)
        hotspot = service.update_hotspot(
            hotspot_id,
            hotspot_data.dict(exclude_unset=True),
            updated_by=current_user.username
        )
        return HotspotResponse.from_orm(hotspot)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating hotspot: {str(e)}"
        )


@router.delete("/{hotspot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotspot(
    hotspot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific hotspot.
    
    - **hotspot_id**: The ID of the hotspot to delete
    """
    try:
        service = HotspotService(db)
        service.delete_hotspot(hotspot_id)
        return None
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting hotspot: {str(e)}"
        )


@router.post("/search", response_model=HotspotListResponse)
async def search_hotspots(
    search_request: HotspotSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced search for hotspots with POST body parameters.
    
    This endpoint accepts the same parameters as GET /hotspots but via POST body,
    useful for complex search queries or when URL length limits are a concern.
    """
    try:
        service = HotspotService(db)
        hotspots, total = service.search_hotspots(
            query=search_request.query,
            hotspot_type=search_request.type,
            owner=search_request.owner,
            company=search_request.company,
            page=search_request.page,
            per_page=search_request.per_page,
            order_by=search_request.order_by,
            order_type=search_request.order_type
        )
        
        # Calculate pagination info
        pages = (total + search_request.per_page - 1) // search_request.per_page
        
        return HotspotListResponse(
            hotspots=[HotspotResponse.from_orm(hotspot) for hotspot in hotspots],
            total=total,
            page=search_request.page,
            per_page=search_request.per_page,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching hotspots: {str(e)}"
        )


@router.post("/validate", response_model=HotspotValidationResponse)
async def validate_hotspot_field(
    validation_request: HotspotValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate hotspot field uniqueness.
    
    - **name**: Name to validate (optional)
    - **mac**: MAC/IP address to validate (optional)
    - **exclude_id**: ID to exclude from validation check (optional, for updates)
    """
    try:
        service = HotspotService(db)
        
        if validation_request.name:
            is_available = service.validate_name_availability(
                validation_request.name,
                validation_request.exclude_id
            )
            return HotspotValidationResponse(
                valid=is_available,
                message=None if is_available else f"Name '{validation_request.name}' is already taken"
            )
        
        if validation_request.mac:
            is_available = service.validate_mac_availability(
                validation_request.mac,
                validation_request.exclude_id
            )
            return HotspotValidationResponse(
                valid=is_available,
                message=None if is_available else f"MAC/IP '{validation_request.mac}' is already taken"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either name or mac must be provided for validation"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating hotspot field: {str(e)}"
        )


@router.delete("/bulk", response_model=HotspotBulkDeleteResponse)
async def bulk_delete_hotspots(
    delete_request: HotspotBulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple hotspots in bulk.
    
    - **hotspot_ids**: List of hotspot IDs to delete
    """
    try:
        service = HotspotService(db)
        deleted_count = service.bulk_delete_hotspots(delete_request.hotspot_ids)
        
        return HotspotBulkDeleteResponse(
            deleted_count=deleted_count,
            message=f"Successfully deleted {deleted_count} hotspot(s)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting hotspots: {str(e)}"
        )


@router.get("/stats/summary", response_model=HotspotStatisticsResponse)
async def get_hotspot_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get hotspot management statistics.
    
    Returns summary statistics including total counts, recent activity,
    and distribution by various categories.
    """
    try:
        service = HotspotService(db)
        stats = service.get_statistics()
        
        return HotspotStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/options/all", response_model=HotspotOptionsResponse)
async def get_hotspot_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get options for hotspot dropdowns.
    
    Returns lists of unique values for various hotspot fields,
    useful for populating dropdown menus and filters in the UI.
    """
    try:
        service = HotspotService(db)
        
        return HotspotOptionsResponse(
            types=service.get_hotspot_types(),
            companies=service.get_companies(),
            owners=service.get_owners()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving options: {str(e)}"
        )