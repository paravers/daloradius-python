<template>
  <div class="user-import-modal">
    <a-modal
      v-model:open="visible"
      title="批量导入用户"
      :width="800"
      :footer="null"
      @cancel="handleCancel"
    >
      <a-steps :current="currentStep" class="mb-6">
        <a-step title="选择文件" description="上传Excel或CSV文件" />
        <a-step title="字段映射" description="配置数据字段对应关系" />
        <a-step title="数据预览" description="预览导入数据" />
        <a-step title="导入结果" description="查看导入结果" />
      </a-steps>

      <!-- 步骤1: 文件上传 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-upload-dragger
          v-model:file-list="fileList"
          :before-upload="beforeUpload"
          :remove="handleRemove"
          accept=".xlsx,.xls,.csv"
          :multiple="false"
        >
          <p class="ant-upload-drag-icon">
            <inbox-outlined />
          </p>
          <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p class="ant-upload-hint">
            支持 Excel (.xlsx, .xls) 和 CSV 格式文件，单次上传仅支持一个文件
          </p>
        </a-upload-dragger>

        <div class="mt-4">
          <a-alert
            message="文件格式要求"
            type="info"
            show-icon
            class="mb-4"
          >
            <template #description>
              <ul class="mb-0">
                <li>Excel文件请确保数据从第一行开始，包含标题行</li>
                <li>CSV文件请使用UTF-8编码，逗号分隔</li>
                <li>必填字段：用户名、邮箱</li>
                <li>可选字段：姓名、角色、状态、手机号</li>
              </ul>
            </template>
          </a-alert>

          <a-button type="link" @click="downloadTemplate">
            <download-outlined /> 下载模板文件
          </a-button>
        </div>
      </div>

      <!-- 步骤2: 字段映射 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-alert
          message="请配置Excel列与系统字段的对应关系"
          type="info"
          show-icon
          class="mb-4"
        />

        <a-table
          :columns="mappingColumns"
          :data-source="fieldMappings"
          :pagination="false"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'excelColumn'">
              <a-select
                v-model:value="record.excelColumn"
                placeholder="请选择Excel列"
                style="width: 100%"
                :options="excelColumns"
              />
            </template>
            <template v-else-if="column.key === 'required'">
              <a-tag :color="record.required ? 'red' : 'blue'">
                {{ record.required ? '必填' : '可选' }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </div>

      <!-- 步骤3: 数据预览 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-alert
          :message="`共解析到 ${previewData.length} 条用户数据`"
          type="success"
          show-icon
          class="mb-4"
        />

        <a-table
          :columns="previewColumns"
          :data-source="previewData"
          :pagination="{ pageSize: 10 }"
          size="small"
          :scroll="{ y: 300 }"
        />

        <div class="mt-4">
          <a-checkbox v-model:checked="skipErrors">
            跳过错误数据，继续导入有效数据
          </a-checkbox>
        </div>
      </div>

      <!-- 步骤4: 导入结果 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-result
          :status="importResult.success ? 'success' : 'error'"
          :title="importResult.success ? '导入成功' : '导入失败'"
          :sub-title="importResult.message"
        >
          <template #extra>
            <a-descriptions :column="2" size="small">
              <a-descriptions-item label="总计">
                {{ importResult.total }}
              </a-descriptions-item>
              <a-descriptions-item label="成功">
                {{ importResult.successCount }}
              </a-descriptions-item>
              <a-descriptions-item label="失败">
                {{ importResult.failCount }}
              </a-descriptions-item>
              <a-descriptions-item label="跳过">
                {{ importResult.skipCount }}
              </a-descriptions-item>
            </a-descriptions>
          </template>
        </a-result>

        <div v-if="importResult.errors?.length > 0" class="mt-4">
          <a-collapse>
            <a-collapse-panel key="errors" header="错误详情">
              <a-list
                :data-source="importResult.errors"
                size="small"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        第 {{ item.row }} 行：{{ item.message }}
                      </template>
                      <template #description>
                        {{ item.data }}
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </div>

      <!-- 底部操作按钮 -->
      <div class="flex justify-between mt-6 pt-4 border-t">
        <a-button 
          v-if="currentStep > 0"
          @click="prevStep"
        >
          上一步
        </a-button>
        
        <div class="flex gap-2">
          <a-button @click="handleCancel">
            取消
          </a-button>
          
          <a-button
            v-if="currentStep < 3"
            type="primary"
            :disabled="!canNextStep"
            :loading="loading"
            @click="nextStep"
          >
            {{ currentStep === 2 ? '开始导入' : '下一步' }}
          </a-button>
          
          <a-button
            v-if="currentStep === 3"
            type="primary"
            @click="handleFinish"
          >
            完成
          </a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { InboxOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import type { UploadFile } from 'ant-design-vue'

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 当前步骤
const currentStep = ref(0)
const loading = ref(false)

// 文件上传
const fileList = ref<UploadFile[]>([])
const excelColumns = ref<Array<{ label: string; value: string }>>([])

// 字段映射配置
const fieldMappings = ref([
  { field: 'username', fieldName: '用户名', required: true, excelColumn: '' },
  { field: 'email', fieldName: '邮箱', required: true, excelColumn: '' },
  { field: 'fullName', fieldName: '姓名', required: false, excelColumn: '' },
  { field: 'roles', fieldName: '角色', required: false, excelColumn: '' },
  { field: 'status', fieldName: '状态', required: false, excelColumn: '' },
  { field: 'phoneNumber', fieldName: '手机号', required: false, excelColumn: '' }
])

const mappingColumns = [
  { title: '系统字段', dataIndex: 'fieldName', key: 'fieldName' },
  { title: 'Excel列', dataIndex: 'excelColumn', key: 'excelColumn', width: 200 },
  { title: '是否必填', dataIndex: 'required', key: 'required', width: 100 }
]

// 数据预览
const previewData = ref<any[]>([])
const skipErrors = ref(false)

const previewColumns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '姓名', dataIndex: 'fullName', key: 'fullName' },
  { title: '角色', dataIndex: 'roles', key: 'roles' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '手机号', dataIndex: 'phoneNumber', key: 'phoneNumber' }
]

// 导入结果
const importResult = ref({
  success: false,
  message: '',
  total: 0,
  successCount: 0,
  failCount: 0,
  skipCount: 0,
  errors: [] as Array<{ row: number; message: string; data: string }>
})

// 计算属性
const canNextStep = computed(() => {
  switch (currentStep.value) {
    case 0:
      return fileList.value.length > 0
    case 1:
      return fieldMappings.value
        .filter(item => item.required)
        .every(item => item.excelColumn)
    case 2:
      return previewData.value.length > 0
    default:
      return false
  }
})

// 文件上传前处理
const beforeUpload = (file: UploadFile) => {
  const isValidFormat = file.name?.endsWith('.xlsx') || 
                       file.name?.endsWith('.xls') || 
                       file.name?.endsWith('.csv')
  
  if (!isValidFormat) {
    message.error('只支持上传 Excel 或 CSV 格式文件')
    return false
  }

  const isLt10M = (file.size || 0) / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB')
    return false
  }

  // 解析文件内容，获取列信息
  parseFile(file)
  
  return false // 阻止自动上传
}

// 移除文件
const handleRemove = () => {
  fileList.value = []
  excelColumns.value = []
}

// 解析文件
const parseFile = async (file: UploadFile) => {
  try {
    loading.value = true
    // 这里应该调用实际的文件解析API
    // 模拟解析结果
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    excelColumns.value = [
      { label: '第1列', value: 'col1' },
      { label: '第2列', value: 'col2' },
      { label: '第3列', value: 'col3' },
      { label: '第4列', value: 'col4' },
      { label: '第5列', value: 'col5' },
      { label: '第6列', value: 'col6' }
    ]
    
    message.success('文件解析成功')
  } catch (error) {
    message.error('文件解析失败')
  } finally {
    loading.value = false
  }
}

// 下载模板
const downloadTemplate = () => {
  // 创建模板数据
  const templateData = [
    ['用户名', '邮箱', '姓名', '角色', '状态', '手机号'],
    ['user001', 'user001@example.com', '用户一', 'user', 'active', '13800138000'],
    ['user002', 'user002@example.com', '用户二', 'operator', 'active', '13800138001']
  ]
  
  // 这里应该生成实际的Excel文件下载
  console.log('下载模板:', templateData)
  message.info('模板下载功能开发中...')
}

// 步骤控制
const nextStep = async () => {
  switch (currentStep.value) {
    case 0:
      currentStep.value = 1
      break
    case 1:
      await previewImportData()
      currentStep.value = 2
      break
    case 2:
      await executeImport()
      currentStep.value = 3
      break
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 预览导入数据
const previewImportData = async () => {
  try {
    loading.value = true
    
    // 模拟数据解析和预览
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    previewData.value = [
      { 
        username: 'user001', 
        email: 'user001@example.com', 
        fullName: '用户一', 
        roles: 'user', 
        status: 'active', 
        phoneNumber: '13800138000' 
      },
      { 
        username: 'user002', 
        email: 'user002@example.com', 
        fullName: '用户二', 
        roles: 'operator', 
        status: 'active', 
        phoneNumber: '13800138001' 
      }
    ]
    
  } catch (error) {
    message.error('数据解析失败')
  } finally {
    loading.value = false
  }
}

// 执行导入
const executeImport = async () => {
  try {
    loading.value = true
    
    // 模拟导入过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    importResult.value = {
      success: true,
      message: '用户数据导入完成',
      total: previewData.value.length,
      successCount: previewData.value.length - 1,
      failCount: 1,
      skipCount: 0,
      errors: [
        {
          row: 2,
          message: '邮箱地址已存在',
          data: 'user002@example.com'
        }
      ]
    }
    
  } catch (error) {
    importResult.value = {
      success: false,
      message: '导入过程中发生错误',
      total: previewData.value.length,
      successCount: 0,
      failCount: previewData.value.length,
      skipCount: 0,
      errors: []
    }
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
const handleCancel = () => {
  emit('update:visible', false)
  // 重置状态
  currentStep.value = 0
  fileList.value = []
  excelColumns.value = []
  previewData.value = []
  fieldMappings.value.forEach(item => item.excelColumn = '')
}

// 完成导入
const handleFinish = () => {
  emit('success')
  handleCancel()
}
</script>

<style scoped>
.step-content {
  min-height: 300px;
}

.ant-upload-drag {
  background-color: #fafafa;
}
</style>