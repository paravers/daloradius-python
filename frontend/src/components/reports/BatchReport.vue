<template>
  <div class="batch-report">
    <a-card title="批量操作报表">
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
        @expand="handleExpand"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'batch_name'">
            <a-tag color="blue">{{ record.batch_name }}</a-tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDateTime(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'total_time'">
            {{ calculateDuration(record.started_at, record.completed_at) }}
          </template>
          <template v-else-if="column.key === 'progress'">
            <a-progress
              :percent="calculateProgress(record.processed_count, record.total_count)"
              :status="getProgressStatus(record.status)"
              size="small"
            />
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'

interface BatchOperation {
  id: number
  batch_name: string
  batch_description?: string
  operation_type: string
  total_count: number
  processed_count: number
  success_count: number
  failed_count: number
  status: string
  created_at: string
  started_at?: string
  completed_at?: string
}

interface Props {
  data: BatchOperation[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  { title: '批次名称', dataIndex: 'batch_name', key: 'batch_name' },
  { title: '操作类型', dataIndex: 'operation_type', key: 'operation_type', width: 120 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '总数/成功/失败', width: 150, customRender: ({ record }: { record: BatchOperation }) => {
    return `${record.total_count} / ${record.success_count} / ${record.failed_count}`
  }},
  { title: '进度', key: 'progress', width: 150 },
  { title: '总耗时', key: 'total_time', width: 120 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
]

const pagination = computed(() => ({
  pageSize: 20,
  showTotal: (total: number) => `共 ${total} 个批次`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'default',
    running: 'processing',
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
  }
  return statusMap[status] || 'default'
}

const calculateProgress = (processed: number, total: number): number => {
  if (!total) return 0
  return Math.round((processed / total) * 100)
}

const getProgressStatus = (status: string): 'success' | 'exception' | 'active' | 'normal' => {
  if (status === 'completed') return 'success'
  if (status === 'failed' || status === 'cancelled') return 'exception'
  if (status === 'running') return 'active'
  return 'normal'
}

const calculateDuration = (start?: string, end?: string): string => {
  if (!start) return '-'
  if (!end) return '进行中...'
  
  const duration = new Date(end).getTime() - new Date(start).getTime()
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

const handleExpand = (expanded: boolean, record: BatchOperation) => {
  console.log('Expand:', expanded, record)
}
</script>
