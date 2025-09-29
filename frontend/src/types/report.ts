// 报表系统相关类型定义
export interface Report {
  id: string;
  name: string;
  type: ReportType;
  description?: string;
  parameters: ReportParameter[];
  status: ReportStatus;
  createTime: string;
  updateTime: string;
  lastRunTime?: string;
  nextRunTime?: string;
  createdBy: string;
}

export enum ReportType {
  USER_USAGE = 'user_usage',
  TRAFFIC_ANALYSIS = 'traffic_analysis',
  REVENUE_STATISTICS = 'revenue_statistics',
  DEVICE_PERFORMANCE = 'device_performance',
  SESSION_ANALYSIS = 'session_analysis',
  BILLING_SUMMARY = 'billing_summary',
  CUSTOM_QUERY = 'custom_query'
}

export enum ReportStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  ARCHIVED = 'archived'
}

export interface ReportParameter {
  key: string;
  label: string;
  type: ParameterType;
  required: boolean;
  defaultValue?: any;
  options?: ParameterOption[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

export enum ParameterType {
  STRING = 'string',
  NUMBER = 'number',
  DATE = 'date',
  DATE_RANGE = 'date_range',
  SELECT = 'select',
  MULTI_SELECT = 'multi_select',
  BOOLEAN = 'boolean',
  USER_SELECT = 'user_select',
  DEVICE_SELECT = 'device_select'
}

export interface ParameterOption {
  label: string;
  value: any;
}

export interface ReportData {
  reportId: string;
  reportName: string;
  generateTime: string;
  parameters: Record<string, any>;
  summary: ReportSummary;
  data: ReportDataItem[];
  charts?: ReportChart[];
}

export interface ReportSummary {
  totalRecords: number;
  totalValue?: number;
  averageValue?: number;
  maxValue?: number;
  minValue?: number;
  customMetrics?: Record<string, any>;
}

export interface ReportDataItem {
  [key: string]: any;
}

export interface ReportChart {
  id: string;
  title: string;
  type: ChartType;
  data: ChartDataItem[];
  options?: ChartOptions;
}

export enum ChartType {
  LINE = 'line',
  BAR = 'bar',
  PIE = 'pie',
  AREA = 'area',
  SCATTER = 'scatter',
  RADAR = 'radar'
}

export interface ChartDataItem {
  name: string;
  value: number;
  [key: string]: any;
}

export interface ChartOptions {
  xAxisLabel?: string;
  yAxisLabel?: string;
  colors?: string[];
  showLegend?: boolean;
  showGrid?: boolean;
  smooth?: boolean;
}

export interface ReportTemplate {
  id: string;
  name: string;
  type: ReportType;
  description: string;
  parameters: ReportParameter[];
  sqlTemplate?: string;
  isBuiltin: boolean;
}

export interface CreateReportRequest {
  name: string;
  type: ReportType;
  description?: string;
  parameters: ReportParameter[];
  templateId?: string;
}

export interface UpdateReportRequest {
  name?: string;
  description?: string;
  parameters?: ReportParameter[];
  status?: ReportStatus;
}

export interface GenerateReportRequest {
  reportId: string;
  parameters: Record<string, any>;
  format?: ReportFormat;
  async?: boolean;
}

export enum ReportFormat {
  JSON = 'json',
  CSV = 'csv',
  EXCEL = 'excel',
  PDF = 'pdf'
}

export interface ReportSearchParams {
  name?: string;
  type?: ReportType;
  status?: ReportStatus;
  createdBy?: string;
  createTimeStart?: string;
  createTimeEnd?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface ReportListResponse {
  reports: Report[];
  total: number;
  page: number;
  pageSize: number;
}

// 用户使用报表数据
export interface UserUsageReport {
  userId: string;
  username: string;
  totalSessions: number;
  totalDuration: number; // 秒
  totalUpload: number; // 字节
  totalDownload: number; // 字节
  lastLoginTime?: string;
  deviceCount: number;
  averageSessionDuration: number;
}

// 流量分析报表数据
export interface TrafficAnalysisReport {
  period: string; // 时间段
  totalTraffic: number;
  uploadTraffic: number;
  downloadTraffic: number;
  peakHour: string;
  peakTraffic: number;
  deviceBreakdown: DeviceTrafficBreakdown[];
  hourlyBreakdown: HourlyTrafficBreakdown[];
}

export interface DeviceTrafficBreakdown {
  deviceId: string;
  deviceName: string;
  traffic: number;
  percentage: number;
}

export interface HourlyTrafficBreakdown {
  hour: string;
  traffic: number;
  sessions: number;
}

// 收入统计报表数据
export interface RevenueReport {
  period: string;
  totalRevenue: number;
  paidAmount: number;
  pendingAmount: number;
  refundAmount: number;
  planBreakdown: PlanRevenueBreakdown[];
  monthlyTrend: MonthlyRevenueBreakdown[];
}

export interface PlanRevenueBreakdown {
  planId: string;
  planName: string;
  revenue: number;
  userCount: number;
  percentage: number;
}

export interface MonthlyRevenueBreakdown {
  month: string;
  revenue: number;
  userCount: number;
  averageRevenue: number;
}

// 设备性能报表数据
export interface DevicePerformanceReport {
  deviceId: string;
  deviceName: string;
  uptime: number;
  averageLatency: number;
  totalSessions: number;
  activeSessions: number;
  errorCount: number;
  successRate: number;
  performanceTrend: PerformanceTrendItem[];
}

export interface PerformanceTrendItem {
  timestamp: string;
  latency: number;
  sessions: number;
  errors: number;
}

// 预定义报表模板
export const BUILTIN_REPORT_TEMPLATES: ReportTemplate[] = [
  {
    id: 'user_usage_monthly',
    name: '用户月度使用统计',
    type: ReportType.USER_USAGE,
    description: '按月统计用户的使用情况，包括流量、时长和会话数',
    parameters: [
      {
        key: 'month',
        label: '统计月份',
        type: ParameterType.DATE,
        required: true,
        defaultValue: new Date().toISOString().slice(0, 7)
      },
      {
        key: 'userGroup',
        label: '用户组',
        type: ParameterType.SELECT,
        required: false,
        options: [
          { label: '全部用户', value: 'all' },
          { label: '付费用户', value: 'paid' },
          { label: '免费用户', value: 'free' }
        ]
      }
    ],
    isBuiltin: true
  },
  {
    id: 'traffic_daily',
    name: '日流量分析报表',
    type: ReportType.TRAFFIC_ANALYSIS,
    description: '分析每日流量使用情况和趋势',
    parameters: [
      {
        key: 'dateRange',
        label: '日期范围',
        type: ParameterType.DATE_RANGE,
        required: true
      },
      {
        key: 'devices',
        label: '设备筛选',
        type: ParameterType.DEVICE_SELECT,
        required: false
      }
    ],
    isBuiltin: true
  },
  {
    id: 'revenue_monthly',
    name: '月度收入统计',
    type: ReportType.REVENUE_STATISTICS,
    description: '统计月度收入情况和趋势分析',
    parameters: [
      {
        key: 'year',
        label: '统计年份',
        type: ParameterType.NUMBER,
        required: true,
        defaultValue: new Date().getFullYear(),
        validation: {
          min: 2020,
          max: 2030
        }
      }
    ],
    isBuiltin: true
  }
];

export const REPORT_TYPE_OPTIONS = [
  { label: '用户使用统计', value: ReportType.USER_USAGE },
  { label: '流量分析', value: ReportType.TRAFFIC_ANALYSIS },
  { label: '收入统计', value: ReportType.REVENUE_STATISTICS },
  { label: '设备性能', value: ReportType.DEVICE_PERFORMANCE },
  { label: '会话分析', value: ReportType.SESSION_ANALYSIS },
  { label: '计费汇总', value: ReportType.BILLING_SUMMARY },
  { label: '自定义查询', value: ReportType.CUSTOM_QUERY }
];

export const REPORT_STATUS_OPTIONS = [
  { label: '草稿', value: ReportStatus.DRAFT, color: 'default' },
  { label: '活跃', value: ReportStatus.ACTIVE, color: 'green' },
  { label: '暂停', value: ReportStatus.PAUSED, color: 'orange' },
  { label: '归档', value: ReportStatus.ARCHIVED, color: 'red' }
];

export const CHART_TYPE_OPTIONS = [
  { label: '折线图', value: ChartType.LINE },
  { label: '柱状图', value: ChartType.BAR },
  { label: '饼图', value: ChartType.PIE },
  { label: '面积图', value: ChartType.AREA },
  { label: '散点图', value: ChartType.SCATTER },
  { label: '雷达图', value: ChartType.RADAR }
];