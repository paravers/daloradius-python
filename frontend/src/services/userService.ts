import type {
  User,
  CreateUserRequest,
  UpdateUserRequest,
  UserQueryParams,
  UserListResponse,
  BatchUserUpdateRequest,
  UserProfile,
  UserSession,
  UserActivity,
  UserRole,
  UserPermission,
} from '@/types'
import { apiService } from './api'

/**
 * 用户服务接口
 */
export interface IUserService {
  // 用户 CRUD 操作
  getUsers(params?: UserQueryParams): Promise<UserListResponse>
  getUser(id: string): Promise<User>
  createUser(data: CreateUserRequest): Promise<User>
  updateUser(id: string, data: UpdateUserRequest): Promise<User>
  deleteUser(id: string): Promise<void>

  // 批量操作
  batchDeleteUsers(ids: string[]): Promise<void>
  batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>

  // 用户状态管理
  activateUser(id: string): Promise<void>
  deactivateUser(id: string): Promise<void>
  suspendUser(id: string): Promise<void>

  // 密码相关
  changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void>
  resetPassword(id: string): Promise<void>

  // 用户资料
  getUserProfile(id: string): Promise<UserProfile>
  updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>

  // 用户会话
  getUserSessions(id: string): Promise<UserSession[]>
  terminateUserSession(id: string, sessionId: string): Promise<void>

  // 用户活动
  getUserActivities(id: string, params?: Record<string, unknown>): Promise<UserActivity[]>

  // 角色权限
  getUserRoles(id: string): Promise<UserRole[]>
  updateUserRoles(id: string, roleIds: string[]): Promise<void>
  getUserPermissions(id: string): Promise<UserPermission[]>
}

/**
 * 用户服务实现
 */
class UserService implements IUserService {
  // 用户 CRUD 操作
  async getUsers(params?: UserQueryParams): Promise<UserListResponse> {
    return await apiService.get<UserListResponse>('/api/v1/users', { params })
  }

  async getUser(id: string): Promise<User> {
    return await apiService.get<User>(`/api/v1/users/${id}`)
  }

  async createUser(data: CreateUserRequest): Promise<User> {
    return await apiService.post<User>('/api/v1/users', data)
  }

  async updateUser(id: string, data: UpdateUserRequest): Promise<User> {
    return await apiService.put<User>(`/api/v1/users/${id}`, data)
  }

  async deleteUser(id: string): Promise<void> {
    await apiService.delete(`/api/v1/users/${id}`)
  }

  // 批量操作
  async batchDeleteUsers(ids: string[]): Promise<void> {
    await apiService.post('/api/v1/users/batch/delete', { ids })
  }

  async batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void> {
    await apiService.post('/api/v1/users/batch/update', { ids, ...data })
  }

  // 用户状态管理
  async activateUser(id: string): Promise<void> {
    await apiService.post(`/api/v1/users/${id}/activate`)
  }

  async deactivateUser(id: string): Promise<void> {
    await apiService.post(`/api/v1/users/${id}/deactivate`)
  }

  async suspendUser(id: string): Promise<void> {
    await apiService.post(`/api/v1/users/${id}/suspend`)
  }

  // 密码相关
  async changePassword(
    id: string,
    data: { currentPassword: string; newPassword: string },
  ): Promise<void> {
    await apiService.post(`/api/v1/users/${id}/change-password`, data)
  }

  async resetPassword(id: string): Promise<void> {
    await apiService.post(`/api/v1/users/${id}/reset-password`)
  }

  // 用户资料
  async getUserProfile(id: string): Promise<UserProfile> {
    return await apiService.get<UserProfile>(`/api/v1/users/${id}/profile`)
  }

  async updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile> {
    return await apiService.put<UserProfile>(`/api/v1/users/${id}/profile`, data)
  }

  // 用户会话
  async getUserSessions(id: string): Promise<UserSession[]> {
    return await apiService.get<UserSession[]>(`/api/v1/users/${id}/sessions`)
  }

  async terminateUserSession(id: string, sessionId: string): Promise<void> {
    await apiService.delete(`/api/v1/users/${id}/sessions/${sessionId}`)
  }

  // 用户活动
  async getUserActivities(id: string, params?: Record<string, unknown>): Promise<UserActivity[]> {
    return await apiService.get<UserActivity[]>(`/api/v1/users/${id}/activities`, { params })
  }

  // 角色权限
  async getUserRoles(id: string): Promise<UserRole[]> {
    return await apiService.get<UserRole[]>(`/api/v1/users/${id}/roles`)
  }

  async updateUserRoles(id: string, roleIds: string[]): Promise<void> {
    await apiService.put(`/api/v1/users/${id}/roles`, { roleIds })
  }

  async getUserPermissions(id: string): Promise<UserPermission[]> {
    return await apiService.get<UserPermission[]>(`/api/v1/users/${id}/permissions`)
  }
}

// 导出单例实例
export const userService = new UserService()
