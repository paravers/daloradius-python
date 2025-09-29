<template>
  <a-modal
    v-model:open="visible"
    :title="isEdit ? '编辑退款' : '申请退款'"
    :width="600"
    :confirm-loading="loading"
    @ok="handleSubmit"
    @cancel="handleCancel"
  >
    <div v-if="payment" class="refund-form">
      <!-- 支付信息展示 -->
      <a-card class="payment-info-card" size="small">
        <template #title>
          <span>原支付信息</span>
        </template>
        
        <a-descriptions :column="2" size="small">
          <a-descriptions-item label="支付号码">
            {{ payment.paymentNumber }}
          </a-descriptions-item>
          
          <a-descriptions-item label="支付金额">
            <span class="original-amount">{{ formatAmount(payment.amount) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付状态">
            <a-tag :color="getStatusColor(payment.status)">
              {{ getStatusText(payment.status) }}
            </a-tag>
          </a-descriptions-item>
          
          <a-descriptions-item label="支付时间">
            {{ payment.paidAt ? formatDateTime(payment.paidAt) : '未支付' }}
          </a-descriptions-item>
          
          <a-descriptions-item label="可退金额">
            <span class="refundable-amount">{{ formatAmount(payment.refundableAmount) }}</span>
          </a-descriptions-item>
          
          <a-descriptions-item label="已退金额">
            <span class="refunded-amount">{{ formatAmount(payment.refundedAmount) }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 退款表单 -->
      <a-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
        class="refund-form-content"
      >
        <a-form-item label="退款金额" name="amount">
          <div class="amount-input">
            <a-input-number
              v-model:value="formData.amount.amount"
              placeholder="请输入退款金额"
              :min="0.01"
              :max="payment.refundableAmount.amount"
              :precision="2"
              style="flex: 1"
            />
            <a-select
              v-model:value="formData.amount.currency"
              style="width: 80px; margin-left: 8px"
              disabled
            >
              <a-select-option value="CNY">CNY</a-select-option>
              <a-select-option value="USD">USD</a-select-option>
              <a-select-option value="EUR">EUR</a-select-option>
            </a-select>
          </div>
          <div class="amount-tips">
            <a-space>
              <a-button 
                type="link" 
                size="small"
                @click="setRefundAmount(payment.refundableAmount.amount * 0.5)"
              >
                50%
              </a-button>
              <a-button 
                type="link" 
                size="small"
                @click="setRefundAmount(payment.refundableAmount.amount)"
              >
                全额
              </a-button>
            </a-space>
          </div>
        </a-form-item>

        <a-form-item label="退款原因" name="reason">
          <a-select
            v-model:value="formData.reason"
            placeholder="请选择退款原因"
            allow-clear
          >
            <a-select-option value="用户申请退款">用户申请退款</a-select-option>
            <a-select-option value="服务质量问题">服务质量问题</a-select-option>
            <a-select-option value="重复扣费">重复扣费</a-select-option>
            <a-select-option value="系统错误">系统错误</a-select-option>
            <a-select-option value="商品问题">商品问题</a-select-option>
            <a-select-option value="其他原因">其他原因</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item v-if="formData.reason === '其他原因'" label="详细说明" name="detailReason">
          <a-textarea
            v-model:value="formData.detailReason"
            placeholder="请详细说明退款原因"
            :rows="3"
            show-count
            :maxlength="500"
          />
        </a-form-item>

        <a-form-item label="退款方式" name="refundMethod">
          <a-radio-group v-model:value="formData.refundMethod">
            <a-radio value="original">原路退回</a-radio>
            <a-radio value="manual">人工退款</a-radio>
          </a-radio-group>
          <div class="refund-method-tip">
            <a-typography-text type="secondary">
              {{ refundMethodTip }}
            </a-typography-text>
          </div>
        </a-form-item>

        <a-form-item v-if="formData.refundMethod === 'manual'" label="退款账户" name="refundAccount">
          <a-input
            v-model:value="formData.refundAccount"
            placeholder="请输入退款账户信息"
          />
        </a-form-item>

        <a-form-item label="紧急程度" name="priority">
          <a-select v-model:value="formData.priority" placeholder="请选择紧急程度">
            <a-select-option value="low">
              <div class="priority-option">
                <a-tag color="green">低</a-tag>
                <span>3-5个工作日</span>
              </div>
            </a-select-option>
            <a-select-option value="normal">
              <div class="priority-option">
                <a-tag color="blue">普通</a-tag>
                <span>1-3个工作日</span>
              </div>
            </a-select-option>
            <a-select-option value="high">
              <div class="priority-option">
                <a-tag color="orange">高</a-tag>
                <span>24小时内</span>
              </div>
            </a-select-option>
            <a-select-option value="urgent">
              <div class="priority-option">
                <a-tag color="red">紧急</a-tag>
                <span>立即处理</span>
              </div>
            </a-select-option>
          </a-select>
        </a-form-item>

        <!-- 高级选项 -->
        <a-form-item>
          <a-checkbox v-model:checked="showAdvanced">
            显示高级选项
          </a-checkbox>
        </a-form-item>

        <template v-if="showAdvanced">
          <a-form-item label="通知用户" name="notifyUser">
            <a-checkbox v-model:checked="formData.notifyUser">
              退款处理完成后通知用户
            </a-checkbox>
          </a-form-item>

          <a-form-item label="内部备注" name="internalNote">
            <a-textarea
              v-model:value="formData.internalNote"
              placeholder="内部处理备注（用户不可见）"
              :rows="2"
              show-count
              :maxlength="200"
            />
          </a-form-item>

          <a-form-item label="扩展信息" name="metadata">
            <div class="metadata-editor">
              <div 
                v-for="(item, index) in metadataList" 
                :key="index" 
                class="metadata-item"
              >
                <a-input
                  v-model:value="item.key"
                  placeholder="键"
                  style="flex: 1"
                />
                <a-input
                  v-model:value="item.value"
                  placeholder="值"
                  style="flex: 1; margin-left: 8px"
                />
                <a-button
                  type="text"
                  danger
                  @click="removeMetadata(index)"
                  style="margin-left: 8px"
                >
                  <template #icon><DeleteOutlined /></template>
                </a-button>
              </div>
              <a-button
                type="dashed"
                block
                @click="addMetadata"
                style="margin-top: 8px"
              >
                <template #icon><PlusOutlined /></template>
                添加扩展信息
              </a-button>
            </div>
          </a-form-item>
        </template>
      </a-form>

      <!-- 退款预览 -->
      <a-card class="refund-preview-card" size="small">
        <template #title>
          <span>退款预览</span>
        </template>
        
        <div class="refund-preview">
          <div class="preview-item">
            <span class="preview-label">退款金额：</span>
            <span class="preview-value amount-value">
              {{ formatAmount(formData.amount) }}
            </span>
          </div>
          
          <div class="preview-item">
            <span class="preview-label">退款原因：</span>
            <span class="preview-value">
              {{ getFullReason() }}
            </span>
          </div>
          
          <div class="preview-item">
            <span class="preview-label">退款方式：</span>
            <span class="preview-value">
              {{ formData.refundMethod === 'original' ? '原路退回' : '人工退款' }}
            </span>
          </div>
          
          <div class="preview-item">
            <span class="preview-label">处理时效：</span>
            <span class="preview-value">
              {{ getPriorityText(formData.priority) }}
            </span>
          </div>
        </div>
      </a-card>

      <!-- 重要提示 -->
      <a-alert
        type="warning"
        show-icon
        class="refund-warning"
      >
        <template #message>
          <div class="warning-content">
            <div>退款注意事项：</div>
            <ul>
              <li>退款申请提交后不可撤销，请确认退款信息</li>
              <li>原路退回通常需要3-7个工作日到账</li>
              <li>人工退款需要提供准确的账户信息</li>
              <li>部分支付方式可能存在手续费</li>
            </ul>
          </div>
        </template>
      </a-alert>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import type { FormInstance } from 'ant-design-vue'
import type { 
  PaymentRecord,
  Refund,
  RefundRequest,
  ExtendedPaymentStatus,
  Money
} from '@/types/billing'
import { paymentService } from '@/services/paymentService'

// Props
interface Props {
  visible: boolean
  payment?: PaymentRecord
  refund?: Refund
}

const props = withDefaults(defineProps<Props>(), {
  payment: undefined,
  refund: undefined
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式状态
const formRef = ref<FormInstance>()
const loading = ref(false)
const showAdvanced = ref(false)

// 表单数据
const formData = reactive<RefundRequest & {
  refundMethod: string
  refundAccount: string
  priority: string
  notifyUser: boolean
  internalNote: string
  detailReason: string
}>({
  paymentId: '',
  amount: {
    amount: 0,
    currency: 'CNY'
  },
  reason: '',
  refundMethod: 'original',
  refundAccount: '',
  priority: 'normal',
  notifyUser: true,
  internalNote: '',
  detailReason: '',
  metadata: {}
})

// 元数据编辑器
const metadataList = ref<Array<{ key: string; value: string }>>([])

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isEdit = computed(() => !!props.refund)

const refundMethodTip = computed(() => {
  if (formData.refundMethod === 'original') {
    return '退款将按原支付方式退回到原账户'
  } else {
    return '需要手动处理退款，请填写退款账户信息'
  }
})

// 表单验证规则
const rules = {
  amount: [
    { required: true, message: '请输入退款金额' },
    { 
      validator: (_rule: any, value: Money) => {
        if (!value || value.amount <= 0) {
          return Promise.reject('退款金额必须大于0')
        }
        if (props.payment && value.amount > props.payment.refundableAmount.amount) {
          return Promise.reject('退款金额不能超过可退金额')
        }
        return Promise.resolve()
      }
    }
  ],
  reason: [
    { required: true, message: '请选择退款原因' }
  ],
  detailReason: [
    { 
      validator: (_rule: any, value: string) => {
        if (formData.reason === '其他原因' && (!value || value.trim().length < 10)) {
          return Promise.reject('请详细说明退款原因，至少10个字符')
        }
        return Promise.resolve()
      }
    }
  ],
  refundMethod: [
    { required: true, message: '请选择退款方式' }
  ],
  refundAccount: [
    { 
      validator: (_rule: any, value: string) => {
        if (formData.refundMethod === 'manual' && (!value || value.trim().length < 5)) {
          return Promise.reject('请填写退款账户信息')
        }
        return Promise.resolve()
      }
    }
  ],
  priority: [
    { required: true, message: '请选择紧急程度' }
  ]
}

// 监听弹窗显示
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
    
    if (props.payment) {
      loadPaymentData()
    }
    
    if (props.refund) {
      loadRefundData()
    }
  }
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    paymentId: '',
    amount: {
      amount: 0,
      currency: 'CNY'
    },
    reason: '',
    refundMethod: 'original',
    refundAccount: '',
    priority: 'normal',
    notifyUser: true,
    internalNote: '',
    detailReason: '',
    metadata: {}
  })
  
  metadataList.value = []
  showAdvanced.value = false
  
  formRef.value?.clearValidate()
}

const loadPaymentData = () => {
  if (!props.payment) return
  
  formData.paymentId = props.payment.id
  formData.amount.currency = props.payment.amount.currency
  
  // 默认设置为可退金额
  formData.amount.amount = props.payment.refundableAmount.amount
}

const loadRefundData = () => {
  if (!props.refund) return
  
  const refund = props.refund
  
  Object.assign(formData, {
    paymentId: refund.paymentId,
    amount: { ...refund.amount },
    reason: refund.reason,
    metadata: refund.metadata || {}
  })
  
  // 转换元数据
  metadataList.value = Object.entries(refund.metadata || {}).map(([key, value]) => ({
    key,
    value: String(value)
  }))
}

const setRefundAmount = (amount: number) => {
  formData.amount.amount = amount
}

const addMetadata = () => {
  metadataList.value.push({ key: '', value: '' })
}

const removeMetadata = (index: number) => {
  metadataList.value.splice(index, 1)
}

const getFullReason = (): string => {
  let reason = formData.reason || '未选择'
  if (formData.reason === '其他原因' && formData.detailReason) {
    reason = formData.detailReason
  }
  return reason
}

const getPriorityText = (priority: string): string => {
  const priorityMap: Record<string, string> = {
    low: '3-5个工作日',
    normal: '1-3个工作日',
    high: '24小时内',
    urgent: '立即处理'
  }
  return priorityMap[priority] || '普通'
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    loading.value = true
    
    // 构建元数据对象
    const metadata: Record<string, any> = {}
    metadataList.value.forEach(item => {
      if (item.key.trim() && item.value.trim()) {
        metadata[item.key.trim()] = item.value.trim()
      }
    })
    
    // 添加表单特有数据到元数据
    metadata.refundMethod = formData.refundMethod
    metadata.priority = formData.priority
    metadata.notifyUser = formData.notifyUser
    
    if (formData.refundAccount) {
      metadata.refundAccount = formData.refundAccount
    }
    
    if (formData.internalNote) {
      metadata.internalNote = formData.internalNote
    }
    
    // 准备提交数据
    const submitData: RefundRequest = {
      paymentId: formData.paymentId,
      amount: formData.amount,
      reason: getFullReason(),
      metadata
    }
    
    const result = await paymentService.createRefund(submitData)
    
    if (result.success) {
      message.success('退款申请提交成功')
      emit('success')
    } else {
      message.error(result.message || '退款申请提交失败')
    }
  } catch (error: any) {
    console.error('Submit refund error:', error)
    if (error.errorFields) {
      // 表单验证错误
      message.error('请检查表单填写')
    } else {
      message.error(error.message || '操作失败')
    }
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  visible.value = false
}

// 工具函数
const formatAmount = (amount: Money): string => {
  if (!amount || amount.amount === 0) return '0.00 CNY'
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
</script>

<style scoped>
.refund-form {
  padding: 0;
}

.payment-info-card {
  margin-bottom: 16px;
  background: #fafafa;
}

.original-amount {
  font-weight: 600;
  color: #1890ff;
}

.refundable-amount {
  font-weight: 600;
  color: #52c41a;
}

.refunded-amount {
  font-weight: 600;
  color: #ff4d4f;
}

.refund-form-content {
  margin-bottom: 16px;
}

.amount-input {
  display: flex;
  align-items: center;
}

.amount-tips {
  margin-top: 8px;
}

.refund-method-tip {
  margin-top: 4px;
}

.priority-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.metadata-editor {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 12px;
  background: #fafafa;
}

.metadata-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.refund-preview-card {
  margin-bottom: 16px;
}

.refund-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  align-items: center;
}

.preview-label {
  width: 80px;
  color: #666;
  font-size: 14px;
}

.preview-value {
  font-weight: 500;
}

.amount-value {
  color: #1890ff;
  font-size: 16px;
}

.refund-warning {
  margin-bottom: 0;
}

.warning-content ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.warning-content li {
  margin-bottom: 4px;
  font-size: 13px;
}
</style>