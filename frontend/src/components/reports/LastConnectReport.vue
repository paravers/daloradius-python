<template>
  <div class="last-connect-report">
    <a-card title="最近连接报表">
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
          <template v-if="column.key === 'username'">
            <a-tag color="blue">{{ record.username }}</a-tag>
          </template>
          <template v-else-if="column.key === 'authdate'">
            {{ formatDateTime(record.authdate) }}
          </template>
          <template v-else-if="column.key === 'reply'">
            <a-tag :color="record.reply === 'Access-Accept' ? 'success' : 'error'">
              {{ record.reply }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ReloadOutlined } from '@ant-design/icons-vue'

interface LastConnect {
  id: number
  username: string
  pass?: string
  reply: string
  authdate: string
}

interface Props {
  data: LastConnect[]
  loading?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '认证时间', dataIndex: 'authdate', key: 'authdate', width: 200 },
  { title: '认证结果', dataIndex: 'reply', key: 'reply', width: 150 },
]

const pagination = computed(() => ({
  total: props.data.length,
  pageSize: 50,
  showTotal: (total: number) => `共 ${total} 条记录`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
