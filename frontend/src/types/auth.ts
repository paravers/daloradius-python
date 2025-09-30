/**
 * 认证相关类型定义
 */

// 用户信息
export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  fullName?: string
  avatar?: string
  is_active: boolean
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' | 'EXPIRED'
  auth_type: string
  roles: string[]
  permissions: string[]
  last_login?: string
  created_at: string
  updated_at?: string
}

// 登录表单
export interface LoginForm {
  username: string
  password: string
  remember?: boolean
  captcha?: string
}

// 注册表单
export interface RegisterForm {
  username: string
  email: string
  password: string
  firstName?: string
  lastName?: string
}

// 认证结果
export interface AuthResult {
  token: string
  refreshToken: string
  user: User
  permissions: string[]
  expiresIn: number
}

// JWT 载荷
export interface JwtPayload {
  sub: string // user id
  username: string
  roles: string[]
  iat: number
  exp: number
}

// 认证状态
export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  permissions: string[]
  isAuthenticated: boolean
  isLoading: boolean
}

// 认证服务接口
export interface IAuthService {
  login(credentials: LoginForm): Promise<AuthResult>
  logout(): Promise<void>
  refreshToken(): Promise<string>
  getCurrentUser(): Promise<User | null>
  checkPermission(permission: string): boolean
  hasRole(role: string): boolean
}