<template>
  <div class="reports-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1>报表中心</h1>
          <p class="page-description">数据统计和分析报表管理</p>
        </div>
        <div class="header-actions">
          <a-button type="primary" @click="showCreateModal = true">
            <template #icon><PlusOutlined /></template>
            创建报表
          </a-button>
          <a-button @click="showTemplateModal = true">
            <template #icon><FileTextOutlined /></template>
            报表模板
          </a-button>
          <a-button @click="refreshDashboard">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        title="在线用户"
        :value="dashboardData?.online_users_count || 0"
        :loading="dashboardLoading"
        color="blue"
        icon="user"
      />
      <StatCard
        title="今日会话"
        :value="dashboardData?.daily_sessions || 0"
        :loading="dashboardLoading"
        color="green"
        icon="calendar"
      />
      <StatCard
        title="系统健康度"
        :value="systemHealthScore"
        :loading="dashboardLoading"
        color="orange"
        icon="heart"
        suffix="%"
      />
      <StatCard
        title="待处理报表"
        :value="pendingReports.length"
        :loading="dashboardLoading"
        color="purple"
        icon="clock-circle"
      />
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧导航 -->
      <div class="sidebar">
        <a-menu
          v-model:selectedKeys="selectedKeys"
          mode="inline"
          @select="handleMenuSelect"
        >
          <a-menu-item-group title="用户报表">
            <a-menu-item key="online-users">
              <template #icon><UserOutlined /></template>
              在线用户报表
            </a-menu-item>
            <a-menu-item key="history">
              <template #icon><HistoryOutlined /></template>
              历史报表
            </a-menu-item>
            <a-menu-item key="last-connect">
              <template #icon><LinkOutlined /></template>
              最近连接
            </a-menu-item>
            <a-menu-item key="new-users">
              <template #icon><UserAddOutlined /></template>
              新用户报表
            </a-menu-item>
            <a-menu-item key="top-users">
              <template #icon><CrownOutlined /></template>
              热门用户
            </a-menu-item>
          </a-menu-item-group>

          <a-menu-item-group title="系统报表">
            <a-menu-item key="system-logs">
              <template #icon><FileSearchOutlined /></template>
              系统日志
            </a-menu-item>
            <a-menu-item key="batch-report">
              <template #icon><GroupOutlined /></template>
              批量报表
            </a-menu-item>
            <a-menu-item key="system-status">
              <template #icon><DashboardOutlined /></template>
              系统状态
            </a-menu-item>
          </a-menu-item-group>

          <a-menu-item-group title="监控报表">
            <a-menu-item key="heartbeat">
              <template #icon><HeartOutlined /></template>
              心跳监控
            </a-menu-item>
            <a-menu-item key="ups-status">
              <template #icon><ThunderboltOutlined /></template>
              UPS状态
            </a-menu-item>
            <a-menu-item key="raid-status">
              <template #icon><HddOutlined /></template>
              RAID状态
            </a-menu-item>
          </a-menu-item-group>
        </a-menu>
      </div>

      <!-- 右侧内容 -->
      <div class="content-area">
        <!-- 报表工具栏 -->
        <div class="report-toolbar">
          <div class="toolbar-left">
            <a-breadcrumb>
              <a-breadcrumb-item>报表中心</a-breadcrumb-item>
              <a-breadcrumb-item>{{ getCurrentReportTitle() }}</a-breadcrumb-item>
            </a-breadcrumb>
          </div>
          <div class="toolbar-right">
            <a-space>
              <a-button @click="showFiltersModal = true">
                <template #icon><FilterOutlined /></template>
                筛选
              </a-button>
              <a-button @click="exportCurrentReport">
                <template #icon><DownloadOutlined /></template>
                导出
              </a-button>
              <a-button @click="refreshCurrentReport">
                <template #icon><ReloadOutlined /></template>
                刷新
              </a-button>
            </a-space>
          </div>
        </div>

        <!-- 动态报表内容 -->
        <div class="report-content">
          <!-- 在线用户报表 -->
          <OnlineUsersReport 
            v-if="selectedKeys[0] === 'online-users'"
            :data="onlineUsers"
            :loading="reportDataLoading"
            @refresh="fetchOnlineUsersReport"
          />

          <!-- 历史报表 -->
          <HistoryReport 
            v-else-if="selectedKeys[0] === 'history'"
            :data="historyReports"
            :loading="reportDataLoading"
            @refresh="fetchHistoryReport"
          />

          <!-- 最近连接报表 -->
          <LastConnectReport 
            v-else-if="selectedKeys[0] === 'last-connect'"
            :data="lastConnectReports"
            :loading="reportDataLoading"
            @refresh="fetchLastConnectReport"
          />

          <!-- 新用户报表 -->
          <NewUsersReport 
            v-else-if="selectedKeys[0] === 'new-users'"
            :data="newUsersReports"
            :loading="reportDataLoading"
            @refresh="fetchNewUsersReport"
          />

          <!-- 热门用户报表 -->
          <TopUsersReport 
            v-else-if="selectedKeys[0] === 'top-users'"
            :data="topUsersReports"
            :loading="reportDataLoading"
            @refresh="fetchTopUsersReport"
          />

          <!-- 系统日志报表 -->
          <SystemLogsReport 
            v-else-if="selectedKeys[0] === 'system-logs'"
            :data="systemLogsReports"
            :loading="reportDataLoading"
            @refresh="fetchSystemLogsReport"
          />

          <!-- 批量报表 -->
          <BatchReport 
            v-else-if="selectedKeys[0] === 'batch-report'"
            :data="batchReports"
            :loading="reportDataLoading"
            @refresh="fetchBatchReport"
          />

          <!-- 系统状态报表 -->
          <SystemStatusReport 
            v-else-if="selectedKeys[0] === 'system-status'"
            :data="systemStatusReport"
            :loading="reportDataLoading"
            @refresh="fetchSystemStatusReport"
          />

          <!-- 心跳监控报表 -->
          <HeartBeatReport 
            v-else-if="selectedKeys[0] === 'heartbeat'"
            :data="heartBeatList"
            :loading="heartBeatLoading"
            @refresh="fetchHeartBeatList"
          />

          <!-- UPS状态报表 -->
          <UpsStatusReport 
            v-else-if="selectedKeys[0] === 'ups-status'"
            :data="upsStatusList"
            :loading="upsStatusLoading"
            @refresh="fetchUpsStatusList"
          />

          <!-- RAID状态报表 -->
          <RaidStatusReport 
            v-else-if="selectedKeys[0] === 'raid-status'"
            :data="raidStatusList"
            :loading="raidStatusLoading"
            @refresh="fetchRaidStatusList"
          />

          <!-- 默认仪表板 -->
          <ReportsDashboard 
            v-else
            :dashboard-data="dashboardData"
            :system-status="systemStatusReport"
            :loading="dashboardLoading"
            @refresh="refreshDashboard"
          />
        </div>
      </div>
    </div>

    <!-- 创建报表模态框 -->
    <CreateReportModal
      v-model:visible="showCreateModal"
      @created="handleReportCreated"
    />

    <!-- 报表模板模态框 -->
    <ReportTemplateModal
      v-model:visible="showTemplateModal"
      @template-selected="handleTemplateSelected"
    />

    <!-- 筛选器模态框 -->
    <ReportFiltersModal
      v-model:visible="showFiltersModal"
      :report-type="selectedKeys[0]"
      @filters-applied="handleFiltersApplied"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  FileTextOutlined,
  ReloadOutlined,
  UserOutlined,
  HistoryOutlined,
  LinkOutlined,
  UserAddOutlined,
  CrownOutlined,
  FileSearchOutlined,
  GroupOutlined,
  DashboardOutlined,
  HeartOutlined,
  ThunderboltOutlined,
  HddOutlined,
  FilterOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

// Store
import { useReportsStore } from '@/stores/reports'
import { storeToRefs } from 'pinia'

// Components
import StatCard from '@/components/common/StatCard.vue'
import OnlineUsersReport from '@/components/reports/OnlineUsersReport.vue'
import HistoryReport from '@/components/reports/HistoryReport.vue'
import LastConnectReport from '@/components/reports/LastConnectReport.vue'
import NewUsersReport from '@/components/reports/NewUsersReport.vue'
import TopUsersReport from '@/components/reports/TopUsersReport.vue'
import SystemLogsReport from '@/components/reports/SystemLogsReport.vue'
import BatchReport from '@/components/reports/BatchReport.vue'
import SystemStatusReport from '@/components/reports/SystemStatusReport.vue'
import HeartBeatReport from '@/components/reports/HeartBeatReport.vue'
import UpsStatusReport from '@/components/reports/UpsStatusReport.vue'
import RaidStatusReport from '@/components/reports/RaidStatusReport.vue'
import ReportsDashboard from '@/components/reports/ReportsDashboard.vue'
import CreateReportModal from '@/components/reports/CreateReportModal.vue'
import ReportTemplateModal from '@/components/reports/ReportTemplateModal.vue'
import ReportFiltersModal from '@/components/reports/ReportFiltersModal.vue'

const reportsStore = useReportsStore()

// 从store中获取响应式数据
const {
  // 仪表板数据
  reportsDashboard: dashboardData,
  dashboardLoading,
  systemHealthScore,
  
  // 报表数据
  onlineUsers,
  historyReports,
  lastConnectReports,
  newUsersReports,
  topUsersReports,
  systemLogsReports,
  batchReports,
  systemStatusReport,
  
  // 监控数据
  heartBeatList,
  heartBeatLoading,
  upsStatusList,
  upsStatusLoading,
  raidStatusList,
  raidStatusLoading,
  
  // UI状态
  reportDataLoading,
  pendingReports
} = storeToRefs(reportsStore)

// 页面状态
const selectedKeys = ref(['online-users'])
const showCreateModal = ref(false)
const showTemplateModal = ref(false)
const showFiltersModal = ref(false)

// 初始化页面
onMounted(async () => {
  await Promise.all([
    reportsStore.fetchReportsDashboard(),
    reportsStore.fetchOnlineUsersReport(),
    reportsStore.fetchPendingReports()
  ])
})

// 刷新仪表板
const refreshDashboard = async () => {
  await Promise.all([
    reportsStore.fetchReportsDashboard(),
    reportsStore.refreshAllSystemData()
  ])
}

// 菜单选择处理
const handleMenuSelect = async ({ key }: { key: string }) => {
  selectedKeys.value = [key]
  
  // 根据选择的报表类型加载相应数据
  switch (key) {
    case 'online-users':
      await reportsStore.fetchOnlineUsersReport()
      break
    case 'history':
      await reportsStore.fetchHistoryReport()
      break
    case 'last-connect':
      await reportsStore.fetchLastConnectReport()
      break
    case 'new-users':
      await reportsStore.fetchNewUsersReport()
      break
    case 'top-users':
      await reportsStore.fetchTopUsersReport()
      break
    case 'system-logs':
      await reportsStore.fetchSystemLogsReport()
      break
    case 'batch-report':
      await reportsStore.fetchBatchReport()
      break
    case 'system-status':
      await reportsStore.fetchSystemStatusReport()
      break
    case 'heartbeat':
      await reportsStore.fetchHeartBeatList()
      break
    case 'ups-status':
      await reportsStore.fetchUpsStatusList()
      break
    case 'raid-status':
      await reportsStore.fetchRaidStatusList()
      break
  }
}

// 获取当前报表标题
const getCurrentReportTitle = () => {
  const titles: Record<string, string> = {
    'online-users': '在线用户报表',
    'history': '历史报表',
    'last-connect': '最近连接报表',
    'new-users': '新用户报表',
    'top-users': '热门用户报表',
    'system-logs': '系统日志报表',
    'batch-report': '批量操作报表',
    'system-status': '系统状态报表',
    'heartbeat': '心跳监控报表',
    'ups-status': 'UPS状态报表',
    'raid-status': 'RAID状态报表'
  }
  return titles[selectedKeys.value[0]] || '报表仪表板'
}

// 刷新当前报表
const refreshCurrentReport = async () => {
  const currentKey = selectedKeys.value[0]
  await handleMenuSelect({ key: currentKey })
}

// 导出当前报表
const exportCurrentReport = async () => {
  try {
    const currentKey = selectedKeys.value[0]
    await reportsStore.exportReport(currentKey, 'excel')
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

// 报表创建处理
const handleReportCreated = (report: Record<string, unknown>) => {
  message.success('报表创建成功')
  refreshCurrentReport()
}

// 模板选择处理
const handleTemplateSelected = (template: Record<string, unknown>) => {
  message.success('模板应用成功')
  refreshCurrentReport()
}

// 筛选器应用处理
const handleFiltersApplied = (filters: Record<string, unknown>) => {
  reportsStore.setReportFilters(filters)
  refreshCurrentReport()
}

// 各种报表的刷新方法
const fetchOnlineUsersReport = () => reportsStore.fetchOnlineUsersReport()
const fetchHistoryReport = () => reportsStore.fetchHistoryReport()
const fetchLastConnectReport = () => reportsStore.fetchLastConnectReport()
const fetchNewUsersReport = () => reportsStore.fetchNewUsersReport()
const fetchTopUsersReport = () => reportsStore.fetchTopUsersReport()
const fetchSystemLogsReport = () => reportsStore.fetchSystemLogsReport()
const fetchBatchReport = () => reportsStore.fetchBatchReport()
const fetchSystemStatusReport = () => reportsStore.fetchSystemStatusReport()
const fetchHeartBeatList = () => reportsStore.fetchHeartBeatList()
const fetchUpsStatusList = () => reportsStore.fetchUpsStatusList()
const fetchRaidStatusList = () => reportsStore.fetchRaidStatusList()
</script>

<style lang="scss" scoped>
.reports-view {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;

  .page-header {
    background: white;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-info {
        h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 600;
          color: #262626;
        }

        .page-description {
          margin: 8px 0 0 0;
          color: #8c8c8c;
          font-size: 14px;
        }
      }

      .header-actions {
        display: flex;
        gap: 12px;
      }
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 24px;
  }

  .main-content {
    display: flex;
    gap: 24px;
    height: calc(100vh - 280px);

    .sidebar {
      width: 280px;
      background: white;
      border-radius: 8px;
      padding: 16px 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      overflow-y: auto;

      :deep(.ant-menu) {
        border: none;
        background: transparent;

        .ant-menu-item-group-title {
          padding-left: 24px;
          font-weight: 600;
          color: #262626;
        }

        .ant-menu-item {
          margin: 0;
          padding-left: 32px !important;
          border-radius: 0;

          &.ant-menu-item-selected {
            background: linear-gradient(90deg, #1890ff, #40a9ff);
            color: white;

            .anticon {
              color: white;
            }
          }

          &:hover:not(.ant-menu-item-selected) {
            background: rgba(24, 144, 255, 0.1);
            color: #1890ff;
          }
        }
      }
    }

    .content-area {
      flex: 1;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      display: flex;
      flex-direction: column;

      .report-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        border-bottom: 1px solid #f0f0f0;

        .toolbar-left {
          :deep(.ant-breadcrumb) {
            font-size: 16px;

            .ant-breadcrumb-link {
              color: #262626;
              font-weight: 500;
            }
          }
        }
      }

      .report-content {
        flex: 1;
        padding: 24px;
        overflow-y: auto;
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .reports-view {
    .main-content {
      flex-direction: column;
      height: auto;

      .sidebar {
        width: 100%;
        order: 2;
      }

      .content-area {
        order: 1;
        min-height: 600px;
      }
    }
  }
}

@media (max-width: 768px) {
  .reports-view {
    padding: 16px;

    .page-header {
      .header-content {
        flex-direction: column;
        gap: 16px;
        text-align: center;
      }
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .main-content {
      .content-area {
        .report-toolbar {
          flex-direction: column;
          gap: 16px;
          align-items: stretch;

          .toolbar-left,
          .toolbar-right {
            text-align: center;
          }
        }
      }
    }
  }
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  EditOutlined,
  CopyOutlined,
  ClockCircleOutlined,
  DownOutlined
} from '@ant-design/icons-vue';
// import DataTable from '@/components/common/DataTable.vue';
// import SearchForm from '@/components/common/SearchForm.vue';
import StatCard from '@/components/common/StatCard.vue';
// TODO: Create missing report detail components
// import ReportDetail from '@/components/reports/ReportDetail.vue';
// import ReportForm from '@/components/reports/ReportForm.vue';
// import ReportResult from '@/components/reports/ReportResult.vue';
// import ReportTemplates from '@/components/reports/ReportTemplates.vue';
// import ReportSchedule from '@/components/reports/ReportSchedule.vue';
import { useReportManagement, useReportGeneration } from '@/composables/useReportManagement';
import type { 
  Report, 
  CreateReportRequest, 
  UpdateReportRequest, 
  ReportType, 
  ReportStatus, 
  ReportFormat 
} from '@/types/report';
import { REPORT_TYPE_OPTIONS, REPORT_STATUS_OPTIONS } from '@/types/report';

// 组合式函数
const {
  reports,
  loading,
  total,
  currentPage,
  pageSize,
  searchParams,
  selectedReports,
  selectedReport,
  hasSelection,
  selectionCount,
  fetchReports,
  createReport,
  updateReport,
  deleteReport: deleteReportById,
  deleteSelectedReports,
  searchReports,
  resetSearch,
  onPageChange,
  toggleAllSelection,
  clearSelection
} = useReportManagement();

const {
  reportData,
  generating,
  exporting,
  generateReport,
  exportReport,
  clearReportData
} = useReportGeneration();

// 响应式状态
const showDetailDrawer = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showResultModal = ref(false);
const showTemplateModal = ref(false);
const showScheduleModal = ref(false);
const editingReport = ref<Report | null>(null);
const schedulingReport = ref<Report | null>(null);

// 模拟统计数据
const monthlyGeneratedCount = ref(45);

// 计算属性
const activeReportsCount = computed(() => 
  reports.value.filter(r => r.status === 'active').length
);

const draftReportsCount = computed(() => 
  reports.value.filter(r => r.status === 'draft').length
);

// 搜索字段配置
const searchFields = [
  {
    key: 'name',
    label: '报表名称',
    type: 'input',
    placeholder: '请输入报表名称'
  },
  {
    key: 'type',
    label: '报表类型',
    type: 'select',
    options: REPORT_TYPE_OPTIONS
  },
  {
    key: 'status',
    label: '报表状态',
    type: 'select',
    options: REPORT_STATUS_OPTIONS
  },
  {
    key: 'createdBy',
    label: '创建人',
    type: 'input',
    placeholder: '请输入创建人'
  }
];

// 表格列配置
const columns = [
  {
    title: '报表名称',
    dataIndex: 'name',
    key: 'name',
    sorter: true,
    width: 200
  },
  {
    title: '报表类型',
    dataIndex: 'type',
    key: 'type',
    slots: { customRender: 'type' },
    width: 120
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' },
    width: 100
  },
  {
    title: '创建人',
    dataIndex: 'createdBy',
    key: 'createdBy',
    width: 100
  },
  {
    title: '最后运行',
    dataIndex: 'lastRunTime',
    key: 'lastRunTime',
    slots: { customRender: 'lastRunTime' },
    width: 160
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    key: 'createTime',
    sorter: true,
    width: 160
  },
  {
    title: '操作',
    key: 'actions',
    slots: { customRender: 'actions' },
    width: 150,
    fixed: 'right'
  }
];

// 事件处理
const handleTableChange = ({ current, pageSize: size }: any) => {
  onPageChange(current, size);
};

const viewReport = (report: Report) => {
  selectedReport.value = report;
  showDetailDrawer.value = true;
};

const editReport = (report: Report) => {
  editingReport.value = report;
  showEditModal.value = true;
};

const handleCreateReport = async (data: CreateReportRequest) => {
  try {
    await createReport(data);
    showCreateModal.value = false;
  } catch (error) {
    console.error(error);
  }
};

const handleUpdateReport = async (data: UpdateReportRequest) => {
  if (!editingReport.value) return;
  
  try {
    await updateReport(editingReport.value.id, data);
    showEditModal.value = false;
    editingReport.value = null;
  } catch (error) {
    console.error(error);
  }
};

const deleteReport = (reportId: string) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个报表吗？删除后无法恢复。',
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => deleteReportById(reportId)
  });
};

const handleBatchDelete = () => {
  if (selectedReports.value.length === 0) {
    message.warning('请先选择要删除的报表');
    return;
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedReports.value.length} 个报表吗？删除后无法恢复。`,
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: deleteSelectedReports
  });
};

const generateReportData = async (report: Report) => {
  try {
    // 这里可以添加参数输入对话框
    const request = {
      reportId: report.id,
      parameters: {}, // 实际应该从用户输入获取
      format: 'json' as ReportFormat
    };
    
    const data = await generateReport(request);
    showResultModal.value = true;
  } catch (error) {
    console.error(error);
  }
};

const duplicateReport = async (report: Report) => {
  try {
    const duplicateData = {
      ...report,
      name: `${report.name} - 副本`,
      status: 'draft' as ReportStatus
    };
    
    await createReport(duplicateData);
    message.success('报表复制成功');
  } catch (error) {
    console.error(error);
  }
};

const scheduleReport = (report: Report) => {
  schedulingReport.value = report;
  showScheduleModal.value = true;
};

const handleScheduleReport = (scheduleData: any) => {
  message.success('定时任务配置成功');
  showScheduleModal.value = false;
  schedulingReport.value = null;
};

const handleSelectTemplate = (template: any) => {
  // 基于模板创建报表
  const templateData = {
    name: `基于${template.name}的报表`,
    type: template.type,
    description: template.description,
    parameters: template.parameters,
    templateId: template.id
  };
  
  showTemplateModal.value = false;
  // 可以直接创建或打开表单预填充数据
  handleCreateReport(templateData);
};

const handleExportReport = (format: ReportFormat) => {
  if (!reportData.value) return;
  exportReport(reportData.value.reportId, format, reportData.value);
};

// 工具函数
const getTypeText = (type: ReportType): string => {
  const typeMap = {
    user_usage: '用户使用统计',
    traffic_analysis: '流量分析',
    revenue_statistics: '收入统计',
    device_performance: '设备性能',
    session_analysis: '会话分析',
    billing_summary: '计费汇总',
    custom_query: '自定义查询'
  };
  return typeMap[type] || type;
};

const getStatusColor = (status: ReportStatus): string => {
  const colorMap = {
    draft: 'default',
    active: 'green',
    paused: 'orange',
    archived: 'red'
  };
  return colorMap[status] || 'default';
};

const getStatusText = (status: ReportStatus): string => {
  const textMap = {
    draft: '草稿',
    active: '活跃',
    paused: '暂停',
    archived: '归档'
  };
  return textMap[status] || status;
};

// 生命周期
onMounted(() => {
  fetchReports();
});
</script>

<style scoped>
.reports-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.page-description {
  margin: 8px 0 0 0;
  color: rgba(0, 0, 0, 0.65);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.search-card {
  margin-bottom: 24px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-info {
  color: #1890ff;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .ant-btn-link {
  padding: 0;
  height: auto;
}

.report-result-modal :deep(.ant-modal-body) {
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}
</style>