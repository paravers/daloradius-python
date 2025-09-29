<template>
  <a-drawer
    v-model:open="visible"
    title="退款详情"
    :width="600"
    placement="right"
  >
    <div v-if="refund" class="refund-detail">
      <!-- 退款基本信息 -->
      <a-card class="detail-card" title="基本信息">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="退款号码">
            <a-typography-text copyable>{{ refund.refundNumber }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item label="退款状态">
            <a-tag :color="getRefundStatusColor(refund.status)" class="status-tag">
              {{ getRefundStatusText(refund.status) }}
            </a-tag>
          </a-descriptions-item>
          
          <a-descriptions-item label="退款金额">
            <div class="amount-info">
              <span class="amount-value">{{ formatAmount(refund.amount) }}</span>
            </div>
          </a-descriptions-item>
          
          <a-descriptions-item label="退款原因">
            <div class="reason-content">{{ refund.reason }}</div>
          </a-descriptions-item>
          
          <a-descriptions-item label="申请时间">
            {{ formatDateTime(refund.createdAt) }}
          </a-descriptions-item>
          
          <a-descriptions-item v-if="refund.approvedAt" label="批准时间">
            <span class="approved-time">{{ formatDateTime(refund.approvedAt) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="refund.processedAt" label="处理完成时间">
            <span class="processed-time">{{ formatDateTime(refund.processedAt) }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 关联支付信息 -->
      <a-card class="detail-card" title="关联支付信息">
        <div v-if="paymentInfo" class="payment-section">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="支付ID">
              <a-typography-text copyable>{{ refund.paymentId }}</a-typography-text>
            </a-descriptions-item>
            
            <a-descriptions-item label="支付号码">
              <a-button type="link" @click="viewPayment(refund.paymentId)">
                {{ paymentInfo.paymentNumber }}
              </a-button>
            </a-descriptions-item>
            
            <a-descriptions-item label="支付金额">
              {{ formatAmount(paymentInfo.amount) }}
            </a-descriptions-item>
            
            <a-descriptions-item label="支付状态">
              <a-tag :color="getPaymentStatusColor(paymentInfo.status)">
                {{ getPaymentStatusText(paymentInfo.status) }}
              </a-tag>
            </a-descriptions-item>
            
            <a-descriptions-item label="支付方式">
              <div class="payment-method">
                <span class="method-icon">{{ getPaymentMethodIcon(paymentInfo.paymentMethodType) }}</span>
                <span>{{ getPaymentMethodText(paymentInfo.paymentMethodType) }}</span>
              </div>
            </a-descriptions-item>
            
            <a-descriptions-item label="用户信息">
              <div class="user-info">
                <div>{{ paymentInfo.userInfo.name }}</div>
                <div class="user-contact">{{ paymentInfo.userInfo.email }}</div>
              </div>
            </a-descriptions-item>
          </a-descriptions>
        </div>
        <div v-else class="loading-payment">
          <a-spin size="small" />
          <span>加载支付信息...</span>
        </div>
      </a-card>

      <!-- 审批信息 -->
      <a-card 
        v-if="showApprovalInfo" 
        class="detail-card" 
        title="审批信息"
      >
        <a-descriptions :column="1" bordered>
          <a-descriptions-item v-if="refund.approvedBy" label="批准人">
            {{ refund.approvedBy }}
          </a-descriptions-item>
          
          <a-descriptions-item v-if="refund.approvedAt" label="批准时间">
            <span class="approved-time">{{ formatDateTime(refund.approvedAt) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="refund.rejectedReason" label="拒绝原因">
            <a-typography-text type="danger">{{ refund.rejectedReason }}</a-typography-text>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 处理信息 -->
      <a-card 
        v-if="showProcessInfo" 
        class="detail-card" 
        title="处理信息"
      >
        <a-descriptions :column="1" bordered>
          <a-descriptions-item v-if="refund.gatewayRefundId" label="网关退款ID">
            <a-typography-text copyable>{{ refund.gatewayRefundId }}</a-typography-text>
          </a-descriptions-item>
          
          <a-descriptions-item v-if="refund.processedAt" label="处理时间">
            <span class="processed-time">{{ formatDateTime(refund.processedAt) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item label="通知状态">
            <a-tag :color="refund.notificationSent ? 'green' : 'orange'">
              {{ refund.notificationSent ? '已通知' : '未通知' }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 扩展信息 -->
      <a-card 
        v-if="refund.metadata && Object.keys(refund.metadata).length > 0" 
        class="detail-card" 
        title="扩展信息"
      >
        <a-descriptions :column="1" bordered>
          <a-descriptions-item 
            v-for="[key, value] in Object.entries(refund.metadata)" 
            :key="key"
            :label="formatMetadataKey(key)"
          >
            <div v-if="isSpecialMetadata(key)" class="special-metadata">
              {{ formatMetadataValue(key, value) }}
            </div>
            <span v-else>{{ value }}</span>
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
              <div class="timeline-title">退款申请创建</div>
              <div class="timeline-desc">用户申请退款: {{ formatAmount(refund.amount) }}</div>
              <div class="timeline-time">{{ formatDateTime(refund.createdAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="refund.status === 'approved' || refund.status === 'completed'" 
            color="blue"
          >
            <template #dot>
              <CheckCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">退款批准</div>
              <div v-if="refund.approvedBy" class="timeline-desc">批准人: {{ refund.approvedBy }}</div>
              <div class="timeline-time">{{ formatDateTime(refund.approvedAt || refund.updatedAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="refund.status === 'rejected'" 
            color="red"
          >
            <template #dot>
              <ExclamationCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">退款拒绝</div>
              <div v-if="refund.rejectedReason" class="timeline-desc">拒绝原因: {{ refund.rejectedReason }}</div>
              <div class="timeline-time">{{ formatDateTime(refund.updatedAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="refund.status === 'completed'" 
            color="green"
          >
            <template #dot>
              <DollarCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">退款完成</div>
              <div v-if="refund.gatewayRefundId" class="timeline-desc">网关退款ID: {{ refund.gatewayRefundId }}</div>
              <div class="timeline-time">{{ formatDateTime(refund.processedAt || refund.updatedAt) }}</div>
            </div>
          </a-timeline-item>
          
          <a-timeline-item 
            v-if="refund.status === 'failed'" 
            color="red"
          >
            <template #dot>
              <MinusCircleOutlined />
            </template>
            <div class="timeline-content">
              <div class="timeline-title">退款失败</div>
              <div class="timeline-time">{{ formatDateTime(refund.updatedAt) }}</div>
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
            v-if="refund?.status === 'pending'"
            type="primary"
            @click="handleApproveRefund"
            :loading="processing"
          >
            批准退款
          </a-button>
          
          <a-button
            v-if="refund?.status === 'pending'"
            @click="showRejectModal"
          >
            拒绝退款
          </a-button>
          
          <a-button
            v-if="refund?.status === 'approved'"
            type="primary"
            @click="handleProcessRefund"
            :loading="processing"
          >
            处理退款
          </a-button>
          
          <a-button
            v-if="refund?.status === 'completed'"
            @click="handleDownloadReceipt"
          >
            下载凭证
          </a-button>
          
          <a-button
            v-if="refund?.paymentId"
            @click="viewPayment(refund.paymentId)"
          >
            查看支付
          </a-button>
        </a-space>
      </div>
    </template>

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
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  DollarCircleOutlined,
  MinusCircleOutlined
} from '@ant-design/icons-vue'
import type { 
  Refund, 
  PaymentRecord,
  RefundStatus,
  ExtendedPaymentStatus,
  PaymentMethodType,
  Money
} from '@/types/billing'
import type { FormInstance } from 'ant-design-vue'
import { useRefunds, usePayments } from '@/composables/usePayments'

// Props
interface Props {
  visible: boolean
  refund?: Refund
}

const props = withDefaults(defineProps<Props>(), {
  refund: undefined
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success?: []
}>()

// Composables
const { approveRefund, rejectRefund, processRefund } = useRefunds()
const { getPayment } = usePayments()

// 响应式状态
const processing = ref(false)
const rejecting = ref(false)
const showRejectRefundModal = ref(false)
const rejectFormRef = ref<FormInstance>()
const paymentInfo = ref<PaymentRecord>()

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

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const showApprovalInfo = computed(() => {
  if (!props.refund) return false
  return ['approved', 'rejected', 'completed'].includes(props.refund.status)
})

const showProcessInfo = computed(() => {
  if (!props.refund) return false
  return ['completed', 'failed'].includes(props.refund.status)
})

// 监听弹窗显示
watch(() => props.visible, (newVal) => {
  if (newVal && props.refund) {
    loadRelatedData()
  }
})

// 方法
const loadRelatedData = async () => {
  if (!props.refund) return
  
  try {
    // 加载关联支付信息
    paymentInfo.value = await getPayment(props.refund.paymentId)
  } catch (error) {
    console.error('Load payment info error:', error)
  }
}

const handleApproveRefund = async () => {
  if (!props.refund) return
  
  try {
    processing.value = true
    
    // 这里应该获取当前登录用户信息
    const approvedBy = 'admin' // 实际应用中应该从用户状态获取
    
    const result = await approveRefund(props.refund.id, approvedBy)
    
    if (result.success) {
      message.success(result.message || '退款已批准')
      emit('success')
    } else {
      message.error(result.message || '批准退款失败')
    }
  } catch (error: any) {
    message.error(error.message || '批准退款失败')
  } finally {
    processing.value = false
  }
}

const showRejectModal = () => {
  // 重置拒绝表单
  rejectForm.reason = ''
  rejectForm.detail = ''
  rejectForm.rejectedBy = ''
  
  showRejectRefundModal.value = true
}

const handleRejectRefund = async () => {
  if (!props.refund) return
  
  try {
    await rejectFormRef.value?.validate()
    
    rejecting.value = true
    
    let reason = rejectForm.reason
    if (rejectForm.reason === '其他原因' && rejectForm.detail) {
      reason = rejectForm.detail
    }
    
    const result = await rejectRefund(props.refund.id, reason, rejectForm.rejectedBy)
    
    if (result.success) {
      message.success(result.message || '退款已拒绝')
      showRejectRefundModal.value = false
      emit('success')
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

const handleProcessRefund = async () => {
  if (!props.refund) return
  
  try {
    processing.value = true
    const result = await processRefund(props.refund.id)
    
    if (result.success) {
      message.success(result.message || '退款处理成功')
      emit('success')
    } else {
      message.error(result.message || '退款处理失败')
    }
  } catch (error: any) {
    message.error(error.message || '退款处理失败')
  } finally {
    processing.value = false
  }
}

const handleDownloadReceipt = () => {
  if (!props.refund) return
  
  // 下载退款凭证
  console.log('Download refund receipt:', props.refund.id)
  message.info('正在生成退款凭证...')
}

const viewPayment = (paymentId: string) => {
  // 跳转到支付详情页面或打开支付详情弹窗
  console.log('View payment:', paymentId)
  message.info('跳转到支付详情页面')
}

// 工具函数
const formatAmount = (amount: Money): string => {
  return `${amount.amount.toFixed(2)} ${amount.currency}`
}

const formatDateTime = (dateTime: string): string => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const formatMetadataKey = (key: string): string => {
  const keyMap: Record<string, string> = {
    refundMethod: '退款方式',
    priority: '紧急程度',
    notifyUser: '用户通知',
    internalNote: '内部备注',
    refundAccount: '退款账户'
  }
  return keyMap[key] || key
}

const isSpecialMetadata = (key: string): boolean => {
  return ['refundMethod', 'priority', 'notifyUser'].includes(key)
}

const formatMetadataValue = (key: string, value: any): string => {
  if (key === 'refundMethod') {
    return value === 'original' ? '原路退回' : '人工退款'
  }
  
  if (key === 'priority') {
    const priorityMap: Record<string, string> = {
      low: '低优先级',
      normal: '普通',
      high: '高优先级',
      urgent: '紧急'
    }
    return priorityMap[value] || value
  }
  
  if (key === 'notifyUser') {
    return value ? '是' : '否'
  }
  
  return String(value)
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

const getPaymentStatusColor = (status: ExtendedPaymentStatus): string => {
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

const getPaymentStatusText = (status: ExtendedPaymentStatus): string => {
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
</script>

<style scoped>
.refund-detail {
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

.reason-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.approved-time {
  color: #52c41a;
  font-weight: 500;
}

.processed-time {
  color: #1890ff;
  font-weight: 500;
}

.payment-section {
  margin-top: 8px;
}

.loading-payment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  text-align: center;
  color: #666;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 8px;
}

.method-icon {
  font-size: 16px;
}

.user-info {
  line-height: 1.4;
}

.user-contact {
  font-size: 12px;
  color: #999;
}

.special-metadata {
  font-weight: 500;
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