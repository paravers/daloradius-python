<template>
  <div class="dynamic-form-container">
    <a-form
      ref="formRef"
      :model="formModel"
      :layout="layout"
      :label-col="labelCol"
      :wrapper-col="wrapperCol"
      :validate-on-rule-change="validateOnRuleChange"
      class="dynamic-form"
      @finish="handleSubmit"
      @finish-failed="handleSubmitFailed"
    >
      <!-- 表单字段网格布局 -->
      <a-row :gutter="16">
        <template v-for="field in visibleFields" :key="field.name">
          <a-col
            :span="getFieldSpan(field)"
            :offset="field.offset"
          >
            <DynamicFormField
              :field="field"
              :model-value="formModel[field.name]"
              :label-col="fieldLabelCol"
              :wrapper-col="fieldWrapperCol"
              @update:model-value="updateFieldValue(field.name, $event)"
              @change="handleFieldChange(field.name, $event)"
              @blur="handleFieldBlur(field.name)"
            />
          </a-col>
        </template>
      </a-row>
      
      <!-- 表单操作按钮 -->
      <a-form-item
        v-if="showSubmitButton || showResetButton"
        :wrapper-col="{ offset: labelCol?.span || 0, span: wrapperCol?.span || 24 }"
        class="form-actions"
      >
        <a-space>
          <a-button
            v-if="showSubmitButton"
            type="primary"
            html-type="submit"
            :loading="submitting"
            :disabled="readonly"
          >
            {{ submitText || '提交' }}
          </a-button>
          
          <a-button
            v-if="showResetButton"
            @click="handleReset"
            :disabled="readonly"
          >
            {{ resetText || '重置' }}
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import DynamicFormField from './DynamicFormField.vue'
import type { FormInstance } from 'ant-design-vue'
import type { IDynamicFormProps, IFormField } from '@/types/common'

// 组件属性定义
interface Props extends IDynamicFormProps {
  submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'horizontal',
  labelCol: () => ({ span: 6 }),
  wrapperCol: () => ({ span: 18 }),
  columns: 1,
  readonly: false,
  showSubmitButton: true,
  showResetButton: true,
  validateOnRuleChange: true,
  submitting: false
})

// 组件事件定义
const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  submit: [values: Record<string, any>]
  reset: []
  fieldChange: [field: string, value: any, allValues: Record<string, any>]
  validationChange: [valid: boolean, errors: Record<string, any>]
}>()

// 响应式状态
const formRef = ref<FormInstance>()
const formModel = reactive<Record<string, any>>({})
const fieldErrors = ref<Record<string, any>>({})

// 监听 modelValue 变化，同步到内部表单模型
watch(() => props.modelValue, (newValue) => {
  Object.keys(newValue).forEach(key => {
    formModel[key] = newValue[key]
  })
}, { immediate: true, deep: true })

// 监听表单模型变化，同步到父组件
watch(formModel, (newValue) => {
  emit('update:modelValue', { ...newValue })
}, { deep: true })

// 初始化表单字段默认值
watch(() => props.fields, (fields) => {
  fields.forEach(field => {
    if (!(field.name in formModel)) {
      formModel[field.name] = getDefaultFieldValue(field)
    }
  })
}, { immediate: true })

// 计算属性 - 可见字段
const visibleFields = computed(() => {
  return props.fields.filter(field => isFieldVisible(field))
})

// 计算属性 - 字段标签列配置
const fieldLabelCol = computed(() => {
  if (props.layout === 'vertical') {
    return { span: 24 }
  }
  return props.labelCol
})

// 计算属性 - 字段包装列配置
const fieldWrapperCol = computed(() => {
  if (props.layout === 'vertical') {
    return { span: 24 }
  }
  return props.wrapperCol
})

// 获取字段默认值
const getDefaultFieldValue = (field: IFormField): any => {
  switch (field.type) {
    case 'checkbox':
      return field.multiple ? [] : false
    case 'select':
      return field.multiple ? [] : undefined
    case 'daterange':
      return []
    case 'number':
      return undefined
    case 'switch':
      return false
    default:
      return ''
  }
}

// 获取字段栅格跨度
const getFieldSpan = (field: IFormField): number => {
  if (field.span) return field.span
  
  // 根据列数计算默认跨度
  return Math.floor(24 / props.columns)
}

// 判断字段是否可见
const isFieldVisible = (field: IFormField): boolean => {
  if (typeof field.visible === 'function') {
    return field.visible(formModel)
  }
  return field.visible !== false
}

// 更新字段值
const updateFieldValue = (fieldName: string, value: any) => {
  formModel[fieldName] = value
  
  // 检查字段依赖关系
  checkFieldDependencies(fieldName)
}

// 处理字段变化
const handleFieldChange = (fieldName: string, value: any) => {
  emit('fieldChange', fieldName, value, { ...formModel })
  
  // 验证相关字段
  validateDependentFields(fieldName)
}

// 处理字段失焦
const handleFieldBlur = (fieldName: string) => {
  // 验证单个字段
  validateField(fieldName)
}

// 检查字段依赖关系
const checkFieldDependencies = (changedFieldName: string) => {
  props.fields.forEach(field => {
    if (field.dependencies && field.dependencies.includes(changedFieldName)) {
      // 重新计算依赖字段的可见性
      nextTick(() => {
        if (!isFieldVisible(field)) {
          // 如果字段不可见，清空其值
          formModel[field.name] = getDefaultFieldValue(field)
        }
      })
    }
  })
}

// 验证相关字段
const validateDependentFields = (changedFieldName: string) => {
  props.fields.forEach(field => {
    if (field.dependencies && field.dependencies.includes(changedFieldName)) {
      validateField(field.name)
    }
  })
}

// 验证单个字段
const validateField = (fieldName: string) => {
  return formRef.value?.validateFields([fieldName]).catch((errorInfo) => {
    fieldErrors.value[fieldName] = errorInfo.errorFields?.[0]?.errors || []
    checkValidationStatus()
  })
}

// 检查整体验证状态
const checkValidationStatus = () => {
  const hasErrors = Object.values(fieldErrors.value).some(errors => 
    Array.isArray(errors) && errors.length > 0
  )
  emit('validationChange', !hasErrors, { ...fieldErrors.value })
}

// 处理表单提交
const handleSubmit = () => {
  formRef.value?.validate().then(() => {
    const submitValues = { ...formModel }
    emit('submit', submitValues)
  }).catch((errorInfo) => {
    message.error('请检查表单填写是否正确')
    console.error('表单验证失败:', errorInfo)
  })
}

// 处理表单提交失败
const handleSubmitFailed = (errorInfo: any) => {
  console.error('表单提交失败:', errorInfo)
  message.error('表单验证失败，请检查填写内容')
}

// 处理表单重置
const handleReset = () => {
  formRef.value?.resetFields()
  
  // 重置为默认值
  props.fields.forEach(field => {
    formModel[field.name] = getDefaultFieldValue(field)
  })
  
  fieldErrors.value = {}
  emit('reset')
}

// 手动验证表单
const validate = () => {
  return formRef.value?.validate()
}

// 验证指定字段
const validateFields = (fields?: string[]) => {
  return formRef.value?.validateFields(fields)
}

// 重置字段
const resetFields = (fields?: string[]) => {
  formRef.value?.resetFields(fields)
}

// 清除验证结果
const clearValidate = (fields?: string[]) => {
  formRef.value?.clearValidate(fields)
}

// 获取表单值
const getFormValues = () => {
  return { ...formModel }
}

// 设置表单值
const setFormValues = (values: Record<string, any>) => {
  Object.keys(values).forEach(key => {
    if (key in formModel) {
      formModel[key] = values[key]
    }
  })
}

// 暴露给父组件的方法
defineExpose({
  validate,
  validateFields,
  resetFields,
  clearValidate,
  getFormValues,
  setFormValues
})
</script>

<style scoped>
.dynamic-form-container {
  background: #fff;
}

.dynamic-form {
  width: 100%;
}

.form-actions {
  margin-top: 24px;
  margin-bottom: 0;
}

:deep(.ant-form-item) {
  margin-bottom: 20px;
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

/* 垂直布局样式 */
.dynamic-form[data-layout="vertical"] {
  :deep(.ant-form-item-label) {
    text-align: left;
    padding-bottom: 4px;
  }
}

/* 内联布局样式 */
.dynamic-form[data-layout="inline"] {
  :deep(.ant-form-item) {
    margin-right: 16px;
    margin-bottom: 16px;
  }
}

/* 只读模式样式 */
.dynamic-form[data-readonly="true"] {
  :deep(.ant-input),
  :deep(.ant-input-number),
  :deep(.ant-select),
  :deep(.ant-cascader),
  :deep(.ant-date-picker),
  :deep(.ant-time-picker),
  :deep(.ant-radio),
  :deep(.ant-checkbox),
  :deep(.ant-switch) {
    background-color: #f5f5f5;
    border-color: #d9d9d9;
    cursor: not-allowed;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dynamic-form-container {
    padding: 16px;
  }
  
  .form-actions {
    text-align: center;
  }
}
</style>