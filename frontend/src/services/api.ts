/**
 * HTTP API 客户端服务
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { IApiService, RequestConfig, RequestInterceptor, ResponseInterceptor } from '@/types'
import { useAuthStore } from '@/stores'
import { message } from 'ant-design-vue'

class ApiService implements IApiService {
  private instance: AxiosInstance
  private baseURL: string
  private timeout: number = 30000

  constructor(baseURL?: string) {
    this.baseURL = baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    this.instance = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  /**
   * 设置请求和响应拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId()

        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          params: config.params,
          data: config.data,
        })

        return config
      },
      (error) => {
        console.error('[API Request Error]', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          data: response.data,
        })

        return response
      },
      async (error) => {
        console.error('[API Response Error]', error)

        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 401:
              // Token过期或无效，尝试刷新token
              await this.handleUnauthorized()
              break
            case 403:
              message.error('无权限访问该资源')
              break
            case 404:
              message.error('请求的资源不存在')
              break
            case 422:
              // 表单验证错误
              this.handleValidationError(data)
              break
            case 500:
              message.error('服务器内部错误，请稍后重试')
              break
            default:
              message.error(data?.message || '网络请求失败')
          }
        } else if (error.request) {
          message.error('网络连接失败，请检查网络设置')
        } else {
          message.error('请求配置错误')
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * 处理401未授权错误
   */
  private async handleUnauthorized(): Promise<void> {
    const authStore = useAuthStore()
    
    if (authStore.refreshToken) {
      try {
        await authStore.refreshTokenAction()
        message.success('登录状态已续期')
      } catch (error) {
        console.error('Token refresh failed:', error)
        await authStore.logout()
        // 跳转到登录页
        window.location.href = '/login'
      }
    } else {
      await authStore.logout()
      window.location.href = '/login'
    }
  }

  /**
   * 处理表单验证错误
   */
  private handleValidationError(data: any): void {
    if (data?.detail && Array.isArray(data.detail)) {
      data.detail.forEach((error: any) => {
        message.error(`${error.loc?.join('.')} ${error.msg}`)
      })
    } else if (data?.message) {
      message.error(data.message)
    }
  }

  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return Math.random().toString(36).substring(2, 15)
  }

  /**
   * GET 请求
   */
  async get<T>(url: string, config?: RequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, this.mergeConfig(config))
    return response.data
  }

  /**
   * POST 请求
   */
  async post<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.instance.post<T>(url, data, this.mergeConfig(config))
    return response.data
  }

  /**
   * PUT 请求
   */
  async put<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.instance.put<T>(url, data, this.mergeConfig(config))
    return response.data
  }

  /**
   * DELETE 请求
   */
  async delete<T>(url: string, config?: RequestConfig): Promise<T> {
    const response = await this.instance.delete<T>(url, this.mergeConfig(config))
    return response.data
  }

  /**
   * PATCH 请求
   */
  async patch<T>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    const response = await this.instance.patch<T>(url, data, this.mergeConfig(config))
    return response.data
  }

  /**
   * 设置认证token
   */
  setAuthToken(token: string): void {
    this.instance.defaults.headers.common.Authorization = `Bearer ${token}`
  }

  /**
   * 清除认证token
   */
  clearAuthToken(): void {
    delete this.instance.defaults.headers.common.Authorization
  }

  /**
   * 添加请求拦截器
   */
  addRequestInterceptor(interceptor: RequestInterceptor): number {
    return this.instance.interceptors.request.use(
      interceptor.onFulfilled,
      interceptor.onRejected
    )
  }

  /**
   * 添加响应拦截器
   */
  addResponseInterceptor(interceptor: ResponseInterceptor): number {
    return this.instance.interceptors.response.use(
      interceptor.onFulfilled,
      interceptor.onRejected
    )
  }

  /**
   * 合并请求配置
   */
  private mergeConfig(config?: RequestConfig): AxiosRequestConfig {
    return {
      timeout: this.timeout,
      ...config,
      headers: {
        ...this.instance.defaults.headers.common,
        ...config?.headers,
      },
    }
  }
}

// 创建全局API服务实例
export const apiService = new ApiService()

// 导出类型和实例
export { ApiService }
export type { IApiService }