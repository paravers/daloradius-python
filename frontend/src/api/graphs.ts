import { apiService } from '@/services/api'

export interface GraphDataRequest {
  graph_type: string
  data_source: string
  time_range: {
    start_date?: string
    end_date?: string
    granularity?: string
    limit?: number
    filters?: Record<string, string | number | boolean>
  }
  chart_config?: Record<string, string | number | boolean | object>
}

export interface GraphDataResponse {
  graph_type: string
  title: string
  subtitle?: string
  data: {
    labels: string[]
    datasets: {
      label: string
      data: number[]
      backgroundColor?: string | string[]
      borderColor?: string | string[]
      borderWidth?: number
      fill?: boolean
      tension?: number
    }[]
  }
  options?: Record<string, string | number | boolean | object>
  metadata?: Record<string, string | number | boolean>
  generated_at: string
}

export interface TopUser {
  username: string
  traffic_mb: number
  sessions: number
  last_login?: string
}

export interface RecentActivity {
  id: number
  action: string
  username: string
  timestamp: string
  details?: string
}

export interface Alert {
  id: number
  level: 'info' | 'warning' | 'error'
  message: string
  timestamp: string
  resolved?: boolean
}

export interface DashboardWidget {
  id: number
  title: string
  type: string
  position_x: number
  position_y: number
  width: number
  height: number
  config: Record<string, string | number | boolean>
  created_at: string
  updated_at: string
}

export interface GraphTemplate {
  id: number
  name: string
  category: string
  description?: string
  config: Record<string, string | number | boolean | object>
  created_at: string
  updated_at: string
}

export interface GraphType {
  name: string
  label: string
  description: string
  required_params: string[]
  optional_params: string[]
}

export interface RealTimeTrends {
  timestamps: string[]
  online_users: number[]
  login_rate: number[]
  traffic_rate: number[]
  system_load: number[]
}

export interface DashboardOverview {
  current_online_users: number
  today_logins: number
  today_traffic: number
  active_sessions: number
  system_health_score: number
  top_users: TopUser[]
  recent_activity: RecentActivity[]
  alerts: Alert[]
  generated_at: string
}

export interface RealTimeStats {
  online_users: number
  today_logins: number
  today_traffic_gb: number
  active_sessions: number
  system_health: number
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  radius_response_time: number
  last_updated: string
}

export const graphsApi = {
  // Graph data endpoints
  async getGraphData(request: GraphDataRequest): Promise<GraphDataResponse> {
    return await apiService.post<GraphDataResponse>('/api/v1/graphs/data', request)
  },

  async getOverallLogins(params: {
    start_date?: string
    end_date?: string
    granularity?: string
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/overall-logins', { params })
  },

  async getDownloadUploadStats(params: {
    start_date?: string
    end_date?: string
    granularity?: string
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/download-upload-stats', { params })
  },

  async getLoggedUsers(params: {
    start_date?: string
    end_date?: string
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/logged-users', { params })
  },

  async getAlltimeStats(): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/alltime-stats')
  },

  async getTopUsers(params: {
    start_date?: string
    end_date?: string
    limit?: number
    traffic_type?: string
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/top-users', { params })
  },

  async getTrafficComparison(params: {
    start_date?: string
    end_date?: string
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/traffic-comparison', { params })
  },

  async getSystemPerformance(params: {
    hours?: number
  }): Promise<GraphDataResponse> {
    return await apiService.get<GraphDataResponse>('/api/v1/graphs/system-performance', { params })
  },

  // Dashboard endpoints
  async getDashboardOverview(): Promise<DashboardOverview> {
    return await apiService.get<DashboardOverview>('/api/dashboard/overview')
  },

  async getDashboardWidgets(dashboardId: string, params?: {
    include_shared?: boolean
  }): Promise<DashboardWidget[]> {
    return await apiService.get<DashboardWidget[]>(`/api/dashboard/widgets/${dashboardId}`, { params })
  },

  async createDashboardWidget(widgetData: Partial<DashboardWidget>): Promise<DashboardWidget> {
    return await apiService.post<DashboardWidget>('/api/dashboard/widgets', widgetData)
  },

  async updateDashboardWidget(widgetId: number, widgetData: Partial<DashboardWidget>): Promise<DashboardWidget> {
    return await apiService.put<DashboardWidget>(`/api/dashboard/widgets/${widgetId}`, widgetData)
  },

  async updateWidgetPosition(widgetId: number, params: {
    position_x: number
    position_y: number
  }): Promise<DashboardWidget> {
    return await apiService.put<DashboardWidget>(`/api/dashboard/widgets/${widgetId}/position`, null, { params })
  },

  async updateWidgetSize(widgetId: number, params: {
    width: number
    height: number
  }): Promise<DashboardWidget> {
    return await apiService.put<DashboardWidget>(`/api/dashboard/widgets/${widgetId}/size`, null, { params })
  },

  async deleteDashboardWidget(widgetId: number): Promise<void> {
    await apiService.delete(`/api/dashboard/widgets/${widgetId}`)
  },

  // Template endpoints
  async getGraphTemplates(params?: { category?: string }): Promise<GraphTemplate[]> {
    return await apiService.get<GraphTemplate[]>('/api/v1/graphs/templates', { params })
  },

  async getGraphTemplate(templateId: number): Promise<GraphTemplate> {
    return await apiService.get<GraphTemplate>(`/api/v1/graphs/templates/${templateId}`)
  },

  async createGraphTemplate(templateData: Partial<GraphTemplate>): Promise<GraphTemplate> {
    return await apiService.post<GraphTemplate>('/api/v1/graphs/templates', templateData)
  },

  async updateGraphTemplate(templateId: number, templateData: Partial<GraphTemplate>): Promise<GraphTemplate> {
    return await apiService.put<GraphTemplate>(`/api/v1/graphs/templates/${templateId}`, templateData)
  },

  // Real-time stats
  async getRealTimeStats(): Promise<RealTimeStats> {
    return await apiService.get<RealTimeStats>('/api/v1/graphs/realtime/stats')
  },

  async getRealTimeTrends(params?: { hours?: number }): Promise<RealTimeTrends> {
    return await apiService.get<RealTimeTrends>('/api/v1/graphs/realtime/trends', { params })
  },

  // Export endpoints
  async exportDataCsv(params: {
    graph_type: string
    start_date?: string
    end_date?: string
  }): Promise<void> {
    const response = await apiService.get('/api/v1/graphs/export/csv', { 
      params,
      responseType: 'blob'
    }) as unknown as { data: Blob }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${params.graph_type}_export.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  async exportDataJson(params: {
    graph_type: string
    start_date?: string
    end_date?: string
  }): Promise<void> {
    const response = await apiService.get('/api/v1/graphs/export/json', { 
      params,
      responseType: 'blob'
    }) as unknown as { data: Blob }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${params.graph_type}_export.json`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  // Graph metadata
  async getGraphTypes(): Promise<GraphType[]> {
    return await apiService.get<GraphType[]>('/api/v1/graphs/types')
  }
}