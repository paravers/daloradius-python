/**
 * 通用数据交互组件类型定义扩展
 * 基于 DRY 原则，为所有数据交互组件提供统一的类型约束
 */

import type { VNode } from 'vue'

// 基础数据源接口
export interface IDataSource<T = any> {
  data: T[]
  total: number
  loading: boolean
  error?: string
}

// 表格列定义接口
export interface ITableColumn<T = any> {
  key: string
  title: string
  dataIndex?: string
  width?: number | string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  filterable?: boolean
  fixed?: 'left' | 'right'
  ellipsis?: boolean
  render?: (value: any, record: T, index: number) => VNode | string
  customFilterDropdown?: boolean
}

// 数据表格属性接口
export interface IDataTableProps<T = any> {
  // 数据配置
  dataSource: IDataSource<T>
  columns: ITableColumn<T>[]
  rowKey?: string | ((record: T) => string)
  
  // 功能配置
  showSelection?: boolean
  showPagination?: boolean
  showExport?: boolean
  showRefresh?: boolean
  bordered?: boolean
  size?: 'small' | 'middle' | 'large'
  
  // 分页配置
  pagination?: IPaginationConfig
  
  // 事件处理
  onSelectionChange?: (selectedRowKeys: string[], selectedRows: T[]) => void
  onRowClick?: (record: T, index: number) => void
  onSort?: (field: string, order: 'ascend' | 'descend' | null) => void
  onFilter?: (filters: Record<string, any>) => void
  onRefresh?: () => void
  onExport?: (selectedRows: T[]) => void
}

// 分页配置接口
export interface IPaginationConfig {
  current: number
  pageSize: number
  total?: number
  showSizeChanger?: boolean
  showQuickJumper?: boolean
  showTotal?: boolean
  pageSizeOptions?: string[]
  onChange?: (page: number, pageSize: number) => void
}

// 表单字段类型枚举
export type FormFieldType = 
  | 'input'
  | 'password'
  | 'textarea'
  | 'select'
  | 'radio'
  | 'checkbox'
  | 'switch'
  | 'date'
  | 'daterange'
  | 'number'
  | 'email'
  | 'url'
  | 'phone'

// 表单字段接口
export interface IFormField {
  name: string
  type: FormFieldType
  label: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  readonly?: boolean
  
  // 验证规则
  rules?: ValidationRule[]
  
  // 字段特定配置
  options?: SelectOption[] // select, radio, checkbox
  multiple?: boolean // select, checkbox
  rows?: number // textarea
  min?: number | string // number, date
  max?: number | string // number, date
  step?: number // number
  format?: string // date
  
  // 联动配置
  dependencies?: string[] // 依赖的其他字段
  visible?: boolean | ((values: Record<string, any>) => boolean)
  
  // 样式配置
  span?: number // 在栅格中占据的列数
  offset?: number // 栅格左侧的间隔格数
}

// 选择项接口
export interface SelectOption {
  label: string
  value: any
  disabled?: boolean
  children?: SelectOption[] // 支持级联选择
}

// 验证规则接口
export interface ValidationRule {
  required?: boolean
  type?: 'string' | 'number' | 'boolean' | 'method' | 'regexp' | 'integer' | 'float' | 'array' | 'object' | 'enum' | 'date' | 'url' | 'hex' | 'email'
  min?: number
  max?: number
  len?: number
  pattern?: RegExp
  validator?: (rule: any, value: any) => Promise<void> | void
  message?: string
  trigger?: 'blur' | 'change' | ['blur', 'change']
}

// 搜索表单属性接口
export interface ISearchFormProps {
  // 表单配置
  fields: IFormField[]
  
  // 布局配置
  layout?: 'horizontal' | 'vertical' | 'inline'
  labelCol?: { span: number; offset?: number }
  wrapperCol?: { span: number; offset?: number }
  
  // 功能配置
  showResetButton?: boolean
  showAdvancedSearch?: boolean
  collapsible?: boolean
  collapsed?: boolean
  
  // 事件处理
  onSearch: (values: Record<string, any>) => void
  onReset?: () => void
  onFieldChange?: (field: string, value: any, allValues: Record<string, any>) => void
  onToggleCollapse?: (collapsed: boolean) => void
}

// 动态表单属性接口
export interface IDynamicFormProps {
  // 表单配置
  fields: IFormField[]
  modelValue: Record<string, any>
  
  // 布局配置
  layout?: 'horizontal' | 'vertical' | 'inline'
  labelCol?: { span: number; offset?: number }
  wrapperCol?: { span: number; offset?: number }
  columns?: 1 | 2 | 3 | 4
  
  // 功能配置
  readonly?: boolean
  showSubmitButton?: boolean
  showResetButton?: boolean
  submitText?: string
  resetText?: string
  
  // 验证配置
  validateOnRuleChange?: boolean
  
  // 事件处理
  onSubmit?: (values: Record<string, any>) => void
  onReset?: () => void
  onFieldChange?: (field: string, value: any, allValues: Record<string, any>) => void
  onValidationChange?: (valid: boolean, errors: Record<string, any>) => void
}

// 导出配置接口
export interface IExportConfig {
  filename?: string
  format?: 'xlsx' | 'csv' | 'pdf'
  columns?: string[] // 指定导出的列
  includeHeaders?: boolean
  customData?: any[] // 自定义导出数据
}

// 操作按钮配置接口
export interface IActionButton {
  key: string
  label: string
  type?: 'primary' | 'default' | 'dashed' | 'link' | 'text'
  icon?: string
  disabled?: boolean | ((record: any) => boolean)
  visible?: boolean | ((record: any) => boolean)
  loading?: boolean
  onClick: (record: any) => void
}

// 批量操作配置接口
export interface IBatchAction {
  key: string
  label: string
  type?: 'primary' | 'default' | 'danger'
  icon?: string
  disabled?: boolean
  confirmText?: string
  onClick: (selectedRowKeys: string[], selectedRows: any[]) => void
}

// 工具栏配置接口
export interface ITableToolbarProps {
  // 左侧区域
  title?: string
  showSelection?: boolean
  selectedRowKeys?: string[]
  batchActions?: IBatchAction[]
  
  // 右侧区域  
  showRefresh?: boolean
  showExport?: boolean
  showColumnSetting?: boolean
  customActions?: IActionButton[]
  
  // 事件处理
  onRefresh?: () => void
  onExport?: (config?: IExportConfig) => void
  onColumnSettingChange?: (columns: string[]) => void
}

// 状态管理相关类型
export interface ITableState<T = any> {
  // 数据状态
  dataSource: IDataSource<T>
  
  // UI 状态
  selectedRowKeys: string[]
  selectedRows: T[]
  sorter: { field?: string; order?: 'ascend' | 'descend' }
  filters: Record<string, any>
  
  // 分页状态
  pagination: IPaginationConfig
}