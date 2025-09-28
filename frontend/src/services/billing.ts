/**
 * 计费管理服务
 */

import type { 
  BillingPlan, 
  BillingHistory, 
  PaginatedResponse, 
  QueryParams 
} from '@/types'
import { apiService } from './api'

class BillingService {
  private readonly baseUrl = '/billing'

  /**
   * 获取计费计划列表
   */
  async getPlans(params?: QueryParams): Promise<PaginatedResponse<BillingPlan>> {
    return await apiService.get<PaginatedResponse<BillingPlan>>(`${this.baseUrl}/plans`, {
      params
    })
  }

  /**
   * 获取计费计划详情
   */
  async getPlan(id: number): Promise<BillingPlan> {
    return await apiService.get<BillingPlan>(`${this.baseUrl}/plans/${id}`)
  }

  /**
   * 创建计费计划
   */
  async createPlan(plan: Partial<BillingPlan>): Promise<BillingPlan> {
    return await apiService.post<BillingPlan>(`${this.baseUrl}/plans`, plan)
  }

  /**
   * 更新计费计划
   */
  async updatePlan(id: number, plan: Partial<BillingPlan>): Promise<BillingPlan> {
    return await apiService.put<BillingPlan>(`${this.baseUrl}/plans/${id}`, plan)
  }

  /**
   * 删除计费计划
   */
  async deletePlan(id: number): Promise<void> {
    await apiService.delete(`${this.baseUrl}/plans/${id}`)
  }

  /**
   * 获取账单历史
   */
  async getBillingHistory(params?: QueryParams): Promise<PaginatedResponse<BillingHistory>> {
    return await apiService.get<PaginatedResponse<BillingHistory>>(`${this.baseUrl}/history`, {
      params
    })
  }

  /**
   * 获取计费统计
   */
  async getBillingStats(params?: {
    startDate?: string
    endDate?: string
    planId?: number
  }) {
    return await apiService.get(`${this.baseUrl}/stats`, {
      params
    })
  }

  /**
   * 处理支付
   */
  async processPayment(paymentData: {
    userId: number
    planId: number
    amount: number
    paymentMethod: string
    transactionId?: string
  }) {
    return await apiService.post(`${this.baseUrl}/payment`, paymentData)
  }

  /**
   * 生成发票
   */
  async generateInvoice(invoiceData: {
    userId: number
    planId: number
    amount: number
    dueDate: string
  }) {
    return await apiService.post(`${this.baseUrl}/invoice`, invoiceData)
  }

  /**
   * 获取发票PDF
   */
  async getInvoicePdf(invoiceId: number): Promise<Blob> {
    return await apiService.get(`${this.baseUrl}/invoice/${invoiceId}/pdf`, {
      responseType: 'blob'
    })
  }
}

export const billingService = new BillingService()
export { BillingService }