/**
 * Batch Operations Service
 * 
 * Service for managing batch operations and history
 */

import { ApiClient } from '@/services/apiClient'
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
  private api: ApiClient

  constructor() {
    this.api = new ApiClient()
  }

  /**
   * Get batch operation history with filtering and pagination
   */
  async getBatchHistory(query: BatchHistoryQuery): Promise<BatchHistoryListResponse> {
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

    const response = await this.api.get(`/batch/history?${params.toString()}`)
    return response.data
  }

  /**
   * Get batch operation details by ID
   */
  async getBatchDetails(batchId: number): Promise<BatchHistoryResponse> {
    const response = await this.api.get(`/batch/history/${batchId}`)
    return response.data
  }

  /**
   * Create a batch history record
   */
  async createBatchHistory(data: BatchHistoryCreate): Promise<BatchHistoryResponse> {
    const response = await this.api.post('/batch/history', data)
    return response.data
  }

  /**
   * Update a batch history record
   */
  async updateBatchHistory(batchId: number, data: BatchHistoryUpdate): Promise<BatchHistoryResponse> {
    const response = await this.api.put(`/batch/history/${batchId}`, data)
    return response.data
  }

  /**
   * Delete a batch history record
   */
  async deleteBatchHistory(batchId: number): Promise<void> {
    await this.api.delete(`/batch/history/${batchId}`)
  }

  /**
   * Execute batch user operations
   */
  async executeBatchUserOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await this.api.post('/batch/users', request)
    return response.data
  }

  /**
   * Execute batch NAS operations
   */
  async executeBatchNasOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await this.api.post('/batch/nas', request)
    return response.data
  }

  /**
   * Execute batch group operations
   */
  async executeBatchGroupOperation(request: BatchOperationRequest): Promise<BatchOperationResult> {
    const response = await this.api.post('/batch/groups', request)
    return response.data
  }

  /**
   * Get available operation types
   */
  async getOperationTypes(): Promise<{
    user_operations: string[]
    nas_operations: string[]
    group_operations: string[]
  }> {
    const response = await this.api.get('/batch/operations/types')
    return response.data
  }

  /**
   * Get batch operations statistics
   */
  async getBatchStats(): Promise<{
    total_operations: number
    recent_operations: number
    status_distribution: Record<string, number>
    operation_type_distribution: Record<string, number>
  }> {
    const response = await this.api.get('/batch/stats')
    return response.data
  }

  /**
   * Helper method to execute batch user deletion with history tracking
   */
  async batchDeleteUsersWithHistory(
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

    return this.executeBatchUserOperation(request)
  }

  /**
   * Helper method to execute batch user status update with history tracking
   */
  async batchUpdateUserStatusWithHistory(
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

    return this.executeBatchUserOperation(request)
  }

  /**
   * Helper method to execute batch NAS deletion with history tracking
   */
  async batchDeleteNasWithHistory(
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

    return this.executeBatchNasOperation(request)
  }

  /**
   * Helper method to execute batch group deletion with history tracking
   */
  async batchDeleteGroupsWithHistory(
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

    return this.executeBatchGroupOperation(request)
  }
}

// Export singleton instance
export const batchService = new BatchService()