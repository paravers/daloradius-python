/**
 * 业务相关类型定义
 */

// RADIUS 用户
export interface RadiusUser {
  id: number
  username: string
  email?: string
  fullName?: string
  status: 'active' | 'inactive' | 'suspended'
  groupName?: string
  planId?: number
  planName?: string
  createdAt: string
  updatedAt: string
  lastLoginAt?: string
  expirationDate?: string
}

// 用户创建表单
export interface CreateUserForm {
  username: string
  password: string
  email?: string
  fullName?: string
  groupName?: string
  planId?: number
  expirationDate?: string
  maxSessions?: number
  attributes?: UserAttribute[]
}

// 用户更新表单
export interface UpdateUserForm {
  email?: string
  fullName?: string
  status?: string
  groupName?: string
  planId?: number
  expirationDate?: string
  maxSessions?: number
  attributes?: UserAttribute[]
}

// 用户属性
export interface UserAttribute {
  attribute: string
  op: string
  value: string
  type: 'check' | 'reply'
}

// 计费计划
export interface BillingPlan {
  id: number
  name: string
  description?: string
  price: number
  currency: string
  billingCycle: 'monthly' | 'quarterly' | 'yearly'
  bandwidth: number
  timeLimit: number
  dataLimit: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// 账单记录
export interface BillingHistory {
  id: number
  userId: number
  username: string
  planId: number
  planName: string
  amount: number
  currency: string
  billingDate: string
  dueDate: string
  status: 'pending' | 'paid' | 'overdue' | 'cancelled'
  paymentMethod?: string
  transactionId?: string
  createdAt: string
}

// NAS 设备
export interface NasDevice {
  id: number
  name: string
  shortname: string
  type: string
  ports: number
  secret: string
  server: string
  community?: string
  description?: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// 会计记录
export interface AccountingRecord {
  id: number
  sessionId: string
  username: string
  nasIpAddress: string
  nasName?: string
  startTime: string
  stopTime?: string
  sessionTime?: number
  inputOctets: number
  outputOctets: number
  calledStationId?: string
  callingStationId?: string
  terminateCause?: string
  serviceType?: string
  framedProtocol?: string
  framedIpAddress?: string
}

// 统计数据
export interface DashboardStats {
  totalUsers: number
  activeUsers: number
  totalSessions: number
  activeSessions: number
  totalRevenue: number
  monthlyRevenue: number
  totalDevices: number
  activeDevices: number
  bandwidth: {
    upload: number
    download: number
  }
}

// 图表数据
export interface ChartData {
  categories: string[]
  series: Array<{
    name: string
    data: number[]
    type?: string
  }>
}