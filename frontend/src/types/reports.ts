/**
 * Reports System Type Definitions
 * 
 * TypeScript interfaces and types for the reports system
 */

export enum ReportType {
  ONLINE_USERS = 'online_users',
  HISTORY = 'history',
  LAST_CONNECT = 'last_connect',
  NEW_USERS = 'new_users',
  TOP_USERS = 'top_users',
  USERNAME_REPORT = 'username_report',
  BATCH_REPORT = 'batch_report',
  SYSTEM_LOGS = 'system_logs',
  SYSTEM_STATUS = 'system_status',
  HEARTBEAT = 'heartbeat'
}

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export enum SystemStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  WARNING = 'warning',
  ERROR = 'error',
  MAINTENANCE = 'maintenance'
}

// =============================================================================
// UPS Status Types
// =============================================================================

export interface UpsStatusBase {
  ups_name: string
  ups_model?: string
  ups_serial?: string
  location?: string
  battery_charge?: number
  battery_runtime?: number
  input_voltage?: number
  output_voltage?: number
  load_percentage?: number
  temperature?: number
  humidity?: number
}

export interface UpsStatusCreate extends UpsStatusBase {
  status?: SystemStatus
}

export interface UpsStatusUpdate {
  ups_model?: string
  location?: string
  status?: SystemStatus
  battery_charge?: number
  battery_runtime?: number
  input_voltage?: number
  output_voltage?: number
  load_percentage?: number
  temperature?: number
  humidity?: number
  last_test_date?: string
  last_battery_replacement?: string
}

export interface UpsStatusResponse extends UpsStatusBase {
  id: number
  status: SystemStatus
  last_test_date?: string
  last_battery_replacement?: string
  created_at: string
  updated_at: string
}

// =============================================================================
// RAID Status Types
// =============================================================================

export interface RaidStatusBase {
  array_name: string
  raid_level: string
  controller_name?: string
  total_disks: number
  active_disks: number
  failed_disks: number
  spare_disks: number
  total_size?: number
  used_size?: number
  available_size?: number
  read_rate?: number
  write_rate?: number
}

export interface RaidStatusCreate extends RaidStatusBase {
  status?: SystemStatus
}

export interface RaidStatusUpdate {
  controller_name?: string
  status?: SystemStatus
  total_disks?: number
  active_disks?: number
  failed_disks?: number
  spare_disks?: number
  total_size?: number
  used_size?: number
  available_size?: number
  read_rate?: number
  write_rate?: number
  last_error?: string
  error_count?: number
}

export interface RaidStatusResponse extends RaidStatusBase {
  id: number
  status: SystemStatus
  last_error?: string
  error_count: number
  last_check?: string
  created_at: string
  updated_at: string
}

// =============================================================================
// HeartBeat Types
// =============================================================================

export interface HeartBeatBase {
  service_name: string
  service_type: string
  host_name: string
  ip_address?: string
  port?: number
  response_time?: number
  uptime?: number
  cpu_usage?: number
  memory_usage?: number
  disk_usage?: number
}

export interface HeartBeatCreate extends HeartBeatBase {
  status?: SystemStatus
}

export interface HeartBeatUpdate {
  ip_address?: string
  port?: number
  status?: SystemStatus
  response_time?: number
  uptime?: number
  cpu_usage?: number
  memory_usage?: number
  disk_usage?: number
  last_heartbeat?: string
  last_response?: string
}

export interface HeartBeatResponse extends HeartBeatBase {
  id: number
  status: SystemStatus
  last_heartbeat?: string
  last_response?: string
  created_at: string
  updated_at: string
}

// =============================================================================
// Report Template Types
// =============================================================================

export interface ReportTemplateBase {
  name: string
  description?: string
  report_type: ReportType
  query_config?: Record<string, any>
  display_config?: Record<string, any>
  filter_config?: Record<string, any>
  is_public: boolean
  is_active: boolean
}

export interface ReportTemplateCreate extends ReportTemplateBase {
  created_by?: string
}

export interface ReportTemplateUpdate {
  name?: string
  description?: string
  query_config?: Record<string, any>
  display_config?: Record<string, any>
  filter_config?: Record<string, any>
  is_public?: boolean
  is_active?: boolean
}

export interface ReportTemplateResponse extends ReportTemplateBase {
  id: number
  created_by?: string
  created_at: string
  updated_at: string
}

// =============================================================================
// Report Generation Types
// =============================================================================

export interface ReportGenerationBase {
  report_name: string
  report_type: ReportType
  template_id?: number
  parameters?: Record<string, any>
  date_range_start?: string
  date_range_end?: string
}

export interface ReportGenerationCreate extends ReportGenerationBase {
  generated_by?: string
}

export interface ReportGenerationUpdate {
  status?: string
  progress?: number
  result_count?: number
  file_path?: string
  file_size?: number
  error_message?: string
  completed_at?: string
}

export interface ReportGenerationResponse extends ReportGenerationBase {
  id: number
  status: string
  progress: number
  result_count?: number
  file_path?: string
  file_size?: number
  error_message?: string
  generated_by?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

// =============================================================================
// Server Monitoring Types
// =============================================================================

export interface ServerMonitoringBase {
  server_name: string
  ip_address: string
  server_type: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in?: number
  network_out?: number
  uptime?: number
  load_average?: string
  active_connections?: number
  services_status?: Record<string, any>
}

export interface ServerMonitoringCreate extends ServerMonitoringBase {}

export interface ServerMonitoringResponse extends ServerMonitoringBase {
  id: number
  recorded_at: string
}

// =============================================================================
// Report Query Types
// =============================================================================

export interface OnlineUsersReportQuery {
  nas_ip?: string
  username?: string
  session_timeout_min?: number
}

export interface HistoryReportQuery {
  username?: string
  nas_ip?: string
  start_date?: string
  end_date?: string
  session_time_min?: number
}

export interface NewUsersReportQuery {
  start_date?: string
  end_date?: string
  group_name?: string
}

export interface TopUsersReportQuery {
  start_date?: string
  end_date?: string
  limit?: number
  order_by?: 'total_traffic' | 'session_time' | 'session_count'
}

export interface SystemLogQuery {
  log_level?: LogLevel
  logger_name?: string
  username?: string
  start_date?: string
  end_date?: string
  search_text?: string
}

export interface BatchReportQuery {
  batch_name?: string
  start_date?: string
  end_date?: string
}

// =============================================================================
// Report Data Types
// =============================================================================

export interface OnlineUserReport {
  username: string
  nas_ip_address: string
  session_id: string
  start_time: string
  session_duration: number
  input_octets: number
  output_octets: number
  framed_ip_address?: string
}

export interface HistoryReportItem {
  username: string
  session_start: string
  session_end?: string
  session_time: number
  input_octets: number
  output_octets: number
  nas_ip_address: string
  terminate_cause?: string
}

export interface NewUserReportItem {
  username: string
  created_date: string
  first_login?: string
  group_name?: string
  email?: string
  status: string
}

export interface TopUserReportItem {
  username: string
  total_traffic: number
  session_time: number
  session_count: number
  last_session?: string
}

export interface SystemLogReportItem {
  timestamp: string
  log_level: string
  logger_name: string
  message: string
  username?: string
  ip_address?: string
}

export interface BatchReportItem {
  batch_name: string
  description?: string
  user_count: number
  success_count: number
  failed_count: number
  created_date: string
}

// =============================================================================
// System Status Report Types
// =============================================================================

export interface SystemStatusReport {
  server_status: Array<{
    server_name: string
    ip_address: string
    server_type: string
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    uptime?: number
    recorded_at: string
  }>
  service_status: Array<{
    service_name: string
    host_name: string
    status: string
    response_time?: number
    last_heartbeat?: string
  }>
  ups_status: UpsStatusResponse[]
  raid_status: RaidStatusResponse[]
  heartbeat_status: HeartBeatResponse[]
  generated_at: string
}

// =============================================================================
// List Response Types
// =============================================================================

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export type UpsStatusListResponse = PaginatedResponse<UpsStatusResponse>
export type RaidStatusListResponse = PaginatedResponse<RaidStatusResponse>
export type HeartBeatListResponse = PaginatedResponse<HeartBeatResponse>
export type ReportTemplateListResponse = PaginatedResponse<ReportTemplateResponse>
export type ReportGenerationListResponse = PaginatedResponse<ReportGenerationResponse>
export type ServerMonitoringListResponse = PaginatedResponse<ServerMonitoringResponse>

// =============================================================================
// Dashboard Types
// =============================================================================

export interface ReportsDashboard {
  online_users_count: number
  daily_sessions: number
  system_health: {
    servers_monitored: number
    services_monitored: number
    ups_devices: number
    raid_arrays: number
  }
  generated_at: string
  error?: string
}

// =============================================================================
// UI Component Types
// =============================================================================

export interface ReportFilter {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'like' | 'in'
  value: any
  label: string
}

export interface ReportColumn {
  key: string
  title: string
  dataIndex: string
  width?: number
  sortable?: boolean
  filterable?: boolean
  formatter?: (value: any, record: any) => string
}

export interface ReportExportOptions {
  format: 'csv' | 'excel' | 'pdf' | 'json'
  filename?: string
  includeHeaders: boolean
  dateRange?: {
    start: string
    end: string
  }
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'area'
  title: string
  xAxis: string
  yAxis: string
  data: any[]
  options?: Record<string, any>
}

// =============================================================================
// Form Types
// =============================================================================

export interface DateRangeSelection {
  start: string
  end: string
}

export interface ReportFormData {
  name: string
  type: ReportType
  description?: string
  dateRange?: DateRangeSelection
  filters?: ReportFilter[]
  template?: number
  parameters?: Record<string, any>
}