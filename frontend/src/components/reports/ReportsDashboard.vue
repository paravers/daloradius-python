<template>
  <div class="reports-dashboard">
    <a-spin :spinning="loading">
      <div class="dashboard-grid">
        <!-- 系统概览卡片 -->
        <a-card title="系统概览" class="overview-card">
          <div class="overview-stats">
            <div class="stat-item">
              <div class="stat-label">在线用户</div>
              <div class="stat-value">{{ dashboardData?.online_users_count || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">今日会话</div>
              <div class="stat-value">{{ dashboardData?.daily_sessions || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">总用户数</div>
              <div class="stat-value">{{ dashboardData?.total_users || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">活跃NAS</div>
              <div class="stat-value">{{ dashboardData?.active_nas_count || 0 }}</div>
            </div>
          </div>
        </a-card>

        <!-- 系统状态卡片 -->
        <a-card title="系统状态" class="status-card">
          <div v-if="systemStatus" class="status-grid">
            <div class="status-item">
              <a-tag :color="getStatusColor(systemStatus.radius_status)">
                RADIUS: {{ systemStatus.radius_status || 'unknown' }}
              </a-tag>
            </div>
            <div class="status-item">
              <a-tag :color="getStatusColor(systemStatus.database_status)">
                Database: {{ systemStatus.database_status || 'unknown' }}
              </a-tag>
            </div>
            <div class="status-item">
              <a-tag :color="getStatusColor(systemStatus.web_status)">
                Web: {{ systemStatus.web_status || 'online' }}
              </a-tag>
            </div>
          </div>
          <a-empty v-else description="无系统状态数据" />
        </a-card>

        <!-- 最近活动 -->
        <a-card title="最近活动" class="activity-card">
          <a-list
            v-if="dashboardData?.recent_activities?.length"
            :data-source="dashboardData.recent_activities"
            size="small"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>{{ item.title }}</template>
                  <template #description>{{ item.timestamp }}</template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
          <a-empty v-else description="暂无活动记录" />
        </a-card>

        <!-- 快速统计 -->
        <a-card title="快速统计" class="quick-stats-card">
          <div class="quick-stats">
            <div class="quick-stat-item">
              <BarChartOutlined class="stat-icon" />
              <div class="stat-content">
                <div class="stat-title">本月新增用户</div>
                <div class="stat-number">{{ dashboardData?.monthly_new_users || 0 }}</div>
              </div>
            </div>
            <div class="quick-stat-item">
              <LineChartOutlined class="stat-icon" />
              <div class="stat-content">
                <div class="stat-title">本周流量 (GB)</div>
                <div class="stat-number">{{ formatBytes(dashboardData?.weekly_traffic || 0) }}</div>
              </div>
            </div>
            <div class="quick-stat-item">
              <ClockCircleOutlined class="stat-icon" />
              <div class="stat-content">
                <div class="stat-title">平均会话时长</div>
                <div class="stat-number">{{ formatDuration(dashboardData?.avg_session_time || 0) }}</div>
              </div>
            </div>
          </div>
        </a-card>
      </div>

      <div class="dashboard-actions">
        <a-button type="primary" @click="$emit('refresh')">
          <template #icon><ReloadOutlined /></template>
          刷新数据
        </a-button>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { BarChartOutlined, LineChartOutlined, ClockCircleOutlined, ReloadOutlined } from '@ant-design/icons-vue'

interface DashboardData {
  online_users_count?: number
  daily_sessions?: number
  total_users?: number
  active_nas_count?: number
  monthly_new_users?: number
  weekly_traffic?: number
  avg_session_time?: number
  recent_activities?: Array<{
    title: string
    timestamp: string
  }>
}

interface SystemStatus {
  radius_status?: string
  database_status?: string
  web_status?: string
}

interface Props {
  dashboardData?: DashboardData | null
  systemStatus?: SystemStatus | null
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const getStatusColor = (status?: string): string => {
  if (!status) return 'default'
  const statusLower = status.toLowerCase()
  if (statusLower === 'online' || statusLower === 'healthy') return 'success'
  if (statusLower === 'warning') return 'warning'
  if (statusLower === 'offline' || statusLower === 'error') return 'error'
  return 'default'
}

const formatBytes = (bytes: number): string => {
  return (bytes / (1024 * 1024 * 1024)).toFixed(2)
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}
</script>

<style scoped lang="scss">
.reports-dashboard {
  padding: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;

  .stat-label {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: bold;
    color: #1890ff;
  }
}

.status-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  padding: 8px;
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quick-stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;

  .stat-icon {
    font-size: 32px;
    color: #1890ff;
  }

  .stat-content {
    flex: 1;

    .stat-title {
      font-size: 14px;
      color: #666;
      margin-bottom: 4px;
    }

    .stat-number {
      font-size: 20px;
      font-weight: bold;
      color: #333;
    }
  }
}

.dashboard-actions {
  text-align: center;
  margin-top: 24px;
}
</style>
