import { ref, computed, reactive } from 'vue'
import type {
  PaymentRecord,
  Refund,
  CreatePaymentRequest,
  UpdatePaymentRequest,
  RefundRequest,
  ExtendedPaymentQueryParams,
  RefundQueryParams,
  PaymentRecordListResponse,
  RefundListResponse,
  PaymentResult,
  RefundResult,
  PaymentStatistics,
  PaymentMethodStatistics,
  ExtendedPaymentStatus,
  RefundStatus,
  PaymentMethodType,
  PaymentGatewayType
} from '@/types/billing'
import { paymentService } from '@/services/paymentService'

/**
 * 支付管理 Composable
 */
export function usePayments() {
  // 响应式状态
  const payments = ref<PaymentRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 分页状态
  const pagination = reactive({
    page: 1,
    pageSize: 10
  })
  
  // 查询参数
  const queryParams = reactive<ExtendedPaymentQueryParams>({
    page: pagination.page,
    pageSize: pagination.pageSize
  })
  
  // 支付统计
  const statistics = ref<PaymentStatistics>()
  const methodStatistics = ref<PaymentMethodStatistics[]>([])
  
  /**
   * 加载支付列表
   */
  const loadPayments = async (params?: Partial<ExtendedPaymentQueryParams>) => {
    try {
      loading.value = true
      error.value = null
      
      // 合并查询参数
      const mergedParams = {
        ...queryParams,
        ...params,
        page: pagination.page,
        pageSize: pagination.pageSize
      }
      
      const response: PaymentRecordListResponse = await paymentService.getPayments(mergedParams)
      
      payments.value = response.data
      total.value = response.total
      
      return response
    } catch (err: any) {
      error.value = err.message || '加载支付列表失败'
      console.error('Load payments error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取单个支付记录
   */
  const getPayment = async (id: string): Promise<PaymentRecord> => {
    try {
      loading.value = true
      error.value = null
      
      const payment = await paymentService.getPayment(id)
      
      // 更新本地缓存
      const index = payments.value.findIndex(p => p.id === id)
      if (index !== -1) {
        payments.value[index] = payment
      }
      
      return payment
    } catch (err: any) {
      error.value = err.message || '获取支付记录失败'
      console.error('Get payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建支付
   */
  const createPayment = async (data: CreatePaymentRequest): Promise<PaymentResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.createPayment(data)
      
      if (result.success) {
        // 刷新列表
        await loadPayments()
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '创建支付失败'
      console.error('Create payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 更新支付
   */
  const updatePayment = async (id: string, data: UpdatePaymentRequest): Promise<PaymentRecord> => {
    try {
      loading.value = true
      error.value = null
      
      const payment = await paymentService.updatePayment(id, data)
      
      // 更新本地缓存
      const index = payments.value.findIndex(p => p.id === id)
      if (index !== -1) {
        payments.value[index] = payment
      }
      
      return payment
    } catch (err: any) {
      error.value = err.message || '更新支付失败'
      console.error('Update payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 删除支付
   */
  const deletePayment = async (id: string): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      await paymentService.deletePayment(id)
      
      // 从本地缓存移除
      const index = payments.value.findIndex(p => p.id === id)
      if (index !== -1) {
        payments.value.splice(index, 1)
        total.value -= 1
      }
    } catch (err: any) {
      error.value = err.message || '删除支付失败'
      console.error('Delete payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 处理支付
   */
  const processPayment = async (id: string): Promise<PaymentResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.processPayment(id)
      
      // 更新本地缓存
      if (result.payment) {
        const index = payments.value.findIndex(p => p.id === id)
        if (index !== -1) {
          payments.value[index] = result.payment
        }
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '支付处理失败'
      console.error('Process payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 取消支付
   */
  const cancelPayment = async (id: string, reason?: string): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      await paymentService.cancelPayment(id, reason)
      
      // 刷新支付记录
      await getPayment(id)
    } catch (err: any) {
      error.value = err.message || '取消支付失败'
      console.error('Cancel payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 重试支付
   */
  const retryPayment = async (id: string): Promise<PaymentResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.retryPayment(id)
      
      // 更新本地缓存
      if (result.payment) {
        const index = payments.value.findIndex(p => p.id === id)
        if (index !== -1) {
          payments.value[index] = result.payment
        }
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '重试支付失败'
      console.error('Retry payment error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 加载支付统计
   */
  const loadStatistics = async (startDate?: string, endDate?: string) => {
    try {
      const [stats, methodStats] = await Promise.all([
        paymentService.getPaymentStatistics(startDate, endDate),
        paymentService.getPaymentMethodStatistics(startDate, endDate)
      ])
      
      statistics.value = stats
      methodStatistics.value = methodStats
      
      return { statistics: stats, methodStatistics: methodStats }
    } catch (err: any) {
      error.value = err.message || '加载统计数据失败'
      console.error('Load statistics error:', err)
      throw err
    }
  }
  
  /**
   * 获取支持的支付方式
   */
  const getSupportedPaymentMethods = async (): Promise<PaymentMethodType[]> => {
    try {
      return await paymentService.getSupportedPaymentMethods()
    } catch (err: any) {
      error.value = err.message || '获取支付方式失败'
      console.error('Get payment methods error:', err)
      throw err
    }
  }
  
  /**
   * 获取支持的支付网关
   */
  const getSupportedGateways = async (): Promise<PaymentGatewayType[]> => {
    try {
      return await paymentService.getSupportedGateways()
    } catch (err: any) {
      error.value = err.message || '获取支付网关失败'
      console.error('Get gateways error:', err)
      throw err
    }
  }
  
  /**
   * 筛选方法
   */
  const filterByStatus = (status: ExtendedPaymentStatus) => {
    queryParams.status = status
    pagination.page = 1
    loadPayments()
  }
  
  const filterByPaymentMethod = (paymentMethodType: PaymentMethodType) => {
    queryParams.paymentMethodType = paymentMethodType
    pagination.page = 1
    loadPayments()
  }
  
  const filterByDateRange = (startDate: string, endDate: string) => {
    queryParams.startDate = startDate
    queryParams.endDate = endDate
    pagination.page = 1
    loadPayments()
  }
  
  const clearFilters = () => {
    Object.keys(queryParams).forEach(key => {
      if (!['page', 'pageSize'].includes(key)) {
        delete (queryParams as any)[key]
      }
    })
    pagination.page = 1
    loadPayments()
  }
  
  /**
   * 分页方法
   */
  const nextPage = () => {
    if (hasNextPage.value) {
      pagination.page += 1
      loadPayments()
    }
  }
  
  const prevPage = () => {
    if (hasPrevPage.value) {
      pagination.page -= 1
      loadPayments()
    }
  }
  
  const setPage = (page: number) => {
    pagination.page = page
    loadPayments()
  }
  
  const setPageSize = (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadPayments()
  }
  
  // 计算属性
  const hasNextPage = computed(() => {
    return pagination.page * pagination.pageSize < total.value
  })
  
  const hasPrevPage = computed(() => {
    return pagination.page > 1
  })
  
  const totalPages = computed(() => {
    return Math.ceil(total.value / pagination.pageSize)
  })
  
  const startIndex = computed(() => {
    return (pagination.page - 1) * pagination.pageSize + 1
  })
  
  const endIndex = computed(() => {
    return Math.min(pagination.page * pagination.pageSize, total.value)
  })
  
  // 返回公共接口
  return {
    // 状态
    payments,
    total,
    loading,
    error,
    pagination,
    queryParams,
    statistics,
    methodStatistics,
    
    // 方法
    loadPayments,
    getPayment,
    createPayment,
    updatePayment,
    deletePayment,
    processPayment,
    cancelPayment,
    retryPayment,
    loadStatistics,
    getSupportedPaymentMethods,
    getSupportedGateways,
    
    // 筛选方法
    filterByStatus,
    filterByPaymentMethod,
    filterByDateRange,
    clearFilters,
    
    // 分页方法
    nextPage,
    prevPage,
    setPage,
    setPageSize,
    
    // 计算属性
    hasNextPage,
    hasPrevPage,
    totalPages,
    startIndex,
    endIndex
  }
}

/**
 * 退款管理 Composable
 */
export function useRefunds() {
  // 响应式状态
  const refunds = ref<Refund[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 分页状态
  const pagination = reactive({
    page: 1,
    pageSize: 10
  })
  
  // 查询参数
  const queryParams = reactive<RefundQueryParams>({
    page: pagination.page,
    pageSize: pagination.pageSize
  })
  
  /**
   * 加载退款列表
   */
  const loadRefunds = async (params?: Partial<RefundQueryParams>) => {
    try {
      loading.value = true
      error.value = null
      
      // 合并查询参数
      const mergedParams = {
        ...queryParams,
        ...params,
        page: pagination.page,
        pageSize: pagination.pageSize
      }
      
      const response: RefundListResponse = await paymentService.getRefunds(mergedParams)
      
      refunds.value = response.data
      total.value = response.total
      
      return response
    } catch (err: any) {
      error.value = err.message || '加载退款列表失败'
      console.error('Load refunds error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取单个退款记录
   */
  const getRefund = async (id: string): Promise<Refund> => {
    try {
      loading.value = true
      error.value = null
      
      const refund = await paymentService.getRefund(id)
      
      // 更新本地缓存
      const index = refunds.value.findIndex(r => r.id === id)
      if (index !== -1) {
        refunds.value[index] = refund
      }
      
      return refund
    } catch (err: any) {
      error.value = err.message || '获取退款记录失败'
      console.error('Get refund error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建退款申请
   */
  const createRefund = async (data: RefundRequest): Promise<RefundResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.createRefund(data)
      
      if (result.success) {
        // 刷新列表
        await loadRefunds()
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '创建退款申请失败'
      console.error('Create refund error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 批准退款
   */
  const approveRefund = async (id: string, approvedBy: string): Promise<RefundResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.approveRefund(id, approvedBy)
      
      // 更新本地缓存
      if (result.refund) {
        const index = refunds.value.findIndex(r => r.id === id)
        if (index !== -1) {
          refunds.value[index] = result.refund
        }
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '批准退款失败'
      console.error('Approve refund error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 拒绝退款
   */
  const rejectRefund = async (id: string, reason: string, rejectedBy: string): Promise<RefundResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.rejectRefund(id, reason, rejectedBy)
      
      // 更新本地缓存
      if (result.refund) {
        const index = refunds.value.findIndex(r => r.id === id)
        if (index !== -1) {
          refunds.value[index] = result.refund
        }
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '拒绝退款失败'
      console.error('Reject refund error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 处理退款
   */
  const processRefund = async (id: string): Promise<RefundResult> => {
    try {
      loading.value = true
      error.value = null
      
      const result = await paymentService.processRefund(id)
      
      // 更新本地缓存
      if (result.refund) {
        const index = refunds.value.findIndex(r => r.id === id)
        if (index !== -1) {
          refunds.value[index] = result.refund
        }
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || '处理退款失败'
      console.error('Process refund error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 筛选方法
   */
  const filterByStatus = (status: RefundStatus) => {
    queryParams.status = status
    pagination.page = 1
    loadRefunds()
  }
  
  const filterByPaymentId = (paymentId: string) => {
    queryParams.paymentId = paymentId
    pagination.page = 1
    loadRefunds()
  }
  
  const filterByDateRange = (startDate: string, endDate: string) => {
    queryParams.startDate = startDate
    queryParams.endDate = endDate
    pagination.page = 1
    loadRefunds()
  }
  
  const clearFilters = () => {
    Object.keys(queryParams).forEach(key => {
      if (!['page', 'pageSize'].includes(key)) {
        delete (queryParams as any)[key]
      }
    })
    pagination.page = 1
    loadRefunds()
  }
  
  /**
   * 分页方法
   */
  const nextPage = () => {
    if (hasNextPage.value) {
      pagination.page += 1
      loadRefunds()
    }
  }
  
  const prevPage = () => {
    if (hasPrevPage.value) {
      pagination.page -= 1
      loadRefunds()
    }
  }
  
  const setPage = (page: number) => {
    pagination.page = page
    loadRefunds()
  }
  
  const setPageSize = (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadRefunds()
  }
  
  // 计算属性
  const hasNextPage = computed(() => {
    return pagination.page * pagination.pageSize < total.value
  })
  
  const hasPrevPage = computed(() => {
    return pagination.page > 1
  })
  
  const totalPages = computed(() => {
    return Math.ceil(total.value / pagination.pageSize)
  })
  
  const startIndex = computed(() => {
    return (pagination.page - 1) * pagination.pageSize + 1
  })
  
  const endIndex = computed(() => {
    return Math.min(pagination.page * pagination.pageSize, total.value)
  })
  
  // 返回公共接口
  return {
    // 状态
    refunds,
    total,
    loading,
    error,
    pagination,
    queryParams,
    
    // 方法
    loadRefunds,
    getRefund,
    createRefund,
    approveRefund,
    rejectRefund,
    processRefund,
    
    // 筛选方法
    filterByStatus,
    filterByPaymentId,
    filterByDateRange,
    clearFilters,
    
    // 分页方法
    nextPage,
    prevPage,
    setPage,
    setPageSize,
    
    // 计算属性
    hasNextPage,
    hasPrevPage,
    totalPages,
    startIndex,
    endIndex
  }
}

export default { usePayments, useRefunds }