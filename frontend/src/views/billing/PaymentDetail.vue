<template>
  <a-drawer
    v-model:open="visible"
    title="支付详情"
    :width="600"
    placement="right"
  >
    <div v-if="payment" class="payment-detail">
      <!-- 支付基本信息 -->
      <a-card class="detail-card" title="基本信息">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="支付号码">
            <a-typography-text copyable>{{ payment.paymentNumber }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付状态">
            <a-tag :color="getStatusColor(payment.status)" class="status-tag">
              {{ getStatusText(payment.status) }}
            </a-tag>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付金额">
            <div class="amount-info">
              <span class="amount-value">{{ formatAmount(payment.amount) }}</span>
            </div>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付方式">
            <div class="payment-method">
              <span class="method-icon">{{ getPaymentMethodIcon(payment.paymentMethodType) }}</span>
              <span>{{ getPaymentMethodText(payment.paymentMethodType) }}</span>
            </div>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付网关">
            <a-tag color="blue">{{ getGatewayText(payment.gatewayType) }}</a-tag>
          </a-descriptions-item>
          
          <a-descriptions-item label="创建时间">
            {{ formatDateTime(payment.createdAt) }}
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.paidAt" label="支付时间">
            <span class="paid-time">{{ formatDateTime(payment.paidAt) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.expiredAt" label="过期时间">
            <span :class="{ 'expired': isExpired(payment.expiredAt) }">
              {{ formatDateTime(payment.expiredAt) }}
            </span>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 用户信息 -->
      <a-card class="detail-card" title="用户信息">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="用户ID">
            <a-typography-text copyable>{{ payment.userId }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item label="用户姓名">
            {{ payment.userInfo.name }}
          </a-descriptions-item>
          
          <a-descriptions-item label="用户邮箱">
            <a-typography-text copyable>{{ payment.userInfo.email }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.userInfo.phone" label="用户手机">
            <a-typography-text copyable>{{ payment.userInfo.phone }}</a-typography-text>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 交易信息 -->
      <a-card class="detail-card" title="交易信息">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item v-if="payment.invoiceId" label="关联发票">
            <a-button type="link" @click="viewInvoice(payment.invoiceId)">
              {{ payment.invoiceId }}
            </a-button>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.transactionId" label="交易ID">
            <a-typography-text copyable>{{ payment.transactionId }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.gatewayTransactionId" label="网关交易ID">
            <a-typography-text copyable>{{ payment.gatewayTransactionId }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.description" label="支付描述">
            {{ payment.description }}
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.failureReason" label="失败原因">
            <a-typography-text type="danger">{{ payment.failureReason }}</a-typography-text>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 退款信息 -->
      <a-card 
        v-if="showRefundInfo" 
        class="detail-card" 
        title="退款信息"
      >
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="可退金额">
            <span class="refundable-amount">{{ formatAmount(payment.refundableAmount) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="payment.refundedAmount.amount > 0" label="已退金额">
            <span class="refunded-amount">{{ formatAmount(payment.refundedAmount) }}</span>
          </a-descriptions-item>
        </a-descriptions>
        
        <!-- 退款记录 -->
        <div v-if="refunds.length > 0" class="refund-records">
          <a-divider>退款记录</a-divider>
          <a-list item-layout="horizontal" :data-source="refunds">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <div class="refund-title">
                      <span>{{ item.refundNumber }}</span>
                      <a-tag :color="getRefundStatusColor(item.status)">
                        {{ getRefundStatusText(item.status) }}
                      </a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="refund-desc">
                      <div>金额: {{ formatAmount(item.amount) }}</div>
                      <div>原因: {{ item.reason }}</div>
                      <div>申请时间: {{ formatDateTime(item.createdAt) }}</div>
                    </div>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-card>

      <!-- 扩展信息 -->
      <a-card 
        v-if="payment.metadata && Object.keys(payment.metadata).length > 0" 
        class="detail-card" 
        title="扩展信息"
      >
        <a-descriptions :column="1" bordered>
          <a-descriptions-item 
            v-for="[key, value] in Object.entries(payment.metadata)" 
            :key="key"
            :label="key"
          >
            {{ value }}
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 操作历史 -->
      <a-card class="detail-card" title="操作历史">
        <a-timeline>
          <a-timeline-item color="green">
            <template #dot>
              <PlusCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">支付创建</div>
              <div class="timeline-time">{{ formatDateTime(payment.createdAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="payment.paidAt" 
            color="blue"
          >
            <template #dot>
              <CheckCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">支付完成</div>
              <div class="timeline-time">{{ formatDateTime(payment.paidAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="payment.status === 'failed' && payment.failureReason" 
            color="red"
          >
            <template #dot>
              <ExclamationCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">支付失败</div>
              <div class="timeline-desc">{{ payment.failureReason }}</div>
              <div class="timeline-time">{{ formatDateTime(payment.updatedAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="payment.status === 'cancelled'" 
            color="gray"
          >
            <template #dot>
              <MinusCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">支付取消</div>
              <div class="timeline-time">{{ formatDateTime(payment.updatedAt) }}</div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </a-card>
    </div>

    <!-- 操作按钮 -->
    <template #footer>
      <div class="drawer-footer">
        <a-space>
          <a-button @click="visible = false">关闭</a-button>
          
          <a-button
            v-if="payment?.status === 'pending'"
            type="primary"
            @click="handleProcessPayment"
            :loading="processing"
          >
            处理支付
          </a-button>
          
          <a-button
            v-if="payment?.status === 'pending'"
            @click="handleCancelPayment"
          >
            取消支付
          </a-button>
          
          <a-button
            v-if="payment?.status === 'failed'"
            type="primary"
            @click="handleRetryPayment"
            :loading="processing"
          >
            重试支付
          </a-button>
          
          <a-button
            v-if="canRefund"
            @click="showCreateRefundModal"
          >
            申请退款
          </a-button>
          
          <a-button
            v-if="canEdit"
            @click="showEditModal"
          >
            编辑
          </a-button>
        </a-space>
      </div>
    </template>

    <!-- 编辑支付弹窗 -->
    <PaymentForm
      v-model:visible="showEditPaymentModal"
      :payment="payment"
      @success="handlePaymentUpdated"
    />

    <!-- 创建退款弹窗 -->
    <RefundForm
      v-model:visible="showRefundModal"
      :payment="payment"
      @success="handleRefundCreated"
    />
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons-vue'
import type { 
  PaymentRecord, 
  Refund,
  ExtendedPaymentStatus,
  RefundStatus,
  PaymentMethodType,
  PaymentGatewayType,
  Money
} from '@/types/billing'
import { usePayments, useRefunds } from '@/composables/usePayments'
import PaymentForm from './PaymentForm.vue'
import RefundForm from './RefundForm.vue'

// Props
interface Props {
  visible: boolean
  payment?: PaymentRecord
}

const props = withDefaults(defineProps<Props>(), {
  payment: undefined
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success?: []
}>()

// Composables
const { processPayment, cancelPayment, retryPayment } = usePayments()
const { loadRefunds, refunds } = useRefunds()

// 响应式状态
const processing = ref(false)
const showEditPaymentModal = ref(false)
const showRefundModal = ref(false)

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const showRefundInfo = computed(() => {
  if (!props.payment) return false
  return ['completed', 'refunded', 'partial_refunded'].includes(props.payment.status)
})

const canRefund = computed(() => {
  if (!props.payment) return false
  return props.payment.status === 'completed' && props.payment.refundableAmount.amount > 0
})

const canEdit = computed(() => {
  if (!props.payment) return false
  return ['pending', 'failed'].includes(props.payment.status)
})

// 监听弹窗显示
watch(() => props.visible, (newVal) => {
  if (newVal && props.payment) {
    loadRelatedData()
  }
})

// 方法
const loadRelatedData = async () => {
  if (!props.payment) return
  
  try {
    // 加载相关退款记录
    await loadRefunds({
      paymentId: props.payment.id,
      page: 1,
      pageSize: 20
    })
  } catch (error) {
    console.error('Load related data error:', error)
  }
}

const handleProcessPayment = async () => {
  if (!props.payment) return
  
  try {
    processing.value = true
    const result = await processPayment(props.payment.id)
    
    if (result.success) {
      message.success(result.message || '支付处理成功')
      emit('success')
    } else {
      message.error(result.message || '支付处理失败')
    }
  } catch (error: any) {
    message.error(error.message || '支付处理失败')
  } finally {
    processing.value = false
  }
}

const handleCancelPayment = () => {
  if (!props.payment) return
  
  Modal.confirm({
    title: '确认取消支付',
    content: '确定要取消这笔支付吗？',
    onOk: async () => {
      try {
        await cancelPayment(props.payment!.id, '管理员取消')
        message.success('支付已取消')
        emit('success')
      } catch (error: any) {
        message.error(error.message || '取消支付失败')
      }
    }
  })
}

const handleRetryPayment = async () => {
  if (!props.payment) return
  
  try {
    processing.value = true
    const result = await retryPayment(props.payment.id)
    
    if (result.success) {
      message.success(result.message || '支付重试成功')
      emit('success')
    } else {
      message.error(result.message || '支付重试失败')
    }
  } catch (error: any) {
    message.error(error.message || '支付重试失败')
  } finally {
    processing.value = false
  }
}

const showEditModal = () => {
  showEditPaymentModal.value = true
}

const showCreateRefundModal = () => {
  showRefundModal.value = true
}

const handlePaymentUpdated = () => {
  showEditPaymentModal.value = false
  message.success('支付更新成功')
  emit('success')
}

const handleRefundCreated = () => {
  showRefundModal.value = false
  message.success('退款申请已提交')
  loadRelatedData() // 重新加载退款记录
  emit('success')
}

const viewInvoice = (invoiceId: string) => {
  // 跳转到发票详情页面
  // 这里可以使用路由跳转
  console.log('View invoice:', invoiceId)
  message.info('跳转到发票详情页面')
}

// 工具函数
const formatAmount = (amount: Money): string => {
  return `${amount.amount.toFixed(2)} ${amount.currency}`
}

const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const isExpired = (expiredAt: string): boolean => {
  return new Date(expiredAt) < new Date()
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

const getPaymentMethodIcon = (method: PaymentMethodType): string => {
  const iconMap: Record<PaymentMethodType, string> = {
    alipay: '💰',
    wechat: '💚',
    bank_card: '💳',
    credit_card: '💎',
    bank_transfer: '🏦'
  }
  return iconMap[method] || '💳'
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

const getGatewayText = (gateway: PaymentGatewayType): string => {
  const textMap: Record<PaymentGatewayType, string> = {
    alipay: '支付宝官方',
    wechat: '微信支付官方',
    unionpay: '银联',
    stripe: 'Stripe'
  }
  return textMap[gateway] || gateway
}
</script>

<style scoped>
.payment-detail {
  padding: 0;
}

.detail-card {
  margin-bottom: 16px;
}

.detail-card:last-child {
  margin-bottom: 0;
}

.status-tag {
  font-weight: 500;
}

.amount-info {
  display: flex;
  align-items: center;
}

.amount-value {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 8px;
}

.method-icon {
  font-size: 16px;
}

.paid-time {
  color: #52c41a;
  font-weight: 500;
}

.expired {
  color: #ff4d4f;
}

.refundable-amount {
  color: #1890ff;
  font-weight: 500;
}

.refunded-amount {
  color: #ff4d4f;
  font-weight: 500;
}

.refund-records {
  margin-top: 16px;
}

.refund-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.refund-desc {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.timeline-content {
  padding-left: 8px;
}

.timeline-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.timeline-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.timeline-time {
  color: #999;
  font-size: 12px;
}

.drawer-footer {
  border-top: 1px solid #e8e8e8;
  padding: 16px 24px;
  text-align: right;
  background: #fff;
}
</style>