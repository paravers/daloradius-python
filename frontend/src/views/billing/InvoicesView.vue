<template>
  <div class="invoices-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-content">
        <h1 class="page-title">
          <Icon name="FileText" class="title-icon" />
          发票管理
        </h1>
        <p class="page-description">管理客户发票，跟踪付款状态和收入</p>
      </div>
      <div class="header-actions">
        <Button 
          type="primary" 
          @click="showCreateModal = true"
          :loading="loading"
        >
          <Icon name="Plus" />
          新建发票
        </Button>
        <Button @click="refreshData">
          <Icon name="Refresh" />
          刷新
        </Button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <StatCard
        title="总发票数"
        :value="total"
        icon="FileText"
        color="#1890ff"
      />
      <StatCard
        title="已付款"
        :value="statusStats.paid"
        icon="CheckCircle"
        color="#52c41a"
      />
      <StatCard
        title="已发送"
        :value="statusStats.sent"
        icon="Send"
        color="#faad14"
      />
      <StatCard
        title="逾期"
        :value="statusStats.overdue"
        icon="AlertTriangle"
        color="#ff4d4f"
      />
      <StatCard
        title="总金额"
        :value="`¥${totalAmount.toLocaleString()}`"
        icon="DollarSign"
        color="#722ed1"
      />
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
      v-if="selectedInvoices.length > 0"
      :selected-count="selectedInvoices.length"
      :total-count="total"
      @clear-selection="clearSelection"
    >
      <Button 
        @click="handleBatchSend"
        :loading="loading"
      >
        <Icon name="Send" />
        批量发送
      </Button>
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
      :data="invoices"
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
        selectedRowKeys: selectedInvoices,
        onChange: handleSelectionChange,
        getCheckboxProps: (record) => ({
          disabled: record.status === 'cancelled'
        })
      }"
      @change="handleTableChange"
      class="data-table"
    >
      <!-- 发票号码列 -->
      <template #invoiceNumber="{ record }">
        <Button 
          type="link" 
          @click="viewInvoice(record)"
          class="invoice-link"
        >
          {{ record.invoiceNumber }}
        </Button>
      </template>

      <!-- 客户信息列 -->
      <template #customer="{ record }">
        <div class="customer-info">
          <div class="customer-name">{{ record.userInfo.name }}</div>
          <div class="customer-email">{{ record.userInfo.email }}</div>
        </div>
      </template>

      <!-- 状态列 -->
      <template #status="{ record }">
        <Badge 
          :status="getStatusBadgeType(record.status)"
          :text="getStatusText(record.status)"
        />
      </template>

      <!-- 金额列 -->
      <template #amount="{ record }">
        <div class="amount-cell">
          <span class="amount-value">
            ¥{{ record.total.amount.toLocaleString() }}
          </span>
          <span class="currency">{{ record.total.currency }}</span>
        </div>
      </template>

      <!-- 日期列 -->
      <template #issueDate="{ record }">
        <Time :value="record.issueDate" format="YYYY-MM-DD" />
      </template>

      <template #dueDate="{ record }">
        <Time 
          :value="record.dueDate" 
          format="YYYY-MM-DD"
          :class="{
            'overdue-date': isOverdue(record.dueDate) && record.status !== 'paid'
          }"
        />
      </template>

      <!-- 操作列 -->
      <template #actions="{ record }">
        <div class="action-buttons">
          <Button 
            type="link" 
            size="small"
            @click="viewInvoice(record)"
          >
            <Icon name="Eye" />
            查看
          </Button>
          
          <Button 
            v-if="record.status === 'draft'"
            type="link" 
            size="small"
            @click="editInvoice(record)"
          >
            <Icon name="Edit" />
            编辑
          </Button>
          
          <Button 
            v-if="record.status === 'draft'"
            type="link" 
            size="small"
            @click="sendInvoice(record.id)"
            :loading="loading"
          >
            <Icon name="Send" />
            发送
          </Button>
          
          <Button 
            v-if="['sent', 'overdue'].includes(record.status)"
            type="link" 
            size="small"
            @click="showMarkPaidModal(record)"
          >
            <Icon name="CheckCircle" />
            标记付款
          </Button>
          
          <Dropdown :trigger="['click']">
            <Button type="link" size="small">
              <Icon name="MoreHorizontal" />
            </Button>
            <template #overlay>
              <Menu>
                <MenuItem @click="exportInvoice(record.id, 'pdf')">
                  <Icon name="Download" />
                  导出PDF
                </MenuItem>
                <MenuItem @click="exportInvoice(record.id, 'excel')">
                  <Icon name="Download" />
                  导出Excel
                </MenuItem>
                <MenuItem 
                  v-if="record.status !== 'cancelled'"
                  @click="showCancelModal(record)"
                >
                  <Icon name="X" />
                  取消发票
                </MenuItem>
                <MenuDivider />
                <MenuItem 
                  v-if="record.status === 'draft'"
                  danger
                  @click="deleteInvoice(record.id)"
                >
                  <Icon name="Trash2" />
                  删除
                </MenuItem>
              </Menu>
            </template>
          </Dropdown>
        </div>
      </template>
    </DataTable>

    <!-- 创建/编辑发票模态框 -->
    <Modal
      v-model:open="showCreateModal"
      :title="editingInvoice ? '编辑发票' : '新建发票'"
      width="1000px"
      :footer="null"
      @cancel="handleModalCancel"
    >
      <InvoiceForm
        :invoice="editingInvoice"
        :loading="loading"
        @submit="handleInvoiceSubmit"
        @cancel="handleModalCancel"
      />
    </Modal>

    <!-- 发票详情模态框 -->
    <Modal
      v-model:open="showDetailModal"
      title="发票详情"
      width="1000px"
      :footer="null"
    >
      <InvoiceDetail
        v-if="viewingInvoice"
        :invoice="viewingInvoice"
        @edit="editInvoice"
        @send="sendInvoice"
        @mark-paid="showMarkPaidModal"
        @export="exportInvoice"
        @close="showDetailModal = false"
      />
    </Modal>

    <!-- 标记付款模态框 -->
    <Modal
      v-model:open="showPaidModal"
      title="标记为已付款"
      @ok="confirmMarkPaid"
      @cancel="showPaidModal = false"
    >
      <div class="mark-paid-form">
        <p>确认发票 <strong>{{ markingInvoice?.invoiceNumber }}</strong> 已收到付款？</p>
        <FormItem label="付款方式">
          <Select 
            v-model:value="paymentMethod"
            placeholder="选择付款方式"
            style="width: 100%"
          >
            <SelectOption value="bank_transfer">银行转账</SelectOption>
            <SelectOption value="credit_card">信用卡</SelectOption>
            <SelectOption value="alipay">支付宝</SelectOption>
            <SelectOption value="wechat">微信支付</SelectOption>
            <SelectOption value="cash">现金</SelectOption>
            <SelectOption value="other">其他</SelectOption>
          </Select>
        </FormItem>
      </div>
    </Modal>

    <!-- 取消发票模态框 -->
    <Modal
      v-model:open="showCancelModal"
      title="取消发票"
      @ok="confirmCancelInvoice"
      @cancel="showCancelModal = false"
    >
      <div class="cancel-invoice-form">
        <p>确定要取消发票 <strong>{{ cancellingInvoice?.invoiceNumber }}</strong> 吗？</p>
        <FormItem label="取消原因">
          <TextArea 
            v-model:value="cancelReason"
            :rows="3"
            placeholder="请输入取消原因（可选）"
          />
        </FormItem>
      </div>
    </Modal>

    <!-- 批量操作确认模态框 -->
    <Modal
      v-model:open="showBatchModal"
      :title="batchAction === 'send' ? '批量发送确认' : '批量删除确认'"
      @ok="confirmBatchAction"
      @cancel="showBatchModal = false"
    >
      <div class="batch-action-content">
        <Icon 
          :name="batchAction === 'send' ? 'Send' : 'AlertTriangle'" 
          :class="['action-icon', batchAction === 'send' ? 'send-icon' : 'warning-icon']"
        />
        <div class="action-text">
          <p v-if="batchAction === 'send'">
            您即将发送 <strong>{{ selectedInvoices.length }}</strong> 张发票。
          </p>
          <p v-else>
            您即将删除 <strong>{{ selectedInvoices.length }}</strong> 张发票。
          </p>
          <p>{{ batchAction === 'send' ? '发票将被发送给对应客户。' : '此操作不可撤销。' }}</p>
          <p>确定要继续吗？</p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { 
  Invoice, 
  CreateInvoiceRequest, 
  UpdateInvoiceRequest 
} from '@/types/billing'
import { useInvoices } from '@/composables/useInvoices'
import { useMessage } from '@/composables/useMessage'
import { 
  Button, 
  Modal, 
  Badge, 
  Dropdown,
  Menu,
  MenuItem,
  MenuDivider,
  Select,
  SelectOption,
  FormItem,
  TextArea,
  type TableColumnType
} from 'ant-design-vue'
import Icon from '@/components/common/Icon.vue'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import TableToolbar from '@/components/common/TableToolbar.vue'
import StatCard from '@/components/common/StatCard.vue'
import Time from '@/components/common/Time.vue'
import InvoiceForm from './components/InvoiceForm.vue'
import InvoiceDetail from './components/InvoiceDetail.vue'

// 组合式函数
const { 
  loading,
  invoices,
  total,
  error,
  queryParams,
  hasInvoices,
  totalPages,
  statusStats,
  totalAmount,
  fetchInvoices,
  createInvoice,
  updateInvoice,
  deleteInvoice: deleteInvoiceService,
  sendInvoice: sendInvoiceService,
  markPaid: markPaidService,
  cancelInvoice: cancelInvoiceService,
  searchInvoices,
  filterInvoices,
  changePage,
  changePageSize,
  resetFilters,
  refreshInvoices,
  deleteInvoices: deleteInvoicesService,
  exportInvoice: exportInvoiceService
} = useInvoices()

const { success, error: showError } = useMessage()

// 响应式状态
const selectedInvoices = ref<string[]>([])
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showPaidModal = ref(false)
const showCancelModal = ref(false)
const showBatchModal = ref(false)
const editingInvoice = ref<Invoice | null>(null)
const viewingInvoice = ref<Invoice | null>(null)
const markingInvoice = ref<Invoice | null>(null)
const cancellingInvoice = ref<Invoice | null>(null)
const paymentMethod = ref('')
const cancelReason = ref('')
const batchAction = ref<'send' | 'delete'>('send')

// 搜索表单
const searchForm = reactive({
  invoiceNumber: '',
  userId: '',
  status: undefined,
  startDate: '',
  endDate: ''
})

// 搜索字段配置
const searchFields = [
  {
    key: 'invoiceNumber',
    label: '发票号码',
    type: 'input',
    placeholder: '请输入发票号码'
  },
  {
    key: 'userId',
    label: '客户',
    type: 'input',
    placeholder: '请输入客户ID或名称'
  },
  {
    key: 'status',
    label: '状态',
    type: 'select',
    placeholder: '选择发票状态',
    options: [
      { label: '草稿', value: 'draft' },
      { label: '已发送', value: 'sent' },
      { label: '已付款', value: 'paid' },
      { label: '逾期', value: 'overdue' },
      { label: '已取消', value: 'cancelled' }
    ]
  },
  {
    key: 'dateRange',
    label: '日期范围',
    type: 'date-range',
    placeholder: ['开始日期', '结束日期']
  }
]

// 表格列配置
const tableColumns: TableColumnType[] = [
  {
    title: '发票号码',
    dataIndex: 'invoiceNumber',
    key: 'invoiceNumber',
    width: 150,
    slots: { customRender: 'invoiceNumber' }
  },
  {
    title: '客户',
    key: 'customer',
    width: 200,
    slots: { customRender: 'customer' }
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    slots: { customRender: 'status' }
  },
  {
    title: '金额',
    key: 'amount',
    width: 120,
    slots: { customRender: 'amount' },
    sorter: true
  },
  {
    title: '开票日期',
    dataIndex: 'issueDate',
    key: 'issueDate',
    width: 120,
    slots: { customRender: 'issueDate' },
    sorter: true
  },
  {
    title: '到期日期',
    dataIndex: 'dueDate',
    key: 'dueDate',
    width: 120,
    slots: { customRender: 'dueDate' },
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    slots: { customRender: 'actions' }
  }
]

// 页面初始化
onMounted(() => {
  loadData()
})

// 加载数据
async function loadData() {
  try {
    await fetchInvoices()
  } catch (err) {
    showError('加载发票列表失败')
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
    // 处理日期范围
    if (searchForm.dateRange) {
      searchForm.startDate = searchForm.dateRange[0]
      searchForm.endDate = searchForm.dateRange[1]
    }
    
    await filterInvoices(searchForm)
    success('搜索完成')
  } catch (err) {
    showError('搜索失败')
  }
}

// 重置搜索
async function handleReset() {
  Object.assign(searchForm, {
    invoiceNumber: '',
    userId: '',
    status: undefined,
    startDate: '',
    endDate: '',
    dateRange: undefined
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
  selectedInvoices.value = selectedRowKeys
}

// 清除选择
function clearSelection() {
  selectedInvoices.value = []
}

// 查看发票详情
function viewInvoice(invoice: Invoice) {
  viewingInvoice.value = invoice
  showDetailModal.value = true
}

// 编辑发票
function editInvoice(invoice: Invoice) {
  editingInvoice.value = invoice
  showCreateModal.value = true
}

// 发送发票
async function sendInvoice(id: string) {
  try {
    await sendInvoiceService(id)
    success('发票已发送')
  } catch (err) {
    showError('发送失败')
  }
}

// 显示标记付款模态框
function showMarkPaidModal(invoice: Invoice) {
  markingInvoice.value = invoice
  paymentMethod.value = ''
  showPaidModal.value = true
}

// 确认标记付款
async function confirmMarkPaid() {
  if (!markingInvoice.value) return
  
  try {
    await markPaidService(markingInvoice.value.id, paymentMethod.value)
    showPaidModal.value = false
    success('已标记为付款')
  } catch (err) {
    showError('标记付款失败')
  }
}

// 显示取消发票模态框
function showCancelModal(invoice: Invoice) {
  cancellingInvoice.value = invoice
  cancelReason.value = ''
  showCancelModal.value = true
}

// 确认取消发票
async function confirmCancelInvoice() {
  if (!cancellingInvoice.value) return
  
  try {
    await cancelInvoiceService(cancellingInvoice.value.id, cancelReason.value)
    showCancelModal.value = false
    success('发票已取消')
  } catch (err) {
    showError('取消发票失败')
  }
}

// 删除发票
async function deleteInvoice(id: string) {
  try {
    await deleteInvoiceService(id)
    success('发票已删除')
  } catch (err) {
    showError('删除失败')
  }
}

// 批量发送处理
function handleBatchSend() {
  if (selectedInvoices.value.length === 0) {
    showError('请先选择要发送的发票')
    return
  }
  batchAction.value = 'send'
  showBatchModal.value = true
}

// 批量删除处理
function handleBatchDelete() {
  if (selectedInvoices.value.length === 0) {
    showError('请先选择要删除的发票')
    return
  }
  batchAction.value = 'delete'
  showBatchModal.value = true
}

// 确认批量操作
async function confirmBatchAction() {
  try {
    if (batchAction.value === 'send') {
      // 批量发送
      await Promise.all(
        selectedInvoices.value.map(id => sendInvoiceService(id))
      )
      success(`已发送 ${selectedInvoices.value.length} 张发票`)
    } else {
      // 批量删除
      await deleteInvoicesService(selectedInvoices.value)
      success(`已删除 ${selectedInvoices.value.length} 张发票`)
    }
    
    selectedInvoices.value = []
    showBatchModal.value = false
  } catch (err) {
    showError(`批量${batchAction.value === 'send' ? '发送' : '删除'}失败`)
  }
}

// 导出发票
async function exportInvoice(id: string, format: 'pdf' | 'excel') {
  try {
    await exportInvoiceService(id, format)
    success(`发票导出成功`)
  } catch (err) {
    showError('导出失败')
  }
}

// 发票提交处理
async function handleInvoiceSubmit(data: CreateInvoiceRequest | UpdateInvoiceRequest) {
  try {
    if (editingInvoice.value) {
      await updateInvoice(editingInvoice.value.id, data as UpdateInvoiceRequest)
      success('发票更新成功')
    } else {
      await createInvoice(data as CreateInvoiceRequest)
      success('发票创建成功')
    }
    handleModalCancel()
  } catch (err) {
    showError(editingInvoice.value ? '更新失败' : '创建失败')
  }
}

// 模态框取消处理
function handleModalCancel() {
  showCreateModal.value = false
  editingInvoice.value = null
}

// 工具函数
function getStatusBadgeType(status: string) {
  const types: Record<string, string> = {
    draft: 'default',
    sent: 'processing',
    paid: 'success',
    overdue: 'error',
    cancelled: 'default'
  }
  return types[status] || 'default'
}

function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    draft: '草稿',
    sent: '已发送',
    paid: '已付款',
    overdue: '逾期',
    cancelled: '已取消'
  }
  return texts[status] || status
}

function isOverdue(dueDate: string): boolean {
  return new Date(dueDate) < new Date()
}
</script>

<style scoped>
.invoices-view {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.search-section {
  margin-bottom: 16px;
}

.data-table {
  background: white;
  border-radius: 8px;
}

.invoice-link {
  font-weight: 500;
  padding: 0;
}

.customer-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-name {
  font-weight: 500;
  color: #262626;
}

.customer-email {
  font-size: 12px;
  color: #8c8c8c;
}

.amount-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.amount-value {
  font-weight: 600;
  color: #262626;
}

.currency {
  font-size: 12px;
  color: #8c8c8c;
}

.overdue-date {
  color: #ff4d4f !important;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.mark-paid-form,
.cancel-invoice-form {
  padding: 16px 0;
}

.mark-paid-form p,
.cancel-invoice-form p {
  margin-bottom: 16px;
}

.batch-action-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.action-icon {
  font-size: 20px;
  margin-top: 2px;
}

.send-icon {
  color: #1890ff;
}

.warning-icon {
  color: #faad14;
}

.action-text p {
  margin: 4px 0;
}

.action-text strong {
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .invoices-view {
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

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .action-buttons {
    justify-content: flex-start;
  }
}
</style>