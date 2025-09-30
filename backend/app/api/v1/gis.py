"""
GIS (Geographic Information System) API

REST API endpoints for GIS operations and geographic data management.
Provides map data, location-based searches, and coordinate management for hotspots.
"""

from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.exceptions import ValidationError, NotFoundError
from app.models.user import User
from app.services.gis import GisService


# Request/Response Models
class CoordinateValidationRequest(BaseModel):
    """Request model for coordinate validation."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class CoordinateValidationResponse(BaseModel):
    """Response model for coordinate validation."""
    valid: bool
    latitude: float
    longitude: float
    errors: Optional[List[str]] = None


class UpdateLocationRequest(BaseModel):
    """Request model for updating hotspot location."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class LocationSearchRequest(BaseModel):
    """Request model for location-based search."""
    latitude: float = Field(..., ge=-90, le=90, description="Search center latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Search center longitude")
    radius_km: float = Field(10.0, gt=0, le=1000, description="Search radius in kilometers")


class BoundingBoxRequest(BaseModel):
    """Request model for bounding box queries."""
    north: float = Field(..., ge=-90, le=90, description="Northern boundary")
    south: float = Field(..., ge=-90, le=90, description="Southern boundary")
    east: float = Field(..., ge=-180, le=180, description="Eastern boundary")
    west: float = Field(..., ge=-180, le=180, description="Western boundary")


class MapDataResponse(BaseModel):
    """Response model for map data."""
    markers: List[Dict[str, Any]]
    bounds: Optional[Dict[str, float]]
    center: Optional[Dict[str, float]]
    statistics: Dict[str, Any]
    filter_bounds: Optional[Dict[str, float]]


class HotspotLocationResponse(BaseModel):
    """Response model for hotspot with location data."""
    id: int
    name: str
    mac_address: Optional[str]
    status: Optional[str]
    comment: Optional[str]
    geocode: Optional[str]
    coordinates: Optional[Dict[str, float]]
    distance_km: Optional[float] = None
    creationdate: Optional[str]
    updatedate: Optional[str]
    creationby: Optional[str]
    updateby: Optional[str]


class HotspotListWithPaginationResponse(BaseModel):
    """Response model for paginated hotspot lists."""
    hotspots: List[HotspotLocationResponse]
    pagination: Dict[str, Any]


class RegionalStatisticsResponse(BaseModel):
    """Response model for regional statistics."""
    total_hotspots: int
    active_hotspots: int
    inactive_hotspots: int
    activity_rate: float
    region_bounds: Dict[str, float]


router = APIRouter(prefix="/gis", tags=["gis"])


@router.get("/map-data", response_model=MapDataResponse)
async def get_map_data(
    north: Optional[float] = Query(None, ge=-90, le=90, description="Northern boundary for filtering"),
    south: Optional[float] = Query(None, ge=-90, le=90, description="Southern boundary for filtering"),
    east: Optional[float] = Query(None, ge=-180, le=180, description="Eastern boundary for filtering"),
    west: Optional[float] = Query(None, ge=-180, le=180, description="Western boundary for filtering"),
    include_inactive: bool = Query(True, description="Include inactive hotspots"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive map data for GIS visualization.
    
    - **bounds**: Optional geographic bounds to filter hotspots (north, south, east, west)
    - **include_inactive**: Whether to include inactive hotspots in results
    
    Returns map markers, geographic bounds, center point, and statistics.
    """
    try:
        service = GisService(db)
        
        # Build bounds filter if provided
        bounds = None
        if all(coord is not None for coord in [north, south, east, west]):
            if south >= north or west >= east:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid bounding box: south must be < north, west must be < east"
                )
            bounds = {'north': north, 'south': south, 'east': east, 'west': west}
        
        map_data = service.get_map_data(bounds=bounds, include_inactive=include_inactive)
        
        return MapDataResponse(**map_data)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get map data: {str(e)}"
        )


@router.post("/search/near-location", response_model=List[HotspotLocationResponse])
async def search_hotspots_near_location(
    search_request: LocationSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for hotspots near a specific location.
    
    - **latitude**: Search center latitude coordinate
    - **longitude**: Search center longitude coordinate
    - **radius_km**: Search radius in kilometers (max 1000)
    
    Returns list of hotspots with distance information, sorted by distance.
    """
    try:
        service = GisService(db)
        
        results = service.search_hotspots_near_location(
            search_request.latitude,
            search_request.longitude,
            search_request.radius_km
        )
        
        return [HotspotLocationResponse(**result) for result in results]
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search hotspots: {str(e)}"
        )


@router.put("/hotspots/{hotspot_id}/location", response_model=HotspotLocationResponse)
async def update_hotspot_location(
    hotspot_id: int = Path(..., description="Hotspot ID"),
    location_request: UpdateLocationRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the geographic location of a hotspot.
    
    - **hotspot_id**: ID of the hotspot to update
    - **latitude**: New latitude coordinate
    - **longitude**: New longitude coordinate
    
    Updates the hotspot's geocode field with new coordinates.
    """
    try:
        service = GisService(db)
        
        result = service.update_hotspot_location(
            hotspot_id,
            location_request.latitude,
            location_request.longitude,
            current_user.username
        )
        
        return HotspotLocationResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update hotspot location: {str(e)}"
        )


@router.delete("/hotspots/{hotspot_id}/location", response_model=HotspotLocationResponse)
async def remove_hotspot_location(
    hotspot_id: int = Path(..., description="Hotspot ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove geographic coordinates from a hotspot.
    
    - **hotspot_id**: ID of the hotspot to update
    
    Clears the hotspot's geocode field, removing location data.
    """
    try:
        service = GisService(db)
        
        result = service.remove_hotspot_location(hotspot_id, current_user.username)
        
        return HotspotLocationResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove hotspot location: {str(e)}"
        )


@router.get("/hotspots/without-location", response_model=HotspotListWithPaginationResponse)
async def get_hotspots_without_location(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get hotspots that don't have geographic coordinates.
    
    - **page**: Page number (starting from 1)
    - **page_size**: Number of items per page (1-100)
    
    Returns paginated list of hotspots without location data.
    """
    try:
        service = GisService(db)
        
        result = service.get_hotspots_without_location(page, page_size)
        
        return HotspotListWithPaginationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hotspots without location: {str(e)}"
        )


@router.post("/statistics/regional", response_model=RegionalStatisticsResponse)
async def get_regional_statistics(
    bounds_request: BoundingBoxRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for hotspots in a specific geographic region.
    
    - **north, south, east, west**: Bounding box coordinates
    
    Returns comprehensive statistics for the specified region.
    """
    try:
        service = GisService(db)
        
        result = service.get_regional_statistics(
            bounds_request.north,
            bounds_request.south,
            bounds_request.east,
            bounds_request.west
        )
        
        return RegionalStatisticsResponse(**result)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get regional statistics: {str(e)}"
        )


@router.get("/search/by-name", response_model=List[HotspotLocationResponse])
async def search_hotspots_by_name(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    coordinates_only: bool = Query(False, description="Only return hotspots with coordinates"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search hotspots by location-related name or description.
    
    - **q**: Search query string (minimum 2 characters)
    - **coordinates_only**: Only return hotspots that have geographic coordinates
    
    Searches hotspot names and descriptions for location-related terms.
    """
    try:
        service = GisService(db)
        
        results = service.search_hotspots_by_name(q, coordinates_only)
        
        return [HotspotLocationResponse(**result) for result in results]
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search hotspots by name: {str(e)}"
        )


@router.post("/validate-coordinates", response_model=CoordinateValidationResponse)
async def validate_coordinates(
    coordinates: CoordinateValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate geographic coordinates.
    
    - **latitude**: Latitude coordinate to validate
    - **longitude**: Longitude coordinate to validate
    
    Returns validation result with details about any errors.
    """
    try:
        from app.services.gis import GisService
        
        # Create a temporary service instance for validation (no DB needed)
        temp_service = type('TempService', (), {
            '_validate_coordinates': lambda self, lat, lon: -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
        })()
        
        is_valid = temp_service._validate_coordinates(coordinates.latitude, coordinates.longitude)
        
        result = {
            'valid': is_valid,
            'latitude': coordinates.latitude,
            'longitude': coordinates.longitude
        }
        
        if not is_valid:
            errors = []
            if not (-90.0 <= coordinates.latitude <= 90.0):
                errors.append("Latitude must be between -90 and 90 degrees")
            if not (-180.0 <= coordinates.longitude <= 180.0):
                errors.append("Longitude must be between -180 and 180 degrees")
            result['errors'] = errors
        
        return CoordinateValidationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate coordinates: {str(e)}"
        )