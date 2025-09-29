<template>
  <a-modal
    v-model:open="visible"
    :title="isEdit ? '编辑支付' : '创建支付'"
    :width="800"
    :confirm-loading="loading"
    @ok="handleSubmit"
    @cancel="handleCancel"
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
    >
      <!-- 用户信息 -->
      <a-divider orientation="left">用户信息</a-divider>
      
      <a-form-item label="用户ID" name="userId">
        <a-input 
          v-model:value="formData.userId" 
          placeholder="请输入用户ID"
          :disabled="isEdit"
        />
      </a-form-item>
      
      <a-form-item label="用户姓名" name="userInfo.name">
        <a-input 
          v-model:value="formData.userInfo.name" 
          placeholder="请输入用户姓名"
        />
      </a-form-item>
      
      <a-form-item label="用户邮箱" name="userInfo.email">
        <a-input 
          v-model:value="formData.userInfo.email" 
          placeholder="请输入用户邮箱"
          type="email"
        />
      </a-form-item>
      
      <a-form-item label="用户手机" name="userInfo.phone">
        <a-input 
          v-model:value="formData.userInfo.phone" 
          placeholder="请输入用户手机号"
        />
      </a-form-item>
      
      <!-- 支付信息 -->
      <a-divider orientation="left">支付信息</a-divider>
      
      <a-form-item label="关联发票" name="invoiceId">
        <a-select
          v-model:value="formData.invoiceId"
          placeholder="请选择关联发票"
          show-search
          :filter-option="filterOption"
          :loading="loadingInvoices"
        >
          <a-select-option 
            v-for="invoice in availableInvoices" 
            :key="invoice.id" 
            :value="invoice.id"
          >
            {{ invoice.invoiceNumber }} - {{ formatAmount(invoice.totalAmount) }}
          </a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="支付金额" name="amount">
        <div class="amount-input">
          <a-input-number
            v-model:value="formData.amount.amount"
            placeholder="请输入支付金额"
            :min="0.01"
            :precision="2"
            style="flex: 1"
          />
          <a-select
            v-model:value="formData.amount.currency"
            style="width: 80px; margin-left: 8px"
          >
            <a-select-option value="CNY">CNY</a-select-option>
            <a-select-option value="USD">USD</a-select-option>
            <a-select-option value="EUR">EUR</a-select-option>
          </a-select>
        </div>
      </a-form-item>
      
      <a-form-item label="支付方式" name="paymentMethodType">
        <a-select
          v-model:value="formData.paymentMethodType"
          placeholder="请选择支付方式"
        >
          <a-select-option value="alipay">
            <div class="payment-method-option">
              <span class="method-icon">💰</span>
              支付宝
            </div>
          </a-select-option>
          <a-select-option value="wechat">
            <div class="payment-method-option">
              <span class="method-icon">💚</span>
              微信支付
            </div>
          </a-select-option>
          <a-select-option value="bank_card">
            <div class="payment-method-option">
              <span class="method-icon">💳</span>
              银行卡
            </div>
          </a-select-option>
          <a-select-option value="credit_card">
            <div class="payment-method-option">
              <span class="method-icon">💎</span>
              信用卡
            </div>
          </a-select-option>
          <a-select-option value="bank_transfer">
            <div class="payment-method-option">
              <span class="method-icon">🏦</span>
              银行转账
            </div>
          </a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="支付网关" name="gatewayType">
        <a-select
          v-model:value="formData.gatewayType"
          placeholder="请选择支付网关"
        >
          <a-select-option value="alipay">支付宝官方</a-select-option>
          <a-select-option value="wechat">微信支付官方</a-select-option>
          <a-select-option value="unionpay">银联</a-select-option>
          <a-select-option value="stripe">Stripe</a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="支付描述" name="description">
        <a-textarea
          v-model:value="formData.description"
          placeholder="请输入支付描述"
          :rows="3"
          show-count
          :maxlength="200"
        />
      </a-form-item>
      
      <!-- 高级选项 -->
      <a-form-item>
        <a-checkbox v-model:checked="showAdvanced">
          显示高级选项
        </a-checkbox>
      </a-form-item>
      
      <template v-if="showAdvanced">
        <a-divider orientation="left">高级选项</a-divider>
        
        <a-form-item label="过期时间" name="expiredAt">
          <a-date-picker
            v-model:value="expiredAt"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            placeholder="请选择过期时间"
            style="width: 100%"
          />
        </a-form-item>
        
        <a-form-item label="通知地址" name="notifyUrl">
          <a-input
            v-model:value="formData.notifyUrl"
            placeholder="请输入支付结果通知地址"
          />
        </a-form-item>
        
        <a-form-item label="返回地址" name="returnUrl">
          <a-input
            v-model:value="formData.returnUrl"
            placeholder="请输入支付完成后返回地址"
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
    
    <!-- 预览区域 -->
    <a-divider orientation="left">支付预览</a-divider>
    
    <div class="payment-preview">
      <a-descriptions :column="2" size="small" bordered>
        <a-descriptions-item label="用户">
          {{ formData.userInfo.name || '未填写' }}
        </a-descriptions-item>
        <a-descriptions-item label="邮箱">
          {{ formData.userInfo.email || '未填写' }}
        </a-descriptions-item>
        <a-descriptions-item label="支付金额">
          <span class="preview-amount">
            {{ formatAmount(formData.amount) }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="支付方式">
          {{ getPaymentMethodText(formData.paymentMethodType) }}
        </a-descriptions-item>
        <a-descriptions-item label="支付网关">
          {{ getGatewayText(formData.gatewayType) }}
        </a-descriptions-item>
        <a-descriptions-item label="过期时间">
          {{ expiredAt ? expiredAt.format('YYYY-MM-DD HH:mm:ss') : '默认30分钟' }}
        </a-descriptions-item>
      </a-descriptions>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import type { FormInstance } from 'ant-design-vue'
import type { 
  CreatePaymentRequest,
  UpdatePaymentRequest,
  PaymentRecord,
  PaymentMethodType,
  PaymentGatewayType,
  Money,
  Invoice
} from '@/types/billing'
import { paymentService } from '@/services/paymentService'
import { invoiceService } from '@/services/invoiceService'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'

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
  success: []
}>()

// 响应式状态
const formRef = ref<FormInstance>()
const loading = ref(false)
const loadingInvoices = ref(false)
const showAdvanced = ref(false)
const expiredAt = ref<Dayjs>()
const availableInvoices = ref<Invoice[]>([])

// 表单数据
const formData = reactive<CreatePaymentRequest>({
  userId: '',
  invoiceId: '',
  userInfo: {
    name: '',
    email: '',
    phone: ''
  },
  amount: {
    amount: 0,
    currency: 'CNY'
  },
  paymentMethodType: 'alipay',
  gatewayType: 'alipay',
  description: '',
  notifyUrl: '',
  returnUrl: '',
  metadata: {}
})

// 元数据编辑器
const metadataList = ref<Array<{ key: string; value: string }>>([])

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isEdit = computed(() => !!props.payment)

// 表单验证规则
const rules = {
  userId: [
    { required: true, message: '请输入用户ID' }
  ],
  'userInfo.name': [
    { required: true, message: '请输入用户姓名' }
  ],
  'userInfo.email': [
    { required: true, message: '请输入用户邮箱' },
    { type: 'email', message: '请输入正确的邮箱格式' }
  ],
  'userInfo.phone': [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式' }
  ],
  invoiceId: [
    { required: true, message: '请选择关联发票' }
  ],
  amount: [
    { required: true, message: '请输入支付金额' },
    { 
      validator: (_rule: any, value: Money) => {
        if (!value || value.amount <= 0) {
          return Promise.reject('支付金额必须大于0')
        }
        return Promise.resolve()
      }
    }
  ],
  paymentMethodType: [
    { required: true, message: '请选择支付方式' }
  ],
  gatewayType: [
    { required: true, message: '请选择支付网关' }
  ],
  description: [
    { required: true, message: '请输入支付描述' },
    { min: 5, message: '支付描述至少需要5个字符' }
  ]
}

// 监听弹窗显示
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
    loadInvoices()
    
    if (props.payment) {
      loadPaymentData()
    }
  }
})

// 监听支付方式变化，自动设置对应网关
watch(() => formData.paymentMethodType, (newMethod) => {
  const gatewayMap: Record<PaymentMethodType, PaymentGatewayType> = {
    alipay: 'alipay',
    wechat: 'wechat',
    bank_card: 'unionpay',
    credit_card: 'stripe',
    bank_transfer: 'unionpay'
  }
  
  formData.gatewayType = gatewayMap[newMethod] || 'alipay'
})

// 方法
const resetForm = () => {
  Object.assign(formData, {
    userId: '',
    invoiceId: '',
    userInfo: {
      name: '',
      email: '',
      phone: ''
    },
    amount: {
      amount: 0,
      currency: 'CNY'
    },
    paymentMethodType: 'alipay',
    gatewayType: 'alipay',
    description: '',
    notifyUrl: '',
    returnUrl: '',
    metadata: {}
  })
  
  metadataList.value = []
  expiredAt.value = undefined
  showAdvanced.value = false
  
  formRef.value?.clearValidate()
}

const loadPaymentData = () => {
  if (!props.payment) return
  
  const payment = props.payment
  
  Object.assign(formData, {
    userId: payment.userId,
    invoiceId: payment.invoiceId,
    userInfo: { ...payment.userInfo },
    amount: { ...payment.amount },
    paymentMethodType: payment.paymentMethodType,
    gatewayType: payment.gatewayType,
    description: payment.description || '',
    notifyUrl: '',
    returnUrl: '',
    metadata: payment.metadata || {}
  })
  
  // 转换元数据
  metadataList.value = Object.entries(payment.metadata || {}).map(([key, value]) => ({
    key,
    value: String(value)
  }))
  
  // 设置过期时间
  if (payment.expiredAt) {
    expiredAt.value = dayjs(payment.expiredAt)
  }
}

const loadInvoices = async () => {
  try {
    loadingInvoices.value = true
    const response = await invoiceService.getInvoices({
      status: 'draft', // 只加载草稿状态的发票
      page: 1,
      pageSize: 100
    })
    availableInvoices.value = response.data
  } catch (error: any) {
    console.error('Load invoices error:', error)
    message.error('加载发票列表失败')
  } finally {
    loadingInvoices.value = false
  }
}

const addMetadata = () => {
  metadataList.value.push({ key: '', value: '' })
}

const removeMetadata = (index: number) => {
  metadataList.value.splice(index, 1)
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
    
    // 准备提交数据
    const submitData: CreatePaymentRequest | UpdatePaymentRequest = {
      ...formData,
      metadata,
      ...(expiredAt.value ? { expiredAt: expiredAt.value.toISOString() } : {})
    }
    
    if (isEdit.value && props.payment) {
      // 编辑模式 - 通常支付创建后不允许编辑关键信息
      await paymentService.updatePayment(props.payment.id, submitData as UpdatePaymentRequest)
      message.success('支付更新成功')
    } else {
      // 创建模式
      const result = await paymentService.createPayment(submitData as CreatePaymentRequest)
      if (result.success) {
        message.success('支付创建成功')
        
        // 如果有支付链接，询问是否打开
        if (result.payUrl) {
          Modal.confirm({
            title: '支付链接已生成',
            content: '是否要打开支付页面？',
            onOk: () => {
              window.open(result.payUrl, '_blank')
            }
          })
        }
      } else {
        message.error(result.message || '支付创建失败')
        return
      }
    }
    
    emit('success')
  } catch (error: any) {
    console.error('Submit payment error:', error)
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

const getPaymentMethodText = (method?: PaymentMethodType): string => {
  if (!method) return '未选择'
  
  const textMap: Record<PaymentMethodType, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    bank_card: '银行卡',
    credit_card: '信用卡',
    bank_transfer: '银行转账'
  }
  return textMap[method] || method
}

const getGatewayText = (gateway?: PaymentGatewayType): string => {
  if (!gateway) return '未选择'
  
  const textMap: Record<PaymentGatewayType, string> = {
    alipay: '支付宝官方',
    wechat: '微信支付官方',
    unionpay: '银联',
    stripe: 'Stripe'
  }
  return textMap[gateway] || gateway
}

const filterOption = (input: string, option: any) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 导入 Modal 用于确认对话框
import { Modal } from 'ant-design-vue'
</script>

<style scoped>
.amount-input {
  display: flex;
  align-items: center;
}

.payment-method-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.method-icon {
  font-size: 16px;
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

.payment-preview {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.preview-amount {
  font-weight: 600;
  color: #1890ff;
  font-size: 16px;
}
</style>