/**
 * 认证服务
 */

import type { IAuthService, LoginForm, RegisterForm, AuthResult, User } from '@/types'
import { apiService } from './api'

class AuthService implements IAuthService {
  private readonly baseUrl = '/auth'

  /**
   * 用户登录
   */
  async login(credentials: LoginForm): Promise<AuthResult> {
    try {
      const result = await apiService.post<AuthResult>(`${this.baseUrl}/login`, {
        username: credentials.username,
        password: credentials.password,
      })

      // 设置token到API服务
      if (result.token) {
        apiService.setAuthToken(result.token)
      }

      return result
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  /**
   * 用户注册
   */
  async register(registerData: RegisterForm): Promise<AuthResult> {
    try {
      const result = await apiService.post<AuthResult>(`${this.baseUrl}/register`, registerData)

      if (result.token) {
        apiService.setAuthToken(result.token)
      }

      return result
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    try {
      await apiService.post(`${this.baseUrl}/logout`)
    } catch (error) {
      console.error('Logout failed:', error)
      // 即使登出接口失败，也要清除本地token
    } finally {
      apiService.clearAuthToken()
    }
  }

  /**
   * 刷新Token
   */
  async refreshToken(): Promise<string> {
    try {
      const result = await apiService.post<{ token: string; refreshToken: string }>(`${this.baseUrl}/refresh`)
      
      if (result.token) {
        apiService.setAuthToken(result.token)
        return result.token
      }
      
      throw new Error('No token in refresh response')
    } catch (error) {
      console.error('Token refresh failed:', error)
      throw error
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      return await apiService.get<User>(`${this.baseUrl}/me`)
    } catch (error) {
      console.error('Get current user failed:', error)
      return null
    }
  }

  /**
   * 检查用户权限
   */
  checkPermission(permission: string): boolean {
    // 这里需要从store中获取用户权限信息
    // 为了避免循环依赖，这里暂时返回true，实际应该在store中实现
    return true
  }

  /**
   * 检查用户角色
   */
  hasRole(role: string): boolean {
    // 同上，需要从store中获取用户角色信息
    return true
  }

  /**
   * 发送验证码
   */
  async sendVerificationCode(email: string): Promise<void> {
    await apiService.post(`${this.baseUrl}/send-verification-code`, { email })
  }

  /**
   * 重置密码
   */
  async resetPassword(data: {
    email: string
    verificationCode: string
    newPassword: string
  }): Promise<void> {
    await apiService.post(`${this.baseUrl}/reset-password`, data)
  }

  /**
   * 修改密码
   */
  async changePassword(data: {
    currentPassword: string
    newPassword: string
  }): Promise<void> {
    await apiService.post(`${this.baseUrl}/change-password`, data)
  }

  /**
   * 验证Token有效性
   */
  async validateToken(token: string): Promise<boolean> {
    try {
      await apiService.post(`${this.baseUrl}/validate-token`, { token })
      return true
    } catch (error) {
      return false
    }
  }
}

// 创建认证服务实例
export const authService = new AuthService()

export { AuthService }
export type { IAuthService }