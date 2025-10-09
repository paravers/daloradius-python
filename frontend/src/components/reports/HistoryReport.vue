<template>
  <div class="history-report">
    <a-card title="历史会话报表">
      <template #extra>
        <a-space>
          <a-range-picker v-model:value="dateRange" @change="handleDateChange" />
          <a-button @click="$emit('refresh')" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :pagination="pagination"
        :scroll="{ x: 1400 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'username'">
            <a-tag color="blue">{{ record.username }}</a-tag>
          </template>
          <template v-else-if="column.key === 'acctstarttime'">
            {{ formatDateTime(record.acctstarttime) }}
          </template>
          <template v-else-if="column.key === 'acctstoptime'">
            {{ formatDateTime(record.acctstoptime) }}
          </template>
          <template v-else-if="column.key === 'acctsessiontime'">
            {{ formatDuration(record.acctsessiontime) }}
          </template>
          <template v-else-if="column.key === 'traffic'">
            <div class="traffic-summary">
              <div>上传: {{ formatBytes(record.acctinputoctets) }}</div>
              <div>下载: {{ formatBytes(record.acctoutputoctets) }}</div>
              <div class="total">总计: {{ formatBytes(record.acctinputoctets + record.acctoutputoctets) }}</div>
            </div>
          </template>
          <template v-else-if="column.key === 'acctterminatecause'">
            <a-tag :color="getTerminateColor(record.acctterminatecause)">
              {{ record.acctterminatecause || 'Unknown' }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import type { Dayjs } from 'dayjs'

interface HistorySession {
  id: number
  username: string
  framedipaddress?: string
  acctstarttime: string
  acctstoptime?: string
  acctsessiontime: number
  acctinputoctets: number
  acctoutputoctets: number
  nasipaddress?: string
  nasshortname?: string
  acctterminatecause?: string
}

interface Props {
  data: HistorySession[]
  loading?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 120,
    fixed: 'left' as const,
  },
  {
    title: 'IP地址',
    dataIndex: 'framedipaddress',
    key: 'framedipaddress',
    width: 140,
  },
  {
    title: '开始时间',
    dataIndex: 'acctstarttime',
    key: 'acctstarttime',
    width: 180,
  },
  {
    title: '结束时间',
    dataIndex: 'acctstoptime',
    key: 'acctstoptime',
    width: 180,
  },
  {
    title: '会话时长',
    dataIndex: 'acctsessiontime',
    key: 'acctsessiontime',
    width: 120,
  },
  {
    title: '流量统计',
    key: 'traffic',
    width: 180,
  },
  {
    title: 'NAS',
    dataIndex: 'nasshortname',
    key: 'nasshortname',
    width: 120,
  },
  {
    title: '终止原因',
    dataIndex: 'acctterminatecause',
    key: 'acctterminatecause',
    width: 150,
  },
]

const pagination = computed(() => ({
  total: props.data.length,
  pageSize: 20,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条历史记录`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDuration = (seconds: number): string => {
  if (!seconds) return '0s'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
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

const getTerminateColor = (cause?: string): string => {
  if (!cause) return 'default'
  const causeLower = cause.toLowerCase()
  if (causeLower.includes('user')) return 'success'
  if (causeLower.includes('timeout')) return 'warning'
  if (causeLower.includes('error') || causeLower.includes('lost')) return 'error'
  return 'default'
}

const handleDateChange = () => {
  // 触发日期变化事件
  console.log('Date range changed:', dateRange.value)
}
</script>

<style scoped lang="scss">
.history-report {
  .traffic-summary {
    font-size: 12px;
    line-height: 1.6;
    
    .total {
      font-weight: bold;
      color: #1890ff;
      margin-top: 4px;
      padding-top: 4px;
      border-top: 1px solid #f0f0f0;
    }
  }
}
</style>
