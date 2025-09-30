/**
 * Accounting API Service
 * 
 * API service for accounting/session statistics operations
 */

import { apiClient } from '@/services/api'
import type {
  AccountingSession,
  AccountingQuery,
  AccountingOverview,
  TopUsersReport,
  HourlyTrafficReport,
  NasUsageReport,
  UserTrafficSummary,
  NasTrafficSummary,
  PaginatedAccountingResponse,
  PaginatedTopUsersResponse,
  CustomQueryRequest,
  CustomQueryResult,
  MaintenanceRequest,
  MaintenanceResult,
  AccountingApiParams,
  ReportFilters,
  AccountingTimeRangeEnum
} from '@/types/accounting'

/**
 * Accounting API Service Class
 */
export class AccountingService {
  private readonly baseUrl = '/accounting'

  // =====================================================================
  // Session Management
  // =====================================================================

  /**
   * Get paginated accounting sessions with filtering
   */
  async getSessions(query: AccountingQuery): Promise<PaginatedAccountingResponse> {
    const params = new URLSearchParams()
    
    // Pagination
    params.append('page', query.page.toString())
    params.append('page_size', query.page_size.toString())
    
    // Sorting
    if (query.sort_field) params.append('sort_field', query.sort_field)
    if (query.sort_order) params.append('sort_order', query.sort_order)
    
    // Filters
    if (query.filters) {
      Object.entries(query.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value.toString())
        }
      })
    }

    const response = await apiClient.get(`${this.baseUrl}/sessions?${params.toString()}`)
    return response.data
  }

  /**
   * Get accounting session by ID
   */
  async getSessionById(sessionId: number): Promise<AccountingSession> {
    const response = await apiClient.get(`${this.baseUrl}/sessions/${sessionId}`)
    return response.data
  }

  /**
   * Get active sessions
   */
  async getActiveSessions(params: AccountingApiParams['activeSessions'] = {}): Promise<PaginatedAccountingResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.page) searchParams.append('page', params.page.toString())
    if (params.page_size) searchParams.append('page_size', params.page_size.toString())
    if (params.nas_ip) searchParams.append('nas_ip', params.nas_ip)
    if (params.username) searchParams.append('username', params.username)

    const response = await apiClient.get(`${this.baseUrl}/sessions/active?${searchParams.toString()}`)
    return response.data
  }

  /**
   * Get sessions for a specific user
   */
  async getUserSessions(
    username: string,
    params: { page?: number; page_size?: number; date_from?: string; date_to?: string } = {}
  ): Promise<PaginatedAccountingResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.page) searchParams.append('page', params.page.toString())
    if (params.page_size) searchParams.append('page_size', params.page_size.toString())
    if (params.date_from) searchParams.append('date_from', params.date_from)
    if (params.date_to) searchParams.append('date_to', params.date_to)

    const response = await apiClient.get(`${this.baseUrl}/sessions/user/${username}?${searchParams.toString()}`)
    return response.data
  }

  // =====================================================================
  // Statistics and Overview
  // =====================================================================

  /**
   * Get comprehensive accounting overview
   */
  async getOverview(params: AccountingApiParams['overview'] = {}): Promise<AccountingOverview> {
    const searchParams = new URLSearchParams()
    
    if (params.time_range) searchParams.append('time_range', params.time_range)
    if (params.date_from) searchParams.append('date_from', params.date_from)
    if (params.date_to) searchParams.append('date_to', params.date_to)
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const response = await apiClient.get(`${this.baseUrl}/overview?${searchParams.toString()}`)
    return response.data
  }

  // =====================================================================
  // Reports
  // =====================================================================

  /**
   * Get top users by traffic consumption
   */
  async getTopUsersReport(params: AccountingApiParams['topUsers'] = {}): Promise<PaginatedTopUsersResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.limit) searchParams.append('limit', params.limit.toString())
    if (params.page) searchParams.append('page', params.page.toString())
    if (params.page_size) searchParams.append('page_size', params.page_size.toString())
    if (params.date_from) searchParams.append('date_from', params.date_from)
    if (params.date_to) searchParams.append('date_to', params.date_to)

    const response = await apiClient.get(`${this.baseUrl}/reports/top-users?${searchParams.toString()}`)
    return response.data
  }

  /**
   * Get hourly traffic distribution report
   */
  async getHourlyTrafficReport(filters: ReportFilters = {}): Promise<HourlyTrafficReport[]> {
    const searchParams = new URLSearchParams()
    
    if (filters.date_from) searchParams.append('date_from', filters.date_from)
    if (filters.date_to) searchParams.append('date_to', filters.date_to)

    const response = await apiClient.get(`${this.baseUrl}/reports/hourly-traffic?${searchParams.toString()}`)
    return response.data
  }

  /**
   * Get NAS usage statistics report
   */
  async getNasUsageReport(filters: ReportFilters = {}): Promise<NasUsageReport[]> {
    const searchParams = new URLSearchParams()
    
    if (filters.date_from) searchParams.append('date_from', filters.date_from)
    if (filters.date_to) searchParams.append('date_to', filters.date_to)

    const response = await apiClient.get(`${this.baseUrl}/reports/nas-usage?${searchParams.toString()}`)
    return response.data
  }

  // =====================================================================
  // Custom Queries and Maintenance
  // =====================================================================

  /**
   * Execute custom accounting query
   */
  async executeCustomQuery(request: CustomQueryRequest): Promise<CustomQueryResult> {
    const response = await apiClient.post(`${this.baseUrl}/custom-query`, request)
    return response.data
  }

  /**
   * Clean up old accounting sessions
   */
  async cleanupOldSessions(request: MaintenanceRequest): Promise<MaintenanceResult> {
    const response = await apiClient.post(`${this.baseUrl}/maintenance/cleanup`, request)
    return response.data
  }

  // =====================================================================
  // Traffic Summaries
  // =====================================================================

  /**
   * Get traffic summary for a user
   */
  async getUserTrafficSummary(
    username: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<UserTrafficSummary[]> {
    const searchParams = new URLSearchParams()
    
    if (dateFrom) searchParams.append('date_from', dateFrom)
    if (dateTo) searchParams.append('date_to', dateTo)

    const response = await apiClient.get(
      `${this.baseUrl}/traffic-summary/user/${username}?${searchParams.toString()}`
    )
    return response.data
  }

  /**
   * Get traffic summary for a NAS
   */
  async getNasTrafficSummary(
    nasIpAddress: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<NasTrafficSummary[]> {
    const searchParams = new URLSearchParams()
    
    if (dateFrom) searchParams.append('date_from', dateFrom)
    if (dateTo) searchParams.append('date_to', dateTo)

    const response = await apiClient.get(
      `${this.baseUrl}/traffic-summary/nas/${nasIpAddress}?${searchParams.toString()}`
    )
    return response.data
  }

  // =====================================================================
  // Session Management Operations
  // =====================================================================

  /**
   * Disconnect a session (for active sessions)
   */
  async disconnectSession(sessionId: number): Promise<void> {
    await apiClient.post(`${this.baseUrl}/sessions/${sessionId}/disconnect`)
  }

  /**
   * Terminate a session (force stop)
   */
  async terminateSession(sessionId: number): Promise<void> {
    await apiClient.post(`${this.baseUrl}/sessions/${sessionId}/terminate`)
  }

  // =====================================================================
  // Export Functions
  // =====================================================================

  /**
   * Export sessions data
   */
  async exportSessions(params: { filters?: any; format?: string }): Promise<Blob> {
    const searchParams = new URLSearchParams()
    
    if (params.format) searchParams.append('format', params.format)
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const response = await apiClient.get(
      `${this.baseUrl}/sessions/export?${searchParams.toString()}`,
      { responseType: 'blob' }
    )
    
    // Create download
    const blob = new Blob([response.data], { 
      type: response.headers['content-type'] || 'application/octet-stream' 
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `accounting-sessions-${new Date().toISOString().split('T')[0]}.${params.format || 'csv'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return blob
  }

  /**
   * Export report data
   */
  async exportReport(params: AccountingApiParams['export']): Promise<Blob> {
    const searchParams = new URLSearchParams()
    
    searchParams.append('type', params.type)
    searchParams.append('format', params.format)
    
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const response = await apiClient.get(
      `${this.baseUrl}/reports/export?${searchParams.toString()}`,
      { responseType: 'blob' }
    )
    
    // Create download
    const blob = new Blob([response.data], { 
      type: response.headers['content-type'] || 'application/octet-stream' 
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `accounting-report-${params.type}-${new Date().toISOString().split('T')[0]}.${params.format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return blob
  }

  /**
   * Export all reports
   */
  async exportAllReports(params: { format?: string; filters?: any }): Promise<Blob> {
    const searchParams = new URLSearchParams()
    
    if (params.format) searchParams.append('format', params.format)
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const response = await apiClient.get(
      `${this.baseUrl}/reports/export-all?${searchParams.toString()}`,
      { responseType: 'blob' }
    )
    
    // Create download
    const blob = new Blob([response.data], { 
      type: response.headers['content-type'] || 'application/octet-stream' 
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `accounting-all-reports-${new Date().toISOString().split('T')[0]}.${params.format || 'xlsx'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    return blob
  }

  // =====================================================================
  // Health Check
  // =====================================================================

  /**
   * Check accounting module health
   */
  async healthCheck(): Promise<{ status: string; module: string; timestamp: string }> {
    const response = await apiClient.get(`${this.baseUrl}/health`)
    return response.data
  }

  // =====================================================================
  // Utility Methods
  // =====================================================================

  /**
   * Build query parameters for API calls
   */
  private buildQueryParams(params: Record<string, any>): URLSearchParams {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(item => searchParams.append(key, item.toString()))
        } else {
          searchParams.append(key, value.toString())
        }
      }
    })
    
    return searchParams
  }

  /**
   * Format date for API calls
   */
  private formatDate(date: Date | string): string {
    if (typeof date === 'string') return date
    return date.toISOString().split('T')[0]
  }

  /**
   * Format datetime for API calls
   */
  private formatDateTime(date: Date | string): string {
    if (typeof date === 'string') return date
    return date.toISOString()
  }

  /**
   * Parse API error response
   */
  private parseErrorResponse(error: any): string {
    if (error.response?.data?.detail) {
      return Array.isArray(error.response.data.detail) 
        ? error.response.data.detail[0].msg 
        : error.response.data.detail
    }
    
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    
    if (error.message) {
      return error.message
    }
    
    return 'An unknown error occurred'
  }
}

// Create and export singleton instance
export const accountingService = new AccountingService()

// Export service class for testing
export { AccountingService as AccountingServiceClass }

// Export default
export default accountingService