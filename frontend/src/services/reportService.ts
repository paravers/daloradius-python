// 报表管理服务
import type {
  Report,
  ReportData,
  ReportTemplate,
  CreateReportRequest,
  UpdateReportRequest,
  GenerateReportRequest,
  ReportSearchParams,
  ReportListResponse,
  UserUsageReport,
  TrafficAnalysisReport,
  RevenueReport,
  DevicePerformanceReport,
  ReportType,
  ReportStatus,
  ReportFormat
} from '@/types/report';
import { BUILTIN_REPORT_TEMPLATES } from '@/types/report';

// 模拟数据
const mockReports: Report[] = [
  {
    id: '1',
    name: '用户月度使用报表',
    type: ReportType.USER_USAGE,
    description: '统计用户每月的流量使用情况',
    parameters: [
      {
        key: 'month',
        label: '统计月份',
        type: 'date' as any,
        required: true,
        defaultValue: '2024-09'
      }
    ],
    status: ReportStatus.ACTIVE,
    createTime: '2024-09-01 10:00:00',
    updateTime: '2024-09-29 14:30:00',
    lastRunTime: '2024-09-29 08:00:00',
    nextRunTime: '2024-10-01 08:00:00',
    createdBy: 'admin'
  },
  {
    id: '2',
    name: '流量趋势分析',
    type: ReportType.TRAFFIC_ANALYSIS,
    description: '分析网络流量的使用趋势和峰值',
    parameters: [
      {
        key: 'dateRange',
        label: '日期范围',
        type: 'date_range' as any,
        required: true
      }
    ],
    status: ReportStatus.ACTIVE,
    createTime: '2024-08-15 15:20:00',
    updateTime: '2024-09-20 11:45:00',
    lastRunTime: '2024-09-29 06:00:00',
    createdBy: 'admin'
  },
  {
    id: '3',
    name: '收入统计报表',
    type: ReportType.REVENUE_STATISTICS,
    description: '统计各计费计划的收入情况',
    parameters: [
      {
        key: 'year',
        label: '统计年份',
        type: 'number' as any,
        required: true,
        defaultValue: 2024
      }
    ],
    status: ReportStatus.PAUSED,
    createTime: '2024-07-10 09:30:00',
    updateTime: '2024-09-15 16:20:00',
    lastRunTime: '2024-09-15 08:00:00',
    createdBy: 'manager'
  }
];

class ReportService {
  private baseUrl = '/api/reports';

  // 获取报表列表
  async getReports(params: ReportSearchParams = {}): Promise<ReportListResponse> {
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      let filteredReports = [...mockReports];
      
      // 应用过滤条件
      if (params.name) {
        filteredReports = filteredReports.filter(report => 
          report.name.toLowerCase().includes(params.name!.toLowerCase())
        );
      }
      
      if (params.type) {
        filteredReports = filteredReports.filter(report => report.type === params.type);
      }
      
      if (params.status) {
        filteredReports = filteredReports.filter(report => report.status === params.status);
      }
      
      if (params.createdBy) {
        filteredReports = filteredReports.filter(report => 
          report.createdBy.toLowerCase().includes(params.createdBy!.toLowerCase())
        );
      }
      
      // 排序
      if (params.sortBy) {
        filteredReports.sort((a, b) => {
          const aValue = (a as any)[params.sortBy!];
          const bValue = (b as any)[params.sortBy!];
          const order = params.sortOrder === 'desc' ? -1 : 1;
          
          if (aValue < bValue) return -1 * order;
          if (aValue > bValue) return 1 * order;
          return 0;
        });
      }
      
      // 分页
      const page = params.page || 1;
      const pageSize = params.pageSize || 10;
      const startIndex = (page - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedReports = filteredReports.slice(startIndex, endIndex);
      
      return {
        reports: paginatedReports,
        total: filteredReports.length,
        page,
        pageSize
      };
    } catch (error) {
      console.error('获取报表列表失败:', error);
      throw new Error('获取报表列表失败');
    }
  }

  // 获取报表详情
  async getReport(id: string): Promise<Report> {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const report = mockReports.find(r => r.id === id);
      if (!report) {
        throw new Error('报表不存在');
      }
      
      return report;
    } catch (error) {
      console.error('获取报表详情失败:', error);
      throw error;
    }
  }

  // 创建报表
  async createReport(data: CreateReportRequest): Promise<Report> {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const newReport: Report = {
        id: Date.now().toString(),
        ...data,
        status: ReportStatus.DRAFT,
        createTime: new Date().toLocaleString('zh-CN'),
        updateTime: new Date().toLocaleString('zh-CN'),
        createdBy: 'admin' // 实际应该从当前用户获取
      };
      
      mockReports.unshift(newReport);
      return newReport;
    } catch (error) {
      console.error('创建报表失败:', error);
      throw new Error('创建报表失败');
    }
  }

  // 更新报表
  async updateReport(id: string, data: UpdateReportRequest): Promise<Report> {
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      const reportIndex = mockReports.findIndex(r => r.id === id);
      if (reportIndex === -1) {
        throw new Error('报表不存在');
      }
      
      const updatedReport = {
        ...mockReports[reportIndex],
        ...data,
        updateTime: new Date().toLocaleString('zh-CN')
      };
      
      mockReports[reportIndex] = updatedReport;
      return updatedReport;
    } catch (error) {
      console.error('更新报表失败:', error);
      throw error;
    }
  }

  // 删除报表
  async deleteReport(id: string): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const reportIndex = mockReports.findIndex(r => r.id === id);
      if (reportIndex === -1) {
        throw new Error('报表不存在');
      }
      
      mockReports.splice(reportIndex, 1);
    } catch (error) {
      console.error('删除报表失败:', error);
      throw error;
    }
  }

  // 生成报表数据
  async generateReport(request: GenerateReportRequest): Promise<ReportData> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const report = mockReports.find(r => r.id === request.reportId);
      if (!report) {
        throw new Error('报表不存在');
      }
      
      // 根据报表类型生成不同的模拟数据
      let data: any[] = [];
      let summary: any = {};
      let charts: any[] = [];
      
      switch (report.type) {
        case ReportType.USER_USAGE:
          data = this.generateUserUsageData();
          summary = {
            totalRecords: data.length,
            totalValue: data.reduce((sum, item) => sum + item.totalTraffic, 0),
            averageValue: data.reduce((sum, item) => sum + item.totalTraffic, 0) / data.length
          };
          charts = this.generateUserUsageCharts(data);
          break;
          
        case ReportType.TRAFFIC_ANALYSIS:
          data = this.generateTrafficAnalysisData();
          summary = {
            totalRecords: data.length,
            totalValue: data.reduce((sum, item) => sum + item.totalTraffic, 0)
          };
          charts = this.generateTrafficAnalysisCharts(data);
          break;
          
        case ReportType.REVENUE_STATISTICS:
          data = this.generateRevenueData();
          summary = {
            totalRecords: data.length,
            totalValue: data.reduce((sum, item) => sum + item.revenue, 0)
          };
          charts = this.generateRevenueCharts(data);
          break;
          
        default:
          data = this.generateDefaultData();
          summary = { totalRecords: data.length };
      }
      
      return {
        reportId: request.reportId,
        reportName: report.name,
        generateTime: new Date().toISOString(),
        parameters: request.parameters,
        summary,
        data,
        charts
      };
    } catch (error) {
      console.error('生成报表数据失败:', error);
      throw error;
    }
  }

  // 获取报表模板
  async getReportTemplates(): Promise<ReportTemplate[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 200));
      return BUILTIN_REPORT_TEMPLATES;
    } catch (error) {
      console.error('获取报表模板失败:', error);
      throw new Error('获取报表模板失败');
    }
  }

  // 导出报表
  async exportReport(reportId: string, format: ReportFormat, data: ReportData): Promise<Blob> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      switch (format) {
        case ReportFormat.CSV:
          return this.exportToCsv(data);
        case ReportFormat.EXCEL:
          return this.exportToExcel(data);
        case ReportFormat.PDF:
          return this.exportToPdf(data);
        default:
          return this.exportToJson(data);
      }
    } catch (error) {
      console.error('导出报表失败:', error);
      throw new Error('导出报表失败');
    }
  }

  // 生成用户使用数据
  private generateUserUsageData(): UserUsageReport[] {
    return Array.from({ length: 20 }, (_, i) => ({
      userId: `user_${i + 1}`,
      username: `user${i + 1}@example.com`,
      totalSessions: Math.floor(Math.random() * 100) + 10,
      totalDuration: Math.floor(Math.random() * 10000) + 1000,
      totalUpload: Math.floor(Math.random() * 1024 * 1024 * 100),
      totalDownload: Math.floor(Math.random() * 1024 * 1024 * 500),
      lastLoginTime: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
      deviceCount: Math.floor(Math.random() * 5) + 1,
      averageSessionDuration: Math.floor(Math.random() * 3600) + 600
    }));
  }

  // 生成流量分析数据
  private generateTrafficAnalysisData(): any[] {
    return Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toISOString().split('T')[0],
        totalTraffic: Math.floor(Math.random() * 1000000000),
        uploadTraffic: Math.floor(Math.random() * 300000000),
        downloadTraffic: Math.floor(Math.random() * 700000000),
        sessions: Math.floor(Math.random() * 1000) + 100,
        users: Math.floor(Math.random() * 500) + 50
      };
    });
  }

  // 生成收入数据
  private generateRevenueData(): any[] {
    return Array.from({ length: 12 }, (_, i) => ({
      month: `2024-${(i + 1).toString().padStart(2, '0')}`,
      revenue: Math.floor(Math.random() * 50000) + 10000,
      userCount: Math.floor(Math.random() * 500) + 100,
      planRevenue: {
        basic: Math.floor(Math.random() * 15000),
        premium: Math.floor(Math.random() * 25000),
        enterprise: Math.floor(Math.random() * 35000)
      }
    }));
  }

  // 生成默认数据
  private generateDefaultData(): any[] {
    return Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      name: `数据项 ${i + 1}`,
      value: Math.floor(Math.random() * 1000),
      timestamp: new Date().toISOString()
    }));
  }

  // 生成用户使用图表
  private generateUserUsageCharts(data: UserUsageReport[]): any[] {
    return [
      {
        id: 'traffic_distribution',
        title: '用户流量分布',
        type: 'pie',
        data: data.slice(0, 10).map(item => ({
          name: item.username,
          value: item.totalDownload + item.totalUpload
        }))
      },
      {
        id: 'session_trend',
        title: '会话数趋势',
        type: 'bar',
        data: data.slice(0, 10).map(item => ({
          name: item.username,
          value: item.totalSessions
        }))
      }
    ];
  }

  // 生成流量分析图表
  private generateTrafficAnalysisCharts(data: any[]): any[] {
    return [
      {
        id: 'traffic_trend',
        title: '流量趋势',
        type: 'line',
        data: data.map(item => ({
          name: item.date,
          value: item.totalTraffic
        }))
      },
      {
        id: 'upload_download',
        title: '上传下载对比',
        type: 'bar',
        data: data.slice(-7).map(item => ({
          name: item.date,
          upload: item.uploadTraffic,
          download: item.downloadTraffic
        }))
      }
    ];
  }

  // 生成收入图表
  private generateRevenueCharts(data: any[]): any[] {
    return [
      {
        id: 'monthly_revenue',
        title: '月度收入趋势',
        type: 'line',
        data: data.map(item => ({
          name: item.month,
          value: item.revenue
        }))
      },
      {
        id: 'plan_revenue',
        title: '计划收入分布',
        type: 'pie',
        data: [
          { name: '基础版', value: data.reduce((sum, item) => sum + item.planRevenue.basic, 0) },
          { name: '高级版', value: data.reduce((sum, item) => sum + item.planRevenue.premium, 0) },
          { name: '企业版', value: data.reduce((sum, item) => sum + item.planRevenue.enterprise, 0) }
        ]
      }
    ];
  }

  // 导出为CSV
  private exportToCsv(data: ReportData): Blob {
    const headers = Object.keys(data.data[0] || {});
    const csvContent = [
      headers.join(','),
      ...data.data.map(row => 
        headers.map(header => JSON.stringify(row[header] || '')).join(',')
      )
    ].join('\n');
    
    return new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
  }

  // 导出为Excel
  private exportToExcel(data: ReportData): Blob {
    // 模拟Excel导出
    const excelContent = JSON.stringify(data, null, 2);
    return new Blob([excelContent], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
  }

  // 导出为PDF
  private exportToPdf(data: ReportData): Blob {
    // 模拟PDF导出
    const pdfContent = `报表: ${data.reportName}\n生成时间: ${data.generateTime}\n\n${JSON.stringify(data.summary, null, 2)}`;
    return new Blob([pdfContent], { type: 'application/pdf' });
  }

  // 导出为JSON
  private exportToJson(data: ReportData): Blob {
    return new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  }
}

export const reportService = new ReportService();