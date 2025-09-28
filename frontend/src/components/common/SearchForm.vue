<template>
  <div class="search-form-container">
    <a-form
      ref="formRef"
      :model="formModel"
      :layout="layout"
      :label-col="labelCol"
      :wrapper-col="wrapperCol"
      class="search-form"
      @finish="handleSearch"
    >
      <!-- 基础搜索字段 -->
      <a-row :gutter="16">
        <template v-for="field in basicFields" :key="field.name">
          <a-col
            :span="getFieldSpan(field)"
            :offset="field.offset"
            v-show="isFieldVisible(field)"
          >
            <DynamicFormField
              :field="field"
              :model-value="formModel[field.name]"
              @update:model-value="updateFieldValue(field.name, $event)"
              @change="handleFieldChange(field.name, $event)"
            />
          </a-col>
        </template>
        
        <!-- 操作按钮区域 -->
        <a-col :span="actionSpan" class="search-actions">
          <a-space>
            <!-- 搜索按钮 -->
            <a-button
              type="primary"
              html-type="submit"
              :loading="loading"
              @click="handleSearch"
            >
              <template #icon>
                <SearchOutlined />
              </template>
              搜索
            </a-button>
            
            <!-- 重置按钮 -->
            <a-button
              v-if="showResetButton"
              @click="handleReset"
            >
              <template #icon>
                <ReloadOutlined />
              </template>
              重置
            </a-button>
            
            <!-- 高级搜索切换 -->
            <a-button
              v-if="showAdvancedSearch && advancedFields.length > 0"
              type="link"
              @click="toggleAdvanced"
            >
              {{ collapsed ? '展开' : '收起' }}
              <DownOutlined :class="{ 'rotate-180': !collapsed }" />
            </a-button>
          </a-space>
        </a-col>
      </a-row>
      
      <!-- 高级搜索字段 -->
      <div
        v-if="showAdvancedSearch && advancedFields.length > 0"
        v-show="!collapsed"
        class="advanced-search-fields"
      >
        <a-divider orientation="left">高级搜索</a-divider>
        <a-row :gutter="16">
          <template v-for="field in advancedFields" :key="field.name">
            <a-col
              :span="getFieldSpan(field)"
              :offset="field.offset"
              v-show="isFieldVisible(field)"
            >
              <DynamicFormField
                :field="field"
                :model-value="formModel[field.name]"
                @update:model-value="updateFieldValue(field.name, $event)"
                @change="handleFieldChange(field.name, $event)"
              />
            </a-col>
          </template>
        </a-row>
      </div>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { SearchOutlined, ReloadOutlined, DownOutlined } from '@ant-design/icons-vue'
import DynamicFormField from './DynamicFormField.vue'
import type { FormInstance } from 'ant-design-vue'
import type { ISearchFormProps, IFormField } from '@/types/common'

// 组件属性定义
interface Props extends ISearchFormProps {
  loading?: boolean
  defaultCollapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'horizontal',
  labelCol: () => ({ span: 6 }),
  wrapperCol: () => ({ span: 18 }),
  showResetButton: true,
  showAdvancedSearch: true,
  collapsible: true,
  collapsed: true,
  loading: false,
  defaultCollapsed: true
})

// 组件事件定义
const emit = defineEmits<{
  search: [values: Record<string, any>]
  reset: []
  fieldChange: [field: string, value: any, allValues: Record<string, any>]
  toggleCollapse: [collapsed: boolean]
}>()

// 响应式状态
const formRef = ref<FormInstance>()
const formModel = reactive<Record<string, any>>({})
const collapsed = ref(props.defaultCollapsed)

// 初始化表单数据
watch(() => props.fields, (fields) => {
  fields.forEach(field => {
    if (!(field.name in formModel)) {
      formModel[field.name] = getDefaultFieldValue(field)
    }
  })
}, { immediate: true })

// 计算属性 - 基础搜索字段
const basicFields = computed(() => {
  return props.fields.filter(field => !field.advanced)
})

// 计算属性 - 高级搜索字段
const advancedFields = computed(() => {
  return props.fields.filter(field => field.advanced)
})

// 计算属性 - 操作按钮占据的栅格
const actionSpan = computed(() => {
  const fieldsPerRow = 24 / (props.labelCol!.span + props.wrapperCol!.span)
  const basicFieldsInLastRow = basicFields.value.length % fieldsPerRow
  
  if (basicFieldsInLastRow === 0) {
    return 24 / fieldsPerRow
  }
  
  return 24 - (basicFieldsInLastRow * (props.labelCol!.span + props.wrapperCol!.span))
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
    default:
      return ''
  }
}

// 获取字段栅格跨度
const getFieldSpan = (field: IFormField): number => {
  if (field.span) return field.span
  
  // 默认根据布局计算
  if (props.layout === 'inline') {
    return 6
  }
  
  return props.labelCol!.span + props.wrapperCol!.span
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
}

// 处理字段变化
const handleFieldChange = (fieldName: string, value: any) => {
  emit('fieldChange', fieldName, value, { ...formModel })
}

// 处理搜索
const handleSearch = () => {
  formRef.value?.validate().then(() => {
    const searchValues = { ...formModel }
    
    // 过滤空值
    Object.keys(searchValues).forEach(key => {
      const value = searchValues[key]
      if (value === '' || value === null || value === undefined || 
          (Array.isArray(value) && value.length === 0)) {
        delete searchValues[key]
      }
    })
    
    emit('search', searchValues)
  }).catch(() => {
    // 验证失败，不执行搜索
  })
}

// 处理重置
const handleReset = () => {
  formRef.value?.resetFields()
  
  // 重置为默认值
  props.fields.forEach(field => {
    formModel[field.name] = getDefaultFieldValue(field)
  })
  
  emit('reset')
}

// 切换高级搜索
const toggleAdvanced = () => {
  collapsed.value = !collapsed.value
  emit('toggleCollapse', collapsed.value)
}

// 获取搜索值
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

// 重置特定字段
const resetField = (fieldName: string) => {
  const field = props.fields.find(f => f.name === fieldName)
  if (field) {
    formModel[fieldName] = getDefaultFieldValue(field)
  }
}

// 暴露给父组件的方法
defineExpose({
  getFormValues,
  setFormValues,
  resetField,
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields()
})
</script>

<style scoped>
.search-form-container {
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 16px;
}

.search-form {
  margin-bottom: 0;
}

.search-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 32px;
}

.advanced-search-fields {
  margin-top: 16px;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s;
}

:deep(.ant-form-item) {
  margin-bottom: 16px;
}

:deep(.ant-form-item-label) {
  text-align: left;
}

:deep(.ant-divider-horizontal) {
  margin: 16px 0;
}

/* 内联布局样式 */
.search-form.ant-form-inline {
  :deep(.ant-form-item) {
    margin-right: 16px;
    margin-bottom: 8px;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form-container {
    padding: 16px;
  }
  
  .search-actions {
    justify-content: center;
    margin-top: 16px;
  }
}
</style>