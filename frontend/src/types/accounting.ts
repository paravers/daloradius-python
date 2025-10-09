/**
 * Accounting Types
 * 
 * TypeScript type definitions for accounting/session statistics module
 */

// =====================================================================
// Base Types
// =====================================================================

export interface AccountingSession {
  radacctid: number
  username: string
  realm?: string
  acctsessionid: string
  acctuniqueid?: string
  groupname?: string
  nasipaddress: string
  nasportid?: string
  nasporttype?: string
  calledstationid?: string
  callingstationid?: string
  framedipaddress?: string
  servicetype?: string
  acctstarttime?: string
  acctstoptime?: string
  acctsessiontime?: number
  acctinputoctets?: number
  acctoutputoctets?: number
  acctinputpackets?: number
  acctoutputpackets?: number
  acctterminatecause?: string
  total_bytes: number
  total_packets: number
  is_active: boolean
  formatted_duration?: string
}

export interface UserTrafficSummary {
  id: number
  username: string
  summary_date: string
  total_sessions: number
  total_session_time: number
  total_input_octets: number
  total_output_octets: number
  total_bytes: number
  avg_session_duration: number
  created_at: string
  updated_at: string
}

export interface NasTrafficSummary {
  id: number
  nasipaddress: string
  summary_date: string
  total_sessions: number
  total_session_time: number
  total_input_octets: number
  total_output_octets: number
  total_bytes: number
  unique_users: number
  avg_session_duration: number
  created_at: string
  updated_at: string
}

// =====================================================================
// Filter Types
// =====================================================================

export type AccountingTimeRangeEnum = 
  | 'TODAY'
  | 'YESTERDAY' 
  | 'THIS_WEEK'
  | 'LAST_WEEK'
  | 'THIS_MONTH'
  | 'LAST_MONTH'
  | 'THIS_YEAR'

export type AccountingStatusEnum = 'active' | 'completed' | 'all'

export interface AccountingQueryFilters {
  username?: string | null
  groupname?: string | null
  nasipaddress?: string | null
  framedipaddress?: string | null
  callingstationid?: string | null
  servicetype?: string | null
  time_range?: AccountingTimeRangeEnum | null
  start_date?: string | null
  end_date?: string | null
  status?: AccountingStatusEnum | null
  active_only?: boolean
  min_input_octets?: number | null
  max_input_octets?: number | null
  min_output_octets?: number | null
  max_output_octets?: number | null
  min_session_time?: number | null
  max_session_time?: number | null
}

export interface SessionFilters extends AccountingQueryFilters {}

export interface ActiveSessionFilters {
  username?: string | null
  nas_ip?: string | null
  sort_by?: string
}

export interface ReportFilters {
  time_range?: AccountingTimeRangeEnum | null
  start_date?: string | null
  end_date?: string | null
  report_type?: 'summary' | 'detailed' | 'comparative'
}

// =====================================================================
// Query Types
// =====================================================================

export interface AccountingQuery {
  page: number
  page_size: number
  sort_field?: string
  sort_order?: 'asc' | 'desc'
  filters?: AccountingQueryFilters
}

export interface CustomQueryRequest {
  query_sql: string
  parameters?: Record<string, any>
  limit?: number
}

export interface MaintenanceRequest {
  days_old: number
  dry_run?: boolean
}

// =====================================================================
// Statistics Types
// =====================================================================

export interface SessionStatistics {
  total_sessions: number
  active_sessions: number
  completed_sessions: number
  average_session_duration: number
  total_session_time: number
  unique_users: number
}

export interface TrafficStatistics {
  total_input_octets: number
  total_output_octets: number
  total_bytes: number
  total_input_packets: number
  total_output_packets: number
  total_packets: number
  average_throughput?: number
}

export interface ActiveSessionStatistics {
  total_active: number
  total_current_traffic: number
  unique_users: number
  average_session_duration: number
}

// =====================================================================
// Report Types
// =====================================================================

export interface AccountingOverview {
  session_stats: SessionStatistics
  traffic_stats: TrafficStatistics
  time_period: string
  last_updated: string
}

export interface TopUsersReport {
  username: string
  total_sessions: number
  total_bytes: number
  total_session_time: number
  last_session?: string
  rank: number
}

export interface HourlyTrafficReport {
  hour: number
  session_count: number
  total_bytes: number
  unique_users: number
}

export interface DailyTrafficReport {
  date: string
  session_count: number
  total_bytes: number
  unique_users: number
  peak_hour: number
}

export interface NasUsageReport {
  nasipaddress: string
  nas_name?: string
  total_sessions: number
  active_sessions: number
  total_bytes: number
  utilization_percentage: number
}

export interface CustomQueryResult {
  columns: string[]
  rows: any[][]
  total_rows: number
  execution_time: number
}

export interface MaintenanceResult {
  operation_type: string
  affected_rows: number
  execution_time: number
  success: boolean
  message: string
}

// =====================================================================
// Response Types
// =====================================================================

export interface PaginatedAccountingResponse {
  data: AccountingSession[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface PaginatedTopUsersResponse {
  data: TopUsersReport[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UserTrafficSummaryResponse extends UserTrafficSummary {}
export interface NasTrafficSummaryResponse extends NasTrafficSummary {}

// =====================================================================
// Store State Types
// =====================================================================

export interface AccountingState {
  // Session data
  sessions: AccountingSession[]
  activeSessions: AccountingSession[]
  recentSessions: AccountingSession[]
  
  // Pagination
  sessionsPagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  
  activeSessionsPagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  
  // Statistics
  overview: AccountingOverview | null
  sessionStatistics: SessionStatistics
  activeSessionStatistics: ActiveSessionStatistics
  
  // Reports
  topUsers: TopUsersReport[]
  overviewReport: AccountingOverview | null
  topUsersReport: TopUsersReport[]
  trafficAnalysisReport: any | null
  nasUsageReport: NasUsageReport[]
  timeAnalysisReport: any | null
  
  // Traffic summaries
  userTrafficSummaries: UserTrafficSummary[]
  nasTrafficSummaries: NasTrafficSummary[]
  
  // Loading states
  loading: {
    sessions: boolean
    activeSessions: boolean
    overview: boolean
    reports: boolean
    export: boolean
  }
  
  // Error states
  error: string | null
}

// =====================================================================
// API Service Types
// =====================================================================

export interface AccountingApiParams {
  sessions?: AccountingQuery
  activeSessions?: {
    page?: number
    page_size?: number
    nas_ip?: string
    username?: string
  }
  overview?: {
    time_range?: AccountingTimeRangeEnum
    date_from?: string
    date_to?: string
    filters?: AccountingQueryFilters
  }
  topUsers?: {
    limit?: number
    page?: number
    page_size?: number
    date_from?: string
    date_to?: string
  }
  reports?: ReportFilters
  export?: {
    type: string
    format: string
    filters?: any
  }
}

// =====================================================================
// Component Props Types
// =====================================================================

export interface SessionsListProps {
  sessions: AccountingSession[]
  loading?: boolean
  compact?: boolean
  showActions?: boolean
}

export interface SessionDetailsDialogProps {
  modelValue: boolean
  session: AccountingSession | null
}

export interface TopUsersListProps {
  users: TopUsersReport[]
  loading?: boolean
  compact?: boolean
  showActions?: boolean
}

export interface OverviewReportProps {
  data: AccountingOverview | null
  loading?: boolean
  filters: ReportFilters
}

// =====================================================================
// Utility Types
// =====================================================================

export type SortOrder = 'asc' | 'desc'

export interface TableHeader {
  title: string
  key: string
  sortable?: boolean
  width?: number
  align?: 'start' | 'center' | 'end'
}

export interface ChartDataPoint {
  label: string
  value: number
  color?: string
}

export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf'
  filename?: string
  includeCharts?: boolean
}

// =====================================================================
// Event Types
// =====================================================================

export interface SessionEvent {
  type: 'view' | 'edit' | 'delete' | 'disconnect' | 'terminate'
  session: AccountingSession
}

export interface ReportEvent {
  type: 'export' | 'refresh' | 'filter'
  reportType: string
  data?: any
}

// =====================================================================
// Form Types
// =====================================================================

export interface SessionFilterForm {
  username: string
  nasipaddress: string
  dateRange: string[]
  status: AccountingStatusEnum
  trafficRange: [number, number]
}

export interface ReportConfigForm {
  timeRange: AccountingTimeRangeEnum
  reportTypes: string[]
  exportFormat: 'csv' | 'xlsx' | 'pdf'
  includeCharts: boolean
}

// =====================================================================
// Validation Types
// =====================================================================

export interface ValidationError {
  field: string
  message: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
}

// =====================================================================
// Theme Types
// =====================================================================

export interface AccountingTheme {
  primary: string
  secondary: string
  success: string
  warning: string
  error: string
  info: string
}

// Note: All types are already exported as named exports above.
// No need for additional export declarations.