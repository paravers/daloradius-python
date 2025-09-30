/**
 * Hotspot Service
 * 
 * Frontend service for hotspot management operations.
 * Provides API client functions for CRUD operations and hotspot management.
 */

import { apiService } from '@/services/api'
import type { 
  Hotspot, 
  HotspotCreate, 
  HotspotUpdate,
  HotspotListResponse,
  HotspotSearchRequest,
  HotspotValidationResponse,
  HotspotBulkDeleteResponse,
  HotspotStatisticsResponse,
  HotspotOptionsResponse
} from '@/types/hotspot'

// API endpoints
const ENDPOINTS = {
  HOTSPOTS: '/hotspots',
  SEARCH: '/hotspots/search',
  VALIDATE: '/hotspots/validate',
  BULK_DELETE: '/hotspots/bulk',
  STATISTICS: '/hotspots/stats/summary',
  OPTIONS: '/hotspots/options/all'
}

export class HotspotService {
  /**
   * Get list of hotspots with optional filtering and pagination
   */
  static async getHotspots(params: {
    query?: string
    type?: string
    owner?: string
    company?: string
    page?: number
    per_page?: number
    order_by?: string
    order_type?: 'asc' | 'desc'
  } = {}): Promise<HotspotListResponse> {
    return await apiService.get<HotspotListResponse>(ENDPOINTS.HOTSPOTS, { params })
  }

  /**
   * Get a specific hotspot by ID
   */
  static async getHotspot(id: number): Promise<Hotspot> {
    return await apiService.get<Hotspot>(`${ENDPOINTS.HOTSPOTS}/${id}`)
  }

  /**
   * Create a new hotspot
   */
  static async createHotspot(hotspotData: HotspotCreate): Promise<Hotspot> {
    return await apiService.post<Hotspot>(ENDPOINTS.HOTSPOTS, hotspotData)
  }

  /**
   * Update an existing hotspot
   */
  static async updateHotspot(id: number, hotspotData: HotspotUpdate): Promise<Hotspot> {
    return await apiService.put<Hotspot>(`${ENDPOINTS.HOTSPOTS}/${id}`, hotspotData)
  }

  /**
   * Delete a hotspot
   */
  static async deleteHotspot(id: number): Promise<void> {
    await apiService.delete(`${ENDPOINTS.HOTSPOTS}/${id}`)
  }

  /**
   * Advanced search for hotspots
   */
  static async searchHotspots(searchRequest: HotspotSearchRequest): Promise<HotspotListResponse> {
    return await apiService.post<HotspotListResponse>(ENDPOINTS.SEARCH, searchRequest)
  }

  /**
   * Validate hotspot field uniqueness
   */
  static async validateField(data: {
    name?: string
    mac?: string
    exclude_id?: number
  }): Promise<HotspotValidationResponse> {
    return await apiService.post<HotspotValidationResponse>(ENDPOINTS.VALIDATE, data)
  }

  /**
   * Validate hotspot name availability
   */
  static async validateName(name: string, excludeId?: number): Promise<boolean> {
    const result = await this.validateField({ name, exclude_id: excludeId })
    return result.valid
  }

  /**
   * Validate MAC/IP address availability
   */
  static async validateMac(mac: string, excludeId?: number): Promise<boolean> {
    const result = await this.validateField({ mac, exclude_id: excludeId })
    return result.valid
  }

  /**
   * Delete multiple hotspots in bulk
   */
  static async bulkDelete(hotspotIds: number[]): Promise<HotspotBulkDeleteResponse> {
    return await apiService.delete<HotspotBulkDeleteResponse>(ENDPOINTS.BULK_DELETE, {
      data: { hotspot_ids: hotspotIds }
    })
  }

  /**
   * Get hotspot management statistics
   */
  static async getStatistics(): Promise<HotspotStatisticsResponse> {
    return await apiService.get<HotspotStatisticsResponse>(ENDPOINTS.STATISTICS)
  }

  /**
   * Get options for hotspot dropdowns
   */
  static async getOptions(): Promise<HotspotOptionsResponse> {
    return await apiService.get<HotspotOptionsResponse>(ENDPOINTS.OPTIONS)
  }

  /**
   * Get all hotspots (simplified)
   */
  static async getAllHotspots(): Promise<Hotspot[]> {
    const response = await this.getHotspots({ per_page: 1000 })
    return response.hotspots
  }

  /**
   * Search hotspots by query string
   */
  static async quickSearch(query: string): Promise<Hotspot[]> {
    const response = await this.getHotspots({ query, per_page: 50 })
    return response.hotspots
  }

  /**
   * Get hotspots by type
   */
  static async getHotspotsByType(type: string): Promise<Hotspot[]> {
    const response = await this.getHotspots({ type, per_page: 1000 })
    return response.hotspots
  }

  /**
   * Get hotspots by owner
   */
  static async getHotspotsByOwner(owner: string): Promise<Hotspot[]> {
    const response = await this.getHotspots({ owner, per_page: 1000 })
    return response.hotspots
  }

  /**
   * Get hotspots by company
   */
  static async getHotspotsByCompany(company: string): Promise<Hotspot[]> {
    const response = await this.getHotspots({ company, per_page: 1000 })
    return response.hotspots
  }

  /**
   * Export hotspots data (for CSV/Excel export)
   */
  static async exportHotspots(filters: {
    query?: string
    type?: string
    owner?: string
    company?: string
  } = {}): Promise<Hotspot[]> {
    const response = await this.getHotspots({ ...filters, per_page: 10000 })
    return response.hotspots
  }
}

export default HotspotService