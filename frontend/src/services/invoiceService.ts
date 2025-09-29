import type {
  Invoice,
  CreateInvoiceRequest,
  UpdateInvoiceRequest,
  InvoiceQueryParams,
  InvoiceListResponse,
  InvoiceItem,
  Money,
  TaxRule,
  Discount,
  ValidationResult
} from '@/types/billing'

/**
 * 发票服务接口
 */
export interface IInvoiceService {
  // 发票 CRUD 操作
  getInvoices(params?: InvoiceQueryParams): Promise<InvoiceListResponse>
  getInvoice(id: string): Promise<Invoice>
  createInvoice(data: CreateInvoiceRequest): Promise<Invoice>
  updateInvoice(id: string, data: UpdateInvoiceRequest): Promise<Invoice>
  deleteInvoice(id: string): Promise<void>
  
  // 发票状态管理
  sendInvoice(id: string): Promise<void>
  markPaid(id: string, paymentMethod?: string): Promise<void>
  markOverdue(id: string): Promise<void>
  cancelInvoice(id: string, reason?: string): Promise<void>
  
  // 发票生成
  generateInvoice(userId: string, planId: string, usage?: any): Promise<Invoice>
  regenerateInvoice(id: string): Promise<Invoice>
  
  // 发票项目管理
  getInvoiceItems(invoiceId: string): Promise<InvoiceItem[]>
  addInvoiceItem(invoiceId: string, item: Omit<InvoiceItem, 'id' | 'invoiceId'>): Promise<InvoiceItem>
  updateInvoiceItem(invoiceId: string, itemId: string, updates: Partial<InvoiceItem>): Promise<InvoiceItem>
  removeInvoiceItem(invoiceId: string, itemId: string): Promise<void>
  
  // 金额计算
  calculateSubtotal(items: InvoiceItem[]): Money
  calculateTax(subtotal: Money, taxRules: TaxRule[]): Money
  calculateDiscount(subtotal: Money, discounts: Discount[]): Money
  calculateTotal(subtotal: Money, tax: Money, discount: Money): Money
  
  // 发票导出
  exportInvoice(id: string, format: 'pdf' | 'excel'): Promise<Blob>
  
  // 验证
  validateInvoiceData(data: CreateInvoiceRequest): ValidationResult
}

/**
 * 模拟发票服务实现
 */
class InvoiceService implements IInvoiceService {
  private mockInvoices: Invoice[] = [
    {
      id: 'INV-2024-001',
      invoiceNumber: 'INV-2024-001',
      userId: 'user1',
      userInfo: {
        name: '张三',
        email: 'zhangsan@example.com',
        phone: '13800138000',
        address: '北京市朝阳区xxx街道xxx号'
      },
      status: 'paid',
      issueDate: '2024-01-15T00:00:00Z',
      dueDate: '2024-02-15T00:00:00Z',
      paidDate: '2024-01-20T10:30:00Z',
      items: [
        {
          id: 'item1',
          invoiceId: 'INV-2024-001',
          description: '基础套餐月租费',
          quantity: 1,
          unitPrice: { amount: 50.00, currency: 'CNY' },
          total: { amount: 50.00, currency: 'CNY' },
          period: {
            start: '2024-01-01T00:00:00Z',
            end: '2024-01-31T23:59:59Z'
          }
        },
        {
          id: 'item2',
          invoiceId: 'INV-2024-001',
          description: '超额流量费',
          quantity: 5,
          unitPrice: { amount: 0.10, currency: 'CNY' },
          total: { amount: 0.50, currency: 'CNY' },
          period: {
            start: '2024-01-01T00:00:00Z',
            end: '2024-01-31T23:59:59Z'
          }
        }
      ],
      subtotal: { amount: 50.50, currency: 'CNY' },
      taxAmount: { amount: 3.03, currency: 'CNY' },
      discountAmount: { amount: 0.00, currency: 'CNY' },
      total: { amount: 53.53, currency: 'CNY' },
      taxRules: [
        {
          name: '增值税',
          rate: 0.06,
          type: 'percentage'
        }
      ],
      discounts: [],
      notes: '感谢您使用我们的服务',
      createdAt: '2024-01-15T00:00:00Z',
      updatedAt: '2024-01-20T10:30:00Z'
    },
    {
      id: 'INV-2024-002',
      invoiceNumber: 'INV-2024-002',
      userId: 'user2',
      userInfo: {
        name: '李四',
        email: 'lisi@example.com',
        phone: '13900139000',
        address: '上海市浦东新区xxx路xxx号'
      },
      status: 'sent',
      issueDate: '2024-01-20T00:00:00Z',
      dueDate: '2024-02-20T00:00:00Z',
      items: [
        {
          id: 'item3',
          invoiceId: 'INV-2024-002',
          description: '企业套餐月租费',
          quantity: 1,
          unitPrice: { amount: 200.00, currency: 'CNY' },
          total: { amount: 200.00, currency: 'CNY' },
          period: {
            start: '2024-01-01T00:00:00Z',
            end: '2024-01-31T23:59:59Z'
          }
        }
      ],
      subtotal: { amount: 200.00, currency: 'CNY' },
      taxAmount: { amount: 12.00, currency: 'CNY' },
      discountAmount: { amount: 20.00, currency: 'CNY' },
      total: { amount: 192.00, currency: 'CNY' },
      taxRules: [
        {
          name: '增值税',
          rate: 0.06,
          type: 'percentage'
        }
      ],
      discounts: [
        {
          name: '新用户优惠',
          amount: { amount: 20.00, currency: 'CNY' },
          type: 'fixed'
        }
      ],
      createdAt: '2024-01-20T00:00:00Z',
      updatedAt: '2024-01-20T00:00:00Z'
    },
    {
      id: 'INV-2024-003',
      invoiceNumber: 'INV-2024-003',
      userId: 'user3',
      userInfo: {
        name: '王五',
        email: 'wangwu@example.com',
        phone: '13700137000',
        address: '广州市天河区xxx大道xxx号'
      },
      status: 'overdue',
      issueDate: '2024-01-10T00:00:00Z',
      dueDate: '2024-01-25T00:00:00Z',
      items: [
        {
          id: 'item4',
          invoiceId: 'INV-2024-003',
          description: '按量计费',
          quantity: 15.5,
          unitPrice: { amount: 0.02, currency: 'CNY' },
          total: { amount: 0.31, currency: 'CNY' },
          period: {
            start: '2024-01-01T00:00:00Z',
            end: '2024-01-31T23:59:59Z'
          }
        }
      ],
      subtotal: { amount: 0.31, currency: 'CNY' },
      taxAmount: { amount: 0.02, currency: 'CNY' },
      discountAmount: { amount: 0.00, currency: 'CNY' },
      total: { amount: 0.33, currency: 'CNY' },
      taxRules: [
        {
          name: '增值税',
          rate: 0.06,
          type: 'percentage'
        }
      ],
      discounts: [],
      createdAt: '2024-01-10T00:00:00Z',
      updatedAt: '2024-01-10T00:00:00Z'
    }
  ]

  private delay(ms: number = 800): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async getInvoices(params?: InvoiceQueryParams): Promise<InvoiceListResponse> {
    await this.delay()
    
    let filteredInvoices = [...this.mockInvoices]
    
    if (params) {
      const { 
        invoiceNumber, 
        userId, 
        status, 
        startDate, 
        endDate,
        page = 1, 
        pageSize = 10 
      } = params
      
      // 发票号码筛选
      if (invoiceNumber) {
        filteredInvoices = filteredInvoices.filter(invoice => 
          invoice.invoiceNumber.toLowerCase().includes(invoiceNumber.toLowerCase())
        )
      }
      
      // 用户筛选
      if (userId) {
        filteredInvoices = filteredInvoices.filter(invoice => invoice.userId === userId)
      }
      
      // 状态筛选
      if (status) {
        filteredInvoices = filteredInvoices.filter(invoice => invoice.status === status)
      }
      
      // 日期范围筛选
      if (startDate) {
        filteredInvoices = filteredInvoices.filter(invoice => 
          new Date(invoice.issueDate) >= new Date(startDate)
        )
      }
      
      if (endDate) {
        filteredInvoices = filteredInvoices.filter(invoice => 
          new Date(invoice.issueDate) <= new Date(endDate)
        )
      }
      
      // 分页
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      filteredInvoices = filteredInvoices.slice(startIndex, endIndex)
    }
    
    return {
      data: filteredInvoices,
      total: this.mockInvoices.length,
      page: params?.page || 1,
      pageSize: params?.pageSize || 10
    }
  }

  async getInvoice(id: string): Promise<Invoice> {
    await this.delay()
    
    const invoice = this.mockInvoices.find(inv => inv.id === id)
    if (!invoice) {
      throw new Error('发票不存在')
    }
    
    return invoice
  }

  async createInvoice(data: CreateInvoiceRequest): Promise<Invoice> {
    await this.delay()
    
    // 验证数据
    const validation = this.validateInvoiceData(data)
    if (!validation.valid) {
      throw new Error(`数据验证失败: ${validation.errors.map(e => e.message).join(', ')}`)
    }
    
    // 生成发票号
    const invoiceNumber = this.generateInvoiceNumber()
    
    // 计算金额
    const subtotal = this.calculateSubtotal(data.items)
    const taxAmount = this.calculateTax(subtotal, data.taxRules || [])
    const discountAmount = this.calculateDiscount(subtotal, data.discounts || [])
    const total = this.calculateTotal(subtotal, taxAmount, discountAmount)
    
    const newInvoice: Invoice = {
      id: `INV-${Date.now()}`,
      invoiceNumber,
      userId: data.userId,
      userInfo: data.userInfo,
      status: 'draft',
      issueDate: new Date().toISOString(),
      dueDate: data.dueDate,
      items: data.items.map((item, index) => ({
        ...item,
        id: `item_${Date.now()}_${index}`,
        invoiceId: `INV-${Date.now()}`
      })),
      subtotal,
      taxAmount,
      discountAmount,
      total,
      taxRules: data.taxRules || [],
      discounts: data.discounts || [],
      notes: data.notes,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockInvoices.unshift(newInvoice)
    return newInvoice
  }

  async updateInvoice(id: string, data: UpdateInvoiceRequest): Promise<Invoice> {
    await this.delay()
    
    const invoiceIndex = this.mockInvoices.findIndex(inv => inv.id === id)
    if (invoiceIndex === -1) {
      throw new Error('发票不存在')
    }
    
    const invoice = this.mockInvoices[invoiceIndex]
    
    // 只有草稿状态的发票才能编辑
    if (invoice.status !== 'draft') {
      throw new Error('只有草稿状态的发票才能编辑')
    }
    
    const updatedInvoice = {
      ...invoice,
      ...data,
      updatedAt: new Date().toISOString()
    }
    
    // 重新计算金额
    if (data.items) {
      const subtotal = this.calculateSubtotal(data.items)
      const taxAmount = this.calculateTax(subtotal, updatedInvoice.taxRules)
      const discountAmount = this.calculateDiscount(subtotal, updatedInvoice.discounts)
      const total = this.calculateTotal(subtotal, taxAmount, discountAmount)
      
      updatedInvoice.subtotal = subtotal
      updatedInvoice.taxAmount = taxAmount
      updatedInvoice.discountAmount = discountAmount
      updatedInvoice.total = total
    }
    
    this.mockInvoices[invoiceIndex] = updatedInvoice
    return updatedInvoice
  }

  async deleteInvoice(id: string): Promise<void> {
    await this.delay()
    
    const invoiceIndex = this.mockInvoices.findIndex(inv => inv.id === id)
    if (invoiceIndex === -1) {
      throw new Error('发票不存在')
    }
    
    const invoice = this.mockInvoices[invoiceIndex]
    
    // 只有草稿状态的发票才能删除
    if (invoice.status !== 'draft') {
      throw new Error('只有草稿状态的发票才能删除')
    }
    
    this.mockInvoices.splice(invoiceIndex, 1)
  }

  async sendInvoice(id: string): Promise<void> {
    await this.updateInvoice(id, { status: 'sent' })
  }

  async markPaid(id: string, paymentMethod?: string): Promise<void> {
    await this.updateInvoice(id, { 
      status: 'paid',
      paidDate: new Date().toISOString(),
      paymentMethod
    })
  }

  async markOverdue(id: string): Promise<void> {
    await this.updateInvoice(id, { status: 'overdue' })
  }

  async cancelInvoice(id: string, reason?: string): Promise<void> {
    await this.updateInvoice(id, { 
      status: 'cancelled',
      notes: reason ? `取消原因: ${reason}` : '已取消'
    })
  }

  async generateInvoice(userId: string, planId: string, usage?: any): Promise<Invoice> {
    await this.delay()
    
    // 模拟根据用户和计划生成发票
    const mockUserInfo = {
      name: '系统生成用户',
      email: `user${userId}@example.com`,
      phone: '13800138000',
      address: '系统生成地址'
    }
    
    const mockItems: Omit<InvoiceItem, 'id' | 'invoiceId'>[] = [
      {
        description: '自动生成费用',
        quantity: 1,
        unitPrice: { amount: 100.00, currency: 'CNY' },
        total: { amount: 100.00, currency: 'CNY' },
        period: {
          start: new Date().toISOString(),
          end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
        }
      }
    ]
    
    return this.createInvoice({
      userId,
      userInfo: mockUserInfo,
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      items: mockItems,
      taxRules: [{ name: '增值税', rate: 0.06, type: 'percentage' }],
      discounts: []
    })
  }

  async regenerateInvoice(id: string): Promise<Invoice> {
    const invoice = await this.getInvoice(id)
    return this.createInvoice({
      userId: invoice.userId,
      userInfo: invoice.userInfo,
      dueDate: invoice.dueDate,
      items: invoice.items.map(({ id, invoiceId, ...item }) => item),
      taxRules: invoice.taxRules,
      discounts: invoice.discounts,
      notes: invoice.notes
    })
  }

  async getInvoiceItems(invoiceId: string): Promise<InvoiceItem[]> {
    const invoice = await this.getInvoice(invoiceId)
    return invoice.items
  }

  async addInvoiceItem(invoiceId: string, item: Omit<InvoiceItem, 'id' | 'invoiceId'>): Promise<InvoiceItem> {
    const invoice = await this.getInvoice(invoiceId)
    
    const newItem: InvoiceItem = {
      ...item,
      id: `item_${Date.now()}`,
      invoiceId
    }
    
    invoice.items.push(newItem)
    await this.updateInvoice(invoiceId, { items: invoice.items })
    
    return newItem
  }

  async updateInvoiceItem(invoiceId: string, itemId: string, updates: Partial<InvoiceItem>): Promise<InvoiceItem> {
    const invoice = await this.getInvoice(invoiceId)
    
    const itemIndex = invoice.items.findIndex(item => item.id === itemId)
    if (itemIndex === -1) {
      throw new Error('发票项目不存在')
    }
    
    const updatedItem = { ...invoice.items[itemIndex], ...updates }
    invoice.items[itemIndex] = updatedItem
    
    await this.updateInvoice(invoiceId, { items: invoice.items })
    
    return updatedItem
  }

  async removeInvoiceItem(invoiceId: string, itemId: string): Promise<void> {
    const invoice = await this.getInvoice(invoiceId)
    
    const itemIndex = invoice.items.findIndex(item => item.id === itemId)
    if (itemIndex === -1) {
      throw new Error('发票项目不存在')
    }
    
    invoice.items.splice(itemIndex, 1)
    await this.updateInvoice(invoiceId, { items: invoice.items })
  }

  calculateSubtotal(items: InvoiceItem[]): Money {
    const total = items.reduce((sum, item) => sum + item.total.amount, 0)
    return {
      amount: Math.round(total * 100) / 100,
      currency: items[0]?.total.currency || 'CNY'
    }
  }

  calculateTax(subtotal: Money, taxRules: TaxRule[]): Money {
    const totalTax = taxRules.reduce((sum, rule) => {
      if (rule.type === 'percentage') {
        return sum + subtotal.amount * rule.rate
      } else {
        return sum + rule.rate // 固定金额税
      }
    }, 0)
    
    return {
      amount: Math.round(totalTax * 100) / 100,
      currency: subtotal.currency
    }
  }

  calculateDiscount(subtotal: Money, discounts: Discount[]): Money {
    const totalDiscount = discounts.reduce((sum, discount) => {
      if (discount.type === 'percentage') {
        return sum + subtotal.amount * (discount.percentage! / 100)
      } else {
        return sum + discount.amount!.amount
      }
    }, 0)
    
    return {
      amount: Math.round(totalDiscount * 100) / 100,
      currency: subtotal.currency
    }
  }

  calculateTotal(subtotal: Money, tax: Money, discount: Money): Money {
    const total = subtotal.amount + tax.amount - discount.amount
    return {
      amount: Math.max(0, Math.round(total * 100) / 100),
      currency: subtotal.currency
    }
  }

  async exportInvoice(id: string, format: 'pdf' | 'excel'): Promise<Blob> {
    await this.delay()
    
    // 模拟生成文件
    const content = `发票导出 - ${id} - ${format} 格式`
    return new Blob([content], { 
      type: format === 'pdf' ? 'application/pdf' : 'application/vnd.ms-excel'
    })
  }

  validateInvoiceData(data: CreateInvoiceRequest): ValidationResult {
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
    
    // 验证到期日期
    const dueDate = new Date(data.dueDate)
    if (isNaN(dueDate.getTime())) {
      errors.push({ field: 'dueDate', message: '无效的到期日期格式' })
    }
    
    // 验证发票项目
    if (!data.items || data.items.length === 0) {
      errors.push({ field: 'items', message: '至少需要一个发票项目' })
    } else {
      data.items.forEach((item, index) => {
        if (!item.description) {
          errors.push({ field: `items[${index}].description`, message: '项目描述不能为空' })
        }
        
        if (item.quantity <= 0) {
          errors.push({ field: `items[${index}].quantity`, message: '项目数量必须大于0' })
        }
        
        if (item.unitPrice.amount < 0) {
          errors.push({ field: `items[${index}].unitPrice`, message: '项目单价不能为负数' })
        }
      })
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }

  private generateInvoiceNumber(): string {
    const year = new Date().getFullYear()
    const sequence = String(this.mockInvoices.length + 1).padStart(3, '0')
    return `INV-${year}-${sequence}`
  }
}

// 导出服务实例
export const invoiceService = new InvoiceService()
export default invoiceService