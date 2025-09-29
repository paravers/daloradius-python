import type {
  BillingPlan,
  BillingRate,
  CreateBillingPlanRequest,
  UpdateBillingPlanRequest,
  BillingPlanQueryParams,
  BillingPlanListResponse,
  Money,
  UsageData,
  ValidationResult
} from '@/types/billing'

/**
 * 计费计划服务接口
 */
export interface IBillingPlanService {
  // 计费计划 CRUD 操作
  getPlans(params?: BillingPlanQueryParams): Promise<BillingPlanListResponse>
  getPlan(id: string): Promise<BillingPlan>
  createPlan(data: CreateBillingPlanRequest): Promise<BillingPlan>
  updatePlan(id: string, data: UpdateBillingPlanRequest): Promise<BillingPlan>
  deletePlan(id: string): Promise<void>
  
  // 计划状态管理
  activatePlan(id: string): Promise<void>
  deactivatePlan(id: string): Promise<void>
  
  // 费率管理
  getPlanRates(planId: string): Promise<BillingRate[]>
  updatePlanRates(planId: string, rates: Partial<BillingRate>[]): Promise<BillingRate[]>
  
  // 计费计算
  calculateCost(planId: string, usage: UsageData): Promise<Money>
  testPlanCalculation(planId: string, testUsage: UsageData): Promise<Money>
  
  // 计划分配
  assignPlanToUser(planId: string, userId: string): Promise<void>
  getUserPlan(userId: string): Promise<BillingPlan | null>
  
  // 验证
  validatePlanData(data: CreateBillingPlanRequest): ValidationResult
}

/**
 * 模拟计费计划服务实现
 */
class BillingPlanService implements IBillingPlanService {
  // 模拟数据
  private mockPlans: BillingPlan[] = [
    {
      id: '1',
      name: '基础套餐',
      type: 'monthly',
      description: '适合个人用户的基础网络服务',
      active: true,
      rates: [
        {
          id: 'rate_1',
          planId: '1',
          name: '月租费',
          type: 'fixed',
          unitPrice: { amount: 50.00, currency: 'CNY' },
          validFrom: '2024-01-01T00:00:00Z',
          createdAt: '2024-01-01T00:00:00Z'
        },
        {
          id: 'rate_2', 
          planId: '1',
          name: '流量费',
          type: 'tiered',
          unitPrice: { amount: 0.10, currency: 'CNY' },
          tierRates: [
            { from: 0, to: 1024 * 1024 * 1024, price: { amount: 0, currency: 'CNY' } }, // 前1GB免费
            { from: 1024 * 1024 * 1024, to: 10 * 1024 * 1024 * 1024, price: { amount: 0.05, currency: 'CNY' } }, // 1-10GB
            { from: 10 * 1024 * 1024 * 1024, price: { amount: 0.10, currency: 'CNY' } } // 10GB以上
          ],
          validFrom: '2024-01-01T00:00:00Z',
          createdAt: '2024-01-01T00:00:00Z'
        }
      ],
      validFrom: '2024-01-01T00:00:00Z',
      maxUsers: 1000,
      features: ['基础网络接入', '邮件支持', '在线自助服务'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z'
    },
    {
      id: '2',
      name: '企业套餐',
      type: 'hybrid',
      description: '适合中小企业的专业网络服务',
      active: true,
      rates: [
        {
          id: 'rate_3',
          planId: '2',
          name: '月租费',
          type: 'fixed',
          unitPrice: { amount: 200.00, currency: 'CNY' },
          validFrom: '2024-01-01T00:00:00Z',
          createdAt: '2024-01-01T00:00:00Z'
        },
        {
          id: 'rate_4',
          planId: '2', 
          name: '带宽费',
          type: 'bandwidth',
          unitPrice: { amount: 10.00, currency: 'CNY' },
          validFrom: '2024-01-01T00:00:00Z',
          createdAt: '2024-01-01T00:00:00Z'
        }
      ],
      validFrom: '2024-01-01T00:00:00Z',
      maxUsers: 100,
      features: ['专业网络接入', '7x24技术支持', '专属客服', 'SLA保障'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z'
    },
    {
      id: '3',
      name: '高级套餐',
      type: 'usage',
      description: '大流量用户的高级网络服务',
      active: false,
      rates: [
        {
          id: 'rate_5',
          planId: '3',
          name: '流量费',
          type: 'volume',
          unitPrice: { amount: 0.02, currency: 'CNY' },
          validFrom: '2024-01-01T00:00:00Z',
          createdAt: '2024-01-01T00:00:00Z'
        }
      ],
      validFrom: '2024-01-01T00:00:00Z',
      features: ['无限制网络接入', '优先技术支持', '高速专线'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z'
    }
  ]

  private delay(ms: number = 800): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async getPlans(params?: BillingPlanQueryParams): Promise<BillingPlanListResponse> {
    await this.delay()
    
    let filteredPlans = [...this.mockPlans]
    
    // 应用筛选条件
    if (params) {
      const { name, type, active, page = 1, pageSize = 10 } = params
      
      if (name) {
        filteredPlans = filteredPlans.filter(plan => 
          plan.name.toLowerCase().includes(name.toLowerCase())
        )
      }
      
      if (type) {
        filteredPlans = filteredPlans.filter(plan => plan.type === type)
      }
      
      if (active !== undefined) {
        filteredPlans = filteredPlans.filter(plan => plan.active === active)
      }
      
      // 分页
      const startIndex = (page - 1) * pageSize
      const endIndex = startIndex + pageSize
      filteredPlans = filteredPlans.slice(startIndex, endIndex)
    }
    
    return {
      data: filteredPlans,
      total: this.mockPlans.length,
      page: params?.page || 1,
      pageSize: params?.pageSize || 10
    }
  }

  async getPlan(id: string): Promise<BillingPlan> {
    await this.delay()
    
    const plan = this.mockPlans.find(p => p.id === id)
    if (!plan) {
      throw new Error('计费计划不存在')
    }
    
    return plan
  }

  async createPlan(data: CreateBillingPlanRequest): Promise<BillingPlan> {
    await this.delay()
    
    // 验证数据
    const validation = this.validatePlanData(data)
    if (!validation.valid) {
      throw new Error(`数据验证失败: ${validation.errors.map(e => e.message).join(', ')}`)
    }
    
    // 检查计划名称是否已存在
    if (this.mockPlans.some(p => p.name === data.name)) {
      throw new Error('计划名称已存在')
    }
    
    const newPlan: BillingPlan = {
      id: String(this.mockPlans.length + 1),
      name: data.name,
      type: data.type,
      description: data.description,
      active: true,
      rates: data.rates.map((rate, index) => ({
        ...rate,
        id: `rate_${this.mockPlans.length + 1}_${index + 1}`,
        planId: String(this.mockPlans.length + 1),
        createdAt: new Date().toISOString()
      })),
      validFrom: data.validFrom,
      validTo: data.validTo,
      maxUsers: data.maxUsers,
      features: data.features,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    this.mockPlans.push(newPlan)
    return newPlan
  }

  async updatePlan(id: string, data: UpdateBillingPlanRequest): Promise<BillingPlan> {
    await this.delay()
    
    const planIndex = this.mockPlans.findIndex(p => p.id === id)
    if (planIndex === -1) {
      throw new Error('计费计划不存在')
    }
    
    // 检查名称冲突（如果更新名称）
    if (data.name && this.mockPlans.some(p => p.id !== id && p.name === data.name)) {
      throw new Error('计划名称已存在')
    }
    
    const updatedPlan = {
      ...this.mockPlans[planIndex],
      ...data,
      updatedAt: new Date().toISOString()
    }
    
    this.mockPlans[planIndex] = updatedPlan
    return updatedPlan
  }

  async deletePlan(id: string): Promise<void> {
    await this.delay()
    
    const planIndex = this.mockPlans.findIndex(p => p.id === id)
    if (planIndex === -1) {
      throw new Error('计费计划不存在')
    }
    
    // 检查是否有用户正在使用此计划
    // 在实际实现中，这里会检查数据库中的用户计划关联
    
    this.mockPlans.splice(planIndex, 1)
  }

  async activatePlan(id: string): Promise<void> {
    await this.updatePlan(id, { active: true })
  }

  async deactivatePlan(id: string): Promise<void> {
    await this.updatePlan(id, { active: false })
  }

  async getPlanRates(planId: string): Promise<BillingRate[]> {
    await this.delay()
    
    const plan = await this.getPlan(planId)
    return plan.rates
  }

  async updatePlanRates(planId: string, rates: Partial<BillingRate>[]): Promise<BillingRate[]> {
    await this.delay()
    
    const plan = await this.getPlan(planId)
    
    // 更新费率
    const updatedRates = rates.map((rateUpdate, index) => ({
      ...plan.rates[index],
      ...rateUpdate,
      planId,
      updatedAt: new Date().toISOString()
    }))
    
    await this.updatePlan(planId, {})
    
    // 更新内存中的费率数据
    const planIndex = this.mockPlans.findIndex(p => p.id === planId)
    if (planIndex !== -1) {
      this.mockPlans[planIndex].rates = updatedRates
    }
    
    return updatedRates
  }

  async calculateCost(planId: string, usage: UsageData): Promise<Money> {
    await this.delay()
    
    const plan = await this.getPlan(planId)
    
    let totalCost = 0
    
    // 计算各项费用
    for (const rate of plan.rates) {
      switch (rate.type) {
        case 'fixed':
          totalCost += rate.unitPrice.amount
          break
        case 'tiered':
          if (rate.tierRates && usage.dataTransfer.total > 0) {
            totalCost += this.calculateTieredCost(usage.dataTransfer.total, rate.tierRates)
          }
          break
        case 'volume':
          totalCost += (usage.dataTransfer.total / (1024 * 1024 * 1024)) * rate.unitPrice.amount // 按GB计算
          break
        case 'bandwidth':
          // 简化的带宽计费，基于峰值使用
          const peakBandwidthMbps = Math.max(usage.dataTransfer.upload, usage.dataTransfer.download) / (1024 * 1024 * 8) // 转换为Mbps
          totalCost += Math.ceil(peakBandwidthMbps / 10) * rate.unitPrice.amount // 按10Mbps档位计费
          break
        case 'time_based':
          totalCost += (usage.sessionTime / 3600) * rate.unitPrice.amount // 按小时计费
          break
      }
    }
    
    return {
      amount: Math.round(totalCost * 100) / 100, // 保留两位小数
      currency: plan.rates[0]?.unitPrice.currency || 'CNY'
    }
  }

  async testPlanCalculation(planId: string, testUsage: UsageData): Promise<Money> {
    // 与 calculateCost 相同的逻辑，用于测试目的
    return this.calculateCost(planId, testUsage)
  }

  async assignPlanToUser(planId: string, userId: string): Promise<void> {
    await this.delay()
    
    // 验证计划存在
    await this.getPlan(planId)
    
    // 在实际实现中，这里会更新用户的计费计划关联
    console.log(`已将计划 ${planId} 分配给用户 ${userId}`)
  }

  async getUserPlan(userId: string): Promise<BillingPlan | null> {
    await this.delay()
    
    // 在实际实现中，这里会从数据库查询用户的当前计费计划
    // 模拟返回第一个激活的计划
    return this.mockPlans.find(p => p.active) || null
  }

  validatePlanData(data: CreateBillingPlanRequest): ValidationResult {
    const errors: Array<{ field: string; message: string }> = []
    
    // 验证计划名称
    if (!data.name || data.name.trim().length < 2) {
      errors.push({ field: 'name', message: '计划名称至少需要2个字符' })
    }
    
    if (data.name && data.name.length > 50) {
      errors.push({ field: 'name', message: '计划名称不能超过50个字符' })
    }
    
    // 验证计划类型
    const validTypes: PlanType[] = ['monthly', 'usage', 'hybrid', 'prepaid', 'postpaid']
    if (!validTypes.includes(data.type)) {
      errors.push({ field: 'type', message: '无效的计划类型' })
    }
    
    // 验证费率配置
    if (!data.rates || data.rates.length === 0) {
      errors.push({ field: 'rates', message: '至少需要配置一个费率' })
    } else {
      data.rates.forEach((rate, index) => {
        if (!rate.name || rate.name.trim().length < 2) {
          errors.push({ field: `rates[${index}].name`, message: '费率名称至少需要2个字符' })
        }
        
        if (!rate.unitPrice || rate.unitPrice.amount < 0) {
          errors.push({ field: `rates[${index}].unitPrice`, message: '费率价格不能为负数' })
        }
        
        if (!rate.unitPrice || !rate.unitPrice.currency) {
          errors.push({ field: `rates[${index}].currency`, message: '必须指定货币类型' })
        }
      })
    }
    
    // 验证日期
    const validFromDate = new Date(data.validFrom)
    if (isNaN(validFromDate.getTime())) {
      errors.push({ field: 'validFrom', message: '无效的生效日期格式' })
    }
    
    if (data.validTo) {
      const validToDate = new Date(data.validTo)
      if (isNaN(validToDate.getTime())) {
        errors.push({ field: 'validTo', message: '无效的失效日期格式' })
      } else if (validToDate <= validFromDate) {
        errors.push({ field: 'validTo', message: '失效日期必须晚于生效日期' })
      }
    }
    
    // 验证用户数限制
    if (data.maxUsers && data.maxUsers < 1) {
      errors.push({ field: 'maxUsers', message: '最大用户数必须大于0' })
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }

  private calculateTieredCost(totalUsage: number, tierRates: any[]): number {
    let cost = 0
    let remainingUsage = totalUsage
    
    for (const tier of tierRates) {
      const tierStart = tier.from
      const tierEnd = tier.to || Infinity
      const tierSize = tierEnd - tierStart
      
      if (remainingUsage <= 0) break
      
      const usageInTier = Math.min(remainingUsage, tierSize)
      cost += (usageInTier / (1024 * 1024 * 1024)) * tier.price.amount // 按GB计算
      
      remainingUsage -= usageInTier
    }
    
    return cost
  }
}

// 导出服务实例
export const billingPlanService = new BillingPlanService()
export default billingPlanService