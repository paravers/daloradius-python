/**
 * 组件相关类型定义
 */

import type { Ref, ComputedRef } from 'vue'
import type { FormInstance, TableColumnType } from 'ant-design-vue'

// 手动定义 FormRules 类型
export type FormRules = Record<string, Array<{
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}>>

// 基础组件接口
export interface IBaseComponent {
  loading: Ref<boolean>
  error: Ref<string | null>
  onMounted(): void
  onUnmounted(): void
  refresh(): Promise<void>
  handleError(error: any): void
  showMessage(message: string, type?: 'success' | 'error' | 'warning' | 'info'): void
}

// 表格组件接口
export interface ITableComponent<T> extends IBaseComponent {
  dataSource: Ref<T[]>
  columns: ComputedRef<TableColumnType[]>
  pagination: Ref<PaginationConfig>
  selectedRowKeys: Ref<(string | number)[]>
  selectedRows: Ref<T[]>
  
  handleSearch(searchParams: Record<string, any>): void
  handleSort(field: string, order: 'ascend' | 'descend' | null): void
  handlePageChange(page: number, pageSize: number): void
  handleSelectionChange(selectedKeys: (string | number)[], selectedRows: T[]): void
  
  handleCreate(): void
  handleEdit(record: T): void
  handleDelete(record: T): void
  handleBatchDelete(records: T[]): void
  handleExport(): void
}

// 表单组件接口
export interface IFormComponent<T> extends IBaseComponent {
  formData: Ref<Partial<T>>
  formRef: Ref<FormInstance | undefined>
  rules: ComputedRef<FormRules>
  submitLoading: Ref<boolean>
  mode: Ref<'create' | 'edit' | 'view'>
  
  validate(): Promise<boolean>
  validateField(field: keyof T): Promise<boolean>
  reset(): void
  setFormData(data: Partial<T>): void
  
  handleSubmit(): Promise<void>
  handleCancel(): void
}

// 分页配置
export interface PaginationConfig {
  current: number
  pageSize: number
  total: number
  showSizeChanger: boolean
  showQuickJumper: boolean
  showTotal: (total: number, range: [number, number]) => string
  pageSizeOptions: string[]
}

// 搜索表单配置
export interface SearchFormConfig {
  fields: SearchFieldConfig[]
  layout?: 'inline' | 'horizontal' | 'vertical'
  showReset?: boolean
  showSearch?: boolean
}

// 搜索字段配置
export interface SearchFieldConfig {
  key: string
  label: string
  type: 'input' | 'select' | 'date' | 'dateRange' | 'number'
  placeholder?: string
  options?: Array<{ label: string; value: any }>
  span?: number
  rules?: any[]
}

// 表格列配置
export interface TableColumnConfig<T = any> {
  key: string
  title: string
  dataIndex: keyof T
  width?: number
  fixed?: 'left' | 'right'
  sorter?: boolean
  filterable?: boolean
  searchable?: boolean
  render?: (value: any, record: T, index: number) => any
  customRender?: (options: { text: any; record: T; index: number; column: any }) => any
}

// 操作按钮配置
export interface ActionButtonConfig<T = any> {
  key: string
  label: string
  type?: 'primary' | 'default' | 'dashed' | 'text' | 'link'
  danger?: boolean
  icon?: any
  permission?: string
  visible?: (record: T) => boolean
  disabled?: (record: T) => boolean
  onClick: (record: T) => void
}

// 批量操作配置
export interface BatchActionConfig<T = any> {
  key: string
  label: string
  type?: 'primary' | 'default' | 'dashed'
  danger?: boolean
  icon?: any
  permission?: string
  disabled?: (selectedRows: T[]) => boolean
  onClick: (selectedRows: T[]) => void
}

// 表单字段配置
export interface FormFieldConfig {
  key: string
  label: string
  type: 'input' | 'password' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'date' | 'dateRange' | 'number' | 'switch' | 'upload'
  placeholder?: string
  disabled?: boolean
  required?: boolean
  span?: number
  options?: Array<{ label: string; value: any; disabled?: boolean }>
  rules?: any[]
  props?: Record<string, any>
}

// 菜单项配置
export interface MenuItemConfig {
  key: string
  title: string
  icon?: any
  path?: string
  children?: MenuItemConfig[]
  permission?: string
  hidden?: boolean
  badge?: {
    count: number
    color?: string
  }
}

// 面包屑配置
export interface BreadcrumbItem {
  title: string
  path?: string
  icon?: any
}