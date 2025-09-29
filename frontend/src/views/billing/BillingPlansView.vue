<template>
  <div class="billing-plans-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-content">
        <h1 class="page-title">
          <Icon name="CreditCard" class="title-icon" />
          计费计划管理
        </h1>
        <p class="page-description">管理系统计费计划，配置计费规则和费率</p>
      </div>
      <div class="header-actions">
        <Button 
          type="primary" 
          @click="showCreateModal = true"
          :loading="loading"
        >
          <Icon name="Plus" />
          新建计划
        </Button>
        <Button @click="refreshData">
          <Icon name="Refresh" />
          刷新
        </Button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <SearchForm
      v-model="searchForm"
      :fields="searchFields"
      @search="handleSearch"
      @reset="handleReset"
      class="search-section"
    />

    <!-- 批量操作工具栏 -->
    <TableToolbar
      v-if="selectedPlans.length > 0"
      :selected-count="selectedPlans.length"
      :total-count="total"
      @clear-selection="clearSelection"
    >
      <Button 
        type="danger" 
        @click="handleBatchDelete"
        :loading="loading"
      >
        <Icon name="Trash2" />
        批量删除
      </Button>
    </TableToolbar>

    <!-- 数据表格 -->
    <DataTable
      :data="plans"
      :columns="tableColumns"
      :loading="loading"
      :pagination="{
        current: queryParams.page,
        pageSize: queryParams.pageSize,
        total: total,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total) => `共 ${total} 条记录`
      }"
      row-key="id"
      :row-selection="{
        selectedRowKeys: selectedPlans,
        onChange: handleSelectionChange
      }"
      @change="handleTableChange"
      class="data-table"
    >
      <!-- 计划状态列 -->
      <template #status="{ record }">
        <Badge 
          :status="record.active ? 'success' : 'default'"
          :text="record.active ? '激活' : '停用'"
        />
      </template>

      <!-- 计划类型列 -->
      <template #type="{ record }">
        <Tag :color="getPlanTypeColor(record.type)">
          {{ getPlanTypeText(record.type) }}
        </Tag>
      </template>

      <!-- 费率数量列 -->
      <template #rateCount="{ record }">
        <span>{{ record.rates?.length || 0 }} 项</span>
      </template>

      <!-- 用户限制列 -->
      <template #maxUsers="{ record }">
        <span v-if="record.maxUsers">{{ record.maxUsers.toLocaleString() }}</span>
        <span v-else class="text-muted">无限制</span>
      </template>

      <!-- 创建时间列 -->
      <template #createdAt="{ record }">
        <Time :value="record.createdAt" />
      </template>

      <!-- 操作列 -->
      <template #actions="{ record }">
        <div class="action-buttons">
          <Button 
            type="link" 
            size="small"
            @click="viewPlan(record)"
          >
            <Icon name="Eye" />
            查看
          </Button>
          <Button 
            type="link" 
            size="small"
            @click="editPlan(record)"
          >
            <Icon name="Edit" />
            编辑
          </Button>
          <Button 
            type="link" 
            size="small"
            @click="record.active ? deactivatePlan(record.id) : activatePlan(record.id)"
            :loading="loading"
          >
            <Icon :name="record.active ? 'Pause' : 'Play'" />
            {{ record.active ? '停用' : '激活' }}
          </Button>
          <Popconfirm
            title="确定要删除这个计费计划吗？"
            description="删除后将无法恢复，且会影响正在使用此计划的用户。"
            @confirm="deletePlan(record.id)"
          >
            <Button 
              type="link" 
              size="small" 
              danger
            >
              <Icon name="Trash2" />
              删除
            </Button>
          </Popconfirm>
        </div>
      </template>
    </DataTable>

    <!-- 创建/编辑计划模态框 -->
    <Modal
      v-model:open="showCreateModal"
      :title="editingPlan ? '编辑计费计划' : '新建计费计划'"
      width="800px"
      @cancel="handleModalCancel"
    >
      <BillingPlanForm
        :plan="editingPlan"
        :loading="loading"
        @submit="handlePlanSubmit"
        @cancel="handleModalCancel"
      />
    </Modal>

    <!-- 计划详情模态框 -->
    <Modal
      v-model:open="showDetailModal"
      title="计费计划详情"
      width="900px"
      :footer="null"
    >
      <BillingPlanDetail
        v-if="viewingPlan"
        :plan="viewingPlan"
        @edit="editPlan"
        @close="showDetailModal = false"
      />
    </Modal>

    <!-- 批量删除确认模态框 -->
    <Modal
      v-model:open="showBatchDeleteModal"
      title="批量删除确认"
      @ok="confirmBatchDelete"
      @cancel="showBatchDeleteModal = false"
    >
      <div class="batch-delete-content">
        <Icon name="AlertTriangle" class="warning-icon" />
        <div class="warning-text">
          <p>您即将删除 <strong>{{ selectedPlans.length }}</strong> 个计费计划。</p>
          <p>此操作不可撤销，且可能影响正在使用这些计划的用户。</p>
          <p>确定要继续吗？</p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { BillingPlan, CreateBillingPlanRequest, UpdateBillingPlanRequest } from '@/types/billing'
import { useBillingPlans } from '@/composables/useBillingPlans'
import { useMessage } from '@/composables/useMessage'
import { formatDateTime } from '@/utils/date'
import { 
  Button, 
  Modal, 
  Badge, 
  Tag, 
  Popconfirm,
  type TableColumnType
} from 'ant-design-vue'
import Icon from '@/components/common/Icon.vue'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import TableToolbar from '@/components/common/TableToolbar.vue'
import Time from '@/components/common/Time.vue'
import BillingPlanForm from './components/BillingPlanForm.vue'
import BillingPlanDetail from './components/BillingPlanDetail.vue'

// 组合式函数
const { 
  loading,
  plans,
  total,
  error,
  queryParams,
  hasPlans,
  totalPages,
  activePlans,
  inactivePlans,
  fetchPlans,
  createPlan,
  updatePlan,
  deletePlan: deletePlanService,
  activatePlan: activatePlanService,
  deactivatePlan: deactivatePlanService,
  searchPlans,
  filterPlans,
  changePage,
  changePageSize,
  resetFilters,
  refreshPlans,
  deletePlans: deletePlansService
} = useBillingPlans()

const { success, error: showError } = useMessage()

// 响应式状态
const selectedPlans = ref<string[]>([])
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showBatchDeleteModal = ref(false)
const editingPlan = ref<BillingPlan | null>(null)
const viewingPlan = ref<BillingPlan | null>(null)

// 搜索表单
const searchForm = reactive({
  name: '',
  type: undefined,
  active: undefined
})

// 搜索字段配置
const searchFields = [
  {
    key: 'name',
    label: '计划名称',
    type: 'input',
    placeholder: '请输入计划名称'
  },
  {
    key: 'type',
    label: '计划类型',
    type: 'select',
    placeholder: '选择计划类型',
    options: [
      { label: '月租', value: 'monthly' },
      { label: '按量计费', value: 'usage' },
      { label: '混合计费', value: 'hybrid' },
      { label: '预付费', value: 'prepaid' },
      { label: '后付费', value: 'postpaid' }
    ]
  },
  {
    key: 'active',
    label: '状态',
    type: 'select',
    placeholder: '选择状态',
    options: [
      { label: '激活', value: true },
      { label: '停用', value: false }
    ]
  }
]

// 表格列配置
const tableColumns: TableColumnType[] = [
  {
    title: '计划名称',
    dataIndex: 'name',
    key: 'name',
    ellipsis: true,
    sorter: true
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    width: 120,
    slots: { customRender: 'type' }
  },
  {
    title: '状态',
    dataIndex: 'active',
    key: 'status',
    width: 100,
    slots: { customRender: 'status' }
  },
  {
    title: '费率项目',
    key: 'rateCount',
    width: 120,
    slots: { customRender: 'rateCount' }
  },
  {
    title: '用户限制',
    dataIndex: 'maxUsers',
    key: 'maxUsers',
    width: 120,
    slots: { customRender: 'maxUsers' }
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 180,
    slots: { customRender: 'createdAt' },
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 250,
    slots: { customRender: 'actions' }
  }
]

// 计算属性
const hasSelectedPlans = computed(() => selectedPlans.value.length > 0)

// 页面初始化
onMounted(() => {
  loadData()
})

// 加载数据
async function loadData() {
  try {
    await fetchPlans()
  } catch (err) {
    showError('加载计费计划失败')
  }
}

// 刷新数据
async function refreshData() {
  await loadData()
  success('数据已刷新')
}

// 搜索处理
async function handleSearch() {
  try {
    await filterPlans(searchForm)
    success('搜索完成')
  } catch (err) {
    showError('搜索失败')
  }
}

// 重置搜索
async function handleReset() {
  Object.assign(searchForm, {
    name: '',
    type: undefined,
    active: undefined
  })
  try {
    await resetFilters()
    success('已重置搜索条件')
  } catch (err) {
    showError('重置失败')
  }
}

// 表格变化处理
async function handleTableChange(pagination: any, filters: any, sorter: any) {
  try {
    await changePage(pagination.current)
    if (pagination.pageSize !== queryParams.pageSize) {
      await changePageSize(pagination.pageSize)
    }
  } catch (err) {
    showError('加载数据失败')
  }
}

// 选择变化处理
function handleSelectionChange(selectedRowKeys: string[]) {
  selectedPlans.value = selectedRowKeys
}

// 清除选择
function clearSelection() {
  selectedPlans.value = []
}

// 查看计划详情
function viewPlan(plan: BillingPlan) {
  viewingPlan.value = plan
  showDetailModal.value = true
}

// 编辑计划
function editPlan(plan: BillingPlan) {
  editingPlan.value = plan
  showCreateModal.value = true
}

// 激活计划
async function activatePlan(id: string) {
  try {
    await activatePlanService(id)
    success('计划已激活')
  } catch (err) {
    showError('激活失败')
  }
}

// 停用计划
async function deactivatePlan(id: string) {
  try {
    await deactivatePlanService(id)
    success('计划已停用')
  } catch (err) {
    showError('停用失败')
  }
}

// 删除计划
async function deletePlan(id: string) {
  try {
    await deletePlanService(id)
    success('计划已删除')
  } catch (err) {
    showError('删除失败')
  }
}

// 批量删除处理
function handleBatchDelete() {
  if (selectedPlans.value.length === 0) {
    showError('请先选择要删除的计划')
    return
  }
  showBatchDeleteModal.value = true
}

// 确认批量删除
async function confirmBatchDelete() {
  try {
    await deletePlansService(selectedPlans.value)
    selectedPlans.value = []
    showBatchDeleteModal.value = false
    success(`已删除 ${selectedPlans.value.length} 个计划`)
  } catch (err) {
    showError('批量删除失败')
  }
}

// 计划提交处理
async function handlePlanSubmit(data: CreateBillingPlanRequest | UpdateBillingPlanRequest) {
  try {
    if (editingPlan.value) {
      await updatePlan(editingPlan.value.id, data as UpdateBillingPlanRequest)
      success('计划更新成功')
    } else {
      await createPlan(data as CreateBillingPlanRequest)
      success('计划创建成功')
    }
    handleModalCancel()
  } catch (err) {
    showError(editingPlan.value ? '更新失败' : '创建失败')
  }
}

// 模态框取消处理
function handleModalCancel() {
  showCreateModal.value = false
  editingPlan.value = null
}

// 获取计划类型颜色
function getPlanTypeColor(type: string): string {
  const colors: Record<string, string> = {
    monthly: 'blue',
    usage: 'green',
    hybrid: 'orange',
    prepaid: 'purple',
    postpaid: 'red'
  }
  return colors[type] || 'default'
}

// 获取计划类型文本
function getPlanTypeText(type: string): string {
  const texts: Record<string, string> = {
    monthly: '月租',
    usage: '按量计费',
    hybrid: '混合计费',
    prepaid: '预付费',
    postpaid: '后付费'
  }
  return texts[type] || type
}
</script>

<style scoped>
.billing-plans-view {
  padding: 24px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header-content {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.title-icon {
  margin-right: 8px;
  color: #1890ff;
}

.page-description {
  margin: 0;
  color: #8c8c8c;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-section {
  margin-bottom: 16px;
}

.data-table {
  background: white;
  border-radius: 8px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.batch-delete-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.warning-icon {
  color: #faad14;
  font-size: 20px;
  margin-top: 2px;
}

.warning-text p {
  margin: 4px 0;
}

.warning-text strong {
  color: #ff4d4f;
}

.text-muted {
  color: #8c8c8c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .billing-plans-view {
    padding: 16px;
  }

  .view-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .page-title {
    font-size: 20px;
  }
}
</style>