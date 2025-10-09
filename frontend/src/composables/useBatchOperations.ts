/**
 * Batch Operations Composable
 *
 * Provides reactive state and methods for managing batch operations
 */

import { ref } from 'vue'
import type {
  BatchOperationRequest,
  BatchHistoryResponse,
  BatchHistoryQuery,
  BatchHistoryListResponse,
} from '@/types/batch'
import { batchService } from '@/services/batchService'

export function useBatchOperations() {
  // State
  const loading = ref(false)
  const batchHistory = ref<BatchHistoryResponse[]>([])
  const stats = ref({
    total_operations: 0,
    recent_operations: 0,
    status_distribution: {} as Record<string, number>,
    operation_type_distribution: {} as Record<string, number>,
  })

  // Methods
  const fetchBatchHistory = async (query: BatchHistoryQuery): Promise<BatchHistoryListResponse> => {
    loading.value = true
    try {
      const response = await batchService.getBatchHistory(query)
      batchHistory.value = response.items
      return response
    } finally {
      loading.value = false
    }
  }

  const fetchBatchStats = async () => {
    try {
      const response = await batchService.getBatchStats()
      stats.value = response
    } catch (error) {
      console.error('Failed to fetch batch stats:', error)
    }
  }

  const getBatchDetails = async (batchId: number): Promise<BatchHistoryResponse> => {
    return await batchService.getBatchDetails(batchId)
  }

  // 批量操作执行函数已经移除，使用下面的特定操作函数

  const deleteBatchHistory = async (batchId: number): Promise<void> => {
    await batchService.deleteBatchHistory(batchId)
    // Remove from local state
    const index = batchHistory.value.findIndex((item) => item.id === batchId)
    if (index > -1) {
      batchHistory.value.splice(index, 1)
    }
  }

  const getOperationTypes = async () => {
    return await batchService.getOperationTypes()
  }

  // Utility methods
  const getStatusColor = (status: string): string => {
    const colorMap: Record<string, string> = {
      pending: '#faad14',
      running: '#1890ff',
      completed: '#52c41a',
      failed: '#ff4d4f',
      cancelled: '#8c8c8c',
    }
    return colorMap[status] || '#8c8c8c'
  }

  const getStatusText = (status: string): string => {
    const textMap: Record<string, string> = {
      pending: '等待中',
      running: '运行中',
      completed: '已完成',
      failed: '已失败',
      cancelled: '已取消',
    }
    return textMap[status] || status
  }

  const getOperationTypeText = (type: string): string => {
    const typeMap: Record<string, string> = {
      user_create: '用户创建',
      user_delete: '用户删除',
      user_update: '用户更新',
      user_activate: '用户激活',
      user_deactivate: '用户停用',
      nas_delete: 'NAS删除',
      nas_update: 'NAS更新',
      group_delete: '组删除',
      group_update: '组更新',
      group_add_users: '组添加用户',
      group_remove_users: '组移除用户',
    }
    return typeMap[type] || type
  }

  const calculateSuccessRate = (operation: BatchHistoryResponse): number => {
    if (operation.total_count === 0) return 0
    return Math.round((operation.success_count / operation.total_count) * 100)
  }

  const formatDuration = (startTime: string, endTime?: string): string | null => {
    if (!endTime) return null

    const start = new Date(startTime).getTime()
    const end = new Date(endTime).getTime()
    const duration = end - start

    const seconds = Math.floor(duration / 1000) % 60
    const minutes = Math.floor(duration / (1000 * 60)) % 60
    const hours = Math.floor(duration / (1000 * 60 * 60))

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    } else {
      return `${seconds}s`
    }
  }

  // Batch operation helpers for existing operations
  const createUserBatchOperation = (
    userIds: number[],
    operationType: 'delete' | 'activate' | 'deactivate' | 'update',
    operationData?: Record<string, unknown>,
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    },
  ): BatchOperationRequest => {
    return {
      operation_type: operationType,
      target_ids: userIds,
      operation_data: operationData || {},
      batch_name: options?.batchName || `用户${getOperationTypeText('user_' + operationType)}`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId,
    }
  }

  const createNasBatchOperation = (
    nasIds: number[],
    operationType: 'delete' | 'update',
    operationData?: Record<string, unknown>,
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    },
  ): BatchOperationRequest => {
    return {
      operation_type: operationType,
      target_ids: nasIds,
      operation_data: operationData || {},
      batch_name: options?.batchName || `NAS${getOperationTypeText('nas_' + operationType)}`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId,
    }
  }

  const createGroupBatchOperation = (
    groupIds: number[],
    operationType: 'delete' | 'update' | 'add_users' | 'remove_users',
    operationData?: Record<string, unknown>,
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    },
  ): BatchOperationRequest => {
    return {
      operation_type: operationType,
      target_ids: groupIds,
      operation_data: operationData || {},
      batch_name: options?.batchName || `组${getOperationTypeText('group_' + operationType)}`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId,
    }
  }

  return {
    // State
    loading,
    batchHistory,
    stats,

    // Methods
    fetchBatchHistory,
    fetchBatchStats,
    getBatchDetails,
    deleteBatchHistory,
    getOperationTypes,

    // Utility methods
    getStatusColor,
    getStatusText,
    getOperationTypeText,
    calculateSuccessRate,
    formatDuration,

    // Batch operation helpers
    createUserBatchOperation,
    createNasBatchOperation,
    createGroupBatchOperation,
  }
}
