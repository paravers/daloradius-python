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
        <a-menu v-model:selectedKeys="selectedKeys" mode="inline" @select="handleMenuSelect">
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
            :data="transformedOnlineUsers"
            :loading="reportDataLoading"
            @refresh="fetchOnlineUsersReport"
          />

          <!-- 历史报表 -->
          <HistoryReport
            v-else-if="selectedKeys[0] === 'history'"
            :data="transformedHistoryReports"
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
            :data="transformedNewUsersReports"
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
            :data="transformedSystemLogsReports"
            :loading="reportDataLoading"
            @refresh="fetchSystemLogsReport"
          />

          <!-- 批量报表 -->
          <BatchReport
            v-else-if="selectedKeys[0] === 'batch-report'"
            :data="transformedBatchReports"
            :loading="reportDataLoading"
            @refresh="fetchBatchReport"
          />

          <!-- 系统状态报表 -->
          <SystemStatusReport
            v-else-if="selectedKeys[0] === 'system-status'"
            :data="systemStatusReport as any"
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
            :system-status="systemStatusReport as any"
            :loading="dashboardLoading"
            @refresh="refreshDashboard"
          />
        </div>
      </div>
    </div>

    <!-- 创建报表模态框 -->
    <CreateReportModal v-model:visible="showCreateModal" @created="handleReportCreated" />

    <!-- 报表模板模态框 -->
    <ReportTemplateModal
      v-model:visible="showTemplateModal"
      @template-selected="(template: any) => handleTemplateSelected(template)"
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
  DownloadOutlined,
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
  pendingReports,
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
    reportsStore.fetchPendingReports(),
  ])
})

// 刷新仪表板
const refreshDashboard = async () => {
  await Promise.all([reportsStore.fetchReportsDashboard(), reportsStore.refreshAllSystemData()])
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
    history: '历史报表',
    'last-connect': '最近连接报表',
    'new-users': '新用户报表',
    'top-users': '热门用户报表',
    'system-logs': '系统日志报表',
    'batch-report': '批量操作报表',
    'system-status': '系统状态报表',
    heartbeat: '心跳监控报表',
    'ups-status': 'UPS状态报表',
    'raid-status': 'RAID状态报表',
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

// 数据转换函数 - 将 store 数据转换为组件期望的格式
const transformedOnlineUsers = computed(() =>
  onlineUsers.value.map((user) => ({
    username: user.username,
    framedipaddress: user.framed_ip_address,
    callingstationid: user.session_id,
    acctstarttime: user.start_time,
    acctsessiontime: user.session_duration,
    nasipaddress: user.nas_ip_address,
    calledstationid: '',
    acctinputoctets: user.input_octets,
    acctoutputoctets: user.output_octets,
    hotspot: '',
    nasshortname: user.nas_ip_address,
  })),
)

const transformedHistoryReports = computed(() =>
  historyReports.value.map((session, index) => ({
    id: index + 1,
    username: session.username,
    acctstarttime: session.session_start,
    acctstoptime: session.session_end,
    acctsessiontime: session.session_time,
    acctinputoctets: session.input_octets,
    acctoutputoctets: session.output_octets,
    nasipaddress: session.nas_ip_address,
    acctterminatecause: session.terminate_cause || 'User-Request',
  })),
)

const transformedNewUsersReports = computed(() =>
  newUsersReports.value.map((user, index) => ({
    id: index + 1,
    username: user.username,
    firstname: '',
    lastname: '',
    email: user.email || '',
    creationdate: user.created_date,
    firstLogin: user.first_login,
  })),
)

const transformedSystemLogsReports = computed(() =>
  systemLogsReports.value.map((log, index) => ({
    id: index + 1,
    timestamp: log.timestamp,
    log_level: log.log_level,
    logger_name: log.logger_name,
    message: log.message,
    username: log.username,
    ip_address: log.ip_address,
  })),
)

const transformedBatchReports = computed(() =>
  batchReports.value.map((batch, index) => ({
    id: index + 1,
    operation_type: 'bulk_operation',
    batch_name: batch.batch_name,
    description: batch.description || '',
    total_count: batch.user_count,
    processed_count: batch.success_count,
    success_count: batch.success_count,
    failed_count: batch.failed_count,
    status: 'completed',
    progress: Math.round((batch.success_count / batch.user_count) * 100),
    created_at: batch.created_date,
    updated_at: batch.created_date,
  })),
)

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
  DownloadOutlined,
} from '@ant-design/icons-vue'
// import DataTable from '@/components/common/DataTable.vue';
// import SearchForm from '@/components/common/SearchForm.vue';
import StatCard from '@/components/common/StatCard.vue'

// 组合式函数 (仅保留已使用的)

// 响应式状态 (仅保留已使用的)
const showCreateModal = ref(false)
const showTemplateModal = ref(false)

// 生命周期
onMounted(() => {
  // 初始化页面数据
  reportsStore.fetchReportsDashboard()
  reportsStore.fetchOnlineUsersReport()
  reportsStore.fetchPendingReports()
})
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
