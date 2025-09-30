/**
 * Batch Operations Service
 * 
 * Service for managing batch operations and history
 */

import { apiService } from '@/services/api'
import type { 
  BatchHistoryResponse,
  BatchHistoryListResponse,
  BatchHistoryQuery,
  BatchHistoryCreate,
  BatchHistoryUpdate,
  BatchOperationRequest,
  BatchOperationResult
} from '@/types/batch'

class BatchService {
  /**
   * Get batch operation history with filtering and pagination
   */
  static async getBatchHistory(query: BatchHistoryQuery): Promise<BatchHistoryListResponse> {
    const params = new URLSearchParams()
    
    if (query.operation_type) params.append('operation_type', query.operation_type)
    if (query.status) params.append('status', query.status)
    if (query.hotspot_id) params.append('hotspot_id', query.hotspot_id.toString())
    if (query.created_after) params.append('created_after', query.created_after)
    if (query.created_before) params.append('created_before', query.created_before)
    if (query.page) params.append('page', query.page.toString())
    if (query.size) params.append('size', query.size.toString())
    if (query.sort_by) params.append('sort_by', query.sort_by)
    if (query.sort_order) params.append('sort_order', query.sort_order)

    const response = await apiService.get<BatchHistoryListResponse>(`/batch/history?${params.toString()}`)
    return response
  }

  /**
   * Get batch operation details by ID
   */
  static async getBatchDetails(batchId: number): Promise<BatchHistoryResponse> {
    const response = await apiService.get<BatchHistoryResponse>(`/batch/history/${batchId}`)
    return response
  }

  /**
   * Create a batch history record
   */
  static async createBatchHistory(data: BatchHistoryCreate): Promise<BatchHistoryResponse> {
    const response = await apiService.post<BatchHistoryResponse>('/batch/history', data)
    return response
  }

  /**
   * Update a batch history record
   */
  static async updateBatchHistory(batchId: number, data: BatchHistoryUpdate): Promise<BatchHistoryResponse> {
    const response = await apiService.put<BatchHistoryResponse>(`/batch/history/${batchId}`, data)
    return response
  }

  /**
   * Delete a batch history record
   */
  static async deleteBatchHistory(batchId: number): Promise<void> {
    await apiService.delete(`/batch/history/${batchId}`)
  }

  /**
   * Execute batch user operations
   */
  static async executeBatchUserOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await apiService.post<BatchOperationResult>('/batch/users', request)
    return response
  }

  /**
   * Execute batch NAS operations
   */
  static async executeBatchNasOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await apiService.post<BatchOperationResult>('/batch/nas', request)
    return response
  }

  /**
   * Execute batch group operations
   */
  static async executeBatchGroupOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await apiService.post<BatchOperationResult>('/batch/groups', request)
    return response
  }

  /**
   * Get available operation types
   */
  static async getOperationTypes(): Promise<{
    user_operations: string[]
    nas_operations: string[]
    group_operations: string[]
  }> {
    const response = await apiService.get<{
      user_operations: string[]
      nas_operations: string[]
      group_operations: string[]
    }>('/batch/operations/types')
    return response
  }

  /**
   * Get batch operations statistics
   */
  static async getBatchStats(): Promise<{
    total_operations: number
    recent_operations: number
    status_distribution: Record<string, number>
    operation_type_distribution: Record<string, number>
  }> {
    const response = await apiService.get<{
      total_operations: number
      recent_operations: number
      status_distribution: Record<string, number>
      operation_type_distribution: Record<string, number>
    }>('/batch/stats')
    return response
  }

  /**
   * Helper method to execute batch user deletion with history tracking
   */
  static async batchDeleteUsersWithHistory(
    userIds: number[],
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    }
  ): Promise<BatchOperationResult> {
    const request: BatchOperationRequest = {
      operation_type: 'delete',
      target_ids: userIds,
      operation_data: {},
      batch_name: options?.batchName || `删除 ${userIds.length} 个用户`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId
    }

    return BatchService.executeBatchUserOperation(request)
  }

  /**
   * Helper method to execute batch user status update with history tracking
   */
  static async batchUpdateUserStatusWithHistory(
    userIds: number[],
    status: 'active' | 'inactive',
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    }
  ): Promise<BatchOperationResult> {
    const operationType = status === 'active' ? 'activate' : 'deactivate'
    const request: BatchOperationRequest = {
      operation_type: operationType,
      target_ids: userIds,
      operation_data: { status },
      batch_name: options?.batchName || `${status === 'active' ? '激活' : '停用'} ${userIds.length} 个用户`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId
    }

    return BatchService.executeBatchUserOperation(request)
  }

  /**
   * Helper method to execute batch NAS deletion with history tracking
   */
  static async batchDeleteNasWithHistory(
    nasIds: number[],
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    }
  ): Promise<BatchOperationResult> {
    const request: BatchOperationRequest = {
      operation_type: 'delete',
      target_ids: nasIds,
      operation_data: {},
      batch_name: options?.batchName || `删除 ${nasIds.length} 个NAS设备`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId
    }

    return BatchService.executeBatchNasOperation(request)
  }

  /**
   * Helper method to execute batch group deletion with history tracking
   */
  static async batchDeleteGroupsWithHistory(
    groupIds: number[],
    options?: {
      batchName?: string
      description?: string
      hotspotId?: number
    }
  ): Promise<BatchOperationResult> {
    const request: BatchOperationRequest = {
      operation_type: 'delete',
      target_ids: groupIds,
      operation_data: {},
      batch_name: options?.batchName || `删除 ${groupIds.length} 个用户组`,
      batch_description: options?.description,
      hotspot_id: options?.hotspotId
    }

    return BatchService.executeBatchGroupOperation(request)
  }
}

// Export class for static access
export { BatchService }

// For backward compatibility, export a singleton instance
export const batchService = {
  getBatchHistory: BatchService.getBatchHistory,
  getBatchDetails: BatchService.getBatchDetails,
  createBatchHistory: BatchService.createBatchHistory,
  updateBatchHistory: BatchService.updateBatchHistory,
  deleteBatchHistory: BatchService.deleteBatchHistory,
  executeBatchUserOperation: BatchService.executeBatchUserOperation,
  executeBatchNasOperation: BatchService.executeBatchNasOperation,
  executeBatchGroupOperation: BatchService.executeBatchGroupOperation,
  getOperationTypes: BatchService.getOperationTypes,
  getBatchStats: BatchService.getBatchStats,
  batchDeleteUsersWithHistory: BatchService.batchDeleteUsersWithHistory,
  batchUpdateUserStatusWithHistory: BatchService.batchUpdateUserStatusWithHistory,
  batchDeleteNasWithHistory: BatchService.batchDeleteNasWithHistory,
  batchDeleteGroupsWithHistory: BatchService.batchDeleteGroupsWithHistory
}