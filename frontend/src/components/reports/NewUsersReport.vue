<template>
  <div class="new-users-report">
    <a-card title="新用户报表">
      <template #extra>
        <a-space>
          <a-range-picker v-model:value="dateRange" />
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
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'username'">
            <a-tag color="blue">{{ record.username }}</a-tag>
          </template>
          <template v-else-if="column.key === 'creationdate'">
            {{ formatDateTime(record.creationdate) }}
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

interface NewUser {
  id: number
  username: string
  firstname?: string
  lastname?: string
  email?: string
  creationdate: string
}

interface Props {
  data: NewUser[]
  loading?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '姓', dataIndex: 'firstname', key: 'firstname' },
  { title: '名', dataIndex: 'lastname', key: 'lastname' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '创建时间', dataIndex: 'creationdate', key: 'creationdate', width: 200 },
]

const pagination = computed(() => ({
  total: props.data.length,
  pageSize: 20,
  showTotal: (total: number) => `共 ${total} 个新用户`,
}))

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
