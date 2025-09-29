/**
 * Batch Operations Types
 * 
 * TypeScript type definitions for batch operations
 */

export interface BatchHistoryBase {
  batch_name: string
  batch_description?: string
  hotspot_id?: number
  operation_type: string
  operation_details?: Record<string, any>
  total_count: number
  success_count: number
  failure_count: number
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
}

export interface BatchHistoryCreate extends BatchHistoryBase {}

export interface BatchHistoryUpdate {
  batch_name?: string
  batch_description?: string
  hotspot_id?: number
  operation_details?: Record<string, any>
  total_count?: number
  success_count?: number
  failure_count?: number
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
}

export interface BatchHistoryResponse extends BatchHistoryBase {
  id: number
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
  error_message?: string
}

export interface BatchOperationRequest {
  operation_type: string
  target_ids: number[]
  operation_data?: Record<string, any>
  batch_name?: string
  batch_description?: string
  hotspot_id?: number
}

export interface BatchOperationResult {
  batch_history_id: number
  operation_type: string
  total_count: number
  success_count: number
  failure_count: number
  status: string
  errors: Array<Record<string, any>>
  details?: Record<string, any>
}

export interface BatchUserOperationRequest extends BatchOperationRequest {
  operation_type: 'create' | 'delete' | 'update' | 'activate' | 'deactivate'
}

export interface BatchNasOperationRequest extends BatchOperationRequest {
  operation_type: 'delete' | 'update' | 'activate' | 'deactivate'
}

export interface BatchGroupOperationRequest extends BatchOperationRequest {
  operation_type: 'add_users' | 'remove_users' | 'delete' | 'update'
}

export interface BatchHistoryQuery {
  operation_type?: string
  status?: string
  hotspot_id?: number
  created_after?: string
  created_before?: string
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface BatchHistoryListResponse {
  items: BatchHistoryResponse[]
  total: number
  page: number
  size: number
  pages: number
}

export interface BatchStats {
  total_operations: number
  recent_operations: number
  status_distribution: Record<string, number>
  operation_type_distribution: Record<string, number>
}

export interface BatchOperationTypes {
  user_operations: string[]
  nas_operations: string[]
  group_operations: string[]
}

// Status enums for better type safety
export enum BatchStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum UserOperationType {
  CREATE = 'create',
  DELETE = 'delete',
  UPDATE = 'update',
  ACTIVATE = 'activate',
  DEACTIVATE = 'deactivate'
}

export enum NasOperationType {
  DELETE = 'delete',
  UPDATE = 'update',
  ACTIVATE = 'activate',
  DEACTIVATE = 'deactivate'
}

export enum GroupOperationType {
  ADD_USERS = 'add_users',
  REMOVE_USERS = 'remove_users',
  DELETE = 'delete',
  UPDATE = 'update'
}