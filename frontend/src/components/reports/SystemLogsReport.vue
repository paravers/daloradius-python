<template>
  <div class="system-logs-report">
    <a-card title="系统日志报表">
      <template #extra>
        <a-space>
          <a-select v-model:value="logLevel" style="width: 120px" placeholder="日志级别">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="DEBUG">DEBUG</a-select-option>
            <a-select-option value="INFO">INFO</a-select-option>
            <a-select-option value="WARNING">WARNING</a-select-option>
            <a-select-option value="ERROR">ERROR</a-select-option>
            <a-select-option value="CRITICAL">CRITICAL</a-select-option>
          </a-select>
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索日志"
            style="width: 200px"
            @search="handleSearch"
          />
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
        :scroll="{ x: 1200 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'log_level'">
            <a-tag :color="getLogLevelColor(record.log_level)">
              {{ record.log_level }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'timestamp'">
            {{ formatDateTime(record.timestamp) }}
          </template>
          <template v-else-if="column.key === 'message'">
            <div class="log-message">{{ record.message }}</div>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'

interface SystemLog {
  id: number
  log_level: string
  logger_name?: string
  message: string
  timestamp: string
  username?: string
}

interface Props {
  data: SystemLog[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const logLevel = ref('')
const searchText = ref('')

const columns = [
  { title: '级别', dataIndex: 'log_level', key: 'log_level', width: 100 },
  { title: '时间', dataIndex: 'timestamp', key: 'timestamp', width: 180 },
  { title: '日志名', dataIndex: 'logger_name', key: 'logger_name', width: 150 },
  { title: '用户', dataIndex: 'username', key: 'username', width: 120 },
  { title: '消息', dataIndex: 'message', key: 'message' },
]

const pagination = computed(() => ({
  pageSize: 50,
  showTotal: (total: number) => `共 ${total} 条日志`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getLogLevelColor = (level: string): string => {
  const levelMap: Record<string, string> = {
    DEBUG: 'default',
    INFO: 'blue',
    WARNING: 'orange',
    ERROR: 'red',
    CRITICAL: 'purple',
  }
  return levelMap[level] || 'default'
}

const handleSearch = () => {
  console.log('Search:', searchText.value)
}
</script>

<style scoped lang="scss">
.system-logs-report {
  .log-message {
    word-break: break-all;
    font-family: monospace;
    font-size: 12px;
  }
}
</style>
