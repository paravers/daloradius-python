import type {
  PaymentRecord,
  Refund,
  CreatePaymentRequest,
  UpdatePaymentRequest,
  ExtendedPaymentQueryParams,
  PaymentRecordListResponse,
  PaymentResult,
  RefundRequest,
  RefundQueryParams,
  RefundListResponse,
  RefundResult,
  PaymentStatistics,
  PaymentMethodStatistics,
  PaymentMethodType,
  PaymentGatewayType,
  ExtendedPaymentStatus,
  RefundStatus,
  Money,
  ValidationResult
} from '@/types/billing'

/**
 * 支付服务接口
 */
export interface IPaymentService {
  // 支付 CRUD 操作
  getPayments(params?: ExtendedPaymentQueryParams): Promise<PaymentRecordListResponse>
  getPayment(id: string): Promise<PaymentRecord>
  createPayment(data: CreatePaymentRequest): Promise<PaymentResult>
  updatePayment(id: string, data: UpdatePaymentRequest): Promise<PaymentRecord>
  deletePayment(id: string): Promise<void>
  
  // 支付状态管理
  processPayment(id: string): Promise<PaymentResult>
  cancelPayment(id: string, reason?: string): Promise<void>
  retryPayment(id: string): Promise<PaymentResult>
  markPaymentCompleted(id: string, transactionId: string): Promise<void>
  markPaymentFailed(id: string, reason: string): Promise<void>
  
  // 退款管理
  getRefunds(params?: RefundQueryParams): Promise<RefundListResponse>
  getRefund(id: string): Promise<Refund>
  createRefund(data: RefundRequest): Promise<RefundResult>
  approveRefund(id: string, approvedBy: string): Promise<RefundResult>
  rejectRefund(id: string, reason: string, rejectedBy: string): Promise<RefundResult>
  processRefund(id: string): Promise<RefundResult>
  
  // 统计分析
  getPaymentStatistics(startDate?: string, endDate?: string): Promise<PaymentStatistics>
  getPaymentMethodStatistics(startDate?: string, endDate?: string): Promise<PaymentMethodStatistics[]>
  
  // 支付方式管理
  getSupportedPaymentMethods(): Promise<PaymentMethodType[]>
  getSupportedGateways(): Promise<PaymentGatewayType[]>
  
  // 验证
  validatePaymentRequest(data: CreatePaymentRequest): ValidationResult
  validateRefundRequest(data: RefundRequest): ValidationResult
}

/**
 * 模拟支付服务实现
 */
class PaymentService implements IPaymentService {
  private mockPayments: PaymentRecord[] = [
    {
      id: 'PAY-2024-001',
      paymentNumber: 'PAY-2024-001',
      userId: 'user1',
      invoiceId: 'INV-2024-001',
      userInfo: {
        name: '张三',
        email: 'zhangsan@example.com',
        phone: '13800138000'
      },
      amount: { amount: 53.53, currency: 'CNY' },
      status: 'completed',
      paymentMethodType: 'alipay',
      gatewayType: 'alipay',
      transactionId: 'TXN-20240115-001',
      gatewayTransactionId: '2024011522001004410588851234',
      description: '基础套餐月租费支付',
      paidAt: '2024-01-15T10:30:00Z',
      refundableAmount: { amount: 53.53, currency: 'CNY' },
      refundedAmount: { amount: 0, currency: 'CNY' },
      createdAt: '2024-01-15T10:25:00Z',
      updatedAt: '2024-01-15T10:30:00Z'
    },
    {
      id: 'PAY-2024-002',
      paymentNumber: 'PAY-2024-002',
      userId: 'user2',
      invoiceId: 'INV-2024-002',
      userInfo: {
        name: '李四',
        email: 'lisi@example.com',
        phone: '13900139000'
      },
      amount: { amount: 192.00, currency: 'CNY' },
      status: 'pending',
      paymentMethodType: 'wechat',
      gatewayType: 'wechat',
      description: '企业套餐月租费支付',
      expiredAt: '2024-01-20T23:59:59Z',
      refundableAmount: { amount: 0, currency: 'CNY' },
      refundedAmount: { amount: 0, currency: 'CNY' },
      createdAt: '2024-01-20T14:15:00Z',
      updatedAt: '2024-01-20T14:15:00Z'
    },
    {
      id: 'PAY-2024-003',
      paymentNumber: 'PAY-2024-003',
      userId: 'user3',
      invoiceId: 'INV-2024-003',
      userInfo: {
        name: '王五',
        email: 'wangwu@example.com',
        phone: '13700137000'
      },
      amount: { amount: 0.33, currency: 'CNY' },
      status: 'failed',
      paymentMethodType: 'credit_card',
      gatewayType: 'stripe',
      failureReason: '银行卡余额不足',
      refundableAmount: { amount: 0, currency: 'CNY' },
      refundedAmount: { amount: 0, currency: 'CNY' },
      createdAt: '2024-01-10T16:45:00Z',
      updatedAt: '2024-01-10T16:48:00Z'
    },
    {
      id: 'PAY-2024-004',
      paymentNumber: 'PAY-2024-004',
      userId: 'user4',
      invoiceId: 'INV-2024-004',
      userInfo: {
        name: '赵六',
        email: 'zhaoliu@example.com',
        phone: '13600136000'
      },
      amount: { amount: 299.99, currency: 'CNY' },
      status: 'partial_refunded',
      paymentMethodType: 'bank_transfer',
      gatewayType: 'unionpay',
      transactionId: 'TXN-20240112-002',
      paidAt: '2024-01-12T09:15:00Z',
      description: '高级套餐年费支付',
      refundableAmount: { amount: 199.99, currency: 'CNY' },
      refundedAmount: { amount: 100.00, currency: 'CNY' },
      createdAt: '2024-01-12T09:10:00Z',
      updatedAt: '2024-01-18T15:20:00Z'
    }
  ]

  private mockRefunds: Refund[] = [
    {
      id: 'REF-2024-001',
      refundNumber: 'REF-2024-001',
      paymentId: 'PAY-2024-004',
      amount: { amount: 100.00, currency: 'CNY' },
      status: 'completed',
      reason: '用户申请部分退款',
      approvedBy: 'admin1',
      approvedAt: '2024-01-18T14:00:00Z',
      gatewayRefundId: 'RFD-20240118-001',
      processedAt: '2024-01-18T15:20:00Z',
      notificationSent: true,
      createdAt: '2024-01-18T13:30:00Z',
      updatedAt: '2024-01-18T15:20:00Z'
    },
    {
      id: 'REF-2024-002',
      refundNumber: 'REF-2024-002',
      paymentId: 'PAY-2024-001',
      amount: { amount: 53.53, currency: 'CNY' },
      status: 'pending',
      reason: '服务质量问题',
      notificationSent: false,
      createdAt: '2024-01-22T10:15:00Z',
      updatedAt: '2024-01-22T10:15:00Z'
    }
  ]

  private delay(ms: number = 800): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async getPayments(params?: ExtendedPaymentQueryParams): Promise<PaymentRecordListResponse> {
    await this.delay()
    
    let filteredPayments = [...this.mockPayments]
    
    if (params) {
      const { 
        paymentNumber, 
        userId, 
        invoiceId,
        status, 
        paymentMethodType,
        gatewayType,
        minAmount,
        maxAmount,
        startDate, 
        endDate,
        page = 1, 
        pageSize = 10 
      } = params
      
      // 支付号码筛选
      if (paymentNumber) {
        filteredPayments = filteredPayments.filter(payment => 
          payment.paymentNumber.toLowerCase().includes(paymentNumber.toLowerCase())
        )
      }
      
      // 用户筛选
      if (userId) {
        filteredPayments = filteredPayments.filter(payment => payment.userId === userId)
      }
      
      // 发票筛选
      if (invoiceId) {
        filteredPayments = filteredPayments.filter(payment => payment.invoiceId === invoiceId)
      }
      
      // 状态筛选
      if (status) {
        filteredPayments = filteredPayments.filter(payment => payment.status === status)
      }
      
      // 支付方式筛选
      if (paymentMethodType) {
        filteredPayments = filteredPayments.filter(payment => payment.paymentMethodType === paymentMethodType)
      }
      
      // 支付网关筛选
      if (gatewayType) {
        filteredPayments = filteredPayments.filter(payment => payment.gatewayType === gatewayType)
      }
      
      // 金额范围筛选
      if (minAmount !== undefined) {
        filteredPayments = filteredPayments.filter(payment => payment.amount.amount >= minAmount)
      }
      
      if (maxAmount !== undefined) {
        filteredPayments = filteredPayments.filter(payment => payment.amount.amount <= maxAmount)
      }
      
      // 日期范围筛选
      if (startDate) {
        filteredPayments = filteredPayments.filter(payment => 
          new Date(payment.createdAt) >= new Date(startDate)
        )
      }
      
      if (endDate) {
        filteredPayments = filteredPayments.filter(payment => 
          new Date(payment.createdAt) <= new Date(endDate)
        )
      }
      
      // 排序
      if (params.sortBy && params.sortOrder) {
        filteredPayments.sort((a, b) => {
          let aValue: any, bValue: any
          
          switch (params.sortBy) {
            case 'amount':
              aValue = a.amount.amount
              bValue = b.amount.amount
              break
            case 'paidAt':
              aValue = a.paidAt || '0'
              bValue = b.paidAt || '0'
              break
            default:
              aValue = a.createdAt
              bValue = b.createdAt
          }
          
          if (params.sortOrder === 'desc') {
            return aValue < bValue ? 1 : -1
          } else {
            return aValue > bValue ? 1 : -1
          }
        })
      }
      
      // 分页
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      filteredPayments = filteredPayments.slice(startIndex, endIndex)
    }
    
    return {
      data: filteredPayments,
      total: this.mockPayments.length,
      page: params?.page || 1,
      pageSize: params?.pageSize || 10
    }
  }

  async getPayment(id: string): Promise<PaymentRecord> {
    await this.delay()
    
    const payment = this.mockPayments.find(p => p.id === id)
    if (!payment) {
      throw new Error('支付记录不存在')
    }
    
    return payment
  }

  async createPayment(data: CreatePaymentRequest): Promise<PaymentResult> {
    await this.delay()
    
    // 验证数据
    const validation = this.validatePaymentRequest(data)
    if (!validation.valid) {
      throw new Error(`数据验证失败: ${validation.errors.map(e => e.message).join(', ')}`)
    }
    
    // 生成支付号
    const paymentNumber = this.generatePaymentNumber()
    
    const newPayment: PaymentRecord = {
      id: `PAY-${Date.now()}`,
      paymentNumber,
      userId: data.userId,
      invoiceId: data.invoiceId,
      userInfo: data.userInfo,
      amount: data.amount,
      status: 'pending',
      paymentMethodType: data.paymentMethodType,
      gatewayType: data.gatewayType,
      description: data.description,
      expiredAt: new Date(Date.now() + 30 * 60 * 1000).toISOString(), // 30分钟过期
      refundableAmount: { amount: 0, currency: data.amount.currency },
      refundedAmount: { amount: 0, currency: data.amount.currency },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockPayments.unshift(newPayment)
    
    // 模拟支付网关响应
    const mockPayUrl = `https://mock-gateway.com/pay/${newPayment.id}`
    
    return {
      success: true,
      payment: newPayment,
      payUrl: mockPayUrl,
      message: '支付订单创建成功'
    }
  }

  async updatePayment(id: string, data: UpdatePaymentRequest): Promise<PaymentRecord> {
    await this.delay()
    
    const paymentIndex = this.mockPayments.findIndex(p => p.id === id)
    if (paymentIndex === -1) {
      throw new Error('支付记录不存在')
    }
    
    const updatedPayment = {
      ...this.mockPayments[paymentIndex],
      ...data,
      updatedAt: new Date().toISOString()
    }
    
    // 如果支付完成，更新可退金额
    if (data.status === 'completed' && this.mockPayments[paymentIndex].status !== 'completed') {
      updatedPayment.refundableAmount = { ...updatedPayment.amount }
    }
    
    this.mockPayments[paymentIndex] = updatedPayment
    return updatedPayment
  }

  async deletePayment(id: string): Promise<void> {
    await this.delay()
    
    const paymentIndex = this.mockPayments.findIndex(p => p.id === id)
    if (paymentIndex === -1) {
      throw new Error('支付记录不存在')
    }
    
    const payment = this.mockPayments[paymentIndex]
    
    // 只有待支付或失败的支付才能删除
    if (!['pending', 'failed', 'cancelled'].includes(payment.status)) {
      throw new Error('只有待支付、失败或已取消的支付记录才能删除')
    }
    
    this.mockPayments.splice(paymentIndex, 1)
  }

  async processPayment(id: string): Promise<PaymentResult> {
    await this.delay(1500) // 模拟网关处理时间
    
    const payment = await this.getPayment(id)
    
    if (payment.status !== 'pending') {
      throw new Error('只有待支付状态的订单才能进行支付')
    }
    
    // 模拟支付结果（80%成功率）
    const success = Math.random() > 0.2
    
    if (success) {
      const transactionId = `TXN-${Date.now()}`
      await this.updatePayment(id, {
        status: 'completed',
        transactionId,
        gatewayTransactionId: `GT-${Date.now()}`,
        paidAt: new Date().toISOString()
      })
      
      return {
        success: true,
        payment: await this.getPayment(id),
        message: '支付成功'
      }
    } else {
      await this.updatePayment(id, {
        status: 'failed',
        failureReason: '支付网关返回失败'
      })
      
      return {
        success: false,
        payment: await this.getPayment(id),
        message: '支付失败',
        errorCode: 'GATEWAY_ERROR'
      }
    }
  }

  async cancelPayment(id: string, reason?: string): Promise<void> {
    await this.updatePayment(id, {
      status: 'cancelled',
      failureReason: reason || '用户取消支付'
    })
  }

  async retryPayment(id: string): Promise<PaymentResult> {
    const payment = await this.getPayment(id)
    
    if (payment.status !== 'failed') {
      throw new Error('只有失败状态的支付才能重试')
    }
    
    // 重置为待支付状态
    await this.updatePayment(id, {
      status: 'pending',
      failureReason: undefined
    })
    
    return this.processPayment(id)
  }

  async markPaymentCompleted(id: string, transactionId: string): Promise<void> {
    await this.updatePayment(id, {
      status: 'completed',
      transactionId,
      paidAt: new Date().toISOString()
    })
  }

  async markPaymentFailed(id: string, reason: string): Promise<void> {
    await this.updatePayment(id, {
      status: 'failed',
      failureReason: reason
    })
  }

  // 退款相关方法
  async getRefunds(params?: RefundQueryParams): Promise<RefundListResponse> {
    await this.delay()
    
    let filteredRefunds = [...this.mockRefunds]
    
    if (params) {
      const { 
        refundNumber, 
        paymentId, 
        userId, 
        status,
        minAmount,
        maxAmount,
        startDate,
        endDate,
        page = 1, 
        pageSize = 10 
      } = params
      
      // 退款号码筛选
      if (refundNumber) {
        filteredRefunds = filteredRefunds.filter(refund => 
          refund.refundNumber.toLowerCase().includes(refundNumber.toLowerCase())
        )
      }
      
      // 支付ID筛选
      if (paymentId) {
        filteredRefunds = filteredRefunds.filter(refund => refund.paymentId === paymentId)
      }
      
      // 用户筛选 - 需要通过支付记录
      if (userId) {
        const userPaymentIds = this.mockPayments
          .filter(p => p.userId === userId)
          .map(p => p.id)
        filteredRefunds = filteredRefunds.filter(refund => 
          userPaymentIds.includes(refund.paymentId)
        )
      }
      
      // 状态筛选
      if (status) {
        filteredRefunds = filteredRefunds.filter(refund => refund.status === status)
      }
      
      // 金额范围筛选
      if (minAmount !== undefined) {
        filteredRefunds = filteredRefunds.filter(refund => refund.amount.amount >= minAmount)
      }
      
      if (maxAmount !== undefined) {
        filteredRefunds = filteredRefunds.filter(refund => refund.amount.amount <= maxAmount)
      }
      
      // 日期范围筛选
      if (startDate) {
        filteredRefunds = filteredRefunds.filter(refund => 
          new Date(refund.createdAt) >= new Date(startDate)
        )
      }
      
      if (endDate) {
        filteredRefunds = filteredRefunds.filter(refund => 
          new Date(refund.createdAt) <= new Date(endDate)
        )
      }
      
      // 分页
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      filteredRefunds = filteredRefunds.slice(startIndex, endIndex)
    }
    
    return {
      data: filteredRefunds,
      total: this.mockRefunds.length,
      page: params?.page || 1,
      pageSize: params?.pageSize || 10
    }
  }

  async getRefund(id: string): Promise<Refund> {
    await this.delay()
    
    const refund = this.mockRefunds.find(r => r.id === id)
    if (!refund) {
      throw new Error('退款记录不存在')
    }
    
    return refund
  }

  async createRefund(data: RefundRequest): Promise<RefundResult> {
    await this.delay()
    
    // 验证数据
    const validation = this.validateRefundRequest(data)
    if (!validation.valid) {
      throw new Error(`数据验证失败: ${validation.errors.map(e => e.message).join(', ')}`)
    }
    
    // 检查支付记录
    const payment = await this.getPayment(data.paymentId)
    
    if (payment.status !== 'completed') {
      throw new Error('只有已完成的支付才能申请退款')
    }
    
    if (payment.refundableAmount.amount < data.amount.amount) {
      throw new Error('退款金额超过可退款余额')
    }
    
    const refundNumber = this.generateRefundNumber()
    
    const newRefund: Refund = {
      id: `REF-${Date.now()}`,
      refundNumber,
      paymentId: data.paymentId,
      amount: data.amount,
      status: 'pending',
      reason: data.reason,
      notificationSent: false,
      metadata: data.metadata,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockRefunds.unshift(newRefund)
    
    return {
      success: true,
      refund: newRefund,
      amount: newRefund.amount,
      message: '退款申请提交成功'
    }
  }

  async approveRefund(id: string, approvedBy: string): Promise<RefundResult> {
    await this.delay()
    
    const refundIndex = this.mockRefunds.findIndex(r => r.id === id)
    if (refundIndex === -1) {
      throw new Error('退款记录不存在')
    }
    
    const refund = this.mockRefunds[refundIndex]
    if (refund.status !== 'pending') {
      throw new Error('只有待处理的退款才能批准')
    }
    
    // 更新退款状态
    const updatedRefund = {
      ...refund,
      status: 'approved' as RefundStatus,
      approvedBy,
      approvedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockRefunds[refundIndex] = updatedRefund
    
    return {
      success: true,
      refund: updatedRefund,
      amount: updatedRefund.amount,
      message: '退款已批准'
    }
  }

  async rejectRefund(id: string, reason: string, rejectedBy: string): Promise<RefundResult> {
    await this.delay()
    
    const refundIndex = this.mockRefunds.findIndex(r => r.id === id)
    if (refundIndex === -1) {
      throw new Error('退款记录不存在')
    }
    
    const refund = this.mockRefunds[refundIndex]
    if (refund.status !== 'pending') {
      throw new Error('只有待处理的退款才能拒绝')
    }
    
    // 更新退款状态
    const updatedRefund = {
      ...refund,
      status: 'rejected' as RefundStatus,
      rejectedReason: reason,
      updatedAt: new Date().toISOString()
    }
    
    this.mockRefunds[refundIndex] = updatedRefund
    
    return {
      success: true,
      refund: updatedRefund,
      amount: updatedRefund.amount,
      message: '退款已拒绝'
    }
  }

  async processRefund(id: string): Promise<RefundResult> {
    await this.delay(2000) // 模拟处理时间
    
    const refund = await this.getRefund(id)
    
    if (refund.status !== 'approved') {
      throw new Error('只有已批准的退款才能处理')
    }
    
    // 模拟退款处理（95%成功率）
    const success = Math.random() > 0.05
    
    if (success) {
      // 更新退款状态
      const updatedRefund = {
        ...refund,
        status: 'completed' as RefundStatus,
        gatewayRefundId: `RFD-${Date.now()}`,
        processedAt: new Date().toISOString(),
        notificationSent: true,
        updatedAt: new Date().toISOString()
      }
      
      const refundIndex = this.mockRefunds.findIndex(r => r.id === id)
      this.mockRefunds[refundIndex] = updatedRefund
      
      // 更新支付记录的退款金额
      const payment = await this.getPayment(refund.paymentId)
      const newRefundedAmount = payment.refundedAmount.amount + refund.amount.amount
      const newRefundableAmount = payment.refundableAmount.amount - refund.amount.amount
      
      let newStatus: ExtendedPaymentStatus = payment.status
      if (newRefundableAmount === 0) {
        newStatus = 'refunded'
      } else if (newRefundedAmount > 0) {
        newStatus = 'partial_refunded'
      }
      
      await this.updatePayment(refund.paymentId, {
        status: newStatus,
        refundedAmount: { amount: newRefundedAmount, currency: payment.amount.currency },
        refundableAmount: { amount: newRefundableAmount, currency: payment.amount.currency }
      })
      
      return {
        success: true,
        refund: updatedRefund,
        amount: updatedRefund.amount,
        message: '退款处理成功'
      }
    } else {
      const updatedRefund = {
        ...refund,
        status: 'failed' as RefundStatus,
        updatedAt: new Date().toISOString()
      }
      
      const refundIndex = this.mockRefunds.findIndex(r => r.id === id)
      this.mockRefunds[refundIndex] = updatedRefund
      
      return {
        success: false,
        refund: updatedRefund,
        amount: updatedRefund.amount,
        message: '退款处理失败',
        errorCode: 'GATEWAY_ERROR'
      }
    }
  }

  // 统计分析方法
  async getPaymentStatistics(startDate?: string, endDate?: string): Promise<PaymentStatistics> {
    await this.delay()
    
    let payments = this.mockPayments
    
    // 日期筛选
    if (startDate) {
      payments = payments.filter(p => new Date(p.createdAt) >= new Date(startDate))
    }
    
    if (endDate) {
      payments = payments.filter(p => new Date(p.createdAt) <= new Date(endDate))
    }
    
    // 计算统计数据
    const totalCount = payments.length
    const totalAmount = payments.reduce((sum, p) => sum + p.amount.amount, 0)
    
    const completedPayments = payments.filter(p => p.status === 'completed')
    const completedCount = completedPayments.length
    const completedAmount = completedPayments.reduce((sum, p) => sum + p.amount.amount, 0)
    
    const pendingPayments = payments.filter(p => p.status === 'pending')
    const pendingCount = pendingPayments.length
    const pendingAmount = pendingPayments.reduce((sum, p) => sum + p.amount.amount, 0)
    
    const failedCount = payments.filter(p => p.status === 'failed').length
    
    const refundedAmount = payments.reduce((sum, p) => sum + p.refundedAmount.amount, 0)
    const refundedCount = payments.filter(p => ['refunded', 'partial_refunded'].includes(p.status)).length
    
    const averageAmount = completedCount > 0 ? completedAmount / completedCount : 0
    const conversionRate = totalCount > 0 ? (completedCount / totalCount) * 100 : 0
    
    return {
      totalAmount: { amount: totalAmount, currency: 'CNY' },
      totalCount,
      completedAmount: { amount: completedAmount, currency: 'CNY' },
      completedCount,
      pendingAmount: { amount: pendingAmount, currency: 'CNY' },
      pendingCount,
      failedCount,
      refundedAmount: { amount: refundedAmount, currency: 'CNY' },
      refundedCount,
      averageAmount: { amount: averageAmount, currency: 'CNY' },
      conversionRate
    }
  }

  async getPaymentMethodStatistics(startDate?: string, endDate?: string): Promise<PaymentMethodStatistics[]> {
    await this.delay()
    
    let payments = this.mockPayments.filter(p => p.status === 'completed')
    
    // 日期筛选
    if (startDate) {
      payments = payments.filter(p => new Date(p.createdAt) >= new Date(startDate))
    }
    
    if (endDate) {
      payments = payments.filter(p => new Date(p.createdAt) <= new Date(endDate))
    }
    
    const totalAmount = payments.reduce((sum, p) => sum + p.amount.amount, 0)
    
    // 按支付方式分组统计
    const methodStats = new Map<PaymentMethodType, { amount: number; count: number }>()
    
    payments.forEach(payment => {
      const existing = methodStats.get(payment.paymentMethodType) || { amount: 0, count: 0 }
      existing.amount += payment.amount.amount
      existing.count += 1
      methodStats.set(payment.paymentMethodType, existing)
    })
    
    // 转换为数组并计算百分比
    const result: PaymentMethodStatistics[] = []
    methodStats.forEach((stats, method) => {
      result.push({
        paymentMethodType: method,
        amount: { amount: stats.amount, currency: 'CNY' },
        count: stats.count,
        percentage: totalAmount > 0 ? (stats.amount / totalAmount) * 100 : 0
      })
    })
    
    // 按金额降序排列
    result.sort((a, b) => b.amount.amount - a.amount.amount)
    
    return result
  }

  async getSupportedPaymentMethods(): Promise<PaymentMethodType[]> {
    await this.delay(200)
    return ['alipay', 'wechat', 'bank_card', 'credit_card', 'bank_transfer']
  }

  async getSupportedGateways(): Promise<PaymentGatewayType[]> {
    await this.delay(200)
    return ['alipay', 'wechat', 'unionpay', 'stripe']
  }

  // 验证方法
  validatePaymentRequest(data: CreatePaymentRequest): ValidationResult {
    const errors: Array<{ field: string; message: string }> = []
    
    // 验证用户ID
    if (!data.userId) {
      errors.push({ field: 'userId', message: '用户ID不能为空' })
    }
    
    // 验证用户信息
    if (!data.userInfo.name) {
      errors.push({ field: 'userInfo.name', message: '用户名称不能为空' })
    }
    
    if (!data.userInfo.email) {
      errors.push({ field: 'userInfo.email', message: '用户邮箱不能为空' })
    }
    
    // 验证金额
    if (!data.amount || data.amount.amount <= 0) {
      errors.push({ field: 'amount', message: '支付金额必须大于0' })
    }
    
    // 验证支付方式
    if (!data.paymentMethodType) {
      errors.push({ field: 'paymentMethodType', message: '支付方式不能为空' })
    }
    
    // 验证支付网关
    if (!data.gatewayType) {
      errors.push({ field: 'gatewayType', message: '支付网关不能为空' })
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }

  validateRefundRequest(data: RefundRequest): ValidationResult {
    const errors: Array<{ field: string; message: string }> = []
    
    // 验证支付ID
    if (!data.paymentId) {
      errors.push({ field: 'paymentId', message: '支付ID不能为空' })
    }
    
    // 验证退款金额
    if (!data.amount || data.amount.amount <= 0) {
      errors.push({ field: 'amount', message: '退款金额必须大于0' })
    }
    
    // 验证退款原因
    if (!data.reason || data.reason.trim().length < 5) {
      errors.push({ field: 'reason', message: '退款原因至少需要5个字符' })
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }

  // 私有工具方法
  private generatePaymentNumber(): string {
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const sequence = String(this.mockPayments.length + 1).padStart(4, '0')
    return `PAY-${year}${month}${day}-${sequence}`
  }

  private generateRefundNumber(): string {
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const sequence = String(this.mockRefunds.length + 1).padStart(4, '0')
    return `REF-${year}${month}${day}-${sequence}`
  }
}

// 导出服务实例
export const paymentService = new PaymentService()
export default paymentService