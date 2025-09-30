"""
GIS Service

Business logic layer for GIS (Geographic Information System) operations.
Handles geographic validation, coordinate processing, and map data management.
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from sqlalchemy.orm import Session
import json
import re

from app.models.hotspot import Hotspot
from app.repositories.gis import GisRepository
from app.core.exceptions import ValidationError, NotFoundError
from app.services.geo_location import geo_service


class GisService:
    """
    Service class for GIS operations and geographic business logic.
    
    Provides high-level geographic operations including coordinate validation,
    map data processing, and spatial analysis for hotspot management.
    """
    
    def __init__(self, db_session: Session):
        """Initialize GIS service with database session."""
        self.db_session = db_session
        self.repository = GisRepository(db_session)
    
    def get_map_data(self, 
                     bounds: Optional[Dict[str, float]] = None,
                     include_inactive: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive map data for GIS visualization.
        
        Args:
            bounds: Optional geographic bounds to filter hotspots
            include_inactive: Whether to include inactive hotspots
            
        Returns:
            Dictionary containing map data and metadata
        """
        # Get hotspots with coordinates
        if bounds:
            hotspots = self.repository.get_hotspots_by_bounding_box(
                bounds['north'], bounds['south'], 
                bounds['east'], bounds['west']
            )
        else:
            hotspots = self.repository.get_hotspots_with_coordinates()
        
        # Filter by status if needed
        if not include_inactive:
            hotspots = [hs for hs in hotspots if hs.status == 'active']
        
        # Convert hotspots to map markers
        markers = []
        for hotspot in hotspots:
            marker_data = self._hotspot_to_marker(hotspot)
            if marker_data:
                markers.append(marker_data)
        
        # Get geographic bounds and center
        geographic_bounds = self.repository.get_geographic_bounds()
        geographic_center = self.repository.get_geographic_center()
        
        # Get statistics
        total_hotspots = len(hotspots)
        active_hotspots = len([hs for hs in hotspots if hs.status == 'active'])
        
        return {
            'markers': markers,
            'bounds': geographic_bounds,
            'center': {
                'latitude': geographic_center[0] if geographic_center else 0,
                'longitude': geographic_center[1] if geographic_center else 0
            } if geographic_center else None,
            'statistics': {
                'total_hotspots': total_hotspots,
                'active_hotspots': active_hotspots,
                'inactive_hotspots': total_hotspots - active_hotspots,
                'activity_rate': (active_hotspots / total_hotspots * 100) if total_hotspots > 0 else 0
            },
            'filter_bounds': bounds
        }
    
    def search_hotspots_near_location(self, 
                                     latitude: float, 
                                     longitude: float, 
                                     radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """
        Search for hotspots near a specific location.
        
        Args:
            latitude: Search center latitude
            longitude: Search center longitude
            radius_km: Search radius in kilometers
            
        Returns:
            List of hotspot data with distance information
            
        Raises:
            ValidationError: If coordinates are invalid
        """
        # Validate coordinates
        if not self._validate_coordinates(latitude, longitude):
            raise ValidationError("Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180")
        
        if radius_km <= 0 or radius_km > 1000:
            raise ValidationError("Radius must be between 0 and 1000 kilometers")
        
        # Get hotspots within radius
        hotspots = self.repository.get_hotspots_by_coordinates(latitude, longitude, radius_km)
        
        # Calculate distances and sort by distance
        results = []
        for hotspot in hotspots:
            coords = self._parse_geocode(hotspot.geocode)
            if coords:
                distance = self._calculate_distance(latitude, longitude, coords[0], coords[1])
                hotspot_data = self._hotspot_to_dict(hotspot)
                hotspot_data['distance_km'] = round(distance, 2)
                results.append(hotspot_data)
        
        # Sort by distance
        results.sort(key=lambda x: x['distance_km'])
        
        return results
    
    def update_hotspot_location(self, 
                               hotspot_id: int, 
                               latitude: float, 
                               longitude: float,
                               updated_by: str = None) -> Dict[str, Any]:
        """
        Update the geographic location of a hotspot.
        
        Args:
            hotspot_id: ID of the hotspot to update
            latitude: New latitude coordinate
            longitude: New longitude coordinate
            updated_by: Username of the operator updating location
            
        Returns:
            Updated hotspot data with new coordinates
            
        Raises:
            NotFoundError: If hotspot not found
            ValidationError: If coordinates are invalid
        """
        # Validate coordinates
        if not self._validate_coordinates(latitude, longitude):
            raise ValidationError("Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180")
        
        # Update coordinates
        hotspot = self.repository.update_hotspot_coordinates(hotspot_id, latitude, longitude, updated_by)
        
        if not hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        return self._hotspot_to_dict(hotspot)
    
    def remove_hotspot_location(self, 
                               hotspot_id: int,
                               updated_by: str = None) -> Dict[str, Any]:
        """
        Remove geographic coordinates from a hotspot.
        
        Args:
            hotspot_id: ID of the hotspot to update
            updated_by: Username of the operator removing location
            
        Returns:
            Updated hotspot data without coordinates
            
        Raises:
            NotFoundError: If hotspot not found
        """
        hotspot = self.repository.remove_hotspot_coordinates(hotspot_id, updated_by)
        
        if not hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        return self._hotspot_to_dict(hotspot)
    
    def get_hotspots_without_location(self, 
                                     page: int = 1, 
                                     page_size: int = 50) -> Dict[str, Any]:
        """
        Get hotspots that don't have geographic coordinates.
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
            
        Returns:
            Dictionary with pagination and hotspot data
        """
        offset = (page - 1) * page_size
        
        hotspots = self.repository.get_hotspots_without_coordinates(page_size, offset)
        
        # Convert to dictionary format
        hotspot_data = [self._hotspot_to_dict(hs) for hs in hotspots]
        
        # Get total count for pagination
        total_count = len(self.repository.get_hotspots_without_coordinates())
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            'hotspots': hotspot_data,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    def get_regional_statistics(self, 
                               north: float, 
                               south: float, 
                               east: float, 
                               west: float) -> Dict[str, Any]:
        """
        Get statistics for hotspots in a specific geographic region.
        
        Args:
            north, south, east, west: Bounding box coordinates
            
        Returns:
            Dictionary with regional statistics
            
        Raises:
            ValidationError: If bounding box is invalid
        """
        # Validate bounding box
        if not (south < north and west < east):
            raise ValidationError("Invalid bounding box: south must be < north, west must be < east")
        
        if not (self._validate_coordinates(north, east) and self._validate_coordinates(south, west)):
            raise ValidationError("Invalid coordinates in bounding box")
        
        region_bounds = {
            'north': north,
            'south': south,
            'east': east,
            'west': west
        }
        
        return self.repository.get_hotspot_statistics_by_region(region_bounds)
    
    def search_hotspots_by_name(self, 
                               location_query: str,
                               include_coordinates_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search hotspots by location-related name or description.
        
        Args:
            location_query: Search query string
            include_coordinates_only: Only return hotspots with coordinates
            
        Returns:
            List of matching hotspot data
        """
        if not location_query or len(location_query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters long")
        
        hotspots = self.repository.search_hotspots_by_location_name(location_query.strip())
        
        # Filter to only include hotspots with coordinates if requested
        if include_coordinates_only:
            hotspots = [hs for hs in hotspots if hs.geocode and self._parse_geocode(hs.geocode)]
        
        return [self._hotspot_to_dict(hs) for hs in hotspots]
    
    def validate_coordinates(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Validate geographic coordinates and return validation result.
        
        Args:
            latitude: Latitude coordinate to validate
            longitude: Longitude coordinate to validate
            
        Returns:
            Dictionary with validation result and details
        """
        is_valid = self._validate_coordinates(latitude, longitude)
        
        result = {
            'valid': is_valid,
            'latitude': latitude,
            'longitude': longitude
        }
        
        if not is_valid:
            errors = []
            if not (-90.0 <= latitude <= 90.0):
                errors.append("Latitude must be between -90 and 90 degrees")
            if not (-180.0 <= longitude <= 180.0):
                errors.append("Longitude must be between -180 and 180 degrees")
            result['errors'] = errors
        
        return result
    
    def _hotspot_to_marker(self, hotspot: Hotspot) -> Optional[Dict[str, Any]]:
        """
        Convert hotspot to map marker data.
        
        Args:
            hotspot: Hotspot instance
            
        Returns:
            Dictionary with marker data or None if no coordinates
        """
        coords = self._parse_geocode(hotspot.geocode)
        if not coords:
            return None
        
        return {
            'id': hotspot.id,
            'name': hotspot.name,
            'latitude': coords[0],
            'longitude': coords[1],
            'status': hotspot.status or 'unknown',
            'comment': hotspot.comment,
            'creationdate': hotspot.creationdate.isoformat() if hotspot.creationdate else None,
            'creationby': hotspot.creationby
        }
    
    def _hotspot_to_dict(self, hotspot: Hotspot) -> Dict[str, Any]:
        """
        Convert hotspot to dictionary format.
        
        Args:
            hotspot: Hotspot instance
            
        Returns:
            Dictionary with hotspot data
        """
        coords = self._parse_geocode(hotspot.geocode)
        
        return {
            'id': hotspot.id,
            'name': hotspot.name,
            'mac_address': hotspot.mac_address,
            'status': hotspot.status,
            'comment': hotspot.comment,
            'geocode': hotspot.geocode,
            'coordinates': {
                'latitude': coords[0] if coords else None,
                'longitude': coords[1] if coords else None
            } if coords else None,
            'creationdate': hotspot.creationdate.isoformat() if hotspot.creationdate else None,
            'updatedate': hotspot.updatedate.isoformat() if hotspot.updatedate else None,
            'creationby': hotspot.creationby,
            'updateby': hotspot.updateby
        }
    
    def _parse_geocode(self, geocode: str) -> Optional[Tuple[float, float]]:
        """
        Parse geocode string into coordinates.
        
        Args:
            geocode: Geocode string in format "latitude,longitude"
            
        Returns:
            Tuple of (latitude, longitude) or None if invalid
        """
        return self.repository._parse_geocode(geocode)
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return self.repository._validate_coordinates(latitude, longitude)
    
    def get_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get geographic location from IP address.
        
        Args:
            ip_address: IP address to locate
            
        Returns:
            Dictionary with location information or None if not found
        """
        return geo_service.get_ip_location(ip_address)
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to geographic coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Dictionary with location information or None if not found
        """
        return geo_service.geocode_address(address)
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert coordinates to address information.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with address information or None if not found
        """
        return geo_service.reverse_geocode(latitude, longitude)
    
    def get_hotspot_with_ip_location(self, hotspot_id: int, ip_address: str) -> Dict[str, Any]:
        """
        Get hotspot with IP-based location if no coordinates are set.
        
        Args:
            hotspot_id: ID of the hotspot
            ip_address: IP address to use for geolocation
            
        Returns:
            Dictionary with hotspot and location data
            
        Raises:
            NotFoundError: If hotspot not found
        """
        hotspot = self.repository.get_by_id(hotspot_id)
        if not hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        hotspot_data = self._hotspot_to_dict(hotspot)
        
        # If hotspot has no coordinates, try IP geolocation
        if not hotspot_data['coordinates'] and ip_address:
            ip_location = self.get_ip_location(ip_address)
            if ip_location and ip_location.get('coordinates'):
                hotspot_data['ip_location'] = ip_location
                hotspot_data['suggested_coordinates'] = ip_location['coordinates']
        
        return hotspot_data
    
    def update_hotspot_from_ip(self, 
                              hotspot_id: int, 
                              ip_address: str,
                              updated_by: str = None) -> Dict[str, Any]:
        """
        Update hotspot location based on IP geolocation.
        
        Args:
            hotspot_id: ID of the hotspot to update
            ip_address: IP address to use for geolocation
            updated_by: Username of the operator updating location
            
        Returns:
            Updated hotspot data with new coordinates
            
        Raises:
            NotFoundError: If hotspot not found
            ValidationError: If IP geolocation fails
        """
        ip_location = self.get_ip_location(ip_address)
        if not ip_location or not ip_location.get('coordinates'):
            raise ValidationError(f"Unable to determine location for IP address: {ip_address}")
        
        coordinates = ip_location['coordinates']
        if not coordinates.get('latitude') or not coordinates.get('longitude'):
            raise ValidationError("IP geolocation did not return valid coordinates")
        
        # Update hotspot location
        hotspot = self.repository.update_hotspot_coordinates(
            hotspot_id,
            coordinates['latitude'],
            coordinates['longitude'],
            updated_by
        )
        
        if not hotspot:
            raise NotFoundError(f"Hotspot with ID {hotspot_id} not found")
        
        result = self._hotspot_to_dict(hotspot)
        result['ip_location'] = ip_location
        
        return result
    
    def get_location_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """
        Get location suggestions for geocoding.
        
        Args:
            query: Address or location query
            
        Returns:
            List of location suggestions
        """
        suggestions = []
        
        # Try geocoding the query
        location = self.geocode_address(query)
        if location:
            suggestions.append({
                'type': 'geocoded',
                'address': location['address'],
                'coordinates': location['coordinates'],
                'source': location['source']
            })
        
        return suggestions

    def _calculate_distance(self, 
                           lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points in kilometers.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        return geo_service.calculate_distance((lat1, lon1), (lat2, lon2))