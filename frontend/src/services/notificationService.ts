/**
 * Notification Service
 * 
 * Provides notification management functionality including sending notifications,
 * managing templates, and retrieving delivery statistics.
 */

import { apiClient } from './api'
import type { AxiosResponse } from 'axios'

// Types
export interface NotificationTemplate {
  id: number
  template_name: string
  template_type: string
  category: string
  subject?: string
  body_text?: string
  body_html?: string
  variables?: string[]
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface CreateTemplateData {
  template_name: string
  template_type: 'email' | 'sms' | 'push' | 'system'
  category: string
  subject?: string
  body_text?: string
  body_html?: string
  variables?: string
  is_active: boolean
}

export interface UpdateTemplateData {
  template_name?: string
  template_type?: 'email' | 'sms' | 'push' | 'system'
  category?: string
  subject?: string
  body_text?: string
  body_html?: string
  variables?: string[]
  is_active?: boolean
}

export interface SendNotificationData {
  recipient_id?: number
  recipient_email?: string
  recipient_phone?: string
  notification_type: 'email' | 'sms' | 'push' | 'system'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  template_id?: number
  subject?: string
  message: string
  variables?: Record<string, any>
  scheduled_for?: string
}

export interface NotificationHistory {
  id: number
  recipient_id?: number
  recipient_email?: string
  recipient_phone?: string
  notification_type: string
  priority: string
  status: string
  subject?: string
  message: string
  template_id?: number
  variables?: Record<string, any>
  created_at: string
  scheduled_for?: string
  sent_at?: string
  delivered_at?: string
  error_message?: string
}

export interface NotificationStats {
  summary: {
    total_sent: number
    total_delivered: number
    total_failed: number
    delivery_rate: number
    average_delivery_time_seconds: number
  }
  by_type: Record<string, {
    sent: number
    delivered: number
    failed: number
  }>
  by_priority: Record<string, {
    sent: number
    delivered: number
    failed: number
  }>
  daily_volume: Array<{
    date: string
    sent: number
    delivered: number
  }>
  error_analysis: {
    bounce_rate: number
    spam_rate: number
    timeout_rate: number
    common_errors: Array<{
      error: string
      count: number
    }>
  }
  period: {
    start_date: string
    end_date: string
    days: number
  }
}

export interface HistoryParams {
  recipient_id?: number
  notification_type?: string
  status?: string
  days?: number
  skip?: number
  limit?: number
}

export interface TemplateParams {
  template_type?: string
  category?: string
  is_active?: boolean
  skip?: number
  limit?: number
}

class NotificationService {
  private baseUrl = '/api/v1/notifications'

  /**
   * Get notification templates
   */
  async getTemplates(params?: TemplateParams): Promise<NotificationTemplate[]> {
    const searchParams = new URLSearchParams()
    
    if (params?.template_type) searchParams.append('template_type', params.template_type)
    if (params?.category) searchParams.append('category', params.category)
    if (params?.is_active !== undefined) searchParams.append('is_active', params.is_active.toString())
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())

    const response: AxiosResponse<NotificationTemplate[]> = await apiClient.get(
      `${this.baseUrl}/templates?${searchParams.toString()}`
    )
    return response.data
  }

  /**
   * Create notification template
   */
  async createTemplate(templateData: CreateTemplateData): Promise<NotificationTemplate> {
    const response: AxiosResponse<NotificationTemplate> = await apiClient.post(
      `${this.baseUrl}/templates`,
      templateData
    )
    return response.data
  }

  /**
   * Get notification template by ID
   */
  async getTemplate(templateId: number): Promise<NotificationTemplate> {
    const response: AxiosResponse<NotificationTemplate> = await apiClient.get(
      `${this.baseUrl}/templates/${templateId}`
    )
    return response.data
  }

  /**
   * Update notification template
   */
  async updateTemplate(templateId: number, updateData: UpdateTemplateData): Promise<NotificationTemplate> {
    const response: AxiosResponse<NotificationTemplate> = await apiClient.put(
      `${this.baseUrl}/templates/${templateId}`,
      updateData
    )
    return response.data
  }

  /**
   * Delete notification template
   */
  async deleteTemplate(templateId: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/templates/${templateId}`)
  }

  /**
   * Send notification
   */
  async sendNotification(notificationData: SendNotificationData): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/send`,
      notificationData
    )
    return response.data
  }

  /**
   * Get notification history
   */
  async getHistory(params?: HistoryParams): Promise<{
    notifications: NotificationHistory[]
    total: number
    filters: HistoryParams
  }> {
    const searchParams = new URLSearchParams()
    
    if (params?.recipient_id) searchParams.append('recipient_id', params.recipient_id.toString())
    if (params?.notification_type) searchParams.append('notification_type', params.notification_type)
    if (params?.status) searchParams.append('status', params.status)
    if (params?.days) searchParams.append('days', params.days.toString())
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())

    const response: AxiosResponse<{
      notifications: NotificationHistory[]
      total: number
      filters: HistoryParams
    }> = await apiClient.get(
      `${this.baseUrl}/history?${searchParams.toString()}`
    )
    return response.data
  }

  /**
   * Get notification statistics
   */
  async getStats(days: number = 30): Promise<NotificationStats> {
    const response: AxiosResponse<NotificationStats> = await apiClient.get(
      `${this.baseUrl}/stats?days=${days}`
    )
    return response.data
  }

  /**
   * Resend failed notification
   */
  async resendNotification(notificationId: number): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/resend/${notificationId}`
    )
    return response.data
  }

  /**
   * Cancel scheduled notification
   */
  async cancelNotification(notificationId: number): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/cancel/${notificationId}`
    )
    return response.data
  }

  /**
   * Get notification delivery status
   */
  async getDeliveryStatus(notificationId: number): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/status/${notificationId}`
    )
    return response.data
  }

  /**
   * Bulk send notifications
   */
  async bulkSend(notifications: SendNotificationData[]): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/bulk-send`,
      { notifications }
    )
    return response.data
  }

  /**
   * Preview notification template
   */
  async previewTemplate(templateId: number, variables?: Record<string, any>): Promise<{
    subject?: string
    body_text?: string
    body_html?: string
    preview_text: string
    preview_html?: string
  }> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/templates/${templateId}/preview`,
      { variables }
    )
    return response.data
  }

  /**
   * Test notification delivery
   */
  async testDelivery(testData: {
    notification_type: string
    recipient_email?: string
    recipient_phone?: string
    test_message: string
  }): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/test`,
      testData
    )
    return response.data
  }

  /**
   * Get notification preferences for user
   */
  async getUserPreferences(userId: number): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/preferences/${userId}`
    )
    return response.data
  }

  /**
   * Update notification preferences for user
   */
  async updateUserPreferences(userId: number, preferences: any): Promise<any> {
    const response: AxiosResponse<any> = await apiClient.put(
      `${this.baseUrl}/preferences/${userId}`,
      preferences
    )
    return response.data
  }

  /**
   * Get notification channels status
   */
  async getChannelsStatus(): Promise<{
    email: { status: string, last_checked: string }
    sms: { status: string, last_checked: string }
    push: { status: string, last_checked: string }
  }> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/channels/status`
    )
    return response.data
  }

  /**
   * Get notification templates by category
   */
  async getTemplatesByCategory(category: string): Promise<NotificationTemplate[]> {
    const response: AxiosResponse<NotificationTemplate[]> = await apiClient.get(
      `${this.baseUrl}/templates/category/${category}`
    )
    return response.data
  }

  /**
   * Validate notification template
   */
  async validateTemplate(templateData: Partial<CreateTemplateData>): Promise<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }> {
    const response: AxiosResponse<any> = await apiClient.post(
      `${this.baseUrl}/templates/validate`,
      templateData
    )
    return response.data
  }

  /**
   * Export notification history
   */
  async exportHistory(params: HistoryParams & { format: 'csv' | 'xlsx' | 'pdf' }): Promise<Blob> {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    const response: AxiosResponse<Blob> = await apiClient.get(
      `${this.baseUrl}/history/export?${searchParams.toString()}`,
      { responseType: 'blob' }
    )
    return response.data
  }

  /**
   * Get notification queue status
   */
  async getQueueStatus(): Promise<{
    pending: number
    processing: number
    failed: number
    retrying: number
    queue_size: number
    processing_rate: number
  }> {
    const response: AxiosResponse<any> = await apiClient.get(
      `${this.baseUrl}/queue/status`
    )
    return response.data
  }

  /**
   * Format notification type for display
   */
  formatNotificationType(type: string): string {
    const typeMap = {
      email: '邮件通知',
      sms: '短信通知',
      push: '推送通知',
      system: '系统通知'
    }
    return typeMap[type as keyof typeof typeMap] || type
  }

  /**
   * Format notification status for display
   */
  formatNotificationStatus(status: string): string {
    const statusMap = {
      pending: '待发送',
      sent: '已发送',
      delivered: '已送达',
      failed: '发送失败',
      cancelled: '已取消'
    }
    return statusMap[status as keyof typeof statusMap] || status
  }

  /**
   * Format notification priority for display
   */
  formatNotificationPriority(priority: string): string {
    const priorityMap = {
      low: '低优先级',
      normal: '普通',
      high: '高优先级',
      urgent: '紧急'
    }
    return priorityMap[priority as keyof typeof priorityMap] || priority
  }

  /**
   * Get notification type icon
   */
  getNotificationTypeIcon(type: string): string {
    const iconMap = {
      email: '📧',
      sms: '📱',
      push: '🔔',
      system: '🖥️'
    }
    return iconMap[type as keyof typeof iconMap] || '📄'
  }

  /**
   * Get priority color
   */
  getPriorityColor(priority: string): string {
    const colorMap = {
      low: '#52c41a',
      normal: '#1890ff',
      high: '#faad14',
      urgent: '#f5222d'
    }
    return colorMap[priority as keyof typeof colorMap] || '#d9d9d9'
  }

  /**
   * Calculate delivery success rate
   */
  calculateSuccessRate(sent: number, delivered: number): number {
    if (sent === 0) return 0
    return Math.round((delivered / sent) * 100 * 10) / 10
  }

  /**
   * Format delivery time
   */
  formatDeliveryTime(seconds: number): string {
    if (seconds < 60) return `${seconds}秒`
    if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
    return `${Math.round(seconds / 3600)}小时`
  }
}

// Export singleton instance
export const notificationService = new NotificationService()

// Export types for use in components
export type {
  NotificationTemplate,
  CreateTemplateData,
  UpdateTemplateData,
  SendNotificationData,
  NotificationHistory,
  NotificationStats,
  HistoryParams,
  TemplateParams
}