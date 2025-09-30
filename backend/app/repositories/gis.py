"""
GIS Repository

This module provides data access layer functionality for GIS (Geographic Information System) operations.
Handles geographic queries, hotspot location management, and spatial data operations.
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, desc, asc, text
from decimal import Decimal
import json

from app.models.hotspot import Hotspot
from .base import BaseRepository


class GisRepository(BaseRepository[Hotspot]):
    """
    Repository class for GIS and geographic data access operations.
    
    Provides specialized geographic queries for hotspot management,
    including location-based search, coordinate validation, and spatial operations.
    """
    
    def __init__(self, db_session: Session):
        """Initialize GIS repository with database session."""
        super().__init__(db_session, Hotspot)
    
    def get_hotspots_with_coordinates(self, 
                                     limit: Optional[int] = None, 
                                     offset: Optional[int] = 0) -> List[Hotspot]:
        """
        Get hotspots that have geographic coordinates.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of Hotspot instances with valid coordinates
        """
        query = self.db_session.query(Hotspot).filter(
            and_(
                Hotspot.geocode.isnot(None),
                Hotspot.geocode != "",
                Hotspot.geocode != "0,0"
            )
        ).order_by(Hotspot.name)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_hotspots_by_coordinates(self, 
                                   latitude: float, 
                                   longitude: float, 
                                   radius_km: float = 10.0) -> List[Hotspot]:
        """
        Get hotspots within a specified radius of given coordinates.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of Hotspot instances within the radius
        """
        # Convert radius from km to degrees (approximate: 1 degree ≈ 111 km)
        radius_deg = radius_km / 111.0
        
        # Simple bounding box query (more sophisticated spatial queries would need PostGIS)
        lat_min = latitude - radius_deg
        lat_max = latitude + radius_deg
        lon_min = longitude - radius_deg
        lon_max = longitude + radius_deg
        
        hotspots = []
        all_hotspots = self.get_hotspots_with_coordinates()
        
        for hotspot in all_hotspots:
            coords = self._parse_geocode(hotspot.geocode)
            if coords:
                hs_lat, hs_lon = coords
                if (lat_min <= hs_lat <= lat_max and 
                    lon_min <= hs_lon <= lon_max):
                    # Calculate actual distance
                    distance = self._calculate_distance(latitude, longitude, hs_lat, hs_lon)
                    if distance <= radius_km:
                        hotspots.append(hotspot)
        
        return hotspots
    
    def get_hotspots_by_bounding_box(self, 
                                    north: float, 
                                    south: float, 
                                    east: float, 
                                    west: float) -> List[Hotspot]:
        """
        Get hotspots within a geographic bounding box.
        
        Args:
            north: Northern boundary latitude
            south: Southern boundary latitude
            east: Eastern boundary longitude
            west: Western boundary longitude
            
        Returns:
            List of Hotspot instances within the bounding box
        """
        hotspots = []
        all_hotspots = self.get_hotspots_with_coordinates()
        
        for hotspot in all_hotspots:
            coords = self._parse_geocode(hotspot.geocode)
            if coords:
                lat, lon = coords
                if (south <= lat <= north and 
                    west <= lon <= east):
                    hotspots.append(hotspot)
        
        return hotspots
    
    def update_hotspot_coordinates(self, 
                                  hotspot_id: int, 
                                  latitude: float, 
                                  longitude: float,
                                  updated_by: str = None) -> Optional[Hotspot]:
        """
        Update geographic coordinates for a hotspot.
        
        Args:
            hotspot_id: ID of the hotspot to update
            latitude: New latitude coordinate
            longitude: New longitude coordinate
            updated_by: Username of the operator updating coordinates
            
        Returns:
            Updated Hotspot instance or None if not found
            
        Raises:
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not self._validate_coordinates(latitude, longitude):
            raise ValueError("Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180")
        
        hotspot = self.get_by_id(hotspot_id)
        if not hotspot:
            return None
        
        # Format geocode as "latitude,longitude"
        geocode = f"{latitude},{longitude}"
        hotspot.geocode = geocode
        
        if updated_by:
            hotspot.updateby = updated_by
        
        self.db_session.commit()
        self.db_session.refresh(hotspot)
        
        return hotspot
    
    def remove_hotspot_coordinates(self, 
                                  hotspot_id: int,
                                  updated_by: str = None) -> Optional[Hotspot]:
        """
        Remove geographic coordinates from a hotspot.
        
        Args:
            hotspot_id: ID of the hotspot to update
            updated_by: Username of the operator removing coordinates
            
        Returns:
            Updated Hotspot instance or None if not found
        """
        hotspot = self.get_by_id(hotspot_id)
        if not hotspot:
            return None
        
        hotspot.geocode = None
        
        if updated_by:
            hotspot.updateby = updated_by
        
        self.db_session.commit()
        self.db_session.refresh(hotspot)
        
        return hotspot
    
    def get_hotspots_without_coordinates(self, 
                                        limit: Optional[int] = None, 
                                        offset: Optional[int] = 0) -> List[Hotspot]:
        """
        Get hotspots that don't have geographic coordinates.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of Hotspot instances without coordinates
        """
        query = self.db_session.query(Hotspot).filter(
            or_(
                Hotspot.geocode.is_(None),
                Hotspot.geocode == "",
                Hotspot.geocode == "0,0"
            )
        ).order_by(Hotspot.name)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_geographic_bounds(self) -> Optional[Dict[str, float]]:
        """
        Get the geographic bounds (bounding box) of all hotspots with coordinates.
        
        Returns:
            Dictionary with 'north', 'south', 'east', 'west' bounds or None if no coordinates
        """
        hotspots = self.get_hotspots_with_coordinates()
        
        if not hotspots:
            return None
        
        latitudes = []
        longitudes = []
        
        for hotspot in hotspots:
            coords = self._parse_geocode(hotspot.geocode)
            if coords:
                lat, lon = coords
                latitudes.append(lat)
                longitudes.append(lon)
        
        if not latitudes:
            return None
        
        return {
            'north': max(latitudes),
            'south': min(latitudes),
            'east': max(longitudes),
            'west': min(longitudes)
        }
    
    def get_geographic_center(self) -> Optional[Tuple[float, float]]:
        """
        Get the geographic center point of all hotspots with coordinates.
        
        Returns:
            Tuple of (latitude, longitude) or None if no coordinates
        """
        bounds = self.get_geographic_bounds()
        
        if not bounds:
            return None
        
        center_lat = (bounds['north'] + bounds['south']) / 2
        center_lon = (bounds['east'] + bounds['west']) / 2
        
        return (center_lat, center_lon)
    
    def get_hotspot_statistics_by_region(self, 
                                        region_bounds: Dict[str, float]) -> Dict[str, Any]:
        """
        Get hotspot statistics for a specific geographic region.
        
        Args:
            region_bounds: Dictionary with 'north', 'south', 'east', 'west' bounds
            
        Returns:
            Dictionary with regional statistics
        """
        regional_hotspots = self.get_hotspots_by_bounding_box(
            region_bounds['north'],
            region_bounds['south'], 
            region_bounds['east'],
            region_bounds['west']
        )
        
        total_hotspots = len(regional_hotspots)
        active_hotspots = len([hs for hs in regional_hotspots if hs.status == 'active'])
        inactive_hotspots = total_hotspots - active_hotspots
        
        return {
            'total_hotspots': total_hotspots,
            'active_hotspots': active_hotspots,
            'inactive_hotspots': inactive_hotspots,
            'activity_rate': (active_hotspots / total_hotspots * 100) if total_hotspots > 0 else 0,
            'region_bounds': region_bounds
        }
    
    def search_hotspots_by_location_name(self, 
                                        location_query: str,
                                        limit: Optional[int] = None) -> List[Hotspot]:
        """
        Search hotspots by location-related fields (name, description, address).
        
        Args:
            location_query: Search query for location-related fields
            limit: Maximum number of records to return
            
        Returns:
            List of matching Hotspot instances
        """
        search_term = f"%{location_query}%"
        
        query = self.db_session.query(Hotspot).filter(
            or_(
                Hotspot.name.ilike(search_term),
                Hotspot.comment.ilike(search_term)
            )
        ).order_by(Hotspot.name)
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def _parse_geocode(self, geocode: str) -> Optional[Tuple[float, float]]:
        """
        Parse geocode string into latitude and longitude coordinates.
        
        Args:
            geocode: Geocode string in format "latitude,longitude"
            
        Returns:
            Tuple of (latitude, longitude) or None if invalid
        """
        if not geocode or geocode in ("", "0,0"):
            return None
        
        try:
            parts = geocode.split(',')
            if len(parts) != 2:
                return None
            
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())
            
            if self._validate_coordinates(latitude, longitude):
                return (latitude, longitude)
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0)
    
    def _calculate_distance(self, 
                           lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points in kilometers.
        Uses the Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r