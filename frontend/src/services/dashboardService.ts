/**
 * Dashboard Service
 * 
 * Provides dashboard-specific API calls and data management
 */

import type { 
  DashboardStats, 
  DashboardOverview, 
  SystemStatus, 
  RecentActivity,
  SystemAlert,
  ChartData,
  ChartDataset,
  TrendDataPoint,
  DashboardWidget
} from '@/types'
import { apiService } from './api'

export interface DashboardStatsResponse {
  total_users: number
  active_users: number
  total_sessions: number
  total_traffic: number
  system_health_score: number
  // 扩展字段
  active_sessions?: number
  monthly_revenue?: number
  total_nas?: number
  active_nas?: number
  today_traffic_gb?: number
  today_logins?: number
  today_sessions?: number
  last_updated?: string
  trends: {
    sessions_trend: TrendDataPoint[]
    traffic_trend: TrendDataPoint[]
    user_activity: TrendDataPoint[]
  }
}

export interface DashboardOverviewResponse {
  stats: DashboardStatsResponse
  recent_activity: RecentActivity[]
  system_alerts: SystemAlert[]
  top_users: Array<{
    username: string
    traffic_gb: number
    sessions: number
    last_login?: string
  }>
  quick_stats: {
    online_users_now: number
    sessions_last_hour: number
    traffic_last_hour_gb: number
    failed_logins_today: number
    nas_response_time_ms: number
  }
  charts_data?: {
    sessions_trend: TrendDataPoint[]
    traffic_trend: TrendDataPoint[]
    user_activity: TrendDataPoint[]
  }
}

export interface SystemStatusResponse {
  database_status: string
  radius_status: string
  cache_status: string
  disk_usage_percent: number
  memory_usage_percent: number
  cpu_usage_percent: number
  uptime_hours: number
}

export interface TrendDataParams {
  metric: 'sessions' | 'traffic' | 'users' | 'revenue'
  days?: number
  granularity?: 'hour' | 'day' | 'week'
}

export interface TopUsersParams {
  days?: number
  metric?: 'traffic' | 'sessions' | 'duration'
  limit?: number
}

export interface AlertsParams {
  severity?: 'info' | 'warning' | 'error'
  acknowledged?: boolean
}

class DashboardService {
  private readonly baseUrl = '/dashboard'

  /**
   * Get dashboard statistics summary
   */
  async getStats(): Promise<DashboardStats> {
    try {
      const response = await apiService.get<DashboardStatsResponse>(`${this.baseUrl}/stats`)
      
      // Transform backend response to frontend format
      return {
        totalUsers: response.total_users,
        activeUsers: response.active_users,
        totalSessions: response.total_sessions,
        activeSessions: response.active_sessions,
        totalRevenue: (response.monthly_revenue ?? 0) * 12, // Estimate yearly from monthly
        monthlyRevenue: response.monthly_revenue ?? 0,
        totalDevices: response.total_nas,
        activeDevices: response.active_nas,
        totalTraffic: response.today_traffic_gb ?? 0,
        bandwidth: {
          upload: (response.today_traffic_gb ?? 0) / 2, // Mock split
          download: (response.today_traffic_gb ?? 0) / 2
        },
        systemHealth: response.system_health_score,
        todayLogins: response.today_logins,
        todaySessions: response.today_sessions,
        lastUpdated: response.last_updated
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      throw error
    }
  }

  /**
   * Get comprehensive dashboard overview
   */
  async getOverview(includeCharts: boolean = false): Promise<DashboardOverview> {
    try {
      const params = includeCharts ? { include_charts: true } : {}
      const response = await apiService.get<DashboardOverviewResponse>(
        `${this.baseUrl}/overview`,
        { params }
      )
      
      return {
        stats: await this._transformStats(response.stats),
        recentSessions: response.recent_activity,
        systemStatus: {
          status: 'healthy',
          uptime: 0,
          cpu_usage: 0,
          memory_usage: 0,
          disk_usage: 0,
          network_status: 'connected',
          last_check: new Date().toISOString()
        },
        alerts: response.system_alerts,
        recentActivity: response.recent_activity,
        systemAlerts: response.system_alerts,
        topUsers: response.top_users.map((user, index) => ({
          ...user,
          rank: index + 1
        })),
        quickStats: {
          traffic_last_hour_gb: response.quick_stats.traffic_last_hour_gb,
          failed_logins_today: response.quick_stats.failed_logins_today,
          nas_response_time_ms: response.quick_stats.nas_response_time_ms,
          onlineUsersNow: response.quick_stats.online_users_now,
          sessionsLastHour: response.quick_stats.sessions_last_hour,
          trafficLastHourGb: response.quick_stats.traffic_last_hour_gb,
          failedLoginsToday: response.quick_stats.failed_logins_today,
          nasResponseTimeMs: response.quick_stats.nas_response_time_ms
        },
        chartsData: response.charts_data
      }
    } catch (error) {
      console.error('Failed to fetch dashboard overview:', error)
      throw error
    }
  }

  /**
   * Get system status information
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await apiService.get<SystemStatusResponse>(`${this.baseUrl}/system-status`)
      
      return {
        status: response.database_status === 'connected' ? 'healthy' : 'error',
        uptime: response.uptime_hours * 3600, // Convert hours to seconds
        cpu_usage: response.cpu_usage_percent,
        memory_usage: response.memory_usage_percent,
        disk_usage: response.disk_usage_percent,
        network_status: response.radius_status,
        last_check: new Date().toISOString(),
        databaseStatus: response.database_status,
        radiusStatus: response.radius_status,
        cacheStatus: response.cache_status,
        diskUsagePercent: response.disk_usage_percent,
        memoryUsagePercent: response.memory_usage_percent,
        cpuUsagePercent: response.cpu_usage_percent,
        uptimeHours: response.uptime_hours
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error)
      throw error
    }
  }

  /**
   * Get recent system activities
   */
  async getRecentActivities(limit: number = 20, activityType?: string): Promise<{
    activities: RecentActivity[]
    total: number
    limit: number
  }> {
    try {
      const params: Record<string, unknown> = { limit }
      if (activityType) {
        params.activity_type = activityType
      }
      
      return await apiService.get(`${this.baseUrl}/recent-activities`, { params })
    } catch (error) {
      console.error('Failed to fetch recent activities:', error)
      throw error
    }
  }

  /**
   * Get system alerts
   */
  async getAlerts(params: AlertsParams = {}): Promise<{
    alerts: SystemAlert[]
    total: number
    unacknowledged_count: number
  }> {
    try {
      return await apiService.get(`${this.baseUrl}/alerts`, { params })
    } catch (error) {
      console.error('Failed to fetch system alerts:', error)
      throw error
    }
  }

  /**
   * Get trend data for charts
   */
  async getTrendData(params: TrendDataParams): Promise<ChartData> {
    try {
      const { metric, days = 30, granularity = 'day' } = params
      
      // This would call a specific trend endpoint
      const response = await apiService.get('/graphs/trend-data', {
        params: { metric, days, granularity }
      })
      
      return this._transformTrendData(response as TrendDataPoint[], metric)
    } catch (error) {
      console.error('Failed to fetch trend data:', error)
      throw error
    }
  }

  /**
   * Get top users analysis
   */
  async getTopUsers(params: TopUsersParams = {}): Promise<Array<{
    username: string
    traffic_gb: number
    sessions: number
    last_login?: string
    rank: number
  }>> {
    try {
      const { days = 7, metric = 'traffic', limit = 10 } = params
      
      const response = await apiService.get('/graphs/top-users', {
        params: { days, metric, limit }
      })
      
      return (response as { users: Array<{
        username: string
        traffic_gb: number
        sessions: number
        last_login?: string
        rank: number
      }> }).users || []
    } catch (error) {
      console.error('Failed to fetch top users:', error)
      throw error
    }
  }

  /**
   * Get real-time metrics for widgets
   */
  async getRealTimeMetrics(): Promise<{
    timestamp: string
    online_users_now: number
    sessions_last_hour: number
    traffic_last_hour_gb: number
    failed_logins_today: number
    system_load_percent: number
    memory_usage_percent: number
    disk_usage_percent: number
  }> {
    try {
      return await apiService.get('/graphs/real-time-stats')
    } catch (error) {
      console.error('Failed to fetch real-time metrics:', error)
      throw error
    }
  }

  /**
   * Acknowledge system alert
   */
  async acknowledgeAlert(alertId: number): Promise<void> {
    try {
      await apiService.post(`${this.baseUrl}/alerts/${alertId}/acknowledge`)
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
      throw error
    }
  }

  /**
   * Get dashboard widgets configuration
   */
  async getWidgetsConfig(): Promise<Array<{
    id: string
    title: string
    type: string
    position: { x: number; y: number }
    size: { width: number; height: number }
    config: Record<string, unknown>
  }>> {
    try {
      return await apiService.get('/graphs/dashboard-widgets')
    } catch (error) {
      console.error('Failed to fetch widgets config:', error)
      return []
    }
  }

  /**
   * Save dashboard widgets configuration
   */
  async saveWidgetsConfig(widgets: DashboardWidget[]): Promise<void> {
    try {
      await apiService.post('/graphs/dashboard-widgets', { widgets })
    } catch (error) {
      console.error('Failed to save widgets config:', error)
      throw error
    }
  }

  /**
   * Export dashboard data
   */
  async exportData(format: 'csv' | 'json' | 'pdf' = 'json'): Promise<Blob> {
    try {
      const response = await apiService.get(`${this.baseUrl}/export`, {
        params: { format },
        responseType: 'blob'
      })
      
      return response as Blob
    } catch (error) {
      console.error('Failed to export dashboard data:', error)
      throw error
    }
  }

  /**
   * Transform backend stats to frontend format
   */
  private async _transformStats(backendStats: DashboardStatsResponse): Promise<DashboardStats> {
    return {
      totalUsers: backendStats.total_users,
      activeUsers: backendStats.active_users,
      totalSessions: backendStats.total_sessions,
      activeSessions: backendStats.active_sessions,
      totalRevenue: (backendStats.monthly_revenue ?? 0) * 12,
      monthlyRevenue: backendStats.monthly_revenue ?? 0,
      totalDevices: backendStats.total_nas,
      activeDevices: backendStats.active_nas,
      totalTraffic: backendStats.today_traffic_gb ?? 0,
      bandwidth: {
        upload: (backendStats.today_traffic_gb ?? 0) / 2,
        download: (backendStats.today_traffic_gb ?? 0) / 2
      },
      systemHealth: backendStats.system_health_score,
      todayLogins: backendStats.today_logins,
      todaySessions: backendStats.today_sessions,
      lastUpdated: backendStats.last_updated
    }
  }

  /**
   * Transform trend data for chart consumption
   */
  private _transformTrendData(data: TrendDataPoint[], metric: string): ChartData {
    if (!data || !Array.isArray(data)) {
      return { labels: [], datasets: [], categories: [], series: [] }
    }

    const categories = data.map((item: TrendDataPoint) => item.date || item.timestamp).filter(Boolean) as string[]
    
    const series: ChartDataset = {
      label: this._getSeriesName(metric),
      data: data.map((item: TrendDataPoint) => {
        switch (metric) {
          case 'sessions':
            return item.session_count || item.value || 0
          case 'traffic':
            return item.traffic_gb || item.value || 0
          case 'users':
            return item.user_count || item.value || 0
          case 'revenue':
            return item.revenue || item.value || 0
          default:
            return item.value || 0
        }
      })
    }

    return { labels: categories, datasets: [series], categories, series: [series] }
  }

  /**
   * Get display name for chart series
   */
  private _getSeriesName(metric: string): string {
    const names = {
      sessions: '会话数',
      traffic: '流量 (GB)',
      users: '用户数',
      revenue: '收入'
    }
    return names[metric as keyof typeof names] || metric
  }

  /**
   * Format number for display
   */
  formatNumber(value: number): string {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`
    }
    return value.toString()
  }

  /**
   * Format bytes for display
   */
  formatBytes(bytes: number): string {
    if (bytes >= 1024 ** 4) {
      return `${(bytes / (1024 ** 4)).toFixed(2)} TB`
    } else if (bytes >= 1024 ** 3) {
      return `${(bytes / (1024 ** 3)).toFixed(2)} GB`
    } else if (bytes >= 1024 ** 2) {
      return `${(bytes / (1024 ** 2)).toFixed(2)} MB`
    } else if (bytes >= 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`
    }
    return `${bytes} B`
  }

  /**
   * Format duration for display
   */
  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m`
    }
    return `${seconds}s`
  }
}

// Create and export dashboard service instance
export const dashboardService = new DashboardService()

export { DashboardService }