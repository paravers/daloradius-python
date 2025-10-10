<template>
  <div class="top-users-report">
    <a-card title="热门用户报表 - 使用量排行">
      <template #extra>
        <a-space>
          <a-select v-model:value="orderBy" style="width: 150px">
            <a-select-option value="total_traffic">总流量</a-select-option>
            <a-select-option value="session_time">会话时长</a-select-option>
            <a-select-option value="session_count">会话次数</a-select-option>
          </a-select>
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
        row-key="username"
      >
        <template #bodyCell="{ column, record, index }">
          <template v-if="column.key === 'rank'">
            <a-tag :color="getRankColor(index + 1)">{{ index + 1 }}</a-tag>
          </template>
          <template v-else-if="column.key === 'username'">
            <a-tag color="blue">{{ record.username }}</a-tag>
          </template>
          <template v-else-if="column.key === 'total_traffic'">
            {{ formatBytes(record.total_traffic) }}
          </template>
          <template v-else-if="column.key === 'session_time'">
            {{ formatDuration(record.session_time) }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'

interface TopUser {
  username: string
  total_traffic: number
  session_time: number
  session_count: number
}

interface Props {
  data: TopUser[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const orderBy = ref('total_traffic')

const columns = [
  { title: '排名', key: 'rank', width: 80 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '总流量', dataIndex: 'total_traffic', key: 'total_traffic', width: 150 },
  { title: '会话时长', dataIndex: 'session_time', key: 'session_time', width: 150 },
  { title: '会话次数', dataIndex: 'session_count', key: 'session_count', width: 120 },
]

const pagination = computed(() => ({
  pageSize: 10,
  showTotal: (total: number) => `Top ${Math.min(total, 10)} 用户`,
}))

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

const formatDuration = (seconds: number): string => {
  if (!seconds) return '0s'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

const getRankColor = (rank: number): string => {
  if (rank === 1) return 'gold'
  if (rank === 2) return 'silver'
  if (rank === 3) return '#cd7f32'
  return 'blue'
}
</script>
