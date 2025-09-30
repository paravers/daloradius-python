<template>
  <div class="dashboard-view">
    <div class="page-header">
      <h1>仪表板</h1>
      <p class="page-description">系统概览和关键指标</p>
      <div class="header-actions">
        <a-button @click="refreshData" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button @click="exportData">
          <template #icon>
            <DownloadOutlined />
          </template>
          导出
        </a-button>
      </div>
    </div>
    
    <div class="dashboard-content">
      <!-- 统计卡片 -->
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="12" :md="6">
          <a-card :loading="loading">
            <a-statistic
              title="在线用户"
              :value="dashboardData?.stats?.activeUsers || 0"
              :value-style="{ color: '#3f8600' }"
            >
              <template #suffix>
                <UserOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card :loading="loading">
            <a-statistic
              title="总用户数"
              :value="dashboardData?.stats?.totalUsers || 0"
              :value-style="{ color: '#1890ff' }"
            >
              <template #suffix>
                <TeamOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card :loading="loading">
            <a-statistic
              title="月收入"
              :value="dashboardData?.stats?.monthlyRevenue || 0"
              prefix="¥"
              :precision="2"
              :value-style="{ color: '#cf1322' }"
            >
              <template #suffix>
                <DollarOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card :loading="loading">
            <a-statistic
              title="活跃设备"
              :value="dashboardData?.stats?.activeDevices || 0"
              :value-style="{ color: '#722ed1' }"
            >
              <template #suffix>
                <WifiOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 快速统计 -->
      <a-row :gutter="[16, 16]" style="margin-top: 16px;">
        <a-col :xs="24" :sm="12" :md="6">
          <a-card size="small" :loading="loading">
            <a-statistic
              title="今日登录"
              :value="dashboardData?.stats?.todayLogins || 0"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card size="small" :loading="loading">
            <a-statistic
              title="活跃会话"
              :value="dashboardData?.stats?.activeSessions || 0"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card size="small" :loading="loading">
            <a-statistic
              title="系统健康度"
              :value="dashboardData?.stats?.systemHealth || 0"
              suffix="%"
              :value-style="getHealthColor(dashboardData?.stats?.systemHealth || 0)"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card size="small" :loading="loading">
            <a-statistic
              title="今日流量"
              :value="formatTraffic(dashboardData?.quickStats?.trafficLastHourGb || 0)"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
      </a-row>
      
      <!-- 图表区域 -->
      <a-row :gutter="[16, 16]" style="margin-top: 16px;">
        <a-col :xs="24" :lg="12">
          <a-card title="用户活跃度趋势" :loading="loading">
            <div v-if="!loading && sessionsChartData" style="height: 300px;">
              <BasicChart
                :data="sessionsChartData"
                type="line"
                :options="chartOptions"
              />
            </div>
            <div v-else-if="!loading" style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              暂无数据
            </div>
          </a-card>
        </a-col>
        <a-col :xs="24" :lg="12">
          <a-card title="流量统计" :loading="loading">
            <div v-if="!loading && trafficChartData" style="height: 300px;">
              <BasicChart
                :data="trafficChartData"
                type="area"
                :options="chartOptions"
              />
            </div>
            <div v-else-if="!loading" style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              暂无数据
            </div>
          </a-card>
        </a-col>
      </a-row>

      <!-- 最近活动和系统警告 -->
      <a-row :gutter="[16, 16]" style="margin-top: 16px;">
        <a-col :xs="24" :lg="12">
          <a-card title="最近活动" :loading="loading">
            <a-list
              v-if="recentActivities.length > 0"
              :data-source="recentActivities"
              size="small"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :title="item.description"
                    :description="formatTime(item.timestamp)"
                  >
                    <template #avatar>
                      <a-avatar :style="getActivityAvatarStyle(item.status)">
                        {{ getActivityIcon(item.activity_type) }}
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
            <a-empty v-else description="暂无活动记录" />
          </a-card>
        </a-col>
        <a-col :xs="24" :lg="12">
          <a-card title="系统警告" :loading="loading">
            <a-list
              v-if="systemAlerts.length > 0"
              :data-source="systemAlerts"
              size="small"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :title="item.title"
                    :description="item.message"
                  >
                    <template #avatar>
                      <a-avatar :style="getAlertAvatarStyle(item.severity)">
                        <ExclamationOutlined v-if="item.severity === 'error'" />
                        <WarningOutlined v-else-if="item.severity === 'warning'" />
                        <InfoCircleOutlined v-else />
                      </a-avatar>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
            <a-empty v-else description="无系统警告" />
          </a-card>
        </a-col>
      </a-row>
      
      <!-- 快速操作 -->
      <a-card title="快速操作" style="margin-top: 16px;">
        <a-space wrap>
          <a-button type="primary" @click="navigateToUsers">
            <template #icon>
              <UserAddOutlined />
            </template>
            添加用户
          </a-button>
          <a-button @click="navigateToReports">
            <template #icon>
              <FileTextOutlined />
            </template>
            生成报表
          </a-button>
          <a-button @click="navigateToSystem">
            <template #icon>
              <SettingOutlined />
            </template>
            系统配置
          </a-button>
          <a-button @click="navigateToAccounting">
            <template #icon>
              <BarChartOutlined />
            </template>
            会计统计
          </a-button>
        </a-space>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  TeamOutlined,
  DollarOutlined,
  WifiOutlined,
  UserAddOutlined,
  FileTextOutlined,
  SettingOutlined,
  BarChartOutlined,
  ReloadOutlined,
  DownloadOutlined,
  ExclamationOutlined,
  WarningOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { dashboardService } from '@/services/dashboardService'
import BasicChart from '@/components/common/BasicChart.vue'
import type { DashboardStats, DashboardOverview, RecentActivity, SystemAlert } from '@/services/dashboardService'

const router = useRouter()
const loading = ref(false)
const dashboardData = ref<DashboardOverview | null>(null)
const recentActivities = ref<RecentActivity[]>([])
const systemAlerts = ref<SystemAlert[]>([])

// 图表数据
const sessionsChartData = computed(() => {
  if (!dashboardData.value?.charts?.sessions) return null
  return dashboardService.formatChartData(
    dashboardData.value.charts.sessions,
    '会话数',
    '#1890ff'
  )
})

const trafficChartData = computed(() => {
  if (!dashboardData.value?.charts?.traffic) return null
  return dashboardService.formatChartData(
    dashboardData.value.charts.traffic,
    '流量 (GB)',
    '#52c41a'
  )
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// 加载仪表板数据
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // 并行加载所有数据
    const [overview, activities, alerts] = await Promise.all([
      dashboardService.getOverview(),
      dashboardService.getRecentActivities(10),
      dashboardService.getSystemAlerts()
    ])
    
    dashboardData.value = overview
    recentActivities.value = activities
    systemAlerts.value = alerts
    
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
    message.error('加载仪表板数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await loadDashboardData()
  message.success('数据已刷新')
}

// 导出数据
const exportData = async () => {
  try {
    const data = await dashboardService.exportOverview()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dashboard_data_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    message.success('数据导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    message.error('数据导出失败')
  }
}

// 工具函数
const formatTime = (timestamp: string) => {
  return dashboardService.formatTimestamp(timestamp)
}

const formatTraffic = (gb: number) => {
  return dashboardService.formatTraffic(gb)
}

const getHealthColor = (health: number) => {
  if (health >= 90) return { color: '#52c41a' }
  if (health >= 70) return { color: '#faad14' }
  return { color: '#f5222d' }
}

const getActivityAvatarStyle = (status: string) => {
  const colors = {
    success: { backgroundColor: '#52c41a' },
    warning: { backgroundColor: '#faad14' },
    error: { backgroundColor: '#f5222d' },
    info: { backgroundColor: '#1890ff' }
  }
  return colors[status as keyof typeof colors] || colors.info
}

const getActivityIcon = (type: string) => {
  const icons = {
    login: '👤',
    logout: '🚪',
    session_start: '🟢',
    session_end: '🔴',
    user_add: '➕',
    user_edit: '✏️',
    system: '⚙️'
  }
  return icons[type as keyof typeof icons] || '📝'
}

const getAlertAvatarStyle = (severity: string) => {
  const colors = {
    error: { backgroundColor: '#f5222d' },
    warning: { backgroundColor: '#faad14' },
    info: { backgroundColor: '#1890ff' }
  }
  return colors[severity as keyof typeof colors] || colors.info
}

// 导航函数
const navigateToUsers = () => {
  router.push('/users')
}

const navigateToReports = () => {
  router.push('/reports')
}

const navigateToSystem = () => {
  router.push('/config')
}

const navigateToAccounting = () => {
  router.push('/accounting')
}

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
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
  gap: 8px;
}

.dashboard-content {
  /* 内容样式 */
}

@media (max-width: 768px) {
  .dashboard-view {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>