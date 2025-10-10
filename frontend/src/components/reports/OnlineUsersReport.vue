<template>
  <div class="online-users-report">
    <a-card title="在线用户报表">
      <template #extra>
        <a-space>
          <a-button @click="$emit('refresh')" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
          <a-button @click="handleExport">
            <template #icon><DownloadOutlined /></template>
            导出
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :pagination="pagination"
        :scroll="{ x: 1200 }"
        row-key="username"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'username'">
            <a-tag color="blue">{{ record.username }}</a-tag>
          </template>
          <template v-else-if="column.key === 'acctstarttime'">
            {{ formatDateTime(record.acctstarttime) }}
          </template>
          <template v-else-if="column.key === 'acctsessiontime'">
            {{ formatDuration(record.acctsessiontime) }}
          </template>
          <template v-else-if="column.key === 'traffic'">
            <div class="traffic-info">
              <div>↑ {{ formatBytes(record.acctinputoctets) }}</div>
              <div>↓ {{ formatBytes(record.acctoutputoctets) }}</div>
            </div>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-button type="link" size="small" @click="viewDetails(record)"> 详情 </a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

interface OnlineUser {
  username: string
  framedipaddress?: string
  callingstationid?: string
  acctstarttime: string
  acctsessiontime: number
  nasipaddress?: string
  calledstationid?: string
  acctinputoctets: number
  acctoutputoctets: number
  hotspot?: string
  nasshortname?: string
}

interface Props {
  data: OnlineUser[]
  loading?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 150,
  },
  {
    title: 'IP地址',
    dataIndex: 'framedipaddress',
    key: 'framedipaddress',
    width: 150,
  },
  {
    title: 'MAC地址',
    dataIndex: 'callingstationid',
    key: 'callingstationid',
    width: 150,
  },
  {
    title: '开始时间',
    dataIndex: 'acctstarttime',
    key: 'acctstarttime',
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
    width: 150,
  },
  {
    title: 'NAS',
    dataIndex: 'nasshortname',
    key: 'nasshortname',
    width: 120,
  },
  {
    title: '热点',
    dataIndex: 'hotspot',
    key: 'hotspot',
    width: 120,
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    fixed: 'right' as const,
  },
]

const pagination = computed(() => ({
  total: props.data.length,
  pageSize: 20,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDuration = (seconds: number): string => {
  if (!seconds) return '0s'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m ${secs}s`
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

const viewDetails = (record: OnlineUser) => {
  message.info(`查看 ${record.username} 的详细信息`)
}

const handleExport = () => {
  message.info('导出功能开发中')
}
</script>

<style scoped lang="scss">
.online-users-report {
  .traffic-info {
    font-size: 12px;
    line-height: 1.4;

    div {
      &:first-child {
        color: #52c41a;
      }
      &:last-child {
        color: #1890ff;
      }
    }
  }
}
</style>
