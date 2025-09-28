/**
 * 认证相关类型定义
 */

// 用户信息
export interface User {
  id: number
  username: string
  email: string
  fullName?: string
  avatar?: string
  status: 'active' | 'inactive' | 'suspended'
  roles: string[]
  permissions: string[]
  createdAt: string
  updatedAt: string
  lastLoginAt?: string
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
  confirmPassword: string
  fullName?: string
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