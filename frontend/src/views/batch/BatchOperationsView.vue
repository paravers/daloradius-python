<template>
  <div class="batch-operations">
    <PageHeader 
      title="批量操作管理"
      subtitle="管理和监控批量操作历史记录"
    />
    
    <div class="content-container">
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <StatsCard
          label="总操作数"
          :value="stats.total_operations"
          icon="database"
          color="primary"
        />
        <StatsCard
          label="本周操作"
          :value="stats.recent_operations"
          icon="calendar-week"
          color="success"
        />
        <StatsCard
          label="成功率"
          :value="successRate + '%'"
          icon="check-circle"
          color="primary"
        />
        <StatsCard
          label="运行中"
          :value="runningOperations"
          icon="sync"
          color="warning"
        />
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <Card>
          <div class="filters-grid">
            <FormField label="操作类型" class="filter-field">
              <Select
                v-model="filters.operation_type"
                :options="operationTypeOptions"
                placeholder="选择操作类型"
                clearable
                @change="handleFilterChange"
              />
            </FormField>
            
            <FormField label="状态" class="filter-field">
              <Select
                v-model="filters.status"
                :options="statusOptions"
                placeholder="选择状态"
                clearable
                @change="handleFilterChange"
              />
            </FormField>
            
            <FormField label="Hotspot" class="filter-field">
              <Input
                v-model="filters.hotspot_id"
                type="number"
                placeholder="输入 Hotspot ID"
                @input="handleFilterChange"
              />
            </FormField>
            
            <FormField label="日期范围" class="filter-field">
              <DatePicker
                v-model="dateRange"
                type="daterange"
                format="YYYY-MM-DD"
                placeholder="选择日期范围"
                @change="handleDateRangeChange"
              />
            </FormField>
            
            <div class="filter-actions">
              <Button @click="resetFilters" variant="secondary">
                <Icon name="refresh" />
                重置
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <!-- Batch Operations Table -->
      <Card class="table-card">
        <template #header>
          <div class="table-header">
            <h3>批量操作历史</h3>
            <Button @click="refreshData" :loading="loading">
              <Icon name="refresh" />
              刷新
            </Button>
          </div>
        </template>
        
        <DataTable
          :dataSource="dataSource"
          :columns="columns"
          :loading="loading"
          :pagination="pagination"
          :show-selection="false"
          @page-change="handlePageChange"
          @sort-change="handleSortChange"
        />
      </Card>

      <!-- Batch Operation Details Modal -->
      <Modal
        v-model:show="showDetailsModal"
        title="批量操作详情"
      >
        <BatchOperationDetails
          v-if="selectedOperation"
          :operation="selectedOperation"
        />
      </Modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import type { BatchHistoryResponse, BatchHistoryQuery } from '@/types/batch'
import { useBatchOperations } from '@/composables/useBatchOperations'
import PageHeader from '@/components/common/PageHeader.vue'
import StatsCard from '@/components/common/StatsCard.vue'
import Card from '@/components/common/Card.vue'
import DataTable from '@/components/common/DataTable.vue'
import FormField from '@/components/common/FormField.vue'
import Select from '@/components/common/Select.vue'
import Input from '@/components/common/Input.vue'
import DatePicker from '@/components/common/DatePicker.vue'
import Button from '@/components/common/Button.vue'
import Icon from '@/components/common/Icon.vue'
import Modal from '@/components/common/Modal.vue'
import BatchOperationDetails from '@/components/batch/BatchOperationDetails.vue'

// Composables
const {
  batchHistory,
  stats,
  loading,
  fetchBatchHistory,
  fetchBatchStats,
  getBatchDetails
} = useBatchOperations()

// Reactive state
const showDetailsModal = ref(false)
const selectedOperation = ref<BatchHistoryResponse | null>(null)
const dateRange = ref<[string, string] | null>(null)

const filters = reactive<BatchHistoryQuery>({
  operation_type: undefined,
  status: undefined,
  hotspot_id: undefined,
  created_after: undefined,
  created_before: undefined,
  page: 1,
  size: 20,
  sort_by: 'created_at',
  sort_order: 'desc'
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: true
})

// Computed
const dataSource = computed(() => ({
  data: batchHistory.value,
  total: pagination.total,
  loading: loading.value
}))

// Options
const operationTypeOptions = [
  { label: '用户创建', value: 'user_create' },
  { label: '用户删除', value: 'user_delete' },
  { label: '用户更新', value: 'user_update' },
  { label: '用户激活', value: 'user_activate' },
  { label: '用户停用', value: 'user_deactivate' },
  { label: 'NAS删除', value: 'nas_delete' },
  { label: 'NAS更新', value: 'nas_update' },
  { label: '组删除', value: 'group_delete' },
  { label: '组更新', value: 'group_update' }
]

const statusOptions = [
  { label: '等待中', value: 'pending' },
  { label: '运行中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '已失败', value: 'failed' },
  { label: '已取消', value: 'cancelled' }
]

// Computed
const successRate = computed(() => {
  if (!stats.value.total_operations) return 0
  const completedOps = Object.entries(stats.value.status_distribution || {})
    .filter(([status]) => status === 'completed')
    .reduce((sum, [, count]) => sum + count, 0)
  return Math.round((completedOps / stats.value.total_operations) * 100)
})

const runningOperations = computed(() => {
  return stats.value.status_distribution?.running || 0
})

// Table columns
const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
    sorter: true
  },
  {
    title: '操作名称',
    dataIndex: 'batch_name',
    key: 'batch_name',
    ellipsis: true
  },
  {
    title: '操作类型',
    dataIndex: 'operation_type',
    key: 'operation_type',
    width: 120,
    customRender: ({ text }: { text: string }) => {
      const option = operationTypeOptions.find(opt => opt.value === text)
      return option ? option.label : text
    }
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    customRender: ({ text }: { text: string }) => {
      const statusMap = {
        pending: { color: 'orange', text: '等待中' },
        running: { color: 'blue', text: '运行中' },
        completed: { color: 'green', text: '已完成' },
        failed: { color: 'red', text: '已失败' },
        cancelled: { color: 'gray', text: '已取消' }
      }
      const status = statusMap[text as keyof typeof statusMap] || { color: 'gray', text }
      return `<span style="color: ${status.color}">${status.text}</span>`
    }
  },
  {
    title: '总数',
    dataIndex: 'total_count',
    key: 'total_count',
    width: 80,
    align: 'center' as const
  },
  {
    title: '成功',
    dataIndex: 'success_count',
    key: 'success_count',
    width: 80,
    align: 'center' as const
  },
  {
    title: '失败',
    dataIndex: 'failure_count',
    key: 'failure_count',
    width: 80,
    align: 'center' as const
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
    sorter: true,
    customRender: ({ text }: { text: string }) => {
      return new Date(text).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    customRender: ({ record }: { record: BatchHistoryResponse }) => {
      return `
        <button class="action-btn view-btn" data-action="view" data-id="${record.id}">
          <span>详情</span>
        </button>
      `
    }
  }
]

// Methods
const handleFilterChange = () => {
  filters.page = 1
  pagination.current = 1
  loadData()
}

const handleDateRangeChange = (dates: string | [string, string] | null) => {
  if (Array.isArray(dates) && dates.length === 2) {
    filters.created_after = new Date(dates[0]).toISOString()
    filters.created_before = new Date(dates[1]).toISOString()
  } else {
    filters.created_after = undefined
    filters.created_before = undefined
  }
  handleFilterChange()
}

const resetFilters = () => {
  Object.assign(filters, {
    operation_type: undefined,
    status: undefined,
    hotspot_id: undefined,
    created_after: undefined,
    created_before: undefined,
    page: 1,
    size: 20,
    sort_by: 'created_at',
    sort_order: 'desc'
  })
  dateRange.value = null
  pagination.current = 1
  loadData()
}

const handlePageChange = (page: number, pageSize: number) => {
  filters.page = page
  filters.size = pageSize
  pagination.current = page
  pagination.pageSize = pageSize
  loadData()
}

const handleSortChange = (sorter: { field?: string; order?: 'ascend' | 'descend' }) => {
  if (sorter.field) {
    filters.sort_by = sorter.field
    filters.sort_order = sorter.order === 'ascend' ? 'asc' : 'desc'
    loadData()
  }
}

const handleRowAction = async (action: string, record: BatchHistoryResponse) => {
  if (action === 'view') {
    await showOperationDetails(record.id)
  }
}

const showOperationDetails = async (operationId: number) => {
  try {
    selectedOperation.value = await getBatchDetails(operationId)
    showDetailsModal.value = true
  } catch {
    message.error('获取操作详情失败')
  }
}

const refreshData = () => {
  loadData()
  fetchBatchStats()
}

const loadData = async () => {
  try {
    const result = await fetchBatchHistory(filters)
    pagination.total = result.total
    pagination.current = result.page
  } catch {
    message.error('加载批量操作历史失败')
  }
}

// Event listeners
const setupTableEventListeners = () => {
  const tableContainer = document.querySelector('.table-card')
  if (tableContainer) {
    tableContainer.addEventListener('click', (event) => {
      const target = event.target as HTMLElement
      const actionBtn = target.closest('.action-btn') as HTMLElement
      if (actionBtn) {
        event.preventDefault()
        const action = actionBtn.getAttribute('data-action')
        const id = actionBtn.getAttribute('data-id')
        if (action && id) {
          const record = batchHistory.value.find(item => item.id === parseInt(id))
          if (record) {
            handleRowAction(action, record)
          }
        }
      }
    })
  }
}

// Lifecycle
onMounted(() => {
  loadData()
  fetchBatchStats()
  setupTableEventListeners()
})

// Watchers
watch(() => batchHistory.value, () => {
  // Re-setup event listeners when table data changes
  setTimeout(setupTableEventListeners, 100)
}, { flush: 'post' })
</script>

<style scoped>
.batch-operations {
  padding: 24px;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.filters-section {
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.filter-field {
  margin-bottom: 0;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-card {
  margin-bottom: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

:deep(.ant-table-cell) {
  padding: 12px 16px;
}

:deep(.action-btn) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

:deep(.action-btn:hover) {
  border-color: #1890ff;
  color: #1890ff;
}

:deep(.view-btn) {
  color: #1890ff;
  border-color: #1890ff;
}

:deep(.view-btn:hover) {
  background: #f6ffed;
}

@media (max-width: 768px) {
  .batch-operations {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>