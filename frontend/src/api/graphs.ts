import axios from '@/utils/axios'

export interface GraphDataRequest {
  graph_type: string
  data_source: string
  time_range: {
    start_date?: string
    end_date?: string
    granularity?: string
    limit?: number
    filters?: Record<string, any>
  }
  chart_config?: Record<string, any>
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
  options?: Record<string, any>
  metadata?: Record<string, any>
  generated_at: string
}

export interface DashboardOverview {
  current_online_users: number
  today_logins: number
  today_traffic: number
  active_sessions: number
  system_health_score: number
  top_users: any[]
  recent_activity: any[]
  alerts: any[]
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
    const response = await axios.post('/api/graphs/data', request)
    return response.data
  },

  async getOverallLogins(params: {
    start_date?: string
    end_date?: string
    granularity?: string
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/overall-logins', { params })
    return response.data
  },

  async getDownloadUploadStats(params: {
    start_date?: string
    end_date?: string
    granularity?: string
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/download-upload-stats', { params })
    return response.data
  },

  async getLoggedUsers(params: {
    start_date?: string
    end_date?: string
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/logged-users', { params })
    return response.data
  },

  async getAlltimeStats(): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/alltime-stats')
    return response.data
  },

  async getTopUsers(params: {
    start_date?: string
    end_date?: string
    limit?: number
    traffic_type?: string
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/top-users', { params })
    return response.data
  },

  async getTrafficComparison(params: {
    start_date?: string
    end_date?: string
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/traffic-comparison', { params })
    return response.data
  },

  async getSystemPerformance(params: {
    hours?: number
  }): Promise<GraphDataResponse> {
    const response = await axios.get('/api/graphs/system-performance', { params })
    return response.data
  },

  // Dashboard endpoints
  async getDashboardOverview(): Promise<DashboardOverview> {
    const response = await axios.get('/api/dashboard/overview')
    return response.data
  },

  async getDashboardWidgets(dashboardId: string, params?: {
    include_shared?: boolean
  }): Promise<any[]> {
    const response = await axios.get(`/api/dashboard/widgets/${dashboardId}`, { params })
    return response.data
  },

  async createDashboardWidget(widgetData: any): Promise<any> {
    const response = await axios.post('/api/dashboard/widgets', widgetData)
    return response.data
  },

  async updateDashboardWidget(widgetId: number, widgetData: any): Promise<any> {
    const response = await axios.put(`/api/dashboard/widgets/${widgetId}`, widgetData)
    return response.data
  },

  async updateWidgetPosition(widgetId: number, params: {
    position_x: number
    position_y: number
  }): Promise<any> {
    const response = await axios.put(`/api/dashboard/widgets/${widgetId}/position`, null, { params })
    return response.data
  },

  async updateWidgetSize(widgetId: number, params: {
    width: number
    height: number
  }): Promise<any> {
    const response = await axios.put(`/api/dashboard/widgets/${widgetId}/size`, null, { params })
    return response.data
  },

  async deleteDashboardWidget(widgetId: number): Promise<any> {
    const response = await axios.delete(`/api/dashboard/widgets/${widgetId}`)
    return response.data
  },

  // Template endpoints
  async getGraphTemplates(params?: { category?: string }): Promise<any[]> {
    const response = await axios.get('/api/graphs/templates', { params })
    return response.data
  },

  async getGraphTemplate(templateId: number): Promise<any> {
    const response = await axios.get(`/api/graphs/templates/${templateId}`)
    return response.data
  },

  async createGraphTemplate(templateData: any): Promise<any> {
    const response = await axios.post('/api/graphs/templates', templateData)
    return response.data
  },

  async updateGraphTemplate(templateId: number, templateData: any): Promise<any> {
    const response = await axios.put(`/api/graphs/templates/${templateId}`, templateData)
    return response.data
  },

  // Real-time stats
  async getRealTimeStats(): Promise<RealTimeStats> {
    const response = await axios.get('/api/graphs/realtime/stats')
    return response.data
  },

  async getRealTimeTrends(params?: { hours?: number }): Promise<any> {
    const response = await axios.get('/api/graphs/realtime/trends', { params })
    return response.data
  },

  // Export endpoints
  async exportDataCsv(params: {
    graph_type: string
    start_date?: string
    end_date?: string
  }): Promise<void> {
    const response = await axios.get('/api/graphs/export/csv', { 
      params,
      responseType: 'blob'
    })
    
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
    const response = await axios.get('/api/graphs/export/json', { 
      params,
      responseType: 'blob'
    })
    
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
  async getGraphTypes(): Promise<any> {
    const response = await axios.get('/api/graphs/types')
    return response.data
  }
}