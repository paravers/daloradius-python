/**
 * 认证状态管理
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User, AuthState, LoginForm, RegisterForm, AuthResult } from '@/types'
import { authService } from '@/services'
import { message } from 'ant-design-vue'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const permissions = ref<string[]>([])
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRoles = computed(() => user.value?.roles || [])
  const userName = computed(() => user.value?.fullName || user.value?.username || '')

  // 初始化，从localStorage恢复状态
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUser = localStorage.getItem('user_info')
    const savedPermissions = localStorage.getItem('user_permissions')

    if (savedToken) {
      token.value = savedToken
    }
    if (savedRefreshToken) {
      refreshToken.value = savedRefreshToken
    }
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('Failed to parse saved user info:', error)
      }
    }
    if (savedPermissions) {
      try {
        permissions.value = JSON.parse(savedPermissions)
      } catch (error) {
        console.error('Failed to parse saved permissions:', error)
      }
    }
  }

  // 保存认证状态到localStorage
  const saveAuthState = (authResult: AuthResult) => {
    token.value = authResult.token
    refreshToken.value = authResult.refreshToken
    user.value = authResult.user
    permissions.value = authResult.permissions

    localStorage.setItem('auth_token', authResult.token)
    localStorage.setItem('refresh_token', authResult.refreshToken)
    localStorage.setItem('user_info', JSON.stringify(authResult.user))
    localStorage.setItem('user_permissions', JSON.stringify(authResult.permissions))
  }

  // 清除认证状态
  const clearAuthState = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    permissions.value = []

    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    localStorage.removeItem('user_permissions')
  }

  // 登录
  const login = async (credentials: LoginForm): Promise<void> => {
    try {
      isLoading.value = true
      const authResult = await authService.login(credentials)
      saveAuthState(authResult)
      message.success('登录成功')
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterForm): Promise<void> => {
    try {
      isLoading.value = true
      const authResult = await authService.register(registerData)
      saveAuthState(authResult)
      message.success('注册成功')
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async (): Promise<void> => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      clearAuthState()
      message.success('已退出登录')
    }
  }

  // 刷新Token
  const refreshTokenAction = async (): Promise<void> => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }
      
      const newToken = await authService.refreshToken()
      token.value = newToken
      localStorage.setItem('auth_token', newToken)
    } catch (error) {
      console.error('Token refresh failed:', error)
      await logout()
      throw error
    }
  }

  // 检查权限
  const hasPermission = (permission: string): boolean => {
    return permissions.value.includes(permission) || permissions.value.includes('*')
  }

  // 检查角色
  const hasRole = (role: string): boolean => {
    return userRoles.value.includes(role) || userRoles.value.includes('admin')
  }

  // 检查多个权限（需要全部具备）
  const hasAllPermissions = (requiredPermissions: string[]): boolean => {
    return requiredPermissions.every(permission => hasPermission(permission))
  }

  // 检查多个权限（只需具备其中一个）
  const hasAnyPermission = (requiredPermissions: string[]): boolean => {
    return requiredPermissions.some(permission => hasPermission(permission))
  }

  // 获取当前用户信息
  const fetchCurrentUser = async (): Promise<void> => {
    try {
      const currentUser = await authService.getCurrentUser()
      if (currentUser) {
        user.value = currentUser
        localStorage.setItem('user_info', JSON.stringify(currentUser))
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error)
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    permissions,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    userRoles,
    userName,
    
    // 方法
    initializeAuth,
    login,
    register,
    logout,
    refreshTokenAction,
    hasPermission,
    hasRole,
    hasAllPermissions,
    hasAnyPermission,
    fetchCurrentUser,
  }
})
