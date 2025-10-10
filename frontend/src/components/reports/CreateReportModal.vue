<template>
  <a-modal
    v-model:open="isVisible"
    title="创建报表"
    width="600px"
    @ok="handleSubmit"
    @cancel="handleCancel"
  >
    <a-form ref="formRef" :model="formData" :rules="rules" layout="vertical">
      <a-form-item label="报表名称" name="name">
        <a-input v-model:value="formData.name" placeholder="请输入报表名称" />
      </a-form-item>

      <a-form-item label="报表类型" name="report_type">
        <a-select v-model:value="formData.report_type" placeholder="选择报表类型">
          <a-select-option value="online_users">在线用户报表</a-select-option>
          <a-select-option value="history">历史会话报表</a-select-option>
          <a-select-option value="last_connect">最近连接报表</a-select-option>
          <a-select-option value="new_users">新用户报表</a-select-option>
          <a-select-option value="top_users">热门用户报表</a-select-option>
          <a-select-option value="system_logs">系统日志报表</a-select-option>
          <a-select-option value="batch_report">批量操作报表</a-select-option>
          <a-select-option value="system_status">系统状态报表</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="描述" name="description">
        <a-textarea v-model:value="formData.description" placeholder="请输入报表描述" :rows="3" />
      </a-form-item>

      <a-form-item label="公开报表" name="is_public">
        <a-switch v-model:checked="formData.is_public" />
        <span class="hint">公开的报表其他用户也可以访问</span>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'created', data: Record<string, unknown>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const isVisible = ref(props.visible)

const formData = reactive({
  name: '',
  report_type: '',
  description: '',
  is_public: false,
})

const rules = {
  name: [{ required: true, message: '请输入报表名称', trigger: 'blur' }],
  report_type: [{ required: true, message: '请选择报表类型', trigger: 'change' }],
}

watch(
  () => props.visible,
  (val) => {
    isVisible.value = val
  },
)

watch(isVisible, (val) => {
  emit('update:visible', val)
  if (!val) {
    resetForm()
  }
})

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    emit('created', { ...formData })
    message.success('报表创建成功')
    isVisible.value = false
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}

const handleCancel = () => {
  isVisible.value = false
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    name: '',
    report_type: '',
    description: '',
    is_public: false,
  })
}
</script>

<style scoped lang="scss">
.hint {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}
</style>
