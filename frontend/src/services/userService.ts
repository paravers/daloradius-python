import type {import type {

  User,  User,

  CreateUserRequest,  CreateUserRequest,

  UpdateUserRequest,  UpdateUserRequest,

  UserQueryParams,  UserQueryParams,

  UserListResponse,  UserListResponse,

  BatchUserUpdateRequest,  BatchUserUpdateRequest,

  UserProfile,  UserProfile,

  UserSession,  UserSession,

  UserActivity,  UserActivity,

  UserRole,  UserRole,

  UserPermission  UserPermission

} from '@/types'} from '@/types'

import { ApiService } from './api'import { ApiService } from './api'



/**/**

 * 用户服务接口 * 用户服务接口

 */ */

export interface IUserService {export interface IUserService {

  // 用户 CRUD 操作  // 用户 CRUD 操作

  getUsers(params?: UserQueryParams): Promise<UserListResponse>  getUsers(params?: UserQueryParams): Promise<UserListResponse>

  getUser(id: string): Promise<User>  getUser(id: string): Promise<User>

  createUser(data: CreateUserRequest): Promise<User>  createUser(data: CreateUserRequest): Promise<User>

  updateUser(id: string, data: UpdateUserRequest): Promise<User>  updateUser(id: string, data: UpdateUserRequest): Promise<User>

  deleteUser(id: string): Promise<void>  deleteUser(id: string): Promise<void>

    

  // 批量操作  // 批量操作

  batchDeleteUsers(ids: string[]): Promise<void>  batchDeleteUsers(ids: string[]): Promise<void>

  batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>  batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>

    

  // 用户状态管理  // 用户状态管理

  activateUser(id: string): Promise<void>  activateUser(id: string): Promise<void>

  deactivateUser(id: string): Promise<void>  deactivateUser(id: string): Promise<void>

  suspendUser(id: string): Promise<void>  suspendUser(id: string): Promise<void>

    

  // 密码相关  // 密码相关

  changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void>  changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void>

  resetPassword(id: string): Promise<void>  resetPassword(id: string): Promise<void>

    

  // 用户资料  // 用户资料

  getUserProfile(id: string): Promise<UserProfile>  getUserProfile(id: string): Promise<UserProfile>

  updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>  updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>

    

  // 用户会话  // 用户会话

  getUserSessions(id: string): Promise<UserSession[]>  getUserSessions(id: string): Promise<UserSession[]>

  terminateUserSession(id: string, sessionId: string): Promise<void>  terminateUserSession(id: string, sessionId: string): Promise<void>

    

  // 用户活动  // 用户活动

  getUserActivities(id: string, params?: any): Promise<UserActivity[]>  getUserActivities(id: string, params?: any): Promise<UserActivity[]>

    

  // 角色权限  // 角色权限

  getUserRoles(id: string): Promise<UserRole[]>  getUserRoles(id: string): Promise<UserRole[]>

  updateUserRoles(id: string, roleIds: string[]): Promise<void>  updateUserRoles(id: string, roleIds: string[]): Promise<void>

  getUserPermissions(id: string): Promise<UserPermission[]>  getUserPermissions(id: string): Promise<UserPermission[]>

}}



/**/**

 * 用户服务实现 - 连接后端API * 用户服务实现 - 连接后端API

 */ */

class UserService implements IUserService {
    getUsers(params?: UserQueryParams): Promise<UserListResponse>
    getUsers(params?: UserQueryParams): Promise<UserListResponse>
    getUsers(params?: unknown): Promise<UserListResponse> {
        throw new Error('Method not implemented.')
    }
    getUser(id: string): Promise<User>
    getUser(id: string): Promise<User>
    getUser(id: unknown): Promise<User> {
        throw new Error('Method not implemented.')
    }
    createUser(data: CreateUserRequest): Promise<User>
    createUser(data: CreateUserRequest): Promise<User>
    createUser(data: unknown): Promise<User> {
        throw new Error('Method not implemented.')
    }
    updateUser(id: string, data: UpdateUserRequest): Promise<User>
    updateUser(id: string, data: UpdateUserRequest): Promise<User>
    updateUser(id: unknown, data: unknown): Promise<User> {
        throw new Error('Method not implemented.')
    }
    deleteUser(id: string): Promise<void>
    deleteUser(id: string): Promise<void>
    deleteUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    batchDeleteUsers(ids: string[]): Promise<void>
    batchDeleteUsers(ids: string[]): Promise<void>
    batchDeleteUsers(ids: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>
    batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>
    batchUpdateUsers(ids: unknown, data: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    activateUser(id: string): Promise<void>
    activateUser(id: string): Promise<void>
    activateUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    deactivateUser(id: string): Promise<void>
    deactivateUser(id: string): Promise<void>
    deactivateUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    suspendUser(id: string): Promise<void>
    suspendUser(id: string): Promise<void>
    suspendUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void>
    changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void>
    changePassword(id: unknown, data: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    resetPassword(id: string): Promise<void>
    resetPassword(id: string): Promise<void>
    resetPassword(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserProfile(id: string): Promise<UserProfile>
    getUserProfile(id: string): Promise<UserProfile>
    getUserProfile(id: unknown): Promise<UserProfile> {
        throw new Error('Method not implemented.')
    }
    updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>
    updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>
    updateUserProfile(id: unknown, data: unknown): Promise<UserProfile> {
        throw new Error('Method not implemented.')
    }
    getUserSessions(id: string): Promise<UserSession[]>
    getUserSessions(id: string): Promise<UserSession[]>
    getUserSessions(id: unknown): Promise<UserSession[]> {
        throw new Error('Method not implemented.')
    }
    terminateUserSession(id: string, sessionId: string): Promise<void>
    terminateUserSession(id: string, sessionId: string): Promise<void>
    terminateUserSession(id: unknown, sessionId: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserActivities(id: string, params?: any): Promise<UserActivity[]>
    getUserActivities(id: string, params?: any): Promise<UserActivity[]>
    getUserActivities(id: unknown, params?: unknown): Promise<UserActivity[]> {
        throw new Error('Method not implemented.')
    }
    getUserRoles(id: string): Promise<UserRole[]>
    getUserRoles(id: string): Promise<UserRole[]>
    getUserRoles(id: unknown): Promise<UserRole[]> {
        throw new Error('Method not implemented.')
    }
    updateUserRoles(id: string, roleIds: string[]): Promise<void>
    updateUserRoles(id: string, roleIds: string[]): Promise<void>
    updateUserRoles(id: unknown, roleIds: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserPermissions(id: string): Promise<UserPermission[]>
    getUserPermissions(id: string): Promise<UserPermission[]>
    getUserPermissions(id: unknown): Promise<UserPermission[]> {
        throw new Error('Method not implemented.')
    }class UserService implements IUserService {
    createUser(data: CreateUserRequest): Promise<User>
    createUser(data: CreateUserRequest): Promise<User>
    createUser(data: unknown): Promise<User> {
        throw new Error('Method not implemented.')
    }
    deleteUser(id: string): Promise<void>
    deleteUser(id: string): Promise<void>
    deleteUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    batchDeleteUsers(ids: string[]): Promise<void>
    batchDeleteUsers(ids: string[]): Promise<void>
    batchDeleteUsers(ids: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>
    batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void>
    batchUpdateUsers(ids: unknown, data: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    activateUser(id: string): Promise<void>
    activateUser(id: string): Promise<void>
    activateUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    deactivateUser(id: string): Promise<void>
    deactivateUser(id: string): Promise<void>
    deactivateUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    suspendUser(id: string): Promise<void>
    suspendUser(id: string): Promise<void>
    suspendUser(id: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserProfile(id: string): Promise<UserProfile>
    getUserProfile(id: string): Promise<UserProfile>
    getUserProfile(id: unknown): Promise<UserProfile> {
        throw new Error('Method not implemented.')
    }
    updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>
    updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile>
    updateUserProfile(id: unknown, data: unknown): Promise<UserProfile> {
        throw new Error('Method not implemented.')
    }
    getUserSessions(id: string): Promise<UserSession[]>
    getUserSessions(id: string): Promise<UserSession[]>
    getUserSessions(id: unknown): Promise<UserSession[]> {
        throw new Error('Method not implemented.')
    }
    terminateUserSession(id: string, sessionId: string): Promise<void>
    terminateUserSession(id: string, sessionId: string): Promise<void>
    terminateUserSession(id: unknown, sessionId: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserActivities(id: string, params?: any): Promise<UserActivity[]>
    getUserActivities(id: string, params?: any): Promise<UserActivity[]>
    getUserActivities(id: unknown, params?: unknown): Promise<UserActivity[]> {
        throw new Error('Method not implemented.')
    }
    getUserRoles(id: string): Promise<UserRole[]>
    getUserRoles(id: string): Promise<UserRole[]>
    getUserRoles(id: unknown): Promise<UserRole[]> {
        throw new Error('Method not implemented.')
    }
    updateUserRoles(id: string, roleIds: string[]): Promise<void>
    updateUserRoles(id: string, roleIds: string[]): Promise<void>
    updateUserRoles(id: unknown, roleIds: unknown): Promise<void> {
        throw new Error('Method not implemented.')
    }
    getUserPermissions(id: string): Promise<UserPermission[]>
    getUserPermissions(id: string): Promise<UserPermission[]>
    getUserPermissions(id: unknown): Promise<UserPermission[]> {
        throw new Error('Method not implemented.')
    }

  private api = new ApiService()  private api = new ApiService()



  // 用户 CRUD 操作  // 用户 CRUD 操作

  async getUsers(params?: UserQueryParams): Promise<UserListResponse> {  async getUsers(params?: UserQueryParams): Promise<UserListResponse> {

    const queryParams = new URLSearchParams()    const queryParams = new URLSearchParams()

        

    if (params) {    if (params) {

      if (params.username) queryParams.append('search', params.username)      if (params.username) queryParams.append('search', params.username)

      if (params.email) queryParams.append('search', params.email)      if (params.email) queryParams.append('search', params.email)

      if (params.status) queryParams.append('status', params.status)      if (params.status) queryParams.append('status', params.status)

      if (params.page) queryParams.append('skip', String((params.page - 1) * (params.pageSize || 20)))      if (params.page) queryParams.append('skip', String((params.page - 1) * (params.pageSize || 20)))

      if (params.pageSize) queryParams.append('limit', String(params.pageSize))      if (params.pageSize) queryParams.append('limit', String(params.pageSize))

    }    }

        

    const response = await this.api.get(`/api/v1/users?${queryParams.toString()}`)    const response = await this.api.get(`/api/v1/users?${queryParams.toString()}`)

    return response.data as UserListResponse    return response.data

  }  }



  async getUser(id: string): Promise<User> {  async getUser(id: string): Promise<User> {

    const response = await this.api.get(`/api/v1/users/${id}`)    const response = await this.api.get(`/api/v1/users/${id}`)

    return response.data as User    return response.data

  }

/**

  async createUser(data: CreateUserRequest): Promise<User> { * 用户服务实现 - 连接后端API

    const response = await this.api.post('/api/v1/users', data) */

    return response.data as Userclass UserService implements IUserService {

  }  private api = new ApiService()

  // 用户 CRUD 操作

  async updateUser(id: string, data: UpdateUserRequest): Promise<User> {  async getUsers(params?: UserQueryParams): Promise<UserListResponse> {

    const response = await this.api.put(`/api/v1/users/${id}`, data)    const queryParams = new URLSearchParams()

    return response.data as User    

  }    if (params) {

      if (params.username) queryParams.append('search', params.username)

  async deleteUser(id: string): Promise<void> {      if (params.email) queryParams.append('search', params.email)

    await this.api.delete(`/api/v1/users/${id}`)      if (params.status) queryParams.append('status', params.status)

  }      if (params.page) queryParams.append('skip', String((params.page - 1) * (params.pageSize || 20)))

      if (params.pageSize) queryParams.append('limit', String(params.pageSize))

  // 批量操作    }

  async batchDeleteUsers(ids: string[]): Promise<void> {    

    await this.api.delete('/api/v1/users/batch', { data: { user_ids: ids.map(id => parseInt(id)) } })    const response = await this.api.get(`/api/v1/users?${queryParams.toString()}`)

  }    return response.data

    }

  async batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void> {    

    // 实现批量更新逻辑    return {

    const promises = ids.map(id => this.updateUser(id, data))      data: filteredUsers,

    await Promise.all(promises)      total: this.mockUsers.length,

  }      page: params?.page || 1,

      pageSize: params?.pageSize || 10

  // 用户状态管理      }

  async activateUser(id: string): Promise<void> {  }

    await this.updateUser(id, { status: 'active' } as UpdateUserRequest)

  }  async getUser(id: string): Promise<User> {

    await this.delay()

  async deactivateUser(id: string): Promise<void> {    

    await this.updateUser(id, { status: 'inactive' } as UpdateUserRequest)    const user = this.mockUsers.find(u => u.id === id)

  }    if (!user) {

      throw new Error('用户不存在')

  async suspendUser(id: string): Promise<void> {    }

    await this.updateUser(id, { status: 'suspended' } as UpdateUserRequest)    

  }    return user

  }

  // 密码相关

  async changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void> {  async createUser(data: CreateUserRequest): Promise<User> {

    await this.api.put(`/api/v1/users/${id}/password`, {    await this.delay()

      current_password: data.currentPassword,    

      new_password: data.newPassword    // 检查用户名和邮箱是否已存在

    })    if (this.mockUsers.some(u => u.username === data.username)) {

  }      throw new Error('用户名已存在')

    }

  async resetPassword(id: string): Promise<void> {    

    // 实现重置密码逻辑    if (this.mockUsers.some(u => u.email === data.email)) {

    await this.api.post(`/api/v1/users/${id}/reset-password`)      throw new Error('邮箱已存在')

  }    }

    

  // 用户资料    const newUser: User = {

  async getUserProfile(id: string): Promise<UserProfile> {      id: String(this.mockUsers.length + 1),

    const user = await this.getUser(id)      username: data.username,

    return {      email: data.email,

      id: user.id,      fullName: data.fullName,

      username: user.username,      status: data.status || 'active',

      email: user.email,      roles: data.roles,

      fullName: user.fullName,      emailVerified: false,

      avatar: user.avatar,      twoFactorEnabled: false,

      phoneNumber: user.phoneNumber,      loginCount: 0,

      bio: '',      failedLoginCount: 0,

      location: '',      createdAt: new Date().toISOString(),

      website: '',      updatedAt: new Date().toISOString()

      socialLinks: {},    }

      preferences: {},    

      privacy: {}    this.mockUsers.push(newUser)

    } as UserProfile    return newUser

  }  }



  async updateUserProfile(id: string, data: Partial<UserProfile>): Promise<UserProfile> {  async updateUser(id: string, data: UpdateUserRequest): Promise<User> {

    const updateData: UpdateUserRequest = {    await this.delay()

      email: data.email,    

      // 映射其他字段    const userIndex = this.mockUsers.findIndex(u => u.id === id)

    } as UpdateUserRequest    if (userIndex === -1) {

          throw new Error('用户不存在')

    await this.updateUser(id, updateData)    }

    return await this.getUserProfile(id)    

  }    // 检查邮箱是否已被其他用户使用

    if (data.email && this.mockUsers.some(u => u.id !== id && u.email === data.email)) {

  // 用户会话      throw new Error('邮箱已被其他用户使用')

  async getUserSessions(id: string): Promise<UserSession[]> {    }

    // 实现获取用户会话逻辑    

    return []    const updatedUser = {

  }      ...this.mockUsers[userIndex],

      ...data,

  async terminateUserSession(id: string, sessionId: string): Promise<void> {      updatedAt: new Date().toISOString()

    // 实现终止会话逻辑    }

    await this.api.delete(`/api/v1/users/${id}/sessions/${sessionId}`)    

  }    this.mockUsers[userIndex] = updatedUser

    return updatedUser

  // 用户活动  }

  async getUserActivities(id: string, params?: any): Promise<UserActivity[]> {

    // 实现获取用户活动逻辑  async deleteUser(id: string): Promise<void> {

    return []    await this.delay()

  }    

    const userIndex = this.mockUsers.findIndex(u => u.id === id)

  // 角色权限    if (userIndex === -1) {

  async getUserRoles(id: string): Promise<UserRole[]> {      throw new Error('用户不存在')

    const response = await this.api.get(`/api/v1/users/${id}/groups`)    }

    return response.data as UserRole[]    

  }    // 不能删除管理员用户

    if (this.mockUsers[userIndex].username === 'admin') {

  async updateUserRoles(id: string, roleIds: string[]): Promise<void> {      throw new Error('不能删除管理员用户')

    // 实现更新用户角色逻辑    }

    for (const roleId of roleIds) {    

      await this.api.post(`/api/v1/users/${id}/groups`, {    this.mockUsers.splice(userIndex, 1)

        groupname: roleId,  }

        priority: 1

      })  async batchDeleteUsers(ids: string[]): Promise<void> {

    }    await this.delay()

  }    

    // 检查是否包含管理员

  async getUserPermissions(id: string): Promise<UserPermission[]> {    const adminIds = ids.filter(id => {

    // 实现获取用户权限逻辑      const user = this.mockUsers.find(u => u.id === id)

    return []      return user?.username === 'admin'

  }    })

    

  // 快速创建用户    if (adminIds.length > 0) {

  async createUserQuick(username: string, password: string, email?: string): Promise<User> {      throw new Error('选中的用户包含管理员，无法删除')

    const response = await this.api.post('/api/v1/users/quick', {    }

      username,    

      password,    // 删除用户

      email    this.mockUsers = this.mockUsers.filter(user => !ids.includes(user.id))

    })  }

    return response.data as User

  }  async batchUpdateUsers(ids: string[], data: BatchUserUpdateRequest): Promise<void> {

    await this.delay()

  // 批量创建用户    

  async createUsersBatch(data: {    ids.forEach(id => {

    count: number      const userIndex = this.mockUsers.findIndex(u => u.id === id)

    username_prefix: string      if (userIndex !== -1) {

    password_length?: number        this.mockUsers[userIndex] = {

    group?: string          ...this.mockUsers[userIndex],

    email_domain?: string          ...data,

  }): Promise<any> {          updatedAt: new Date().toISOString()

    const response = await this.api.post('/api/v1/users/batch', data)        }

    return response.data      }

  }    })

  }

  // 导入用户

  async importUsers(file: File): Promise<any> {  async activateUser(id: string): Promise<void> {

    const formData = new FormData()    await this.updateUser(id, { status: 'active' })

    formData.append('file', file)  }

    

    const response = await this.api.post('/api/v1/users/import', formData, {  async deactivateUser(id: string): Promise<void> {

      headers: {    await this.updateUser(id, { status: 'inactive' })

        'Content-Type': 'multipart/form-data'  }

      }

    })  async suspendUser(id: string): Promise<void> {

    return response.data    await this.updateUser(id, { status: 'suspended' })

  }  }



  // 搜索用户  async changePassword(id: string, data: { currentPassword: string; newPassword: string }): Promise<void> {

  async searchUsers(query: string, limit?: number): Promise<User[]> {    await this.delay()

    const response = await this.api.get(`/api/v1/users/search/${query}?limit=${limit || 10}`)    

    return response.data as User[]    // 模拟密码验证

  }    console.log('更改密码:', id, data)

  }

  // 获取在线用户

  async getOnlineUsers(): Promise<any[]> {  async resetPassword(id: string): Promise<void> {

    const response = await this.api.get('/api/v1/users/online/active')    await this.delay()

    return response.data as any[]    

  }    // 模拟重置密码

}    console.log('重置密码:', id)

  }

// 导出服务实例

export const userService = new UserService()  async getUserProfile(id: string): Promise<UserProfile> {

export default userService    await this.delay()
    
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