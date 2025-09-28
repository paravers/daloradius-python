<template>
  <a-form-item
    :label="field.label"
    :name="field.name"
    :rules="computedRules"
    :required="field.required"
    :label-col="labelCol"
    :wrapper-col="wrapperCol"
  >
    <!-- 输入框 -->
    <a-input
      v-if="field.type === 'input'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :maxlength="field.maxLength"
      :allow-clear="true"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 密码输入框 -->
    <a-input-password
      v-else-if="field.type === 'password'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :maxlength="field.maxLength"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 文本域 -->
    <a-textarea
      v-else-if="field.type === 'textarea'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :rows="field.rows || 3"
      :maxlength="field.maxLength"
      :show-count="!!field.maxLength"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 数字输入框 -->
    <a-input-number
      v-else-if="field.type === 'number'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :min="field.min"
      :max="field.max"
      :step="field.step || 1"
      :precision="field.precision"
      style="width: 100%"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 邮箱输入框 -->
    <a-input
      v-else-if="field.type === 'email'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      type="email"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- URL输入框 -->
    <a-input
      v-else-if="field.type === 'url'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      type="url"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 电话输入框 -->
    <a-input
      v-else-if="field.type === 'phone'"
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      type="tel"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 选择器 -->
    <a-select
      v-else-if="field.type === 'select'"
      :value="modelValue"
      :placeholder="field.placeholder || `请选择${field.label}`"
      :disabled="field.disabled"
      :mode="field.multiple ? 'multiple' : undefined"
      :options="field.options"
      :allow-clear="true"
      :show-search="field.showSearch !== false"
      :filter-option="filterOption"
      style="width: 100%"
      @update:value="updateValue"
      @change="handleChange"
    />
    
    <!-- 单选框组 -->
    <a-radio-group
      v-else-if="field.type === 'radio'"
      :value="modelValue"
      :disabled="field.disabled"
      @update:value="updateValue"
      @change="handleChange"
    >
      <a-radio
        v-for="option in field.options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </a-radio>
    </a-radio-group>
    
    <!-- 复选框组 -->
    <a-checkbox-group
      v-else-if="field.type === 'checkbox' && field.options"
      :value="modelValue"
      :disabled="field.disabled"
      @update:value="updateValue"
      @change="handleChange"
    >
      <a-checkbox
        v-for="option in field.options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </a-checkbox>
    </a-checkbox-group>
    
    <!-- 单个复选框 -->
    <a-checkbox
      v-else-if="field.type === 'checkbox' && !field.options"
      :checked="modelValue"
      :disabled="field.disabled"
      @update:checked="updateValue"
      @change="handleChange"
    >
      {{ field.checkedText || field.label }}
    </a-checkbox>
    
    <!-- 开关 -->
    <a-switch
      v-else-if="field.type === 'switch'"
      :checked="modelValue"
      :disabled="field.disabled"
      :checked-children="field.checkedText"
      :un-checked-children="field.uncheckedText"
      @update:checked="updateValue"
      @change="handleChange"
    />
    
    <!-- 日期选择器 -->
    <a-date-picker
      v-else-if="field.type === 'date'"
      :value="modelValue"
      :placeholder="field.placeholder || `请选择${field.label}`"
      :disabled="field.disabled"
      :format="field.format || 'YYYY-MM-DD'"
      :show-time="field.showTime"
      style="width: 100%"
      @update:value="updateValue"
      @change="handleChange"
    />
    
    <!-- 日期范围选择器 -->
    <a-range-picker
      v-else-if="field.type === 'daterange'"
      :value="modelValue"
      :placeholder="field.placeholder || ['开始日期', '结束日期']"
      :disabled="field.disabled"
      :format="field.format || 'YYYY-MM-DD'"
      :show-time="field.showTime"
      style="width: 100%"
      @update:value="updateValue"
      @change="handleChange"
    />
    
    <!-- 默认文本输入 -->
    <a-input
      v-else
      :value="modelValue"
      :placeholder="field.placeholder || `请输入${field.label}`"
      :disabled="field.disabled"
      :readonly="field.readonly"
      @update:value="updateValue"
      @change="handleChange"
      @blur="handleBlur"
    />
    
    <!-- 字段提示信息 -->
    <template v-if="field.tooltip" #help>
      <div class="field-tooltip">
        {{ field.tooltip }}
      </div>
    </template>
  </a-form-item>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { IFormField, ValidationRule, SelectOption } from '@/types/common'

// 组件属性定义
interface Props {
  field: IFormField
  modelValue: any
  labelCol?: { span: number; offset?: number }
  wrapperCol?: { span: number; offset?: number }
}

const props = defineProps<Props>()

// 组件事件定义
const emit = defineEmits<{
  'update:modelValue': [value: any]
  change: [value: any]
  blur: [event: Event]
}>()

// 计算属性 - 处理验证规则
const computedRules = computed(() => {
  if (!props.field.rules) return []
  
  return props.field.rules.map(rule => {
    const processedRule = { ...rule }
    
    // 处理必填验证
    if (rule.required) {
      processedRule.message = rule.message || `请${getRequiredMessage()}`
    }
    
    // 处理类型验证
    if (rule.type && !rule.message) {
      processedRule.message = getTypeMessage(rule.type)
    }
    
    // 处理长度验证
    if ((rule.min || rule.max || rule.len) && !rule.message) {
      processedRule.message = getLengthMessage(rule)
    }
    
    return processedRule
  })
})

// 获取必填验证提示文本
const getRequiredMessage = (): string => {
  const { type, label } = props.field
  
  if (['select', 'radio', 'checkbox', 'date', 'daterange'].includes(type)) {
    return `选择${label}`
  }
  
  return `输入${label}`
}

// 获取类型验证提示文本
const getTypeMessage = (type: string): string => {
  const messages: Record<string, string> = {
    email: '请输入正确的邮箱地址',
    url: '请输入正确的网址',
    number: '请输入数字',
    integer: '请输入整数',
    date: '请选择正确的日期',
    regexp: '格式不正确'
  }
  
  return messages[type] || '格式不正确'
}

// 获取长度验证提示文本
const getLengthMessage = (rule: ValidationRule): string => {
  const { label } = props.field
  
  if (rule.len) {
    return `${label}长度必须是${rule.len}个字符`
  }
  
  if (rule.min && rule.max) {
    return `${label}长度在${rule.min}到${rule.max}个字符之间`
  }
  
  if (rule.min) {
    return `${label}长度不能少于${rule.min}个字符`
  }
  
  if (rule.max) {
    return `${label}长度不能超过${rule.max}个字符`
  }
  
  return '长度不符合要求'
}

// 更新值
const updateValue = (value: any) => {
  emit('update:modelValue', value)
}

// 处理变化
const handleChange = (value: any) => {
  emit('change', value)
}

// 处理失焦
const handleBlur = (event: Event) => {
  emit('blur', event)
}

// 选择器过滤函数
const filterOption = (input: string, option: SelectOption) => {
  const label = option.label.toLowerCase()
  const inputValue = input.toLowerCase()
  return label.includes(inputValue)
}
</script>

<style scoped>
.field-tooltip {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  line-height: 1.5;
}

:deep(.ant-form-item-label > label) {
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
}

:deep(.ant-form-item-required) {
  &::before {
    color: #ff4d4f;
  }
}

/* 确保选择器样式一致 */
:deep(.ant-select),
:deep(.ant-cascader),
:deep(.ant-date-picker),
:deep(.ant-time-picker) {
  width: 100%;
}

/* 单选框和复选框组样式 */
:deep(.ant-radio-group),
:deep(.ant-checkbox-group) {
  width: 100%;
  
  .ant-radio,
  .ant-checkbox {
    margin-right: 12px;
    margin-bottom: 8px;
    white-space: nowrap;
  }
}

/* 开关样式 */
:deep(.ant-switch) {
  margin-right: 8px;
}
</style>