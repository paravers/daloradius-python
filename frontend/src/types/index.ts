/**
 * 导出所有类型定义
 */

// 通用类型
export * from './common'

// 业务类型
export * from './user'

// API 相关
export * from './api'

// 认证相关
export * from './auth'

// 业务相关
export * from './business'

// 组件相关
export * from './components'

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
export interface RouteMeta extends Record<string | number | symbol, any> {
  title: string
  icon?: any
  requiresAuth?: boolean
  roles?: string[]
  permissions?: string[]
  hidden?: boolean
  keepAlive?: boolean
  badge?: {
    count: number
    color?: string
  }
}