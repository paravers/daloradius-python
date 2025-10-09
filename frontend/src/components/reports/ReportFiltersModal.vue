<template>
  <a-modal
    v-model:open="isVisible"
    title="筛选报表数据"
    width="600px"
    @ok="handleApply"
    @cancel="handleCancel"
  >
    <a-form layout="vertical">
      <!-- 通用筛选器 -->
      <a-form-item label="日期范围">
        <a-range-picker
          v-model:value="filters.dateRange"
          style="width: 100%"
          :presets="datePresets"
        />
      </a-form-item>

      <!-- 用户报表特定筛选器 -->
      <template v-if="isUserReport">
        <a-form-item label="用户名">
          <a-input v-model:value="filters.username" placeholder="输入用户名" />
        </a-form-item>

        <a-form-item label="NAS IP">
          <a-input v-model:value="filters.nasIp" placeholder="输入 NAS IP 地址" />
        </a-form-item>
      </template>

      <!-- 系统日志特定筛选器 -->
      <template v-if="reportType === 'system-logs'">
        <a-form-item label="日志级别">
          <a-select v-model:value="filters.logLevel" placeholder="选择日志级别">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="DEBUG">DEBUG</a-select-option>
            <a-select-option value="INFO">INFO</a-select-option>
            <a-select-option value="WARNING">WARNING</a-select-option>
            <a-select-option value="ERROR">ERROR</a-select-option>
            <a-select-option value="CRITICAL">CRITICAL</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="搜索关键词">
          <a-input v-model:value="filters.searchText" placeholder="搜索日志内容" />
        </a-form-item>
      </template>

      <!-- 批量报表特定筛选器 -->
      <template v-if="reportType === 'batch-report'">
        <a-form-item label="批次名称">
          <a-input v-model:value="filters.batchName" placeholder="输入批次名称" />
        </a-form-item>

        <a-form-item label="操作状态">
          <a-select v-model:value="filters.status" placeholder="选择状态">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="pending">等待中</a-select-option>
            <a-select-option value="running">运行中</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="failed">已失败</a-select-option>
            <a-select-option value="cancelled">已取消</a-select-option>
          </a-select>
        </a-form-item>
      </template>

      <!-- Top Users 特定筛选器 -->
      <template v-if="reportType === 'top-users'">
        <a-form-item label="排序依据">
          <a-select v-model:value="filters.orderBy">
            <a-select-option value="total_traffic">总流量</a-select-option>
            <a-select-option value="session_time">会话时长</a-select-option>
            <a-select-option value="session_count">会话次数</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="显示数量">
          <a-input-number
            v-model:value="filters.limit"
            :min="5"
            :max="100"
            style="width: 100%"
          />
        </a-form-item>
      </template>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'

interface Props {
  visible: boolean
  reportType?: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'filters-applied', filters: Record<string, unknown>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isVisible = ref(props.visible)

const filters = ref<Record<string, unknown>>({
  dateRange: null,
  username: '',
  nasIp: '',
  logLevel: '',
  searchText: '',
  batchName: '',
  status: '',
  orderBy: 'total_traffic',
  limit: 10,
})

const datePresets = [
  { label: '今天', value: [dayjs().startOf('day'), dayjs()] as [Dayjs, Dayjs] },
  { label: '昨天', value: [dayjs().subtract(1, 'day').startOf('day'), dayjs().subtract(1, 'day').endOf('day')] as [Dayjs, Dayjs] },
  { label: '最近7天', value: [dayjs().subtract(7, 'day'), dayjs()] as [Dayjs, Dayjs] },
  { label: '最近30天', value: [dayjs().subtract(30, 'day'), dayjs()] as [Dayjs, Dayjs] },
  { label: '本月', value: [dayjs().startOf('month'), dayjs()] as [Dayjs, Dayjs] },
  { label: '上月', value: [dayjs().subtract(1, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')] as [Dayjs, Dayjs] },
]

const isUserReport = computed(() => {
  return ['online-users', 'history', 'last-connect', 'new-users'].includes(props.reportType || '')
})

watch(() => props.visible, (val) => {
  isVisible.value = val
})

watch(isVisible, (val) => {
  emit('update:visible', val)
})

const handleApply = () => {
  emit('filters-applied', { ...filters.value })
  isVisible.value = false
}

const handleCancel = () => {
  isVisible.value = false
}
</script>
