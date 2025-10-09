/**
 * 导出所有类型定义
 */

// 通用类型
export * from './common'

// 核心业务类型 - 按需导入避免冲突
export * from './user'
export * from './billing'
export * from './accounting'
export * from './hotspot'
export * from './radius'
export * from './batch'
export * from './device'
export * from './group'
export * from './report'
export * from './config'

// API 相关
export * from './api'

// 仪表板相关类型
export interface DashboardStats {
  totalUsers: number
  activeUsers: number
  totalSessions: number
  totalTraffic: number
  systemHealth?: number
  // 扩展字段以匹配实际使用
  activeSessions?: number
  totalRevenue?: number
  monthlyRevenue?: number
  totalDevices?: number
  activeDevices?: number
  dailyTraffic?: {
    upload: number
    download: number
  }
  bandwidth?: {
    upload: number
    download: number
  }
  todayLogins?: number
  todaySessions?: number
  lastUpdated?: string
}

export interface DashboardOverview {
  stats: DashboardStats
  recentSessions: RecentActivity[]
  systemStatus: SystemStatus
  alerts: SystemAlert[]
  recentActivity?: RecentActivity[]
  systemAlerts?: SystemAlert[]
  topUsers?: Array<{
    username: string
    traffic_gb: number
    sessions: number
    last_login?: string
    rank: number
  }>
  quickStats?: {
    traffic_last_hour_gb: number
    failed_logins_today: number
    nas_response_time_ms: number
    onlineUsersNow?: number
    sessionsLastHour?: number
    trafficLastHourGb?: number
    failedLoginsToday?: number
    nasResponseTimeMs?: number
  }
  chartsData?: {
    sessions_trend: TrendDataPoint[]
    traffic_trend: TrendDataPoint[]
    user_activity: TrendDataPoint[]
  }
}

export interface SystemStatus {
  status: 'healthy' | 'warning' | 'error'
  uptime: number
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_status: string
  last_check: string
  databaseStatus?: string
  radiusStatus?: string
  cacheStatus?: string
  diskUsagePercent?: number
  memoryUsagePercent?: number
  cpuUsagePercent?: number
  uptimeHours?: number
}

export interface RecentActivity {
  id: string
  type: 'user_login' | 'user_logout' | 'system_event' | 'admin_action'
  message: string
  timestamp: string
  user?: string
  details?: Record<string, unknown>
}

export interface SystemAlert {
  id: string
  level: 'info' | 'warning' | 'error' | 'critical'
  title: string
  message: string
  timestamp: string
  resolved?: boolean
  source?: string
}

export interface QuickStats {
  label: string
  value: number | string
  change?: number
  trend?: 'up' | 'down' | 'stable'
  icon?: string
}

// 图表数据类型
export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
  // 扩展字段支持不同的图表库
  categories?: string[]
  series?: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  fill?: boolean
}

// 趋势数据类型
export interface TrendDataPoint {
  date: string
  timestamp?: string
  value: number
  label?: string
  // 扩展字段
  session_count?: number
  traffic_gb?: number
  user_count?: number
  revenue?: number
}

// API响应类型
export interface DashboardStatsResponse {
  stats: DashboardStats
  trends: {
    sessions_trend: TrendDataPoint[]
    traffic_trend: TrendDataPoint[]
    user_activity: TrendDataPoint[]
  }
}

export interface DashboardOverviewResponse {
  overview: DashboardOverview
  widgets: DashboardWidget[]
}

export interface DashboardWidget {
  id: string
  type: string
  title: string
  config: Record<string, unknown>
  position: { x: number; y: number; w: number; h: number }
}

export interface SystemStatusResponse {
  status: SystemStatus
  services: ServiceStatus[]
}

export interface ServiceStatus {
  name: string
  status: 'running' | 'stopped' | 'error'
  uptime?: number
  memory_usage?: number
  cpu_usage?: number
}

// API参数类型
export interface TrendDataParams {
  metric: string
  period: string
  start_date?: string
  end_date?: string
}

export interface TopUsersParams {
  limit: number
  period?: string
  sort_by?: string
}

export interface AlertsParams {
  level?: string
  resolved?: boolean
  limit?: number
}

// 全局类型定义
export interface GlobalConfig {
  title: string
  version: string
  apiBaseUrl: string
  theme: 'light' | 'dark'
  locale: string
  timezone: string
}

// 环境配置
export interface EnvironmentConfig {
  NODE_ENV: string
  VITE_API_BASE_URL: string
  VITE_APP_TITLE: string
  VITE_APP_VERSION: string
}

// 应用状态
export interface AppState {
  loading: boolean
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  locale: string
  breadcrumbs: Array<{
    title: string
    path?: string
  }>
}

// 路由元信息
export interface RouteMeta extends Record<string | number | symbol, unknown> {
  requiresAuth?: boolean
  icon?: string | object
  roles?: string[]
  permissions?: string[]
}