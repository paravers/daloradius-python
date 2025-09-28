/**
 * 用户管理服务
 */

import type { 
  RadiusUser, 
  CreateUserForm, 
  UpdateUserForm, 
  PaginatedResponse, 
  QueryParams 
} from '@/types'
import { apiService } from './api'

class UserService {
  private readonly baseUrl = '/users'

  /**
   * 获取用户列表
   */
  async getUsers(params?: QueryParams): Promise<PaginatedResponse<RadiusUser>> {
    return await apiService.get<PaginatedResponse<RadiusUser>>(this.baseUrl, {
      params
    })
  }

  /**
   * 获取用户详情
   */
  async getUser(id: number): Promise<RadiusUser> {
    return await apiService.get<RadiusUser>(`${this.baseUrl}/${id}`)
  }

  /**
   * 创建用户
   */
  async createUser(user: CreateUserForm): Promise<RadiusUser> {
    return await apiService.post<RadiusUser>(this.baseUrl, user)
  }

  /**
   * 更新用户
   */
  async updateUser(id: number, user: UpdateUserForm): Promise<RadiusUser> {
    return await apiService.put<RadiusUser>(`${this.baseUrl}/${id}`, user)
  }

  /**
   * 删除用户
   */
  async deleteUser(id: number): Promise<void> {
    await apiService.delete(`${this.baseUrl}/${id}`)
  }

  /**
   * 批量删除用户
   */
  async batchDeleteUsers(ids: number[]): Promise<void> {
    await apiService.delete(`${this.baseUrl}/batch`, {
      data: { ids }
    })
  }

  /**
   * 重置用户密码
   */
  async resetPassword(id: number, newPassword: string): Promise<void> {
    await apiService.post(`${this.baseUrl}/${id}/reset-password`, {
      password: newPassword
    })
  }

  /**
   * 启用/禁用用户
   */
  async toggleUserStatus(id: number, status: 'active' | 'inactive'): Promise<void> {
    await apiService.patch(`${this.baseUrl}/${id}/status`, {
      status
    })
  }

  /**
   * 获取用户会话记录
   */
  async getUserSessions(userId: number, params?: QueryParams) {
    return await apiService.get(`${this.baseUrl}/${userId}/sessions`, {
      params
    })
  }

  /**
   * 获取用户账单记录
   */
  async getUserBilling(userId: number, params?: QueryParams) {
    return await apiService.get(`${this.baseUrl}/${userId}/billing`, {
      params
    })
  }

  /**
   * 导出用户数据
   */
  async exportUsers(params?: QueryParams): Promise<Blob> {
    return await apiService.get(`${this.baseUrl}/export`, {
      params,
      responseType: 'blob'
    })
  }

  /**
   * 批量导入用户
   */
  async importUsers(file: File): Promise<{
    success: number
    failed: number
    errors: string[]
  }> {
    const formData = new FormData()
    formData.append('file', file)

    return await apiService.post(`${this.baseUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

export const userService = new UserService()
export { UserService }