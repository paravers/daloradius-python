<template>
  <div class="heartbeat-report">
    <a-card title="心跳监控报表">
      <template #extra>
        <a-button @click="$emit('refresh')" :loading="loading">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </template>

      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'service_name'">
            <strong>{{ record.service_name }}</strong>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'response_time'">
            {{ record.response_time || 0 }} ms
          </template>
          <template v-else-if="column.key === 'uptime'">
            {{ formatUptime(record.uptime) }}
          </template>
          <template v-else-if="column.key === 'last_heartbeat'">
            {{ formatDateTime(record.last_heartbeat) }}
          </template>
          <template v-else-if="column.key === 'resources'">
            <div class="resource-indicators">
              <a-tooltip title="CPU">
                <a-progress
                  type="circle"
                  :percent="record.cpu_usage || 0"
                  :width="40"
                  :status="getResourceStatus(record.cpu_usage || 0)"
                />
              </a-tooltip>
              <a-tooltip title="Memory">
                <a-progress
                  type="circle"
                  :percent="record.memory_usage || 0"
                  :width="40"
                  :status="getResourceStatus(record.memory_usage || 0)"
                />
              </a-tooltip>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'

interface HeartBeat {
  id: number
  service_name: string
  service_type: string
  host_name: string
  ip_address?: string
  port?: number
  status: string
  response_time?: number
  uptime?: number
  cpu_usage?: number
  memory_usage?: number
  last_heartbeat?: string
}

interface Props {
  data: HeartBeat[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  { title: '服务名称', dataIndex: 'service_name', key: 'service_name', width: 150 },
  { title: '服务类型', dataIndex: 'service_type', key: 'service_type', width: 120 },
  { title: '主机', dataIndex: 'host_name', key: 'host_name', width: 150 },
  { title: 'IP:端口', width: 150, customRender: ({ record }: { record: HeartBeat }) => {
    return `${record.ip_address || '-'}:${record.port || '-'}`
  }},
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '响应时间', key: 'response_time', width: 100 },
  { title: '运行时长', key: 'uptime', width: 120 },
  { title: '资源', key: 'resources', width: 120 },
  { title: '最后心跳', key: 'last_heartbeat', width: 180 },
]

const pagination = computed(() => ({
  pageSize: 20,
  showTotal: (total: number) => `共 ${total} 个服务`,
}))

const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    online: 'success',
    offline: 'error',
    warning: 'warning',
    error: 'error',
    maintenance: 'default',
  }
  return statusMap[status?.toLowerCase()] || 'default'
}

const getResourceStatus = (usage: number): 'success' | 'exception' | 'normal' => {
  if (usage >= 90) return 'exception'
  if (usage >= 75) return 'normal'
  return 'success'
}

const formatUptime = (seconds?: number): string => {
  if (!seconds) return '-'
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  if (days > 0) return `${days}天 ${hours}小时`
  return `${hours}小时`
}

const formatDateTime = (dateStr?: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.heartbeat-report {
  .resource-indicators {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
}
</style>
