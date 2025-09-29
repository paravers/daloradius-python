<template>
  <div class="payments-view">
    <!-- 页面标题和操作区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">支付管理</h1>
        <div class="header-actions">
          <a-button 
            type="primary"
            @click="showCreatePaymentModal = true"
          >
            <template #icon><PlusOutlined /></template>
            创建支付
          </a-button>
          <a-button @click="refreshData">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="statistics">
      <div class="stats-row">
        <a-card class="stat-card">
          <a-statistic
            title="总支付金额"
            :value="statistics.totalAmount.amount"
            :precision="2"
            suffix="元"
          />
        </a-card>
        <a-card class="stat-card">
          <a-statistic
            title="总支付笔数"
            :value="statistics.totalCount"
          />
        </a-card>
        <a-card class="stat-card">
          <a-statistic
            title="成功支付金额"
            :value="statistics.completedAmount.amount"
            :precision="2"
            suffix="元"
          />
        </a-card>
        <a-card class="stat-card">
          <a-statistic
            title="成功率"
            :value="statistics.conversionRate"
            :precision="2"
            suffix="%"
          />
        </a-card>
      </div>
    </div>

    <!-- 筛选区域 -->
    <a-card class="filter-card">
      <div class="filter-row">
        <div class="filter-item">
          <label>支付号码：</label>
          <a-input
            v-model:value="queryParams.paymentNumber"
            placeholder="请输入支付号码"
            allow-clear
            @press-enter="handleSearch"
          />
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
        <div class="filter-item">
          <label>支付状态：</label>
          <a-select
            v-model:value="queryParams.status"
            placeholder="请选择状态"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="pending">待支付</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="failed">失败</a-select-option>
            <a-select-option value="cancelled">已取消</a-select-option>
            <a-select-option value="refunded">已退款</a-select-option>
            <a-select-option value="partial_refunded">部分退款</a-select-option>
          </a-select>
        </div>
        <div class="filter-item">
          <label>支付方式：</label>
          <a-select
            v-model:value="queryParams.paymentMethodType"
            placeholder="请选择支付方式"
            allow-clear
            style="width: 120px"
          >
            <a-select-option value="alipay">支付宝</a-select-option>
            <a-select-option value="wechat">微信支付</a-select-option>
            <a-select-option value="bank_card">银行卡</a-select-option>
            <a-select-option value="credit_card">信用卡</a-select-option>
            <a-select-option value="bank_transfer">银行转账</a-select-option>
          </a-select>
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

    <!-- 支付列表 -->
    <a-card class="table-card">
      <a-table
        :columns="columns"
        :data-source="payments"
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
          <template v-if="column.key === 'paymentNumber'">
            <a-button type="link" @click="showPaymentDetail(record)">
              {{ record.paymentNumber }}
            </a-button>
          </template>
          
          <template v-else-if="column.key === 'userInfo'">
            <div class="user-info">
              <div>{{ record.userInfo.name }}</div>
              <div class="user-contact">{{ record.userInfo.email }}</div>
            </div>
          </template>
          
          <template v-else-if="column.key === 'amount'">
            <span class="amount">{{ formatAmount(record.amount) }}</span>
          </template>
          
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          
          <template v-else-if="column.key === 'paymentMethodType'">
            <a-tag color="blue">
              {{ getPaymentMethodText(record.paymentMethodType) }}
            </a-tag>
          </template>
          
          <template v-else-if="column.key === 'refundInfo'">
            <div v-if="record.refundedAmount.amount > 0" class="refund-info">
              <div>已退款: {{ formatAmount(record.refundedAmount) }}</div>
              <div>可退款: {{ formatAmount(record.refundableAmount) }}</div>
            </div>
            <div v-else>
              可退款: {{ formatAmount(record.refundableAmount) }}
            </div>
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
                @click="handleProcessPayment(record)"
                :loading="processingPayments.has(record.id)"
              >
                处理支付
              </a-button>
              
              <a-button
                v-if="record.status === 'pending'"
                size="small"
                @click="handleCancelPayment(record)"
              >
                取消
              </a-button>
              
              <a-button
                v-if="record.status === 'failed'"
                type="primary"
                size="small"
                @click="handleRetryPayment(record)"
                :loading="processingPayments.has(record.id)"
              >
                重试
              </a-button>
              
              <a-button
                v-if="canRefund(record)"
                size="small"
                @click="showCreateRefundModal(record)"
              >
                申请退款
              </a-button>
              
              <a-dropdown>
                <template #overlay>
                  <a-menu>
                    <a-menu-item @click="showPaymentDetail(record)">
                      <EyeOutlined /> 查看详情
                    </a-menu-item>
                    <a-menu-item 
                      v-if="['pending', 'failed', 'cancelled'].includes(record.status)"
                      @click="handleDeletePayment(record)"
                    >
                      <DeleteOutlined /> 删除
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

    <!-- 创建支付弹窗 -->
    <PaymentForm
      v-model:visible="showCreatePaymentModal"
      @success="handlePaymentCreated"
    />

    <!-- 支付详情弹窗 -->
    <PaymentDetail
      v-model:visible="showPaymentDetailModal"
      :payment="selectedPayment"
    />

    <!-- 创建退款弹窗 -->
    <RefundForm
      v-model:visible="showCreateRefundModal"
      :payment="selectedPayment"
      @success="handleRefundCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  ClearOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
import type { 
  PaymentRecord, 
  ExtendedPaymentStatus, 
  PaymentMethodType,
  Money
} from '@/types/billing'
import { usePayments } from '@/composables/usePayments'
import PaymentForm from './PaymentForm.vue'
import PaymentDetail from './PaymentDetail.vue'
import RefundForm from './RefundForm.vue'
import type { Dayjs } from 'dayjs'

// 使用 composable
const {
  payments,
  total,
  loading,
  pagination,
  queryParams,
  statistics,
  loadPayments,
  deletePayment,
  processPayment,
  cancelPayment,
  retryPayment,
  loadStatistics,
  setPage,
  setPageSize
} = usePayments()

// 响应式状态
const showCreatePaymentModal = ref(false)
const showPaymentDetailModal = ref(false)
const showRefundModal = ref(false)
const selectedPayment = ref<PaymentRecord>()
const dateRange = ref<[Dayjs, Dayjs] | null>(null)
const processingPayments = ref(new Set<string>())

// 表格列配置
const columns = [
  {
    title: '支付号码',
    dataIndex: 'paymentNumber',
    key: 'paymentNumber',
    width: 180
  },
  {
    title: '用户信息',
    dataIndex: 'userInfo',
    key: 'userInfo',
    width: 200
  },
  {
    title: '金额',
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
    title: '支付方式',
    dataIndex: 'paymentMethodType',
    key: 'paymentMethodType',
    width: 120
  },
  {
    title: '退款信息',
    dataIndex: 'refundInfo',
    key: 'refundInfo',
    width: 150
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 180,
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 240,
    fixed: 'right'
  }
]

// 初始化
onMounted(async () => {
  await Promise.all([
    loadPayments(),
    loadStatistics()
  ])
})

// 方法
const refreshData = async () => {
  await Promise.all([
    loadPayments(),
    loadStatistics()
  ])
  message.success('数据已刷新')
}

const handleSearch = () => {
  pagination.page = 1
  loadPayments()
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
  loadPayments()
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

const showPaymentDetail = (payment: PaymentRecord) => {
  selectedPayment.value = payment
  showPaymentDetailModal.value = true
}

const showCreateRefundModal = (payment: PaymentRecord) => {
  selectedPayment.value = payment
  showRefundModal.value = true
}

const handlePaymentCreated = () => {
  showCreatePaymentModal.value = false
  loadPayments()
  loadStatistics()
  message.success('支付创建成功')
}

const handleRefundCreated = () => {
  showRefundModal.value = false
  loadPayments()
  loadStatistics()
  message.success('退款申请提交成功')
}

const handleProcessPayment = async (payment: PaymentRecord) => {
  processingPayments.value.add(payment.id)
  try {
    const result = await processPayment(payment.id)
    
    if (result.success) {
      message.success(result.message || '支付处理成功')
    } else {
      message.error(result.message || '支付处理失败')
    }
    
    await loadStatistics()
  } catch (error: any) {
    message.error(error.message || '支付处理失败')
  } finally {
    processingPayments.value.delete(payment.id)
  }
}

const handleCancelPayment = (payment: PaymentRecord) => {
  Modal.confirm({
    title: '确认取消支付',
    content: `确定要取消支付 ${payment.paymentNumber} 吗？`,
    onOk: async () => {
      try {
        await cancelPayment(payment.id, '用户取消')
        message.success('支付已取消')
        await loadStatistics()
      } catch (error: any) {
        message.error(error.message || '取消支付失败')
      }
    }
  })
}

const handleRetryPayment = async (payment: PaymentRecord) => {
  processingPayments.value.add(payment.id)
  try {
    const result = await retryPayment(payment.id)
    
    if (result.success) {
      message.success(result.message || '支付重试成功')
    } else {
      message.error(result.message || '支付重试失败')
    }
    
    await loadStatistics()
  } catch (error: any) {
    message.error(error.message || '支付重试失败')
  } finally {
    processingPayments.value.delete(payment.id)
  }
}

const handleDeletePayment = (payment: PaymentRecord) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除支付记录 ${payment.paymentNumber} 吗？`,
    onOk: async () => {
      try {
        await deletePayment(payment.id)
        message.success('支付记录已删除')
        await loadStatistics()
      } catch (error: any) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

// 工具函数
const formatAmount = (amount: Money): string => {
  return `${amount.amount.toFixed(2)} ${amount.currency}`
}

const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const getStatusColor = (status: ExtendedPaymentStatus): string => {
  const colorMap: Record<ExtendedPaymentStatus, string> = {
    pending: 'orange',
    completed: 'green',
    failed: 'red',
    cancelled: 'gray',
    refunded: 'purple',
    partial_refunded: 'cyan'
  }
  return colorMap[status] || 'default'
}

const getStatusText = (status: ExtendedPaymentStatus): string => {
  const textMap: Record<ExtendedPaymentStatus, string> = {
    pending: '待支付',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
    refunded: '已退款',
    partial_refunded: '部分退款'
  }
  return textMap[status] || status
}

const getPaymentMethodText = (method: PaymentMethodType): string => {
  const textMap: Record<PaymentMethodType, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    bank_card: '银行卡',
    credit_card: '信用卡',
    bank_transfer: '银行转账'
  }
  return textMap[method] || method
}

const canRefund = (payment: PaymentRecord): boolean => {
  return payment.status === 'completed' && payment.refundableAmount.amount > 0
}
</script>

<style scoped>
.payments-view {
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

.stats-cards {
  margin-bottom: 24px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  text-align: center;
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

.user-info {
  line-height: 1.4;
}

.user-contact {
  font-size: 12px;
  color: #999;
}

.amount {
  font-weight: 500;
  color: #1890ff;
}

.refund-info {
  font-size: 12px;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .payments-view {
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
  
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>