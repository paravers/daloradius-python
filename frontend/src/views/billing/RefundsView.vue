<template>
  <div class="refunds-view">
    <!-- 页面标题和操作区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">退款管理</h1>
        <div class="header-actions">
          <a-button @click="refreshData">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <a-card class="filter-card">
      <div class="filter-row">
        <div class="filter-item">
          <label>退款号码：</label>
          <a-input
            v-model:value="queryParams.refundNumber"
            placeholder="请输入退款号码"
            allow-clear
            @press-enter="handleSearch"
          />
        </div>
        <div class="filter-item">
          <label>支付ID：</label>
          <a-input
            v-model:value="queryParams.paymentId"
            placeholder="请输入支付ID"
            allow-clear
            @press-enter="handleSearch"
          />
        </div>
        <div class="filter-item">
          <label>退款状态：</label>
          <a-select
            v-model:value="queryParams.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="pending">待处理</a-select-option>
            <a-select-option value="approved">已批准</a-select-option>
            <a-select-option value="rejected">已拒绝</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="failed">失败</a-select-option>
          </a-select>
        </div>
        <div class="filter-item">
          <label>用户ID：</label>
          <a-input
            v-model:value="queryParams.userId"
            placeholder="请输入用户ID"
            allow-clear
            @press-enter="handleSearch"
          />
        </div>
      </div>
      <div class="filter-row">
        <div class="filter-item">
          <label>日期范围：</label>
          <a-range-picker
            v-model:value="dateRange"
            format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </div>
        <div class="filter-item">
          <label>金额范围：</label>
          <a-input-number
            v-model:value="queryParams.minAmount"
            placeholder="最小金额"
            :min="0"
            :precision="2"
            style="width: 100px"
          />
          <span style="margin: 0 8px">-</span>
          <a-input-number
            v-model:value="queryParams.maxAmount"
            placeholder="最大金额"
            :min="0"
            :precision="2"
            style="width: 100px"
          />
        </div>
        <div class="filter-actions">
          <a-button type="primary" @click="handleSearch">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button @click="handleResetFilters">
            <template #icon><ClearOutlined /></template>
            重置
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 退款列表 -->
    <a-card class="table-card">
      <a-table
        :columns="columns"
        :data-source="refunds"
        :loading="loading"
        :pagination="{
          current: pagination.page,
          pageSize: pagination.pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          onChange: setPage,
          onShowSizeChange: (current, size) => setPageSize(size)
        }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'refundNumber'">
            <a-button type="link" @click="showRefundDetail(record)">
              {{ record.refundNumber }}
            </a-button>
          </template>
          
          <template v-else-if="column.key === 'paymentInfo'">
            <div class="payment-info">
              <div>
                <a-button type="link" size="small" @click="viewPayment(record.paymentId)">
                  {{ record.paymentId }}
                </a-button>
              </div>
            </div>
          </template>
          
          <template v-else-if="column.key === 'amount'">
            <span class="amount">{{ formatAmount(record.amount) }}</span>
          </template>
          
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getRefundStatusColor(record.status)">
              {{ getRefundStatusText(record.status) }}
            </a-tag>
          </template>
          
          <template v-else-if="column.key === 'reason'">
            <a-tooltip :title="record.reason">
              <span class="reason-text">{{ truncateText(record.reason, 30) }}</span>
            </a-tooltip>
          </template>
          
          <template v-else-if="column.key === 'approvalInfo'">
            <div v-if="record.status === 'approved' || record.status === 'completed'" class="approval-info">
              <div>批准人: {{ record.approvedBy || '-' }}</div>
              <div v-if="record.approvedAt">时间: {{ formatDateTime(record.approvedAt) }}</div>
            </div>
            <div v-else-if="record.status === 'rejected'" class="rejection-info">
              <div>拒绝原因: {{ record.rejectedReason || '-' }}</div>
            </div>
            <span v-else>-</span>
          </template>
          
          <template v-else-if="column.key === 'processInfo'">
            <div v-if="record.status === 'completed'" class="process-info">
              <div>网关ID: {{ record.gatewayRefundId || '-' }}</div>
              <div v-if="record.processedAt">完成时间: {{ formatDateTime(record.processedAt) }}</div>
            </div>
            <span v-else>-</span>
          </template>
          
          <template v-else-if="column.key === 'createdAt'">
            {{ formatDateTime(record.createdAt) }}
          </template>
          
          <template v-else-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button
                v-if="record.status === 'pending'"
                type="primary"
                size="small"
                @click="handleApproveRefund(record)"
                :loading="processingRefunds.has(record.id)"
              >
                批准
              </a-button>
              
              <a-button
                v-if="record.status === 'pending'"
                size="small"
                @click="showRejectModal(record)"
              >
                拒绝
              </a-button>
              
              <a-button
                v-if="record.status === 'approved'"
                type="primary"
                size="small"
                @click="handleProcessRefund(record)"
                :loading="processingRefunds.has(record.id)"
              >
                处理退款
              </a-button>
              
              <a-dropdown>
                <template #overlay>
                  <a-menu>
                    <a-menu-item @click="showRefundDetail(record)">
                      <EyeOutlined /> 查看详情
                    </a-menu-item>
                    <a-menu-item @click="viewPayment(record.paymentId)">
                      <LinkOutlined /> 查看支付
                    </a-menu-item>
                    <a-menu-item 
                      v-if="record.status === 'completed'"
                      @click="downloadRefundReceipt(record)"
                    >
                      <DownloadOutlined /> 下载凭证
                    </a-menu-item>
                  </a-menu>
                </template>
                <a-button size="small">
                  更多 <DownOutlined />
                </a-button>
              </a-dropdown>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 拒绝退款弹窗 -->
    <a-modal
      v-model:open="showRejectRefundModal"
      title="拒绝退款"
      :confirm-loading="rejecting"
      @ok="handleRejectRefund"
      @cancel="showRejectRefundModal = false"
    >
      <a-form
        ref="rejectFormRef"
        :model="rejectForm"
        :rules="rejectRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="拒绝原因" name="reason">
          <a-select
            v-model:value="rejectForm.reason"
            placeholder="请选择拒绝原因"
          >
            <a-select-option value="不符合退款政策">不符合退款政策</a-select-option>
            <a-select-option value="超过退款期限">超过退款期限</a-select-option>
            <a-select-option value="资料不完整">资料不完整</a-select-option>
            <a-select-option value="重复申请">重复申请</a-select-option>
            <a-select-option value="其他原因">其他原因</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item v-if="rejectForm.reason === '其他原因'" label="详细说明" name="detail">
          <a-textarea
            v-model:value="rejectForm.detail"
            placeholder="请详细说明拒绝原因"
            :rows="3"
            show-count
            :maxlength="200"
          />
        </a-form-item>
        
        <a-form-item label="处理人" name="rejectedBy">
          <a-input
            v-model:value="rejectForm.rejectedBy"
            placeholder="请输入处理人姓名"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 退款详情弹窗 -->
    <RefundDetail
      v-model:visible="showRefundDetailModal"
      :refund="selectedRefund"
      @success="handleRefundUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  ReloadOutlined,
  SearchOutlined,
  ClearOutlined,
  EyeOutlined,
  LinkOutlined,
  DownloadOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
import type { 
  Refund,
  RefundStatus,
  Money
} from '@/types/billing'
import type { FormInstance } from 'ant-design-vue'
import { useRefunds } from '@/composables/usePayments'
import RefundDetail from './RefundDetail.vue'
import type { Dayjs } from 'dayjs'

// 使用 composable
const {
  refunds,
  total,
  loading,
  pagination,
  queryParams,
  loadRefunds,
  approveRefund,
  rejectRefund,
  processRefund,
  setPage,
  setPageSize
} = useRefunds()

// 响应式状态
const showRefundDetailModal = ref(false)
const showRejectRefundModal = ref(false)
const selectedRefund = ref<Refund>()
const dateRange = ref<[Dayjs, Dayjs] | null>(null)
const processingRefunds = ref(new Set<string>())
const rejecting = ref(false)
const rejectFormRef = ref<FormInstance>()

// 拒绝表单
const rejectForm = reactive({
  reason: '',
  detail: '',
  rejectedBy: ''
})

// 拒绝表单验证规则
const rejectRules = {
  reason: [
    { required: true, message: '请选择拒绝原因' }
  ],
  detail: [
    { 
      validator: (_rule: any, value: string) => {
        if (rejectForm.reason === '其他原因' && (!value || value.trim().length < 10)) {
          return Promise.reject('请详细说明拒绝原因，至少10个字符')
        }
        return Promise.resolve()
      }
    }
  ],
  rejectedBy: [
    { required: true, message: '请输入处理人姓名' }
  ]
}

// 表格列配置
const columns = [
  {
    title: '退款号码',
    dataIndex: 'refundNumber',
    key: 'refundNumber',
    width: 180
  },
  {
    title: '支付信息',
    dataIndex: 'paymentInfo',
    key: 'paymentInfo',
    width: 150
  },
  {
    title: '退款金额',
    dataIndex: 'amount',
    key: 'amount',
    width: 120,
    sorter: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '退款原因',
    dataIndex: 'reason',
    key: 'reason',
    width: 200
  },
  {
    title: '审批信息',
    dataIndex: 'approvalInfo',
    key: 'approvalInfo',
    width: 160
  },
  {
    title: '处理信息',
    dataIndex: 'processInfo',
    key: 'processInfo',
    width: 160
  },
  {
    title: '申请时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 180,
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right'
  }
]

// 初始化
onMounted(async () => {
  await loadRefunds()
})

// 方法
const refreshData = async () => {
  await loadRefunds()
  message.success('数据已刷新')
}

const handleSearch = () => {
  pagination.page = 1
  loadRefunds()
}

const handleResetFilters = () => {
  // 重置查询参数
  Object.keys(queryParams).forEach(key => {
    if (!['page', 'pageSize'].includes(key)) {
      delete (queryParams as any)[key]
    }
  })
  dateRange.value = null
  pagination.page = 1
  loadRefunds()
}

const handleDateRangeChange = (dates: [Dayjs, Dayjs] | null) => {
  if (dates) {
    queryParams.startDate = dates[0].format('YYYY-MM-DD')
    queryParams.endDate = dates[1].format('YYYY-MM-DD')
  } else {
    delete queryParams.startDate
    delete queryParams.endDate
  }
}

const showRefundDetail = (refund: Refund) => {
  selectedRefund.value = refund
  showRefundDetailModal.value = true
}

const showRejectModal = (refund: Refund) => {
  selectedRefund.value = refund
  
  // 重置拒绝表单
  rejectForm.reason = ''
  rejectForm.detail = ''
  rejectForm.rejectedBy = ''
  
  showRejectRefundModal.value = true
}

const handleApproveRefund = async (refund: Refund) => {
  processingRefunds.value.add(refund.id)
  try {
    // 这里应该获取当前登录用户信息
    const approvedBy = 'admin' // 实际应用中应该从用户状态获取
    
    const result = await approveRefund(refund.id, approvedBy)
    
    if (result.success) {
      message.success(result.message || '退款已批准')
    } else {
      message.error(result.message || '批准退款失败')
    }
  } catch (error: any) {
    message.error(error.message || '批准退款失败')
  } finally {
    processingRefunds.value.delete(refund.id)
  }
}

const handleRejectRefund = async () => {
  if (!selectedRefund.value) return
  
  try {
    await rejectFormRef.value?.validate()
    
    rejecting.value = true
    
    let reason = rejectForm.reason
    if (rejectForm.reason === '其他原因' && rejectForm.detail) {
      reason = rejectForm.detail
    }
    
    const result = await rejectRefund(selectedRefund.value.id, reason, rejectForm.rejectedBy)
    
    if (result.success) {
      message.success(result.message || '退款已拒绝')
      showRejectRefundModal.value = false
    } else {
      message.error(result.message || '拒绝退款失败')
    }
  } catch (error: any) {
    if (error.errorFields) {
      message.error('请检查表单填写')
    } else {
      message.error(error.message || '拒绝退款失败')
    }
  } finally {
    rejecting.value = false
  }
}

const handleProcessRefund = async (refund: Refund) => {
  processingRefunds.value.add(refund.id)
  try {
    const result = await processRefund(refund.id)
    
    if (result.success) {
      message.success(result.message || '退款处理成功')
    } else {
      message.error(result.message || '退款处理失败')
    }
  } catch (error: any) {
    message.error(error.message || '退款处理失败')
  } finally {
    processingRefunds.value.delete(refund.id)
  }
}

const handleRefundUpdated = () => {
  showRefundDetailModal.value = false
  loadRefunds()
  message.success('退款信息已更新')
}

const viewPayment = (paymentId: string) => {
  // 跳转到支付详情页面或打开支付详情弹窗
  console.log('View payment:', paymentId)
  message.info('跳转到支付详情页面')
}

const downloadRefundReceipt = (refund: Refund) => {
  // 下载退款凭证
  console.log('Download refund receipt:', refund.id)
  message.info('正在生成退款凭证...')
}

// 工具函数
const formatAmount = (amount: Money): string => {
  return `${amount.amount.toFixed(2)} ${amount.currency}`
}

const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const getRefundStatusColor = (status: RefundStatus): string => {
  const colorMap: Record<RefundStatus, string> = {
    pending: 'orange',
    approved: 'blue',
    rejected: 'red',
    completed: 'green',
    failed: 'red'
  }
  return colorMap[status] || 'default'
}

const getRefundStatusText = (status: RefundStatus): string => {
  const textMap: Record<RefundStatus, string> = {
    pending: '待处理',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}
</script>

<style scoped>
.refunds-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 24px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: end;
  margin-bottom: 16px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-item label {
  font-size: 14px;
  color: #666;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.table-card {
  overflow: hidden;
}

.payment-info {
  line-height: 1.4;
}

.amount {
  font-weight: 500;
  color: #1890ff;
}

.reason-text {
  cursor: pointer;
}

.approval-info,
.rejection-info,
.process-info {
  font-size: 12px;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .refunds-view {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
  }
}
</style>