<template>
  <div class="system-status-report">
    <a-card title="系统状态报表">
      <template #extra>
        <a-button @click="$emit('refresh')" :loading="loading">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </template>

      <a-spin :spinning="loading">
        <div class="status-grid">
          <!-- RADIUS 服务状态 -->
          <div class="status-section">
            <h3><WifiOutlined /> RADIUS 服务</h3>
            <a-descriptions bordered :column="2" size="small">
              <a-descriptions-item label="状态">
                <a-tag :color="getStatusColor(data?.radius_status)">
                  {{ data?.radius_status || 'unknown' }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="端口">
                {{ data?.radius_port || 'N/A' }}
              </a-descriptions-item>
              <a-descriptions-item label="认证请求">
                {{ data?.auth_requests || 0 }}
              </a-descriptions-item>
              <a-descriptions-item label="计费请求">
                {{ data?.acct_requests || 0 }}
              </a-descriptions-item>
            </a-descriptions>
          </div>

          <!-- 数据库状态 -->
          <div class="status-section">
            <h3><DatabaseOutlined /> 数据库</h3>
            <a-descriptions bordered :column="2" size="small">
              <a-descriptions-item label="状态">
                <a-tag :color="getStatusColor(data?.database_status)">
                  {{ data?.database_status || 'unknown' }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="连接数">
                {{ data?.db_connections || 0 }}
              </a-descriptions-item>
              <a-descriptions-item label="表数量">
                {{ data?.db_tables || 0 }}
              </a-descriptions-item>
              <a-descriptions-item label="数据库大小">
                {{ formatBytes(data?.db_size || 0) }}
              </a-descriptions-item>
            </a-descriptions>
          </div>

          <!-- Web 服务状态 -->
          <div class="status-section">
            <h3><GlobalOutlined /> Web 服务</h3>
            <a-descriptions bordered :column="2" size="small">
              <a-descriptions-item label="状态">
                <a-tag color="success">{{ data?.web_status || 'online' }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="在线用户">
                {{ data?.online_users || 0 }}
              </a-descriptions-item>
              <a-descriptions-item label="今日访问">
                {{ data?.daily_visits || 0 }}
              </a-descriptions-item>
              <a-descriptions-item label="活跃会话">
                {{ data?.active_sessions || 0 }}
              </a-descriptions-item>
            </a-descriptions>
          </div>

          <!-- 系统资源 -->
          <div class="status-section">
            <h3><CloudServerOutlined /> 系统资源</h3>
            <a-descriptions bordered :column="1" size="small">
              <a-descriptions-item label="CPU 使用率">
                <a-progress
                  :percent="data?.cpu_usage || 0"
                  :status="getResourceStatus(data?.cpu_usage || 0)"
                />
              </a-descriptions-item>
              <a-descriptions-item label="内存使用率">
                <a-progress
                  :percent="data?.memory_usage || 0"
                  :status="getResourceStatus(data?.memory_usage || 0)"
                />
              </a-descriptions-item>
              <a-descriptions-item label="磁盘使用率">
                <a-progress
                  :percent="data?.disk_usage || 0"
                  :status="getResourceStatus(data?.disk_usage || 0)"
                />
              </a-descriptions-item>
            </a-descriptions>
          </div>
        </div>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import {
  ReloadOutlined,
  WifiOutlined,
  DatabaseOutlined,
  GlobalOutlined,
  CloudServerOutlined,
} from '@ant-design/icons-vue'

interface SystemStatusData {
  radius_status?: string
  radius_port?: number
  auth_requests?: number
  acct_requests?: number
  database_status?: string
  db_connections?: number
  db_tables?: number
  db_size?: number
  web_status?: string
  online_users?: number
  daily_visits?: number
  active_sessions?: number
  cpu_usage?: number
  memory_usage?: number
  disk_usage?: number
}

interface Props {
  data?: SystemStatusData | null
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

const getResourceStatus = (usage: number): 'success' | 'exception' | 'normal' => {
  if (usage >= 90) return 'exception'
  if (usage >= 75) return 'normal'
  return 'success'
}

const formatBytes = (bytes: number): string => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(2)} ${units[unitIndex]}`
}
</script>

<style scoped lang="scss">
.system-status-report {
  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
  }

  .status-section {
    h3 {
      margin-bottom: 16px;
      font-size: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
