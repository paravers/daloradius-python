"""
Geo Location Service

Service for IP geolocation, coordinate validation, and geographic utilities.
Integrates with GeoIP databases and external location services.
"""

import ipaddress
import logging
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path

try:
    import geoip2.database
    import geoip2.errors
    from geoip2.models import City
    GEOIP2_AVAILABLE = True
except ImportError:
    GEOIP2_AVAILABLE = False
    logging.warning("GeoIP2 not available. Install with: pip install geoip2")

try:
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    logging.warning("GeoPy not available. Install with: pip install geopy")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from app.core.config import settings


class GeoLocationService:
    """
    Service for geographic location operations including IP geolocation,
    coordinate validation, and address geocoding.
    """

    def __init__(self):
        """Initialize geo location service with available providers."""
        self.logger = logging.getLogger(__name__)

        # Initialize GeoIP2 database if available
        self.geoip_reader = None
        if GEOIP2_AVAILABLE:
            self._init_geoip_database()

        # Initialize GeoPy geocoder if available
        self.geocoder = None
        if GEOPY_AVAILABLE:
            self.geocoder = Nominatim(user_agent="daloradius-gis")

    def _init_geoip_database(self):
        """Initialize GeoIP2 database reader."""
        try:
            # Try common GeoIP database locations
            possible_paths = [
                "/usr/share/GeoIP/GeoLite2-City.mmdb",
                "/var/lib/GeoIP/GeoLite2-City.mmdb",
                "./data/GeoLite2-City.mmdb",
                str(Path.home() / "GeoLite2-City.mmdb")
            ]

            for path in possible_paths:
                if Path(path).exists():
                    self.geoip_reader = geoip2.database.Reader(path)
                    self.logger.info(f"GeoIP database loaded from: {path}")
                    break

            if not self.geoip_reader:
                self.logger.warning(
                    "GeoIP database not found. Download GeoLite2-City.mmdb from MaxMind")

        except Exception as e:
            self.logger.error(f"Failed to initialize GeoIP database: {e}")

    def get_ip_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get geographic location information from IP address.

        Args:
            ip_address: IP address to locate

        Returns:
            Dictionary with location information or None if not found
        """
        if not self._is_valid_ip(ip_address):
            return None

        # Try GeoIP2 first
        if self.geoip_reader:
            try:
                response = self.geoip_reader.city(ip_address)
                return self._format_geoip_response(response)
            except geoip2.errors.AddressNotFoundError:
                self.logger.debug(
                    f"IP {ip_address} not found in GeoIP database")
            except Exception as e:
                self.logger.error(f"GeoIP lookup error for {ip_address}: {e}")

        # Fallback to online services
        return self._get_ip_location_online(ip_address)

    def _format_geoip_response(self, response: City) -> Dict[str, Any]:
        """Format GeoIP2 response to standard format."""
        return {
            'ip': str(response.traits.ip_address),
            'country': {
                'code': response.country.iso_code,
                'name': response.country.name
            },
            'region': {
                'code': response.subdivisions.most_specific.iso_code,
                'name': response.subdivisions.most_specific.name
            },
            'city': response.city.name,
            'postal_code': response.postal.code,
            'coordinates': {
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None
            },
            'accuracy_radius': response.location.accuracy_radius,
            'timezone': response.location.time_zone,
            'isp': getattr(response.traits, 'isp', None),
            'organization': getattr(response.traits, 'organization', None),
            'source': 'geoip2'
        }

    def _get_ip_location_online(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get IP location from online services as fallback."""
        if not REQUESTS_AVAILABLE:
            return None

        try:
            # Try ip-api.com (free service)
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('status') == 'success':
                    return {
                        'ip': ip_address,
                        'country': {
                            'code': data.get('countryCode'),
                            'name': data.get('country')
                        },
                        'region': {
                            'code': data.get('region'),
                            'name': data.get('regionName')
                        },
                        'city': data.get('city'),
                        'postal_code': data.get('zip'),
                        'coordinates': {
                            'latitude': data.get('lat'),
                            'longitude': data.get('lon')
                        },
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'organization': data.get('org'),
                        'source': 'ip-api'
                    }

        except Exception as e:
            self.logger.error(f"Online IP lookup error for {ip_address}: {e}")

        return None

    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to geographic coordinates.

        Args:
            address: Address string to geocode

        Returns:
            Dictionary with location information or None if not found
        """
        if not GEOPY_AVAILABLE or not self.geocoder:
            return None

        try:
            location = self.geocoder.geocode(address, timeout=10)

            if location:
                return {
                    'address': location.address,
                    'coordinates': {
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    },
                    'raw': location.raw,
                    'source': 'nominatim'
                }

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.error(f"Geocoding error for '{address}': {e}")
        except Exception as e:
            self.logger.error(f"Unexpected geocoding error: {e}")

        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert coordinates to address information.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with address information or None if not found
        """
        if not GEOPY_AVAILABLE or not self.geocoder:
            return None

        if not self.validate_coordinates(latitude, longitude):
            return None

        try:
            location = self.geocoder.reverse(
                (latitude, longitude),
                timeout=10,
                language='zh'  # Prefer Chinese for Chinese locations
            )

            if location:
                return {
                    'address': location.address,
                    'coordinates': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'raw': location.raw,
                    'source': 'nominatim'
                }

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.error(
                f"Reverse geocoding error for {latitude},{longitude}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected reverse geocoding error: {e}")

        return None

    def calculate_distance(self,
                           point1: Tuple[float, float],
                           point2: Tuple[float, float]) -> float:
        """
        Calculate distance between two geographic points.

        Args:
            point1: First point as (latitude, longitude)
            point2: Second point as (latitude, longitude)

        Returns:
            Distance in kilometers
        """
        if GEOPY_AVAILABLE:
            try:
                return geodesic(point1, point2).kilometers
            except Exception as e:
                self.logger.error(f"GeoPy distance calculation error: {e}")

        # Fallback to Haversine formula
        return self._haversine_distance(point1, point2)

    def _haversine_distance(self,
                            point1: Tuple[float, float],
                            point2: Tuple[float, float]) -> float:
        """
        Calculate distance using Haversine formula.

        Args:
            point1: First point as (latitude, longitude)
            point2: Second point as (latitude, longitude)

        Returns:
            Distance in kilometers
        """
        import math

        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        r = 6371

        return c * r

    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            True if coordinates are valid, False otherwise
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            return (-90.0 <= lat <= 90.0) and (-180.0 <= lon <= 180.0)
        except (ValueError, TypeError):
            return False

    def _is_valid_ip(self, ip_address: str) -> bool:
        """
        Validate IP address format.

        Args:
            ip_address: IP address string

        Returns:
            True if valid IP address, False otherwise
        """
        try:
            ipaddress.ip_address(ip_address)

            # Skip private/local addresses for geolocation
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast:
                return False

            return True
        except ValueError:
            return False

    def get_country_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """
        Get country information by ISO code.

        Args:
            country_code: ISO country code (e.g., 'CN', 'US')

        Returns:
            Dictionary with country information or None if not found
        """
        # Basic country information - could be expanded with a country database
        countries = {
            'CN': {'name': '中国', 'name_en': 'China', 'continent': 'Asia'},
            'US': {'name': '美国', 'name_en': 'United States', 'continent': 'North America'},
            'JP': {'name': '日本', 'name_en': 'Japan', 'continent': 'Asia'},
            'KR': {'name': '韩国', 'name_en': 'South Korea', 'continent': 'Asia'},
            'GB': {'name': '英国', 'name_en': 'United Kingdom', 'continent': 'Europe'},
            'DE': {'name': '德国', 'name_en': 'Germany', 'continent': 'Europe'},
            'FR': {'name': '法国', 'name_en': 'France', 'continent': 'Europe'},
            'CA': {'name': '加拿大', 'name_en': 'Canada', 'continent': 'North America'},
            'AU': {'name': '澳大利亚', 'name_en': 'Australia', 'continent': 'Oceania'},
            'SG': {'name': '新加坡', 'name_en': 'Singapore', 'continent': 'Asia'},
            'IN': {'name': '印度', 'name_en': 'India', 'continent': 'Asia'},
            'BR': {'name': '巴西', 'name_en': 'Brazil', 'continent': 'South America'},
            'RU': {'name': '俄国', 'name_en': 'Russia', 'continent': 'Europe/Asia'}
        }

        return countries.get(country_code.upper())

    def get_nearby_cities(self,
                          latitude: float,
                          longitude: float,
                          radius_km: float = 50) -> List[Dict[str, Any]]:
        """
        Get nearby cities within specified radius.
        Note: This is a simplified implementation. 
        A full implementation would require a cities database.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in kilometers

        Returns:
            List of nearby cities
        """
        # This would typically query a cities database
        # For now, return empty list with a note
        self.logger.info(
            f"Nearby cities search requested for {latitude},{longitude} within {radius_km}km")
        return []

    def format_coordinates(self,
                           latitude: float,
                           longitude: float,
                           format_type: str = 'decimal') -> str:
        """
        Format coordinates in different representations.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            format_type: Format type ('decimal', 'dms', 'simple')

        Returns:
            Formatted coordinate string
        """
        if not self.validate_coordinates(latitude, longitude):
            return "Invalid coordinates"

        if format_type == 'dms':
            # Degrees, Minutes, Seconds format
            def to_dms(coord, is_lat=True):
                abs_coord = abs(coord)
                degrees = int(abs_coord)
                minutes = int((abs_coord - degrees) * 60)
                seconds = ((abs_coord - degrees) * 60 - minutes) * 60

                if is_lat:
                    direction = 'N' if coord >= 0 else 'S'
                else:
                    direction = 'E' if coord >= 0 else 'W'

                return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"

            lat_dms = to_dms(latitude, True)
            lon_dms = to_dms(longitude, False)
            return f"{lat_dms}, {lon_dms}"

        elif format_type == 'simple':
            return f"{latitude:.6f},{longitude:.6f}"

        else:  # decimal (default)
            return f"{latitude:.6f}°, {longitude:.6f}°"

    def is_point_in_china(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are within China's approximate boundaries.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            True if point is likely in China, False otherwise
        """
        # Approximate boundaries of China
        china_bounds = {
            'north': 53.5,
            'south': 18.2,
            'east': 134.8,
            'west': 73.5
        }

        return (china_bounds['south'] <= latitude <= china_bounds['north'] and
                china_bounds['west'] <= longitude <= china_bounds['east'])

    def cleanup(self):
        """Clean up resources."""
        if self.geoip_reader:
            try:
                self.geoip_reader.close()
            except Exception as e:
                self.logger.error(f"Error closing GeoIP reader: {e}")


# Global service instance
geo_service = GeoLocationService()

# Cleanup function for application shutdown


def cleanup_geo_service():
    """Clean up geo service resources."""
    geo_service.cleanup()
