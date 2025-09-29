/**
 * Hotspot Service
 * 
 * Frontend service for hotspot management operations.
 * Provides API client functions for CRUD operations and hotspot management.
 */

import api from '@/services/api'
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
    const response = await api.get(ENDPOINTS.HOTSPOTS, { params })
    return response.data
  }

  /**
   * Get a specific hotspot by ID
   */
  static async getHotspot(id: number): Promise<Hotspot> {
    const response = await api.get(`${ENDPOINTS.HOTSPOTS}/${id}`)
    return response.data
  }

  /**
   * Create a new hotspot
   */
  static async createHotspot(hotspotData: HotspotCreate): Promise<Hotspot> {
    const response = await api.post(ENDPOINTS.HOTSPOTS, hotspotData)
    return response.data
  }

  /**
   * Update an existing hotspot
   */
  static async updateHotspot(id: number, hotspotData: HotspotUpdate): Promise<Hotspot> {
    const response = await api.put(`${ENDPOINTS.HOTSPOTS}/${id}`, hotspotData)
    return response.data
  }

  /**
   * Delete a hotspot
   */
  static async deleteHotspot(id: number): Promise<void> {
    await api.delete(`${ENDPOINTS.HOTSPOTS}/${id}`)
  }

  /**
   * Advanced search for hotspots
   */
  static async searchHotspots(searchRequest: HotspotSearchRequest): Promise<HotspotListResponse> {
    const response = await api.post(ENDPOINTS.SEARCH, searchRequest)
    return response.data
  }

  /**
   * Validate hotspot field uniqueness
   */
  static async validateField(data: {
    name?: string
    mac?: string
    exclude_id?: number
  }): Promise<HotspotValidationResponse> {
    const response = await api.post(ENDPOINTS.VALIDATE, data)
    return response.data
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
    const response = await api.delete(ENDPOINTS.BULK_DELETE, {
      data: { hotspot_ids: hotspotIds }
    })
    return response.data
  }

  /**
   * Get hotspot management statistics
   */
  static async getStatistics(): Promise<HotspotStatisticsResponse> {
    const response = await api.get(ENDPOINTS.STATISTICS)
    return response.data
  }

  /**
   * Get options for hotspot dropdowns
   */
  static async getOptions(): Promise<HotspotOptionsResponse> {
    const response = await api.get(ENDPOINTS.OPTIONS)
    return response.data
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