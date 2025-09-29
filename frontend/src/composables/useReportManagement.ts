// 报表管理组合式函数
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import { reportService } from '@/services/reportService';
import type {
  Report,
  ReportData,
  ReportTemplate,
  CreateReportRequest,
  UpdateReportRequest,
  GenerateReportRequest,
  ReportSearchParams,
  ReportStatus,
  ReportType,
  ReportFormat
} from '@/types/report';

export function useReportManagement() {
  // 响应式状态
  const reports = ref<Report[]>([]);
  const loading = ref(false);
  const total = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);
  
  // 搜索参数
  const searchParams = reactive<ReportSearchParams>({
    name: '',
    type: undefined,
    status: undefined,
    createdBy: '',
    page: 1,
    pageSize: 10,
    sortBy: 'createTime',
    sortOrder: 'desc'
  });

  // 选中的报表
  const selectedReports = ref<string[]>([]);
  const selectedReport = ref<Report | null>(null);

  // 计算属性
  const hasSelection = computed(() => selectedReports.value.length > 0);
  const selectionCount = computed(() => selectedReports.value.length);

  // 获取报表列表
  const fetchReports = async (params?: Partial<ReportSearchParams>) => {
    try {
      loading.value = true;
      const queryParams = { ...searchParams, ...params };
      const response = await reportService.getReports(queryParams);
      
      reports.value = response.reports;
      total.value = response.total;
      currentPage.value = response.page;
      pageSize.value = response.pageSize;
    } catch (error) {
      message.error('获取报表列表失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 获取报表详情
  const fetchReport = async (id: string) => {
    try {
      loading.value = true;
      const report = await reportService.getReport(id);
      selectedReport.value = report;
      return report;
    } catch (error) {
      message.error('获取报表详情失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 创建报表
  const createReport = async (data: CreateReportRequest) => {
    try {
      loading.value = true;
      const report = await reportService.createReport(data);
      message.success('报表创建成功');
      await fetchReports(); // 刷新列表
      return report;
    } catch (error) {
      message.error('报表创建失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 更新报表
  const updateReport = async (id: string, data: UpdateReportRequest) => {
    try {
      loading.value = true;
      const report = await reportService.updateReport(id, data);
      message.success('报表更新成功');
      await fetchReports(); // 刷新列表
      return report;
    } catch (error) {
      message.error('报表更新失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 删除报表
  const deleteReport = async (id: string) => {
    try {
      loading.value = true;
      await reportService.deleteReport(id);
      message.success('报表删除成功');
      await fetchReports(); // 刷新列表
    } catch (error) {
      message.error('报表删除失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 批量删除报表
  const deleteSelectedReports = async () => {
    if (selectedReports.value.length === 0) {
      message.warning('请先选择要删除的报表');
      return;
    }

    try {
      loading.value = true;
      for (const reportId of selectedReports.value) {
        await reportService.deleteReport(reportId);
      }
      message.success(`成功删除 ${selectedReports.value.length} 个报表`);
      selectedReports.value = [];
      await fetchReports(); // 刷新列表
    } catch (error) {
      message.error('批量删除报表失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 搜索报表
  const searchReports = async () => {
    searchParams.page = 1;
    await fetchReports();
  };

  // 重置搜索
  const resetSearch = () => {
    Object.assign(searchParams, {
      name: '',
      type: undefined,
      status: undefined,
      createdBy: '',
      page: 1,
      pageSize: 10,
      sortBy: 'createTime',
      sortOrder: 'desc'
    });
    fetchReports();
  };

  // 分页变化
  const onPageChange = (page: number, size: number) => {
    searchParams.page = page;
    searchParams.pageSize = size;
    fetchReports();
  };

  // 排序变化
  const onSortChange = (sortBy: string, sortOrder: 'asc' | 'desc') => {
    searchParams.sortBy = sortBy;
    searchParams.sortOrder = sortOrder;
    fetchReports();
  };

  // 选择报表
  const toggleReportSelection = (reportId: string) => {
    const index = selectedReports.value.indexOf(reportId);
    if (index > -1) {
      selectedReports.value.splice(index, 1);
    } else {
      selectedReports.value.push(reportId);
    }
  };

  // 全选/取消全选
  const toggleAllSelection = (checked: boolean) => {
    selectedReports.value = checked ? reports.value.map(r => r.id) : [];
  };

  // 清空选择
  const clearSelection = () => {
    selectedReports.value = [];
  };

  return {
    // 状态
    reports,
    loading,
    total,
    currentPage,
    pageSize,
    searchParams,
    selectedReports,
    selectedReport,
    
    // 计算属性
    hasSelection,
    selectionCount,
    
    // 方法
    fetchReports,
    fetchReport,
    createReport,
    updateReport,
    deleteReport,
    deleteSelectedReports,
    searchReports,
    resetSearch,
    onPageChange,
    onSortChange,
    toggleReportSelection,
    toggleAllSelection,
    clearSelection
  };
}

// 报表生成管理
export function useReportGeneration() {
  const reportData = ref<ReportData | null>(null);
  const generating = ref(false);
  const exporting = ref(false);

  // 生成报表
  const generateReport = async (request: GenerateReportRequest): Promise<ReportData> => {
    try {
      generating.value = true;
      const data = await reportService.generateReport(request);
      reportData.value = data;
      message.success('报表生成成功');
      return data;
    } catch (error) {
      message.error('报表生成失败');
      throw error;
    } finally {
      generating.value = false;
    }
  };

  // 导出报表
  const exportReport = async (reportId: string, format: ReportFormat, data?: ReportData) => {
    if (!data && !reportData.value) {
      message.warning('请先生成报表数据');
      return;
    }

    try {
      exporting.value = true;
      const exportData = data || reportData.value!;
      const blob = await reportService.exportReport(reportId, format, exportData);
      
      // 下载文件
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exportData.reportName}-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      message.success(`报表导出成功 (${format.toUpperCase()})`);
    } catch (error) {
      message.error('报表导出失败');
      throw error;
    } finally {
      exporting.value = false;
    }
  };

  // 清空报表数据
  const clearReportData = () => {
    reportData.value = null;
  };

  // 格式化数值
  const formatValue = (value: any, type?: string): string => {
    if (value === null || value === undefined) return '-';
    
    switch (type) {
      case 'traffic':
        return formatTraffic(value);
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return `${(value * 100).toFixed(2)}%`;
      case 'duration':
        return formatDuration(value);
      default:
        return String(value);
    }
  };

  // 格式化流量
  const formatTraffic = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

  // 格式化货币
  const formatCurrency = (amount: number): string => {
    return `¥${amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`;
  };

  // 格式化时长
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}小时${minutes}分${secs}秒`;
    } else if (minutes > 0) {
      return `${minutes}分${secs}秒`;
    } else {
      return `${secs}秒`;
    }
  };

  return {
    reportData,
    generating,
    exporting,
    generateReport,
    exportReport,
    clearReportData,
    formatValue,
    formatTraffic,
    formatCurrency,
    formatDuration
  };
}

// 报表模板管理
export function useReportTemplates() {
  const templates = ref<ReportTemplate[]>([]);
  const loading = ref(false);

  // 获取报表模板
  const fetchTemplates = async () => {
    try {
      loading.value = true;
      const result = await reportService.getReportTemplates();
      templates.value = result;
    } catch (error) {
      message.error('获取报表模板失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 根据类型筛选模板
  const getTemplatesByType = (type: ReportType) => {
    return templates.value.filter(template => template.type === type);
  };

  // 获取模板
  const getTemplate = (id: string) => {
    return templates.value.find(template => template.id === id);
  };

  return {
    templates,
    loading,
    fetchTemplates,
    getTemplatesByType,
    getTemplate
  };
}