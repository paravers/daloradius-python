/**
 * NAS 设备管理服务
 * 提供NAS设备的完整API交互功能
 */

import { ApiService } from './api'

export interface NasDevice {
  id: number
  nasname: string
  shortname: string
  type: string
  ports?: number
  secret: string
  server?: string
  community?: string
  description?: string
  isActive: boolean
  lastSeen?: string
  totalRequests: number
  successfulRequests: number
  createdAt: string
  updatedAt: string
}

export interface CreateNasRequest {
  nasname: string
  shortname: string
  type: string
  ports?: number
  secret: string
  server?: string
  community?: string
  description?: string
}

export interface UpdateNasRequest {
  shortname?: string
  type?: string
  ports?: number
  secret?: string
  server?: string
  community?: string
  description?: string
}

export interface NasQueryParams {
  skip?: number
  limit?: number
  search?: string
  nas_type?: string
  status?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface NasListResponse {
  devices: NasDevice[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface NasStatusResponse {
  nas_id: number
  nasname: string
  shortname: string
  is_active: boolean
  last_seen?: string
  active_sessions: number
  total_ports?: number
  port_utilization: number
  monitoring?: NasMonitoringData
  performance: NasPerformanceData
  status: 'healthy' | 'warning' | 'critical' | 'unknown'
}

export interface NasMonitoringData {
  check_time: string
  ping_success?: boolean
  radius_auth_success?: boolean
  radius_acct_success?: boolean
  snmp_success?: boolean
  status: string
}

export interface NasPerformanceData {
  total_requests: number
  successful_requests: number
  success_rate: number
  last_seen?: string
}

export interface ConnectivityTestResult {
  nas_id: number
  nasname: string
  timestamp: string
  tests: {
    ping?: {
      success: boolean
      response_time_ms?: number
      error?: string
    }
    radius?: {
      port_1812?: { success: boolean; error?: string }
      port_1813?: { success: boolean; error?: string }
    }
    snmp?: {
      success: boolean
      error?: string
    }
  }
}

export interface NasSessionsResponse {
  sessions: NasSession[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface NasSession {
  session_id: string
  username: string
  start_time: string
  session_time: number
  input_octets: number
  output_octets: number
  framed_ip?: string
  calling_station?: string
  called_station?: string
}

export interface NasStatistics {
  total_nas: number
  active_nas: number
  inactive_nas: number
  total_active_sessions: number
  total_ports: number
  utilization_percent: number
  nas_by_type: { [key: string]: number }
  top_nas_by_sessions: Array<{
    id: number
    nasname: string
    shortname: string
    active_sessions: number
  }>
}

export interface BatchDeleteResult {
  total_requested: number
  deleted_count: number
  failed_count: number
  errors: string[]
}

/**
 * NAS服务类
 */
class NasService {
  private api = new ApiService()

  // NAS CRUD 操作
  async getNasDevices(params?: NasQueryParams): Promise<NasListResponse> {
    const queryParams = new URLSearchParams()
    
    if (params) {
      if (params.skip !== undefined) queryParams.append('skip', params.skip.toString())
      if (params.limit !== undefined) queryParams.append('limit', params.limit.toString())
      if (params.search) queryParams.append('search', params.search)
      if (params.nas_type) queryParams.append('nas_type', params.nas_type)
      if (params.status) queryParams.append('status', params.status)
      if (params.sort_by) queryParams.append('sort_by', params.sort_by)
      if (params.sort_order) queryParams.append('sort_order', params.sort_order)
    }
    
    const response = await this.api.get(`/api/v1/nas?${queryParams.toString()}`)
    return response.data as NasListResponse
  }

  async getNasDevice(id: number): Promise<NasDevice> {
    const response = await this.api.get(`/api/v1/nas/${id}`)
    return response.data as NasDevice
  }

  async createNasDevice(data: CreateNasRequest): Promise<NasDevice> {
    const response = await this.api.post('/api/v1/nas', data)
    return response.data as NasDevice
  }

  async updateNasDevice(id: number, data: UpdateNasRequest): Promise<NasDevice> {
    const response = await this.api.put(`/api/v1/nas/${id}`, data)
    return response.data as NasDevice
  }

  async deleteNasDevice(id: number): Promise<void> {
    await this.api.delete(`/api/v1/nas/${id}`)
  }

  // 批量操作
  async batchDeleteNas(ids: number[]): Promise<BatchDeleteResult> {
    const response = await this.api.delete('/api/v1/nas/batch', { data: { nas_ids: ids } })
    return response.data as BatchDeleteResult
  }

  // NAS 监控和状态
  async getNasStatus(id: number): Promise<NasStatusResponse> {
    const response = await this.api.get(`/api/v1/nas/${id}/status`)
    return response.data as NasStatusResponse
  }

  async testNasConnection(id: number): Promise<ConnectivityTestResult> {
    const response = await this.api.post(`/api/v1/nas/${id}/test-connection`)
    return response.data as ConnectivityTestResult
  }

  async getNasActiveSessions(
    id: number, 
    skip: number = 0, 
    limit: number = 20
  ): Promise<NasSessionsResponse> {
    const response = await this.api.get(`/api/v1/nas/${id}/sessions?skip=${skip}&limit=${limit}`)
    return response.data as NasSessionsResponse
  }

  // 搜索和工具方法
  async searchNasDevices(query: string, limit: number = 10): Promise<NasDevice[]> {
    const response = await this.api.get(`/api/v1/nas/search/${encodeURIComponent(query)}?limit=${limit}`)
    return response.data as NasDevice[]
  }

  async getAvailableNasTypes(): Promise<Array<{ value: string; label: string }>> {
    const response = await this.api.get('/api/v1/nas/types/available')
    return response.data
  }

  // 统计信息
  async getNasStatistics(): Promise<NasStatistics> {
    const response = await this.api.get('/api/v1/nas/statistics/overview')
    return response.data as NasStatistics
  }

  // 工具方法
  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${remainingSeconds}s`
    } else if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    } else {
      return `${remainingSeconds}s`
    }
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'healthy':
        return 'green'
      case 'warning':
        return 'orange'
      case 'critical':
        return 'red'
      case 'unknown':
      default:
        return 'gray'
    }
  }

  getStatusText(status: string): string {
    switch (status) {
      case 'healthy':
        return '健康'
      case 'warning':
        return '警告'
      case 'critical':
        return '严重'
      case 'unknown':
      default:
        return '未知'
    }
  }

  calculateUtilization(activeSessions: number, totalPorts: number): number {
    if (!totalPorts || totalPorts === 0) return 0
    return Math.round((activeSessions / totalPorts) * 100 * 100) / 100
  }

  getUtilizationColor(utilization: number): string {
    if (utilization >= 90) return 'red'
    if (utilization >= 70) return 'orange'
    return 'green'
  }

  validateNasName(nasname: string): boolean {
    // Basic validation for IP address or hostname
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
    
    return ipRegex.test(nasname) || hostnameRegex.test(nasname)
  }

  validateSecret(secret: string): boolean {
    // Secret should be at least 8 characters long
    return secret && secret.length >= 8
  }

  generateRandomSecret(length: number = 16): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }
}

// 导出服务实例
export const nasService = new NasService()
export default nasService