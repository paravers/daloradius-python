<template>
  <div class="billing-plan-form">
    <Form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      layout="vertical"
      @finish="handleSubmit"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h3 class="section-title">
          <Icon name="Info" />
          基本信息
        </h3>
        <div class="form-grid">
          <FormItem
            label="计划名称"
            name="name"
            required
          >
            <Input
              v-model:value="formData.name"
              placeholder="请输入计划名称"
              :maxlength="50"
              show-count
            />
          </FormItem>
          <FormItem
            label="计划类型"
            name="type"
            required
          >
            <Select
              v-model:value="formData.type"
              placeholder="选择计划类型"
            >
              <SelectOption value="monthly">月租</SelectOption>
              <SelectOption value="usage">按量计费</SelectOption>
              <SelectOption value="hybrid">混合计费</SelectOption>
              <SelectOption value="prepaid">预付费</SelectOption>
              <SelectOption value="postpaid">后付费</SelectOption>
            </Select>
          </FormItem>
        </div>
        <FormItem
          label="计划描述"
          name="description"
        >
          <TextArea
            v-model:value="formData.description"
            :rows="3"
            placeholder="请输入计划描述"
            :maxlength="200"
            show-count
          />
        </FormItem>
      </div>

      <!-- 有效期设置 -->
      <div class="form-section">
        <h3 class="section-title">
          <Icon name="Calendar" />
          有效期设置
        </h3>
        <div class="form-grid">
          <FormItem
            label="生效日期"
            name="validFrom"
            required
          >
            <DatePicker
              v-model:value="formData.validFrom"
              placeholder="选择生效日期"
              style="width: 100%"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </FormItem>
          <FormItem
            label="失效日期"
            name="validTo"
          >
            <DatePicker
              v-model:value="formData.validTo"
              placeholder="选择失效日期（可选）"
              style="width: 100%"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </FormItem>
        </div>
      </div>

      <!-- 用户限制 -->
      <div class="form-section">
        <h3 class="section-title">
          <Icon name="Users" />
          用户限制
        </h3>
        <FormItem
          label="最大用户数"
          name="maxUsers"
        >
          <InputNumber
            v-model:value="formData.maxUsers"
            placeholder="留空表示无限制"
            :min="1"
            style="width: 100%"
          />
        </FormItem>
      </div>

      <!-- 费率配置 -->
      <div class="form-section">
        <h3 class="section-title">
          <Icon name="DollarSign" />
          费率配置
          <Button
            type="dashed"
            size="small"
            @click="addRate"
            class="add-rate-btn"
          >
            <Icon name="Plus" />
            添加费率
          </Button>
        </h3>
        <div class="rates-container">
          <div
            v-for="(rate, index) in formData.rates"
            :key="index"
            class="rate-item"
          >
            <div class="rate-header">
              <span class="rate-index">费率 {{ index + 1 }}</span>
              <Button
                type="text"
                size="small"
                danger
                @click="removeRate(index)"
                :disabled="formData.rates.length === 1"
              >
                <Icon name="Trash2" />
              </Button>
            </div>
            <div class="rate-form">
              <div class="form-grid">
                <FormItem
                  :name="['rates', index, 'name']"
                  label="费率名称"
                  :rules="[{ required: true, message: '请输入费率名称' }]"
                >
                  <Input
                    v-model:value="rate.name"
                    placeholder="如：月租费、流量费"
                  />
                </FormItem>
                <FormItem
                  :name="['rates', index, 'type']"
                  label="费率类型"
                  :rules="[{ required: true, message: '请选择费率类型' }]"
                >
                  <Select
                    v-model:value="rate.type"
                    placeholder="选择费率类型"
                    @change="handleRateTypeChange(index, $event)"
                  >
                    <SelectOption value="fixed">固定费用</SelectOption>
                    <SelectOption value="volume">流量计费</SelectOption>
                    <SelectOption value="tiered">阶梯计费</SelectOption>
                    <SelectOption value="bandwidth">带宽计费</SelectOption>
                    <SelectOption value="time_based">时长计费</SelectOption>
                  </Select>
                </FormItem>
              </div>
              <div class="form-grid">
                <FormItem
                  :name="['rates', index, 'unitPrice', 'amount']"
                  label="单价"
                  :rules="[{ required: true, message: '请输入单价' }]"
                >
                  <InputNumber
                    v-model:value="rate.unitPrice.amount"
                    placeholder="0.00"
                    :min="0"
                    :precision="2"
                    style="width: 100%"
                  />
                </FormItem>
                <FormItem
                  :name="['rates', index, 'unitPrice', 'currency']"
                  label="货币"
                  :rules="[{ required: true, message: '请选择货币' }]"
                >
                  <Select
                    v-model:value="rate.unitPrice.currency"
                    placeholder="选择货币"
                  >
                    <SelectOption value="CNY">人民币 (CNY)</SelectOption>
                    <SelectOption value="USD">美元 (USD)</SelectOption>
                    <SelectOption value="EUR">欧元 (EUR)</SelectOption>
                  </Select>
                </FormItem>
              </div>

              <!-- 阶梯计费配置 -->
              <div v-if="rate.type === 'tiered'" class="tier-rates-config">
                <div class="tier-header">
                  <span>阶梯费率配置</span>
                  <Button
                    type="dashed"
                    size="small"
                    @click="addTierRate(index)"
                  >
                    <Icon name="Plus" />
                    添加阶梯
                  </Button>
                </div>
                <div
                  v-for="(tier, tierIndex) in rate.tierRates"
                  :key="tierIndex"
                  class="tier-item"
                >
                  <div class="tier-form">
                    <FormItem label="起始值">
                      <InputNumber
                        v-model:value="tier.from"
                        placeholder="0"
                        :min="0"
                        style="width: 100%"
                      />
                    </FormItem>
                    <FormItem label="结束值">
                      <InputNumber
                        v-model:value="tier.to"
                        placeholder="留空表示无上限"
                        :min="tier.from"
                        style="width: 100%"
                      />
                    </FormItem>
                    <FormItem label="单价">
                      <InputNumber
                        v-model:value="tier.price.amount"
                        placeholder="0.00"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </FormItem>
                    <Button
                      type="text"
                      danger
                      @click="removeTierRate(index, tierIndex)"
                    >
                      <Icon name="Trash2" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能特性 -->
      <div class="form-section">
        <h3 class="section-title">
          <Icon name="Star" />
          功能特性
        </h3>
        <FormItem
          label="包含功能"
          name="features"
        >
          <div class="features-input">
            <div class="feature-tags">
              <Tag
                v-for="(feature, index) in formData.features"
                :key="index"
                closable
                @close="removeFeature(index)"
              >
                {{ feature }}
              </Tag>
            </div>
            <div class="add-feature">
              <Input
                v-model:value="newFeature"
                placeholder="输入功能特性后按回车添加"
                @press-enter="addFeature"
                style="width: 300px"
              />
              <Button @click="addFeature">添加</Button>
            </div>
          </div>
        </FormItem>
      </div>

      <!-- 表单操作 -->
      <div class="form-actions">
        <Button @click="handleCancel">
          取消
        </Button>
        <Button
          type="primary"
          html-type="submit"
          :loading="loading"
        >
          {{ isEdit ? '保存更改' : '创建计划' }}
        </Button>
      </div>
    </Form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import type { 
  BillingPlan, 
  CreateBillingPlanRequest,
  BillingRate,
  TierRate,
  Money
} from '@/types/billing'
import { 
  Form, 
  FormItem, 
  Input, 
  InputNumber,
  TextArea,
  Select, 
  SelectOption,
  DatePicker,
  Button,
  Tag,
  type FormInstance,
  type Rule
} from 'ant-design-vue'
import Icon from '@/components/common/Icon.vue'
import { useMessage } from '@/composables/useMessage'

// 组件属性
interface Props {
  plan?: BillingPlan | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  plan: null,
  loading: false
})

// 组件事件
interface Emits {
  (e: 'submit', data: CreateBillingPlanRequest): void
  (e: 'cancel'): void
}

const emit = defineEmits<Emits>()

// 响应式状态
const formRef = ref<FormInstance>()
const newFeature = ref('')
const { error: showError } = useMessage()

// 表单数据
const formData = reactive<CreateBillingPlanRequest>({
  name: '',
  type: 'monthly',
  description: '',
  validFrom: '',
  validTo: '',
  maxUsers: undefined,
  rates: [
    {
      name: '',
      type: 'fixed',
      unitPrice: {
        amount: 0,
        currency: 'CNY'
      },
      validFrom: ''
    }
  ],
  features: []
})

// 表单验证规则
const formRules: Record<string, Rule[]> = {
  name: [
    { required: true, message: '请输入计划名称' },
    { min: 2, max: 50, message: '计划名称长度在2-50个字符之间' }
  ],
  type: [
    { required: true, message: '请选择计划类型' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符' }
  ],
  validFrom: [
    { required: true, message: '请选择生效日期' }
  ],
  validTo: [
    {
      validator: (rule: any, value: string) => {
        if (!value || !formData.validFrom) return Promise.resolve()
        if (new Date(value) <= new Date(formData.validFrom)) {
          return Promise.reject('失效日期必须晚于生效日期')
        }
        return Promise.resolve()
      }
    }
  ],
  maxUsers: [
    { type: 'number', min: 1, message: '最大用户数必须大于0' }
  ]
}

// 计算属性
const isEdit = computed(() => !!props.plan)

// 监听计划变化
watch(
  () => props.plan,
  (newPlan) => {
    if (newPlan) {
      // 编辑模式，填充表单数据
      Object.assign(formData, {
        name: newPlan.name,
        type: newPlan.type,
        description: newPlan.description,
        validFrom: newPlan.validFrom.split('T')[0], // 转换为日期格式
        validTo: newPlan.validTo ? newPlan.validTo.split('T')[0] : '',
        maxUsers: newPlan.maxUsers,
        rates: newPlan.rates.map(rate => ({
          name: rate.name,
          type: rate.type,
          unitPrice: {
            amount: rate.unitPrice.amount,
            currency: rate.unitPrice.currency
          },
          validFrom: rate.validFrom.split('T')[0],
          tierRates: rate.tierRates ? [...rate.tierRates] : undefined
        })),
        features: [...(newPlan.features || [])]
      })
    } else {
      // 新建模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

// 页面初始化
onMounted(() => {
  if (!props.plan) {
    resetForm()
  }
})

// 重置表单
function resetForm() {
  Object.assign(formData, {
    name: '',
    type: 'monthly',
    description: '',
    validFrom: '',
    validTo: '',
    maxUsers: undefined,
    rates: [
      {
        name: '',
        type: 'fixed',
        unitPrice: {
          amount: 0,
          currency: 'CNY'
        },
        validFrom: ''
      }
    ],
    features: []
  })
  newFeature.value = ''
}

// 添加费率
function addRate() {
  formData.rates.push({
    name: '',
    type: 'fixed',
    unitPrice: {
      amount: 0,
      currency: 'CNY'
    },
    validFrom: formData.validFrom || ''
  })
}

// 移除费率
function removeRate(index: number) {
  if (formData.rates.length > 1) {
    formData.rates.splice(index, 1)
  }
}

// 费率类型变化处理
function handleRateTypeChange(index: number, type: string) {
  const rate = formData.rates[index]
  
  // 清理阶梯费率配置
  if (type !== 'tiered') {
    delete rate.tierRates
  } else if (!rate.tierRates) {
    // 初始化阶梯费率
    rate.tierRates = [
      {
        from: 0,
        to: 1024 * 1024 * 1024, // 1GB
        price: { amount: 0, currency: rate.unitPrice.currency }
      }
    ]
  }
}

// 添加阶梯费率
function addTierRate(rateIndex: number) {
  const rate = formData.rates[rateIndex]
  if (!rate.tierRates) {
    rate.tierRates = []
  }
  
  const lastTier = rate.tierRates[rate.tierRates.length - 1]
  const from = lastTier ? (lastTier.to || 0) : 0
  
  rate.tierRates.push({
    from,
    to: undefined,
    price: { amount: 0, currency: rate.unitPrice.currency }
  })
}

// 移除阶梯费率
function removeTierRate(rateIndex: number, tierIndex: number) {
  const rate = formData.rates[rateIndex]
  if (rate.tierRates && rate.tierRates.length > 1) {
    rate.tierRates.splice(tierIndex, 1)
  }
}

// 添加功能特性
function addFeature() {
  const feature = newFeature.value.trim()
  if (feature && !formData.features.includes(feature)) {
    formData.features.push(feature)
    newFeature.value = ''
  }
}

// 移除功能特性
function removeFeature(index: number) {
  formData.features.splice(index, 1)
}

// 表单提交
async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    // 处理表单数据
    const submitData: CreateBillingPlanRequest = {
      ...formData,
      validFrom: formData.validFrom + 'T00:00:00Z',
      validTo: formData.validTo ? formData.validTo + 'T23:59:59Z' : undefined,
      rates: formData.rates.map(rate => ({
        ...rate,
        validFrom: (rate.validFrom || formData.validFrom) + 'T00:00:00Z'
      }))
    }
    
    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败:', error)
    showError('请检查表单数据')
  }
}

// 表单取消
function handleCancel() {
  emit('cancel')
}
</script>

<style scoped>
.billing-plan-form {
  max-width: 800px;
}

.form-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.section-title svg {
  margin-right: 8px;
  color: #1890ff;
}

.add-rate-btn {
  margin-left: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.rates-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rate-item {
  padding: 16px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
}

.rate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.rate-index {
  font-weight: 500;
  color: #595959;
}

.rate-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tier-rates-config {
  margin-top: 16px;
}

.tier-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 500;
}

.tier-item {
  margin-bottom: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
}

.tier-form {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 12px;
  align-items: end;
}

.features-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.add-feature {
  display: flex;
  gap: 8px;
  align-items: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .tier-form {
    grid-template-columns: 1fr;
  }
  
  .add-feature {
    flex-direction: column;
    align-items: stretch;
  }
  
  .add-feature input {
    width: 100% !important;
  }
}
</style>