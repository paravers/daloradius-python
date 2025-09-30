/**
 * GIS (Geographic Information System) Service
 * 
 * TypeScript service for GIS operations, map data management, and location-based functionality.
 * Provides API integration for geographic hotspot management and coordinate operations.
 */

import type { AxiosResponse } from 'axios'
import { apiService } from './api'

// Type definitions for GIS operations
export interface GeoCoordinates {
  latitude: number
  longitude: number
}

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

export interface HotspotMarker {
  id: number
  name: string
  latitude: number
  longitude: number
  status: string
  comment?: string
  creationdate?: string
  creationby?: string
}

export interface MapData {
  markers: HotspotMarker[]
  bounds?: MapBounds
  center?: GeoCoordinates
  statistics: {
    total_hotspots: number
    active_hotspots: number
    inactive_hotspots: number
    activity_rate: number
  }
  filter_bounds?: MapBounds
}

export interface HotspotLocation {
  id: number
  name: string
  mac_address?: string
  status?: string
  comment?: string
  geocode?: string
  coordinates?: GeoCoordinates
  distance_km?: number
  creationdate?: string
  updatedate?: string
  creationby?: string
  updateby?: string
}

export interface LocationSearchRequest {
  latitude: number
  longitude: number
  radius_km: number
}

export interface UpdateLocationRequest {
  latitude: number
  longitude: number
}

export interface CoordinateValidationRequest {
  latitude: number
  longitude: number
}

export interface CoordinateValidationResponse {
  valid: boolean
  latitude: number
  longitude: number
  errors?: string[]
}

export interface HotspotListResponse {
  hotspots: HotspotLocation[]
  pagination: {
    current_page: number
    page_size: number
    total_count: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface RegionalStatistics {
  total_hotspots: number
  active_hotspots: number
  inactive_hotspots: number
  activity_rate: number
  region_bounds: MapBounds
}

/**
 * GIS Service Class
 * 
 * Provides methods for interacting with GIS API endpoints including
 * map data retrieval, location-based searches, and coordinate management.
 */
export class GisService {
  private readonly basePath = '/api/v1/gis'

  /**
   * Get comprehensive map data for GIS visualization
   * 
   * @param bounds - Optional geographic bounds to filter hotspots
   * @param includeInactive - Whether to include inactive hotspots
   * @returns Promise resolving to map data
   */
  async getMapData(bounds?: MapBounds, includeInactive: boolean = true): Promise<MapData> {
    const params: Record<string, any> = {
      include_inactive: includeInactive
    }

    if (bounds) {
      params.north = bounds.north
      params.south = bounds.south
      params.east = bounds.east
      params.west = bounds.west
    }

    const response: AxiosResponse<MapData> = await apiService.get(
      `${this.basePath}/map-data`,
      { params }
    )

    return response.data
  }

  /**
   * Search for hotspots near a specific location
   * 
   * @param searchRequest - Location search parameters
   * @returns Promise resolving to list of nearby hotspots with distance
   */
  async searchHotspotsNearLocation(searchRequest: LocationSearchRequest): Promise<HotspotLocation[]> {
    const response: AxiosResponse<HotspotLocation[]> = await apiService.post(
      `${this.basePath}/search/near-location`,
      searchRequest
    )

    return response.data
  }

  /**
   * Update the geographic location of a hotspot
   * 
   * @param hotspotId - ID of the hotspot to update
   * @param location - New location coordinates
   * @returns Promise resolving to updated hotspot data
   */
  async updateHotspotLocation(hotspotId: number, location: UpdateLocationRequest): Promise<HotspotLocation> {
    const response: AxiosResponse<HotspotLocation> = await apiService.put(
      `${this.basePath}/hotspots/${hotspotId}/location`,
      location
    )

    return response.data
  }

  /**
   * Remove geographic coordinates from a hotspot
   * 
   * @param hotspotId - ID of the hotspot to update
   * @returns Promise resolving to updated hotspot data
   */
  async removeHotspotLocation(hotspotId: number): Promise<HotspotLocation> {
    const response: AxiosResponse<HotspotLocation> = await apiService.delete(
      `${this.basePath}/hotspots/${hotspotId}/location`
    )

    return response.data
  }

  /**
   * Get hotspots that don't have geographic coordinates
   * 
   * @param page - Page number (1-based)
   * @param pageSize - Number of items per page
   * @returns Promise resolving to paginated list of hotspots without location
   */
  async getHotspotsWithoutLocation(page: number = 1, pageSize: number = 50): Promise<HotspotListResponse> {
    const response: AxiosResponse<HotspotListResponse> = await apiService.get(
      `${this.basePath}/hotspots/without-location`,
      {
        params: {
          page,
          page_size: pageSize
        }
      }
    )

    return response.data
  }

  /**
   * Get statistics for hotspots in a specific geographic region
   * 
   * @param bounds - Geographic bounding box
   * @returns Promise resolving to regional statistics
   */
  async getRegionalStatistics(bounds: MapBounds): Promise<RegionalStatistics> {
    const response: AxiosResponse<RegionalStatistics> = await apiService.post(
      `${this.basePath}/statistics/regional`,
      bounds
    )

    return response.data
  }

  /**
   * Search hotspots by location-related name or description
   * 
   * @param query - Search query string
   * @param coordinatesOnly - Only return hotspots with coordinates
   * @returns Promise resolving to list of matching hotspots
   */
  async searchHotspotsByName(query: string, coordinatesOnly: boolean = false): Promise<HotspotLocation[]> {
    const response: AxiosResponse<HotspotLocation[]> = await apiService.get(
      `${this.basePath}/search/by-name`,
      {
        params: {
          q: query,
          coordinates_only: coordinatesOnly
        }
      }
    )

    return response.data
  }

  /**
   * Validate geographic coordinates
   * 
   * @param coordinates - Coordinates to validate
   * @returns Promise resolving to validation result
   */
  async validateCoordinates(coordinates: CoordinateValidationRequest): Promise<CoordinateValidationResponse> {
    const response: AxiosResponse<CoordinateValidationResponse> = await apiService.post(
      `${this.basePath}/validate-coordinates`,
      coordinates
    )

    return response.data
  }

  /**
   * Get geographic bounds for all hotspots with coordinates
   * 
   * @returns Promise resolving to map data with geographic bounds
   */
  async getGeographicBounds(): Promise<MapBounds | null> {
    const mapData = await this.getMapData()
    return mapData.bounds || null
  }

  /**
   * Get geographic center point for all hotspots with coordinates
   * 
   * @returns Promise resolving to center coordinates
   */
  async getGeographicCenter(): Promise<GeoCoordinates | null> {
    const mapData = await this.getMapData()
    return mapData.center || null
  }

  /**
   * Calculate distance between two geographic points using Haversine formula
   * 
   * @param point1 - First geographic point
   * @param point2 - Second geographic point
   * @returns Distance in kilometers
   */
  calculateDistance(point1: GeoCoordinates, point2: GeoCoordinates): number {
    const R = 6371 // Earth's radius in kilometers
    const dLat = this.toRadians(point2.latitude - point1.latitude)
    const dLon = this.toRadians(point2.longitude - point1.longitude)
    
    const lat1 = this.toRadians(point1.latitude)
    const lat2 = this.toRadians(point2.latitude)

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

    return R * c
  }

  /**
   * Validate coordinate values
   * 
   * @param latitude - Latitude to validate
   * @param longitude - Longitude to validate
   * @returns Boolean indicating if coordinates are valid
   */
  isValidCoordinates(latitude: number, longitude: number): boolean {
    return latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180
  }

  /**
   * Parse geocode string into coordinates
   * 
   * @param geocode - Geocode string in format "latitude,longitude"
   * @returns Parsed coordinates or null if invalid
   */
  parseGeocode(geocode: string): GeoCoordinates | null {
    if (!geocode || geocode === '' || geocode === '0,0') {
      return null
    }

    try {
      const parts = geocode.split(',')
      if (parts.length !== 2) {
        return null
      }

      const latitude = parseFloat(parts[0].trim())
      const longitude = parseFloat(parts[1].trim())

      if (this.isValidCoordinates(latitude, longitude)) {
        return { latitude, longitude }
      }
    } catch {
      // Ignore parsing errors
    }

    return null
  }

  /**
   * Format coordinates to geocode string
   * 
   * @param coordinates - Coordinates to format
   * @returns Formatted geocode string
   */
  formatGeocode(coordinates: GeoCoordinates): string {
    return `${coordinates.latitude},${coordinates.longitude}`
  }

  /**
   * Create a bounding box around a center point with specified radius
   * 
   * @param center - Center point coordinates
   * @param radiusKm - Radius in kilometers
   * @returns Bounding box coordinates
   */
  createBoundingBox(center: GeoCoordinates, radiusKm: number): MapBounds {
    // Approximate conversion: 1 degree ≈ 111 km
    const radiusDeg = radiusKm / 111

    return {
      north: center.latitude + radiusDeg,
      south: center.latitude - radiusDeg,
      east: center.longitude + radiusDeg,
      west: center.longitude - radiusDeg
    }
  }

  /**
   * Check if a point is within a bounding box
   * 
   * @param point - Point to check
   * @param bounds - Bounding box
   * @returns Boolean indicating if point is within bounds
   */
  isPointInBounds(point: GeoCoordinates, bounds: MapBounds): boolean {
    return (
      point.latitude >= bounds.south &&
      point.latitude <= bounds.north &&
      point.longitude >= bounds.west &&
      point.longitude <= bounds.east
    )
  }

  /**
   * Convert degrees to radians
   * 
   * @param degrees - Degrees to convert
   * @returns Radians
   */
  private toRadians(degrees: number): number {
    return degrees * (Math.PI / 180)
  }
}

// Export singleton instance
export const gisService = new GisService()

// Export default
export default gisService