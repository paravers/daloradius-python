/**
 * Reports API Service
 * 
 * Service class for handling all reports-related API calls
 */

import { AxiosResponse } from 'axios'
import { apiClient } from './apiClient'
import {
  // UPS Status types
  UpsStatusCreate,
  UpsStatusUpdate,
  UpsStatusResponse,
  UpsStatusListResponse,
  
  // RAID Status types
  RaidStatusCreate,
  RaidStatusUpdate,
  RaidStatusResponse,
  RaidStatusListResponse,
  
  // HeartBeat types
  HeartBeatCreate,
  HeartBeatUpdate,
  HeartBeatResponse,
  HeartBeatListResponse,
  
  // Report Template types
  ReportTemplateCreate,
  ReportTemplateUpdate,
  ReportTemplateResponse,
  ReportTemplateListResponse,
  
  // Report Generation types
  ReportGenerationCreate,
  ReportGenerationResponse,
  ReportGenerationListResponse,
  
  // Server Monitoring types
  ServerMonitoringCreate,
  ServerMonitoringResponse,
  ServerMonitoringListResponse,
  
  // Report Query types
  OnlineUsersReportQuery,
  HistoryReportQuery,
  NewUsersReportQuery,
  TopUsersReportQuery,
  SystemLogQuery,
  BatchReportQuery,
  
  // Report Data types
  OnlineUserReport,
  HistoryReportItem,
  NewUserReportItem,
  TopUserReportItem,
  SystemLogReportItem,
  BatchReportItem,
  SystemStatusReport,
  ReportsDashboard,
  
  // Enums
  ReportType
} from '@/types/reports'

export class ReportsApiService {
  private readonly baseUrl = '/reports'

  // =============================================================================
  // UPS Status API Methods
  // =============================================================================

  async createUpsStatus(data: UpsStatusCreate): Promise<UpsStatusResponse> {
    const response: AxiosResponse<UpsStatusResponse> = await apiClient.post(
      `${this.baseUrl}/ups-status`,
      data
    )
    return response.data
  }

  async getUpsStatus(id: number): Promise<UpsStatusResponse> {
    const response: AxiosResponse<UpsStatusResponse> = await apiClient.get(
      `${this.baseUrl}/ups-status/${id}`
    )
    return response.data
  }

  async updateUpsStatus(id: number, data: UpsStatusUpdate): Promise<UpsStatusResponse> {
    const response: AxiosResponse<UpsStatusResponse> = await apiClient.put(
      `${this.baseUrl}/ups-status/${id}`,
      data
    )
    return response.data
  }

  async deleteUpsStatus(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/ups-status/${id}`)
  }

  async listUpsStatus(params?: {
    skip?: number
    limit?: number
  }): Promise<UpsStatusResponse[]> {
    const response: AxiosResponse<UpsStatusResponse[]> = await apiClient.get(
      `${this.baseUrl}/ups-status`,
      { params }
    )
    return response.data
  }

  async getUpsSummary(): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/ups-status/summary`
    )
    return response.data
  }

  // =============================================================================
  // RAID Status API Methods
  // =============================================================================

  async createRaidStatus(data: RaidStatusCreate): Promise<RaidStatusResponse> {
    const response: AxiosResponse<RaidStatusResponse> = await apiClient.post(
      `${this.baseUrl}/raid-status`,
      data
    )
    return response.data
  }

  async getRaidStatus(id: number): Promise<RaidStatusResponse> {
    const response: AxiosResponse<RaidStatusResponse> = await apiClient.get(
      `${this.baseUrl}/raid-status/${id}`
    )
    return response.data
  }

  async updateRaidStatus(id: number, data: RaidStatusUpdate): Promise<RaidStatusResponse> {
    const response: AxiosResponse<RaidStatusResponse> = await apiClient.put(
      `${this.baseUrl}/raid-status/${id}`,
      data
    )
    return response.data
  }

  async deleteRaidStatus(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/raid-status/${id}`)
  }

  async listRaidStatus(params?: {
    skip?: number
    limit?: number
  }): Promise<RaidStatusResponse[]> {
    const response: AxiosResponse<RaidStatusResponse[]> = await apiClient.get(
      `${this.baseUrl}/raid-status`,
      { params }
    )
    return response.data
  }

  async getRaidSummary(): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/raid-status/summary`
    )
    return response.data
  }

  // =============================================================================
  // HeartBeat API Methods
  // =============================================================================

  async createHeartBeat(data: HeartBeatCreate): Promise<HeartBeatResponse> {
    const response: AxiosResponse<HeartBeatResponse> = await apiClient.post(
      `${this.baseUrl}/heartbeat`,
      data
    )
    return response.data
  }

  async getHeartBeat(id: number): Promise<HeartBeatResponse> {
    const response: AxiosResponse<HeartBeatResponse> = await apiClient.get(
      `${this.baseUrl}/heartbeat/${id}`
    )
    return response.data
  }

  async updateHeartBeat(id: number, data: HeartBeatUpdate): Promise<HeartBeatResponse> {
    const response: AxiosResponse<HeartBeatResponse> = await apiClient.put(
      `${this.baseUrl}/heartbeat/${id}`,
      data
    )
    return response.data
  }

  async deleteHeartBeat(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/heartbeat/${id}`)
  }

  async listHeartBeats(params?: {
    skip?: number
    limit?: number
  }): Promise<HeartBeatResponse[]> {
    const response: AxiosResponse<HeartBeatResponse[]> = await apiClient.get(
      `${this.baseUrl}/heartbeat`,
      { params }
    )
    return response.data
  }

  async getHeartBeatSummary(): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/heartbeat/summary`
    )
    return response.data
  }

  // =============================================================================
  // Report Template API Methods
  // =============================================================================

  async createReportTemplate(data: ReportTemplateCreate): Promise<ReportTemplateResponse> {
    const response: AxiosResponse<ReportTemplateResponse> = await apiClient.post(
      `${this.baseUrl}/templates`,
      data
    )
    return response.data
  }

  async getReportTemplate(id: number): Promise<ReportTemplateResponse> {
    const response: AxiosResponse<ReportTemplateResponse> = await apiClient.get(
      `${this.baseUrl}/templates/${id}`
    )
    return response.data
  }

  async updateReportTemplate(id: number, data: ReportTemplateUpdate): Promise<ReportTemplateResponse> {
    const response: AxiosResponse<ReportTemplateResponse> = await apiClient.put(
      `${this.baseUrl}/templates/${id}`,
      data
    )
    return response.data
  }

  async deleteReportTemplate(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/templates/${id}`)
  }

  async listReportTemplates(params?: {
    skip?: number
    limit?: number
    report_type?: ReportType
  }): Promise<ReportTemplateResponse[]> {
    const response: AxiosResponse<ReportTemplateResponse[]> = await apiClient.get(
      `${this.baseUrl}/templates`,
      { params }
    )
    return response.data
  }

  // =============================================================================
  // Report Generation API Methods
  // =============================================================================

  async createReportGeneration(data: ReportGenerationCreate): Promise<ReportGenerationResponse> {
    const response: AxiosResponse<ReportGenerationResponse> = await apiClient.post(
      `${this.baseUrl}/generate`,
      data
    )
    return response.data
  }

  async getReportGeneration(id: number): Promise<ReportGenerationResponse> {
    const response: AxiosResponse<ReportGenerationResponse> = await apiClient.get(
      `${this.baseUrl}/generate/${id}`
    )
    return response.data
  }

  async getUserReportGenerations(username: string): Promise<ReportGenerationResponse[]> {
    const response: AxiosResponse<ReportGenerationResponse[]> = await apiClient.get(
      `${this.baseUrl}/generate/user/${username}`
    )
    return response.data
  }

  async getPendingReports(): Promise<ReportGenerationResponse[]> {
    const response: AxiosResponse<ReportGenerationResponse[]> = await apiClient.get(
      `${this.baseUrl}/generate/pending`
    )
    return response.data
  }

  // =============================================================================
  // Report Data API Methods
  // =============================================================================

  async getOnlineUsersReport(query?: OnlineUsersReportQuery): Promise<OnlineUserReport[]> {
    const response: AxiosResponse<OnlineUserReport[]> = await apiClient.get(
      `${this.baseUrl}/data/online-users`,
      { params: query }
    )
    return response.data
  }

  async getHistoryReport(query?: HistoryReportQuery): Promise<HistoryReportItem[]> {
    const response: AxiosResponse<HistoryReportItem[]> = await apiClient.get(
      `${this.baseUrl}/data/history`,
      { params: query }
    )
    return response.data
  }

  async getLastConnectReport(limit = 100): Promise<any[]> {
    const response: AxiosResponse<any[]> = await apiClient.get(
      `${this.baseUrl}/data/last-connect`,
      { params: { limit } }
    )
    return response.data
  }

  async getNewUsersReport(query?: NewUsersReportQuery): Promise<NewUserReportItem[]> {
    const response: AxiosResponse<NewUserReportItem[]> = await apiClient.get(
      `${this.baseUrl}/data/new-users`,
      { params: query }
    )
    return response.data
  }

  async getTopUsersReport(query?: TopUsersReportQuery): Promise<TopUserReportItem[]> {
    const response: AxiosResponse<TopUserReportItem[]> = await apiClient.get(
      `${this.baseUrl}/data/top-users`,
      { params: query }
    )
    return response.data
  }

  async getSystemLogsReport(query?: SystemLogQuery): Promise<SystemLogReportItem[]> {
    const response: AxiosResponse<SystemLogReportItem[]> = await apiClient.get(
      `${this.baseUrl}/data/system-logs`,
      { params: query }
    )
    return response.data
  }

  async getBatchReport(query?: BatchReportQuery): Promise<BatchReportItem[]> {
    const response: AxiosResponse<BatchReportItem[]> = await apiClient.get(
      `${this.baseUrl}/data/batch`,
      { params: query }
    )
    return response.data
  }

  async getSystemStatusReport(): Promise<SystemStatusReport> {
    const response: AxiosResponse<SystemStatusReport> = await apiClient.get(
      `${this.baseUrl}/data/system-status`
    )
    return response.data
  }

  async getReportsDashboard(): Promise<ReportsDashboard> {
    const response: AxiosResponse<ReportsDashboard> = await apiClient.get(
      `${this.baseUrl}/dashboard`
    )
    return response.data
  }

  // =============================================================================
  // Utility Methods
  // =============================================================================

  async exportReport(
    reportType: string,
    format: 'csv' | 'excel' | 'pdf' | 'json',
    query?: any
  ): Promise<Blob> {
    const response = await apiClient.get(
      `${this.baseUrl}/export/${reportType}`,
      {
        params: { ...query, format },
        responseType: 'blob'
      }
    )
    return response.data
  }

  async downloadReportFile(generationId: number): Promise<Blob> {
    const response = await apiClient.get(
      `${this.baseUrl}/download/${generationId}`,
      { responseType: 'blob' }
    )
    return response.data
  }

  // =============================================================================
  // Real-time Methods
  // =============================================================================

  async getRealtimeSystemStatus(): Promise<any> {
    const response = await apiClient.get(
      `${this.baseUrl}/realtime/system-status`
    )
    return response.data
  }

  async getRealtimeOnlineUsers(): Promise<OnlineUserReport[]> {
    const response: AxiosResponse<OnlineUserReport[]> = await apiClient.get(
      `${this.baseUrl}/realtime/online-users`
    )
    return response.data
  }

  // =============================================================================
  // Batch Operations
  // =============================================================================

  async bulkUpdateSystemStatus(updates: Array<{
    type: 'ups' | 'raid' | 'heartbeat'
    id: number
    data: any
  }>): Promise<any> {
    const response = await apiClient.post(
      `${this.baseUrl}/bulk/system-status`,
      { updates }
    )
    return response.data
  }

  async scheduleReportGeneration(data: {
    report_type: ReportType
    schedule: string // cron expression
    parameters?: any
  }): Promise<any> {
    const response = await apiClient.post(
      `${this.baseUrl}/schedule`,
      data
    )
    return response.data
  }

  // =============================================================================
  // Analytics Methods
  // =============================================================================

  async getReportAnalytics(dateRange?: {
    start: string
    end: string
  }): Promise<any> {
    const response = await apiClient.get(
      `${this.baseUrl}/analytics`,
      { params: dateRange }
    )
    return response.data
  }

  async getUsageStatistics(): Promise<any> {
    const response = await apiClient.get(
      `${this.baseUrl}/analytics/usage`
    )
    return response.data
  }

  async getPerformanceMetrics(): Promise<any> {
    const response = await apiClient.get(
      `${this.baseUrl}/analytics/performance`
    )
    return response.data
  }
}

// Create and export singleton instance
export const reportsApiService = new ReportsApiService()