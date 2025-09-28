/**
 * 用户相关类型定义
 */

export interface User {
  id: string
  username: string
  email: string
  fullName?: string
  avatar?: string
  status: 'active' | 'inactive' | 'suspended'
  roles: string[]
  permissions?: string[]
  lastLoginAt?: string
  lastLoginIp?: string
  loginCount?: number
  failedLoginCount?: number
  failedLoginAt?: string
  emailVerified: boolean
  emailVerifiedAt?: string
  phoneNumber?: string
  phoneVerified?: boolean
  twoFactorEnabled: boolean
  createdAt: string
  updatedAt: string
  deletedAt?: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  fullName?: string
  roles: string[]
  status?: 'active' | 'inactive'
  phoneNumber?: string
  sendWelcomeEmail?: boolean
}

export interface UpdateUserRequest {
  email?: string
  fullName?: string
  roles?: string[]
  status?: 'active' | 'inactive' | 'suspended'
  phoneNumber?: string
  avatar?: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface ResetPasswordRequest {
  email: string
}

export interface UserQueryParams {
  page?: number
  pageSize?: number
  username?: string
  email?: string
  fullName?: string
  status?: 'active' | 'inactive' | 'suspended'
  roles?: string[]
  startDate?: string
  endDate?: string
  sortField?: string
  sortOrder?: 'ascend' | 'descend'
}

export interface UserListResponse {
  data: User[]
  total: number
  page: number
  pageSize: number
}

export interface BatchUserUpdateRequest {
  status?: 'active' | 'inactive' | 'suspended'
  roles?: string[]
}

export interface UserProfile {
  id: string
  username: string
  email: string
  fullName?: string
  avatar?: string
  phoneNumber?: string
  emailVerified: boolean
  phoneVerified: boolean
  twoFactorEnabled: boolean
  preferences: UserPreferences
  lastLoginAt?: string
  createdAt: string
}

export interface UserPreferences {
  language: string
  timezone: string
  dateFormat: string
  theme: 'light' | 'dark' | 'auto'
  notifications: {
    email: boolean
    push: boolean
    sms: boolean
  }
}

export interface UserSession {
  id: string
  userId: string
  deviceInfo: string
  ipAddress: string
  location?: string
  userAgent: string
  isActive: boolean
  createdAt: string
  lastActiveAt: string
  expiresAt: string
}

export interface UserActivity {
  id: string
  userId: string
  action: string
  resource: string
  resourceId?: string
  details?: Record<string, any>
  ipAddress: string
  userAgent: string
  createdAt: string
}

export interface LoginRequest {
  username: string
  password: string
  rememberMe?: boolean
  captcha?: string
}

export interface LoginResponse {
  user: User
  accessToken: string
  refreshToken: string
  expiresIn: number
  permissions: string[]
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface VerifyPhoneRequest {
  code: string
}

export interface TwoFactorSetupResponse {
  qrCode: string
  secret: string
  backupCodes: string[]
}

export interface TwoFactorVerifyRequest {
  code: string
}

export interface UserRole {
  id: string
  name: string
  displayName: string
  description?: string
  permissions: string[]
  isSystem: boolean
  createdAt: string
  updatedAt: string
}

export interface UserPermission {
  id: string
  name: string
  displayName: string
  description?: string
  resource: string
  action: string
  createdAt: string
}

// 导出所有类型的联合类型，便于其他模块使用
export type UserTypes = 
  | User 
  | CreateUserRequest 
  | UpdateUserRequest 
  | UserProfile 
  | UserSession 
  | UserActivity 
  | UserRole 
  | UserPermission