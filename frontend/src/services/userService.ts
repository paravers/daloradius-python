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
  UserPermission
} from '@/types'

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
  getUserActivities(id: string, params?: any): Promise<UserActivity[]>
  
  // 角色权限
  getUserRoles(id: string): Promise<UserRole[]>
  updateUserRoles(id: string, roleIds: string[]): Promise<void>
  getUserPermissions(id: string): Promise<UserPermission[]>
}

/**
 * 模拟用户服务实现
 * 实际项目中这里应该调用真实的 API
 */
class UserService implements IUserService {
  // 模拟数据
  private mockUsers: User[] = [
    {
      id: '1',
      username: 'admin',
      email: 'admin@example.com',
      fullName: '系统管理员',
      avatar: 'https://via.placeholder.com/40',
      status: 'active',
      roles: ['admin', 'user'],
      permissions: ['*'],
      lastLoginAt: '2024-01-20 10:30:00',
      lastLoginIp: '192.168.1.100',
      loginCount: 156,
      failedLoginCount: 0,
      emailVerified: true,
      emailVerifiedAt: '2024-01-01 09:00:00',
      phoneNumber: '+86 138****8888',
      phoneVerified: true,
      twoFactorEnabled: true,
      createdAt: '2024-01-01 09:00:00',
      updatedAt: '2024-01-20 10:30:00'
    },
    {
      id: '2',
      username: 'operator1',
      email: 'operator1@example.com',
      fullName: '操作员一号',
      status: 'active',
      roles: ['operator'],
      lastLoginAt: '2024-01-19 16:45:00',
      lastLoginIp: '192.168.1.101',
      loginCount: 89,
      failedLoginCount: 1,
      emailVerified: true,
      twoFactorEnabled: false,
      createdAt: '2024-01-02 10:15:00',
      updatedAt: '2024-01-19 16:45:00'
    },
    {
      id: '3',
      username: 'user001',
      email: 'user001@example.com',
      fullName: '普通用户',
      status: 'inactive',
      roles: ['user'],
      lastLoginAt: '2024-01-15 14:20:00',
      loginCount: 23,
      failedLoginCount: 0,
      emailVerified: false,
      twoFactorEnabled: false,
      createdAt: '2024-01-10 11:30:00',
      updatedAt: '2024-01-15 14:20:00'
    }
  ]

  private delay(ms: number = 500): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async getUsers(params?: UserQueryParams): Promise<UserListResponse> {
    await this.delay()
    
    let filteredUsers = [...this.mockUsers]
    
    // 应用筛选条件
    if (params) {
      const { username, email, status, page = 1, pageSize = 10 } = params
      
      if (username) {
        filteredUsers = filteredUsers.filter(user => 
          user.username.toLowerCase().includes(username.toLowerCase())
        )
      }
      
      if (email) {
        filteredUsers = filteredUsers.filter(user => 
          user.email.toLowerCase().includes(email.toLowerCase())
        )
      }
      
      if (status) {
        filteredUsers = filteredUsers.filter(user => user.status === status)
      }
      
      // 分页
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      filteredUsers = filteredUsers.slice(startIndex, endIndex)
    }
    
    return {
      data: filteredUsers,
      total: this.mockUsers.length,
      page: params?.page || 1,
      pageSize: params?.pageSize || 10
    }
  }

  async getUser(id: string): Promise<User> {
    await this.delay()
    
    const user = this.mockUsers.find(u => u.id === id)
    if (!user) {
      throw new Error('用户不存在')
    }
    
    return user
  }

  async createUser(data: CreateUserRequest): Promise<User> {
    await this.delay()
    
    // 检查用户名和邮箱是否已存在
    if (this.mockUsers.some(u => u.username === data.username)) {
      throw new Error('用户名已存在')
    }
    
    if (this.mockUsers.some(u => u.email === data.email)) {
      throw new Error('邮箱已存在')
    }
    
    const newUser: User = {
      id: String(this.mockUsers.length + 1),
      username: data.username,
      email: data.email,
      fullName: data.fullName,
      status: data.status || 'active',
      roles: data.roles,
      emailVerified: false,
      twoFactorEnabled: false,
      loginCount: 0,
      failedLoginCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockUsers.push(newUser)
    return newUser
  }

  async updateUser(id: string, data: UpdateUserRequest): Promise<User> {
    await this.delay()
    
    const userIndex = this.mockUsers.findIndex(u => u.id === id)
    if (userIndex === -1) {
      throw new Error('用户不存在')
    }
    
    // 检查邮箱是否已被其他用户使用
    if (data.email && this.mockUsers.some(u => u.id !== id && u.email === data.email)) {
      throw new Error('邮箱已被其他用户使用')
    }
    
    const updatedUser = {
      ...this.mockUsers[userIndex],
      ...data,
      updatedAt: new Date().toISOString()
    }
    
    this.mockUsers[userIndex] = updatedUser
    return updatedUser
  }

  async deleteUser(id: string): Promise<void> {
    await this.delay()
    
    const userIndex = this.mockUsers.findIndex(u => u.id === id)
    if (userIndex === -1) {
      throw new Error('用户不存在')
    }
    
    // 不能删除管理员用户
    if (this.mockUsers[userIndex].username === 'admin') {
      throw new Error('不能删除管理员用户')
    }
    
    this.mockUsers.splice(userIndex, 1)
  }

  async batchDeleteUsers(ids: string[]): Promise<void> {
    await this.delay()
    
    // 检查是否包含管理员
    const adminIds = ids.filter(id => {
      const user = this.mockUsers.find(u => u.id === id)
      return user?.username === 'admin'
    })
    
    if (adminIds.length > 0) {
      throw new Error('选中的用户包含管理员，无法删除')
    }
    
    // 删除用户
    this.mockUsers = this.mockUsers.filter(user => !ids.includes(user.id))
  }

  async batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void> {
    await this.delay()
    
    ids.forEach(id => {
      const userIndex = this.mockUsers.findIndex(u => u.id === id)
      if (userIndex !== -1) {
        this.mockUsers[userIndex] = {
          ...this.mockUsers[userIndex],
          ...data,
          updatedAt: new Date().toISOString()
        }
      }
    })
  }

  async activateUser(id: string): Promise<void> {
    await this.updateUser(id, { status: 'active' })
  }

  async deactivateUser(id: string): Promise<void> {
    await this.updateUser(id, { status: 'inactive' })
  }

  async suspendUser(id: string): Promise<void> {
    await this.updateUser(id, { status: 'suspended' })
  }

  async changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void> {
    await this.delay()
    
    // 模拟密码验证
    console.log('更改密码:', id, data)
  }

  async resetPassword(id: string): Promise<void> {
    await this.delay()
    
    // 模拟重置密码
    console.log('重置密码:', id)
  }

  async getUserProfile(id: string): Promise<UserProfile> {
    await this.delay()
    
    const user = await this.getUser(id)
    return {
      id: user.id,
      username: user.username,
      email: user.email,
      fullName: user.fullName,
      avatar: user.avatar,
      phoneNumber: user.phoneNumber,
      emailVerified: user.emailVerified,
      phoneVerified: user.phoneVerified || false,
      twoFactorEnabled: user.twoFactorEnabled,
      preferences: {
        language: 'zh-CN',
        timezone: 'Asia/Shanghai',
        dateFormat: 'YYYY-MM-DD',
        theme: 'light',
        notifications: {
          email: true,
          push: false,
          sms: false
        }
      },
      lastLoginAt: user.lastLoginAt,
      createdAt: user.createdAt
    }
  }

  async updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile> {
    await this.delay()
    
    // 更新用户基本信息
    await this.updateUser(id, {
      email: data.email,
      fullName: data.fullName,
      phoneNumber: data.phoneNumber,
      avatar: data.avatar
    })
    
    return this.getUserProfile(id)
  }

  async getUserSessions(id: string): Promise<UserSession[]> {
    await this.delay()
    
    // 模拟会话数据
    return []
  }

  async terminateUserSession(id: string, sessionId: string): Promise<void> {
    await this.delay()
    console.log('终止会话:', id, sessionId)
  }

  async getUserActivities(id: string, params?: any): Promise<UserActivity[]> {
    await this.delay()
    
    // 模拟活动数据
    return []
  }

  async getUserRoles(id: string): Promise<UserRole[]> {
    await this.delay()
    
    const user = await this.getUser(id)
    // 模拟角色数据
    return user.roles.map(role => ({
      id: role,
      name: role,
      displayName: role === 'admin' ? '管理员' : role === 'operator' ? '操作员' : '用户',
      permissions: role === 'admin' ? ['*'] : [],
      isSystem: true,
      createdAt: '2024-01-01 00:00:00',
      updatedAt: '2024-01-01 00:00:00'
    }))
  }

  async updateUserRoles(id: string, roleIds: string[]): Promise<void> {
    await this.updateUser(id, { roles: roleIds })
  }

  async getUserPermissions(id: string): Promise<UserPermission[]> {
    await this.delay()
    
    // 模拟权限数据
    return []
  }
}

// 导出服务实例
export const userService = new UserService()
export default userService