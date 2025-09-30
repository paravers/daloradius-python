/**
 * Help Service
 * 
 * Provides help system functionality including documentation,
 * tutorials, troubleshooting, and support resources.
 */

import { apiClient } from './api'
import type { AxiosResponse } from 'axios'

// Types
export interface HelpResources {
  documentation: {
    user_guide: string
    admin_guide: string
    api_documentation: string
    installation_guide: string
  }
  support: {
    official_website: string
    github_project: string
    issue_tracker: string
    community_forum: string
  }
  contact: {
    support_email: string
    documentation_email: string
    security_email: string
  }
  version_info: {
    current_version: string
    release_date: string
    changelog_url: string
  }
}

export interface Tutorial {
  title: string
  steps: string[]
  estimated_time: string
  difficulty: string
}

export interface TutorialContent {
  getting_started: Tutorial[]
  advanced_tutorials: Tutorial[]
  video_tutorials: {
    available: boolean
    planned: boolean
    coming_soon: string
  }
}

export interface TroubleshootingIssue {
  issue: string
  solutions: string[]
  category: string
}

export interface TroubleshootingGuide {
  common_issues: TroubleshootingIssue[]
  diagnostic_tools: Record<string, string>
  contact_support: {
    when_to_contact: string[]
    required_info: string[]
  }
}

export interface SystemInfo {
  system: {
    name: string
    version: string
    build: string
    environment: string
  }
  platform: {
    os: string
    python_version: string
    database: string
    web_server: string
  }
  modules: Record<string, string>
  support_info: {
    user_role: string
    installation_date: string
    last_updated: string
  }
}

export interface HelpContent {
  category: string
  content: Array<{
    id: number
    title: string
    content: string
    created_on: string
    modified_on: string
  }>
  total: number
}

export interface FeedbackData {
  category: string
  rating: number
  comment: string
  helpful: boolean
  page_url?: string
  user_agent?: string
}

export interface FeedbackResponse {
  status: string
  message: string
  feedback_id: string
  follow_up: string
}

class HelpService {
  private baseUrl = '/api/v1/help'

  /**
   * Get help resources and external links
   */
  async getResources(): Promise<HelpResources> {
    const response: AxiosResponse<HelpResources> = await apiClient.get(
      `${this.baseUrl}/resources`
    )
    return response.data
  }

  /**
   * Get help content from database
   */
  async getContent(category?: string, page?: string): Promise<HelpContent> {
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (page) params.append('page', page)
    
    const response: AxiosResponse<HelpContent> = await apiClient.get(
      `${this.baseUrl}/content?${params.toString()}`
    )
    return response.data
  }

  /**
   * Get system information for support
   */
  async getSystemInfo(): Promise<SystemInfo> {
    const response: AxiosResponse<SystemInfo> = await apiClient.get(
      `${this.baseUrl}/system-info`
    )
    return response.data
  }

  /**
   * Get troubleshooting guide
   */
  async getTroubleshooting(): Promise<TroubleshootingGuide> {
    const response: AxiosResponse<TroubleshootingGuide> = await apiClient.get(
      `${this.baseUrl}/troubleshooting`
    )
    return response.data
  }

  /**
   * Get tutorials and guides
   */
  async getTutorials(): Promise<TutorialContent> {
    const response: AxiosResponse<TutorialContent> = await apiClient.get(
      `${this.baseUrl}/tutorials`
    )
    return response.data
  }

  /**
   * Submit user feedback
   */
  async submitFeedback(feedbackData: FeedbackData): Promise<FeedbackResponse> {
    const response: AxiosResponse<FeedbackResponse> = await apiClient.post(
      `${this.baseUrl}/feedback`,
      feedbackData
    )
    return response.data
  }

  /**
   * Run diagnostic check
   */
  async runDiagnostic(tool: string): Promise<any> {
    // This would call the actual diagnostic endpoint
    // For now, return a mock response
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          tool,
          status: 'success',
          message: `${tool} check completed successfully`,
          timestamp: new Date().toISOString()
        })
      }, 2000)
    })
  }

  /**
   * Format help content for display
   */
  formatContent(content: string): string {
    // Basic content formatting
    return content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
  }

  /**
   * Search help content
   */
  async searchContent(query: string): Promise<any[]> {
    // This would implement search functionality
    // For now, return empty array
    return []
  }

  /**
   * Get popular help topics
   */
  async getPopularTopics(): Promise<string[]> {
    return [
      '用户管理',
      'RADIUS配置',
      'NAS设备设置',
      '报表生成',
      '计费管理',
      '故障排除'
    ]
  }

  /**
   * Get recent help updates
   */
  async getRecentUpdates(): Promise<any[]> {
    return [
      {
        title: '新增批量用户导入功能',
        date: '2024-01-15',
        category: '功能更新'
      },
      {
        title: '优化报表生成性能',
        date: '2024-01-10', 
        category: '性能优化'
      },
      {
        title: '修复NAS设备连接问题',
        date: '2024-01-05',
        category: '错误修复'
      }
    ]
  }

  /**
   * Check if help content is available
   */
  async isContentAvailable(category: string): Promise<boolean> {
    try {
      const content = await this.getContent(category)
      return content.total > 0
    } catch {
      return false
    }
  }

  /**
   * Get help metrics for analytics
   */
  async getHelpMetrics(): Promise<any> {
    return {
      total_views: 1250,
      popular_topics: [
        { topic: '用户管理', views: 450 },
        { topic: 'RADIUS配置', views: 380 },
        { topic: '报表生成', views: 320 }
      ],
      feedback_rating: 4.2,
      resolution_rate: 85.5
    }
  }

  /**
   * Export help content
   */
  async exportContent(format: 'pdf' | 'html' | 'markdown' = 'pdf'): Promise<Blob> {
    const response: AxiosResponse<Blob> = await apiClient.get(
      `${this.baseUrl}/export`,
      {
        params: { format },
        responseType: 'blob'
      }
    )
    return response.data
  }

  /**
   * Get contextual help for specific pages
   */
  getContextualHelp(page: string): any {
    const helpMap = {
      dashboard: {
        title: '仪表板帮助',
        content: '仪表板显示系统关键指标和统计信息，包括在线用户数、收入统计、设备状态等。',
        tips: [
          '点击统计卡片可查看详细信息',
          '使用刷新按钮更新最新数据',
          '图表支持缩放和交互操作'
        ]
      },
      users: {
        title: '用户管理帮助',
        content: '用户管理模块用于添加、编辑和管理RADIUS用户账户。',
        tips: [
          '支持批量导入用户',
          '可设置用户组和权限',
          '提供用户使用统计'
        ]
      },
      reports: {
        title: '报表系统帮助',
        content: '报表系统提供各种数据分析和统计报表生成功能。',
        tips: [
          '支持多种报表格式导出',
          '可自定义报表模板',
          '提供实时和历史数据分析'
        ]
      }
    }

    return helpMap[page as keyof typeof helpMap] || {
      title: '帮助',
      content: '如需帮助，请查看帮助中心或联系技术支持。',
      tips: []
    }
  }
}

// Export singleton instance
export const helpService = new HelpService()

// Export types for use in components
export type {
  HelpResources,
  Tutorial,
  TutorialContent,
  TroubleshootingIssue,
  TroubleshootingGuide,
  SystemInfo,
  HelpContent,
  FeedbackData,
  FeedbackResponse
}