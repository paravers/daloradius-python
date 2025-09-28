/**
 * API 相关类型定义
 */

// 基础 API 响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 分页查询参数
export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

// 查询参数基类
export interface QueryParams extends PaginationParams {
  search?: string
  filters?: Record<string, any>
}

// HTTP 请求配置
export interface RequestConfig {
  headers?: Record<string, string>
  timeout?: number
  withCredentials?: boolean
  params?: any
  responseType?: 'json' | 'text' | 'blob' | 'arraybuffer' | 'document' | 'stream'
  data?: any
}

// API 服务接口
export interface IApiService {
  get<T>(url: string, config?: RequestConfig): Promise<T>
  post<T>(url: string, data?: any, config?: RequestConfig): Promise<T>
  put<T>(url: string, data?: any, config?: RequestConfig): Promise<T>
  patch<T>(url: string, data?: any, config?: RequestConfig): Promise<T>
  delete<T>(url: string, config?: RequestConfig): Promise<T>
  setAuthToken(token: string): void
  clearAuthToken(): void
}

// 请求拦截器
export interface RequestInterceptor {
  onFulfilled?: (config: any) => any
  onRejected?: (error: any) => any
}

// 响应拦截器
export interface ResponseInterceptor {
  onFulfilled?: (response: any) => any
  onRejected?: (error: any) => any
}