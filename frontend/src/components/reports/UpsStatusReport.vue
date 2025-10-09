<template>
  <div class="ups-status-report">
    <a-card title="UPS 状态报表">
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
          <template v-if="column.key === 'ups_name'">
            <strong>{{ record.ups_name }}</strong>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'battery_charge'">
            <a-progress
              :percent="record.battery_charge || 0"
              :status="getBatteryStatus(record.battery_charge || 0)"
              size="small"
            />
          </template>
          <template v-else-if="column.key === 'load_percentage'">
            <a-progress
              :percent="record.load_percentage || 0"
              :status="getLoadStatus(record.load_percentage || 0)"
              size="small"
            />
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

interface UpsStatus {
  id: number
  ups_name: string
  ups_model?: string
  status: string
  battery_charge?: number
  battery_runtime?: number
  input_voltage?: number
  output_voltage?: number
  load_percentage?: number
  temperature?: number
  location?: string
  last_test_date?: string
}

interface Props {
  data: UpsStatus[]
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  (e: 'refresh'): void
}>()

const columns = [
  { title: 'UPS 名称', dataIndex: 'ups_name', key: 'ups_name', width: 150 },
  { title: '型号', dataIndex: 'ups_model', key: 'ups_model', width: 150 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '电池电量', key: 'battery_charge', width: 200 },
  { title: '负载', key: 'load_percentage', width: 200 },
  { title: '位置', dataIndex: 'location', key: 'location', width: 150 },
]

const pagination = computed(() => ({
  pageSize: 10,
  showTotal: (total: number) => `共 ${total} 台 UPS`,
}))

const expandedRowRender = (record: UpsStatus) => {
  return h(Descriptions, { bordered: true, column: 2, size: 'small' }, () => [
    h(Descriptions.Item, { label: '输入电压' }, () => `${record.input_voltage || 0} V`),
    h(Descriptions.Item, { label: '输出电压' }, () => `${record.output_voltage || 0} V`),
    h(Descriptions.Item, { label: '电池运行时间' }, () => `${record.battery_runtime || 0} 分钟`),
    h(Descriptions.Item, { label: '温度' }, () => `${record.temperature || 0} °C`),
    h(Descriptions.Item, { label: '最后测试' }, () => formatDateTime(record.last_test_date)),
  ])
}

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

const getBatteryStatus = (charge: number): 'success' | 'exception' | 'normal' => {
  if (charge < 20) return 'exception'
  if (charge < 50) return 'normal'
  return 'success'
}

const getLoadStatus = (load: number): 'success' | 'exception' | 'normal' => {
  if (load > 90) return 'exception'
  if (load > 75) return 'normal'
  return 'success'
}

const formatDateTime = (dateStr?: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
