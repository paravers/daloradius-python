import { ref, computed, reactive } from 'vue'
import type {
  Invoice,
  CreateInvoiceRequest,
  UpdateInvoiceRequest,
  InvoiceQueryParams,
  InvoiceListResponse,
  InvoiceItem,
  Money,
  ValidationResult
} from '@/types/billing'
import { invoiceService, type IInvoiceService } from '@/services/invoiceService'

/**
 * 发票管理 - 发票列表组合式函数
 */
export function useInvoices(service: IInvoiceService = invoiceService) {
  // 状态管理
  const loading = ref(false)
  const invoices = ref<Invoice[]>([])
  const total = ref(0)
  const error = ref<string | null>(null)

  // 查询参数
  const queryParams = reactive<InvoiceQueryParams>({
    page: 1,
    pageSize: 10,
    invoiceNumber: '',
    userId: '',
    status: undefined,
    startDate: '',
    endDate: ''
  })

  // 计算属性
  const hasInvoices = computed(() => invoices.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / queryParams.pageSize))
  
  // 按状态分组统计
  const statusStats = computed(() => {
    const stats = {
      draft: 0,
      sent: 0,
      paid: 0,
      overdue: 0,
      cancelled: 0
    }
    
    invoices.value.forEach(invoice => {
      stats[invoice.status]++
    })
    
    return stats
  })
  
  // 总金额统计
  const totalAmount = computed(() => {
    return invoices.value.reduce((sum, invoice) => sum + invoice.total.amount, 0)
  })

  /**
   * 获取发票列表
   */
  async function fetchInvoices(params?: Partial<InvoiceQueryParams>) {
    try {
      loading.value = true
      error.value = null
      
      const searchParams = { ...queryParams, ...params }
      Object.assign(queryParams, searchParams)
      
      const response: InvoiceListResponse = await service.getInvoices(searchParams)
      
      invoices.value = response.data
      total.value = response.total
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取发票列表失败'
      console.error('获取发票列表失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个发票详情
   */
  async function fetchInvoice(id: string) {
    try {
      loading.value = true
      error.value = null
      
      const invoice = await service.getInvoice(id)
      
      // 更新列表中的对应发票
      const index = invoices.value.findIndex(inv => inv.id === id)
      if (index !== -1) {
        invoices.value[index] = invoice
      }
      
      return invoice
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取发票详情失败'
      console.error('获取发票详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建发票
   */
  async function createInvoice(data: CreateInvoiceRequest) {
    try {
      loading.value = true
      error.value = null
      
      const newInvoice = await service.createInvoice(data)
      
      // 添加到列表开头
      invoices.value.unshift(newInvoice)
      total.value += 1
      
      return newInvoice
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建发票失败'
      console.error('创建发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新发票
   */
  async function updateInvoice(id: string, data: UpdateInvoiceRequest) {
    try {
      loading.value = true
      error.value = null
      
      const updatedInvoice = await service.updateInvoice(id, data)
      
      // 更新列表中的对应发票
      const index = invoices.value.findIndex(inv => inv.id === id)
      if (index !== -1) {
        invoices.value[index] = updatedInvoice
      }
      
      return updatedInvoice
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新发票失败'
      console.error('更新发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除发票
   */
  async function deleteInvoice(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.deleteInvoice(id)
      
      // 从列表中移除
      const index = invoices.value.findIndex(inv => inv.id === id)
      if (index !== -1) {
        invoices.value.splice(index, 1)
        total.value -= 1
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除发票失败'
      console.error('删除发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 发送发票
   */
  async function sendInvoice(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.sendInvoice(id)
      
      // 更新本地状态
      const invoice = invoices.value.find(inv => inv.id === id)
      if (invoice) {
        invoice.status = 'sent'
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送发票失败'
      console.error('发送发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 标记为已付款
   */
  async function markPaid(id: string, paymentMethod?: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.markPaid(id, paymentMethod)
      
      // 更新本地状态
      const invoice = invoices.value.find(inv => inv.id === id)
      if (invoice) {
        invoice.status = 'paid'
        invoice.paidDate = new Date().toISOString()
        if (paymentMethod) {
          invoice.paymentMethod = paymentMethod
        }
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '标记付款失败'
      console.error('标记付款失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 标记为逾期
   */
  async function markOverdue(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.markOverdue(id)
      
      // 更新本地状态
      const invoice = invoices.value.find(inv => inv.id === id)
      if (invoice) {
        invoice.status = 'overdue'
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '标记逾期失败'
      console.error('标记逾期失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 取消发票
   */
  async function cancelInvoice(id: string, reason?: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.cancelInvoice(id, reason)
      
      // 更新本地状态
      const invoice = invoices.value.find(inv => inv.id === id)
      if (invoice) {
        invoice.status = 'cancelled'
        if (reason) {
          invoice.notes = `取消原因: ${reason}`
        }
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '取消发票失败'
      console.error('取消发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 搜索发票
   */
  function searchInvoices(searchTerm: string) {
    queryParams.invoiceNumber = searchTerm
    queryParams.page = 1
    return fetchInvoices()
  }

  /**
   * 筛选发票
   */
  function filterInvoices(filters: Partial<InvoiceQueryParams>) {
    Object.assign(queryParams, filters)
    queryParams.page = 1
    return fetchInvoices()
  }

  /**
   * 分页
   */
  function changePage(page: number) {
    queryParams.page = page
    return fetchInvoices()
  }

  /**
   * 改变页面大小
   */
  function changePageSize(pageSize: number) {
    queryParams.pageSize = pageSize
    queryParams.page = 1
    return fetchInvoices()
  }

  /**
   * 重置筛选条件
   */
  function resetFilters() {
    Object.assign(queryParams, {
      page: 1,
      pageSize: 10,
      invoiceNumber: '',
      userId: '',
      status: undefined,
      startDate: '',
      endDate: ''
    })
    return fetchInvoices()
  }

  /**
   * 刷新发票列表
   */
  function refreshInvoices() {
    return fetchInvoices()
  }

  /**
   * 批量删除发票
   */
  async function deleteInvoices(ids: string[]) {
    const results = await Promise.allSettled(
      ids.map(id => deleteInvoice(id))
    )
    
    const failed = results
      .map((result, index) => ({ result, id: ids[index] }))
      .filter(({ result }) => result.status === 'rejected')
    
    if (failed.length > 0) {
      const failedIds = failed.map(({ id }) => id)
      throw new Error(`删除失败的发票: ${failedIds.join(', ')}`)
    }
    
    return true
  }

  /**
   * 导出发票
   */
  async function exportInvoice(id: string, format: 'pdf' | 'excel') {
    try {
      loading.value = true
      error.value = null
      
      const blob = await service.exportInvoice(id, format)
      
      // 创建下载链接
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `invoice_${id}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导出发票失败'
      console.error('导出发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 验证发票数据
   */
  function validateInvoiceData(data: CreateInvoiceRequest): ValidationResult {
    return service.validateInvoiceData(data)
  }

  return {
    // 状态
    loading: readonly(loading),
    invoices: readonly(invoices),
    total: readonly(total),
    error: readonly(error),
    queryParams: readonly(queryParams),
    
    // 计算属性
    hasInvoices,
    totalPages,
    statusStats,
    totalAmount,
    
    // 方法
    fetchInvoices,
    fetchInvoice,
    createInvoice,
    updateInvoice,
    deleteInvoice,
    sendInvoice,
    markPaid,
    markOverdue,
    cancelInvoice,
    searchInvoices,
    filterInvoices,
    changePage,
    changePageSize,
    resetFilters,
    refreshInvoices,
    deleteInvoices,
    exportInvoice,
    validateInvoiceData
  }
}

/**
 * 发票管理 - 发票生成组合式函数
 */
export function useInvoiceGeneration(service: IInvoiceService = invoiceService) {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 生成发票
   */
  async function generateInvoice(userId: string, planId: string, usage?: any): Promise<Invoice> {
    try {
      loading.value = true
      error.value = null
      
      return await service.generateInvoice(userId, planId, usage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成发票失败'
      console.error('生成发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 重新生成发票
   */
  async function regenerateInvoice(id: string): Promise<Invoice> {
    try {
      loading.value = true
      error.value = null
      
      return await service.regenerateInvoice(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '重新生成发票失败'
      console.error('重新生成发票失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    generateInvoice,
    regenerateInvoice
  }
}

/**
 * 发票管理 - 发票项目管理组合式函数
 */
export function useInvoiceItems(service: IInvoiceService = invoiceService) {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const items = ref<InvoiceItem[]>([])

  /**
   * 获取发票项目
   */
  async function fetchInvoiceItems(invoiceId: string): Promise<InvoiceItem[]> {
    try {
      loading.value = true
      error.value = null
      
      const itemList = await service.getInvoiceItems(invoiceId)
      items.value = itemList
      
      return itemList
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取发票项目失败'
      console.error('获取发票项目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加发票项目
   */
  async function addInvoiceItem(invoiceId: string, item: Omit<InvoiceItem, 'id' | 'invoiceId'>): Promise<InvoiceItem> {
    try {
      loading.value = true
      error.value = null
      
      const newItem = await service.addInvoiceItem(invoiceId, item)
      items.value.push(newItem)
      
      return newItem
    } catch (err) {
      error.value = err instanceof Error ? err.message : '添加发票项目失败'
      console.error('添加发票项目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新发票项目
   */
  async function updateInvoiceItem(invoiceId: string, itemId: string, updates: Partial<InvoiceItem>): Promise<InvoiceItem> {
    try {
      loading.value = true
      error.value = null
      
      const updatedItem = await service.updateInvoiceItem(invoiceId, itemId, updates)
      
      const index = items.value.findIndex(item => item.id === itemId)
      if (index !== -1) {
        items.value[index] = updatedItem
      }
      
      return updatedItem
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新发票项目失败'
      console.error('更新发票项目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除发票项目
   */
  async function removeInvoiceItem(invoiceId: string, itemId: string): Promise<void> {
    try {
      loading.value = true
      error.value = null
      
      await service.removeInvoiceItem(invoiceId, itemId)
      
      const index = items.value.findIndex(item => item.id === itemId)
      if (index !== -1) {
        items.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除发票项目失败'
      console.error('删除发票项目失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    items: readonly(items),
    fetchInvoiceItems,
    addInvoiceItem,
    updateInvoiceItem,
    removeInvoiceItem
  }
}

// 导入 readonly 函数
import { readonly } from 'vue'