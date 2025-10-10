<template>
  <div class="raid-status-report">
    <a-card title="RAID 状态报表">
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
        :expandable="{ expandedRowRender }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'array_name'">
            <strong>{{ record.array_name }}</strong>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'raid_level'">
            <a-tag color="blue">{{ record.raid_level }}</a-tag>
          </template>
          <template v-else-if="column.key === 'disk_status'">
            <div class="disk-status">
              <a-tag color="success">活跃: {{ record.active_disks }}</a-tag>
              <a-tag v-if="record.failed_disks > 0" color="error">
                故障: {{ record.failed_disks }}
              </a-tag>
              <a-tag color="default">备用: {{ record.spare_disks }}</a-tag>
            </div>
          </template>
          <template v-else-if="column.key === 'storage'">
            <div class="storage-info">
              <div>总计: {{ formatBytes(record.total_size) }}</div>
              <div>已用: {{ formatBytes(record.used_size) }}</div>
              <a-progress
                :percent="calculateUsagePercent(record.used_size, record.total_size)"
                size="small"
                :status="
                  getStorageStatus(calculateUsagePercent(record.used_size, record.total_size))
                "
              />
            </div>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { Descriptions } from 'ant-design-vue'

interface RaidStatus {
  id: number
  array_name: string
  raid_level: string
  controller_name?: string
  total_disks: number
  active_disks: number
  failed_disks: number
  spare_disks: number
  total_size?: number
  used_size?: number
  available_size?: number
  read_rate?: number
  write_rate?: number
  status: string
  last_error?: string
  error_count: number
}

interface Props {
  data: RaidStatus[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  { title: '阵列名称', dataIndex: 'array_name', key: 'array_name', width: 150 },
  { title: 'RAID 级别', key: 'raid_level', width: 100 },
  { title: '控制器', dataIndex: 'controller_name', key: 'controller_name', width: 150 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '磁盘状态', key: 'disk_status', width: 250 },
  { title: '存储', key: 'storage', width: 200 },
]

const pagination = computed(() => ({
  pageSize: 10,
  showTotal: (total: number) => `共 ${total} 个 RAID 阵列`,
}))

const expandedRowRender = (record: RaidStatus) => {
  return h(Descriptions, { bordered: true, column: 2, size: 'small' }, () => [
    h(Descriptions.Item, { label: '读取速率' }, () => `${record.read_rate || 0} MB/s`),
    h(Descriptions.Item, { label: '写入速率' }, () => `${record.write_rate || 0} MB/s`),
    h(Descriptions.Item, { label: '错误计数' }, () => record.error_count),
    h(Descriptions.Item, { label: '最后错误' }, () => record.last_error || '无'),
    h(Descriptions.Item, { label: '可用空间', span: 2 }, () => formatBytes(record.available_size)),
  ])
}

const formatBytes = (bytes?: number): string => {
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

const calculateUsagePercent = (used?: number, total?: number): number => {
  if (!used || !total) return 0
  return Math.round((used / total) * 100)
}

const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    online: 'success',
    offline: 'error',
    warning: 'warning',
    degraded: 'warning',
    error: 'error',
    rebuilding: 'processing',
  }
  return statusMap[status?.toLowerCase()] || 'default'
}

const getStorageStatus = (percent: number): 'success' | 'exception' | 'normal' => {
  if (percent >= 90) return 'exception'
  if (percent >= 75) return 'normal'
  return 'success'
}
</script>

<style scoped lang="scss">
.raid-status-report {
  .disk-status {
    display: flex;
    gap: 8px;
  }

  .storage-info {
    font-size: 12px;

    > div {
      margin-bottom: 4px;
    }
  }
}
</style>
