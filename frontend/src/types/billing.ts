/**
 * 计费管理相关类型定义
 */

// 基础货币类型
export interface Money {
  amount: number
  currency: string
}

// 计费计划类型
export type PlanType = 'monthly' | 'usage' | 'hybrid' | 'prepaid' | 'postpaid'

// 费率类型
export type RateType = 'fixed' | 'tiered' | 'volume' | 'time_based' | 'bandwidth'

// 发票状态
export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled' | 'refunded'

// 支付状态
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'refunded'

// 支付方式
export type PaymentMethod = 'credit_card' | 'debit_card' | 'bank_transfer' | 'paypal' | 'alipay' | 'wechat_pay' | 'cash'

// 通知方式
export type NotificationMethod = 'email' | 'sms' | 'push'

// 计费计划接口
export interface BillingPlan {
  id: string
  name: string
  type: PlanType
  description?: string
  active: boolean
  rates: BillingRate[]
  validFrom: string
  validTo?: string
  maxUsers?: number
  features: string[]
  createdAt: string
  updatedAt: string
}

// 计费费率接口
export interface BillingRate {
  id: string
  planId: string
  name: string
  type: RateType
  unitPrice: Money
  minQuantity?: number
  maxQuantity?: number
  tierRates?: TierRate[]
  validFrom: string
  validTo?: string
  createdAt: string
}

// 阶梯费率
export interface TierRate {
  from: number
  to?: number
  price: Money
}

// 使用数据
export interface UsageData {
  userId: string
  period: DateRange
  dataTransfer: {
    upload: number    // bytes
    download: number  // bytes
    total: number     // bytes
  }
  sessionTime: number // seconds
  sessionCount: number
  features: Record<string, any>
}

// 日期范围
export interface DateRange {
  start: string
  end: string
}

// 发票接口
export interface Invoice {
  id: string
  number: string
  userId: string
  userInfo: {
    username: string
    fullName?: string
    email: string
    address?: Address
  }
  status: InvoiceStatus
  issueDate: string
  dueDate: string
  items: InvoiceItem[]
  subtotalAmount: Money
  taxAmount: Money
  totalAmount: Money
  paidAmount: Money
  balanceAmount: Money
  paymentTerms?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

// 发票明细
export interface InvoiceItem {
  id: string
  invoiceId: string
  description: string
  quantity: number
  unitPrice: Money
  totalPrice: Money
  taxRate?: number
  taxAmount?: Money
  period?: DateRange
}

// 地址信息
export interface Address {
  street: string
  city: string
  state: string
  country: string
  postalCode: string
}

// 支付接口
export interface Payment {
  id: string
  invoiceId: string
  userId: string
  amount: Money
  method: PaymentMethod
  status: PaymentStatus
  transactionId?: string
  gatewayResponse?: Record<string, any>
  failureReason?: string
  processedAt?: string
  createdAt: string
}

// 计费历史
export interface BillingHistory {
  id: string
  userId: string
  planId: string
  planName: string
  billingPeriodStart: string
  billingPeriodEnd: string
  usageData: UsageData
  calculatedAmount: Money
  invoiceId?: string
  createdAt: string
}

// 支付网关接口
export interface PaymentGateway {
  id: string
  name: string
  type: string
  active: boolean
  config: Record<string, any>
  supportedMethods: PaymentMethod[]
  createdAt: string
  updatedAt: string
}

// 折扣信息
export interface Discount {
  id: string
  name: string
  type: 'percentage' | 'fixed_amount'
  value: number
  minAmount?: Money
  maxDiscount?: Money
  validFrom: string
  validTo?: string
  active: boolean
}

// 税务规则
export interface TaxRule {
  id: string
  name: string
  rate: number
  type: 'vat' | 'sales_tax' | 'gst'
  region: string
  active: boolean
}

// 创建计费计划请求
export interface CreateBillingPlanRequest {
  name: string
  type: PlanType
  description?: string
  rates: Omit<BillingRate, 'id' | 'planId' | 'createdAt'>[]
  validFrom: string
  validTo?: string
  maxUsers?: number
  features: string[]
}

// 更新计费计划请求
export interface UpdateBillingPlanRequest {
  name?: string
  description?: string
  active?: boolean
  validTo?: string
  maxUsers?: number
  features?: string[]
}

// 创建发票请求
export interface CreateInvoiceRequest {
  userId: string
  items: Omit<InvoiceItem, 'id' | 'invoiceId'>[]
  dueDate: string
  paymentTerms?: string
  notes?: string
}

// 支付请求
export interface PaymentRequest {
  invoiceId: string
  amount: Money
  method: PaymentMethod
  gatewayId?: string
  paymentData?: Record<string, any>
}

// 支付结果
export interface PaymentResult {
  success: boolean
  paymentId?: string
  transactionId?: string
  errorCode?: string
  errorMessage?: string
  gatewayResponse?: Record<string, any>
}

// 退款结果


// 计费报表查询参数
export interface BillingReportQuery {
  startDate: string
  endDate: string
  userId?: string
  planId?: string
  status?: InvoiceStatus[]
  groupBy?: 'day' | 'week' | 'month' | 'year'
}

// 计费报表数据
export interface BillingReportData {
  period: string
  totalRevenue: Money
  totalInvoices: number
  paidInvoices: number
  unpaidInvoices: number
  overdueInvoices: number
  averageInvoiceAmount: Money
  topPlans: Array<{
    planId: string
    planName: string
    revenue: Money
    userCount: number
  }>
}

// 查询参数接口
export interface BillingPlanQueryParams {
  page?: number
  pageSize?: number
  name?: string
  type?: PlanType
  active?: boolean
  sortField?: string
  sortOrder?: 'ascend' | 'descend'
}

export interface InvoiceQueryParams {
  page?: number
  pageSize?: number
  userId?: string
  status?: InvoiceStatus
  startDate?: string
  endDate?: string
  sortField?: string
  sortOrder?: 'ascend' | 'descend'
}

export interface PaymentQueryParams {
  page?: number
  pageSize?: number
  userId?: string
  invoiceId?: string
  method?: PaymentMethod
  status?: PaymentStatus
  startDate?: string
  endDate?: string
  sortField?: string
  sortOrder?: 'ascend' | 'descend'
}

// 分页响应接口
export interface BillingPlanListResponse {
  data: BillingPlan[]
  total: number
  page: number
  pageSize: number
}

export interface InvoiceListResponse {
  data: Invoice[]
  total: number
  page: number
  pageSize: number
}

export interface PaymentListResponse {
  data: Payment[]
  total: number
  page: number
  pageSize: number
}

// 验证结果
export interface ValidationResult {
  valid: boolean
  errors: Array<{
    field: string
    message: string
  }>
}

// 计费配置
export interface BillingConfig {
  defaultCurrency: string
  taxRate: number
  paymentTermsDays: number
  overdueGraceDays: number
  autoGenerateInvoices: boolean
  emailNotifications: boolean
  smsNotifications: boolean
}

// 统计数据
export interface BillingStatistics {
  totalRevenue: Money
  monthlyRevenue: Money
  totalInvoices: number
  paidInvoices: number
  overdueInvoices: number
  activeSubscriptions: number
  topPaymentMethods: Array<{
    method: PaymentMethod
    count: number
    amount: Money
  }>
}

// ==================== 支付管理扩展类型 ====================

/**
 * 扩展的支付状态（包含部分退款状态）
 */
export type ExtendedPaymentStatus = PaymentStatus | 'partial_refunded'

/**
 * 支付方式类型
 */
export type PaymentMethodType = 
  | 'alipay'       // 支付宝
  | 'wechat'       // 微信支付
  | 'bank_card'    // 银行卡
  | 'credit_card'  // 信用卡
  | 'bank_transfer' // 银行转账
  | 'cash'         // 现金
  | 'other'        // 其他

/**
 * 支付网关类型
 */
export type PaymentGatewayType = 
  | 'alipay'
  | 'wechat'
  | 'stripe'
  | 'paypal'
  | 'unionpay'
  | 'internal'

/**
 * 退款状态
 */
export type RefundStatus = 
  | 'pending'      // 待处理
  | 'approved'     // 已批准
  | 'rejected'     // 已拒绝
  | 'processing'   // 处理中
  | 'completed'    // 已完成
  | 'failed'       // 失败

/**
 * 增强的支付记录接口
 */
export interface PaymentRecord {
  id: string
  paymentNumber: string
  userId: string
  invoiceId?: string
  userInfo: {
    name: string
    email: string
    phone?: string
  }
  amount: Money
  status: ExtendedPaymentStatus
  paymentMethodType: PaymentMethodType
  gatewayType: PaymentGatewayType
  transactionId?: string
  gatewayTransactionId?: string
  gatewayOrderId?: string
  description?: string
  failureReason?: string
  paidAt?: string
  expiredAt?: string
  refundableAmount: Money
  refundedAmount: Money
  createdAt: string
  updatedAt: string
}

/**
 * 退款记录
 */
export interface Refund {
  id: string
  refundNumber: string
  paymentId: string
  payment?: PaymentRecord
  amount: Money
  status: RefundStatus
  reason: string
  approvedBy?: string
  approvedAt?: string
  rejectedReason?: string
  gatewayRefundId?: string
  processedAt?: string
  notificationSent: boolean
  metadata?: Record<string, any>
  createdAt: string
  updatedAt: string
}

/**
 * 支付日志
 */
export interface PaymentLog {
  id: string
  paymentId: string
  action: string
  status: string
  message?: string
  data?: Record<string, any>
  operatorId?: string
  operatorName?: string
  ipAddress?: string
  userAgent?: string
  createdAt: string
}

/**
 * 支付网关结果
 */
export interface GatewayResult {
  success: boolean
  transactionId?: string
  gatewayOrderId?: string
  payUrl?: string
  qrCode?: string
  message?: string
  errorCode?: string
  metadata?: Record<string, any>
}

/**
 * 创建支付请求
 */
export interface CreatePaymentRequest {
  userId: string
  invoiceId?: string
  amount: Money
  paymentMethodType: PaymentMethodType
  gatewayType: PaymentGatewayType
  description?: string
  returnUrl?: string
  notifyUrl?: string
  userInfo: {
    name: string
    email: string
    phone?: string
  }
  metadata?: Record<string, any>
}

/**
 * 更新支付请求
 */
export interface UpdatePaymentRequest {
  status?: ExtendedPaymentStatus
  transactionId?: string
  gatewayTransactionId?: string
  failureReason?: string
  paidAt?: string
  refundedAmount?: Money
  refundableAmount?: Money
  metadata?: Record<string, any>
}

/**
 * 扩展的支付查询参数
 */
export interface ExtendedPaymentQueryParams {
  page?: number
  pageSize?: number
  paymentNumber?: string
  userId?: string
  invoiceId?: string
  status?: ExtendedPaymentStatus
  paymentMethodType?: PaymentMethodType
  gatewayType?: PaymentGatewayType
  minAmount?: number
  maxAmount?: number
  startDate?: string
  endDate?: string
  sortBy?: 'createdAt' | 'amount' | 'paidAt'
  sortOrder?: 'asc' | 'desc'
}

/**
 * 支付记录列表响应
 */
export interface PaymentRecordListResponse {
  data: PaymentRecord[]
  total: number
  page: number
  pageSize: number
}

/**
 * 支付结果
 */
export interface PaymentResult {
  success: boolean
  payment?: PaymentRecord
  payUrl?: string
  qrCode?: string
  message?: string
  errorCode?: string
}

/**
 * 退款请求
 */
export interface RefundRequest {
  paymentId: string
  amount: Money
  reason: string
  notifyCustomer?: boolean
  metadata?: Record<string, any>
}

/**
 * 退款查询参数
 */
export interface RefundQueryParams {
  page?: number
  pageSize?: number
  refundNumber?: string
  paymentId?: string
  userId?: string
  status?: RefundStatus
  minAmount?: number
  maxAmount?: number
  startDate?: string
  endDate?: string
  sortBy?: 'createdAt' | 'amount' | 'processedAt'
  sortOrder?: 'asc' | 'desc'
}

/**
 * 退款列表响应
 */
export interface RefundListResponse {
  data: Refund[]
  total: number
  page: number
  pageSize: number
}

/**
 * 退款结果
 */
export interface RefundResult {
  success: boolean
  refund?: Refund
  amount?: Money
  message?: string
  errorCode?: string
}

/**
 * 支付统计
 */
export interface PaymentStatistics {
  totalAmount: Money
  totalCount: number
  completedAmount: Money
  completedCount: number
  pendingAmount: Money
  pendingCount: number
  failedCount: number
  refundedAmount: Money
  refundedCount: number
  averageAmount: Money
  conversionRate: number
}

/**
 * 支付方式统计
 */
export interface PaymentMethodStatistics {
  paymentMethodType: PaymentMethodType
  amount: Money
  count: number
  percentage: number
}

/**
 * 支付网关配置
 */
export interface PaymentGatewayConfig {
  id: string
  name: string
  type: PaymentGatewayType
  active: boolean
  config: {
    appId?: string
    merchantId?: string
    publicKey?: string
    privateKey?: string
    apiUrl?: string
    notifyUrl?: string
    returnUrl?: string
    [key: string]: any
  }
  supportedMethods: PaymentMethodType[]
  supportedCurrencies: string[]
  createdAt: string
  updatedAt: string
}

// 导出所有类型的联合类型
export type BillingTypes = 
  | BillingPlan 
  | BillingRate 
  | Invoice 
  | InvoiceItem 
  | Payment 
  | PaymentRecord
  | Refund
  | BillingHistory 
  | PaymentGateway