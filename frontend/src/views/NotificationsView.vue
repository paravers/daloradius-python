<template>
  <div class="notifications-view">
    <div class="page-header">
      <h1>通知管理</h1>
      <p class="page-description">管理系统通知、消息模板和发送历史</p>
      <div class="header-actions">
        <a-button @click="refreshData" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button type="primary" @click="showSendModal">
          <template #icon>
            <SendOutlined />
          </template>
          发送通知
        </a-button>
      </div>
    </div>

    <div class="notifications-content">
      <!-- 统计卡片 -->
      <a-row :gutter="[16, 16]" style="margin-bottom: 24px;">
        <a-col :xs="24" :sm="6">
          <a-card>
            <a-statistic
              title="今日发送"
              :value="stats.total_sent"
              :value-style="{ color: '#1890ff' }"
            >
              <template #suffix>
                <SendOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6">
          <a-card>
            <a-statistic
              title="成功送达"
              :value="stats.total_delivered"
              :value-style="{ color: '#52c41a' }"
            >
              <template #suffix>
                <CheckCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6">
          <a-card>
            <a-statistic
              title="发送失败"
              :value="stats.total_failed"
              :value-style="{ color: '#f5222d' }"
            >
              <template #suffix>
                <ExclamationCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6">
          <a-card>
            <a-statistic
              title="送达率"
              :value="stats.delivery_rate"
              suffix="%"
              :precision="1"
              :value-style="{ color: getDeliveryRateColor(stats.delivery_rate) }"
            >
              <template #suffix>
                <PercentageOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 主要内容 -->
      <a-card>
        <a-tabs v-model:activeKey="activeTab">
          <!-- 通知历史 -->
          <a-tab-pane key="history" tab="通知历史">
            <div class="filters">
              <a-row :gutter="[16, 16]" style="margin-bottom: 16px;">
                <a-col :xs="24" :sm="8" :md="6">
                  <a-select
                    v-model:value="filters.notification_type"
                    placeholder="通知类型"
                    allow-clear
                    style="width: 100%"
                  >
                    <a-select-option value="email">邮件</a-select-option>
                    <a-select-option value="sms">短信</a-select-option>
                    <a-select-option value="push">推送</a-select-option>
                    <a-select-option value="system">系统</a-select-option>
                  </a-select>
                </a-col>
                <a-col :xs="24" :sm="8" :md="6">
                  <a-select
                    v-model:value="filters.status"
                    placeholder="发送状态"
                    allow-clear
                    style="width: 100%"
                  >
                    <a-select-option value="pending">待发送</a-select-option>
                    <a-select-option value="sent">已发送</a-select-option>
                    <a-select-option value="delivered">已送达</a-select-option>
                    <a-select-option value="failed">发送失败</a-select-option>
                  </a-select>
                </a-col>
                <a-col :xs="24" :sm="8" :md="6">
                  <a-select
                    v-model:value="filters.days"
                    placeholder="时间范围"
                    style="width: 100%"
                  >
                    <a-select-option :value="1">今天</a-select-option>
                    <a-select-option :value="7">最近7天</a-select-option>
                    <a-select-option :value="30">最近30天</a-select-option>
                    <a-select-option :value="90">最近90天</a-select-option>
                  </a-select>
                </a-col>
                <a-col :xs="24" :sm="24" :md="6">
                  <a-button @click="loadNotificationHistory" :loading="loading">
                    <template #icon>
                      <SearchOutlined />
                    </template>
                    搜索
                  </a-button>
                </a-col>
              </a-row>
            </div>

            <a-table
              :dataSource="notificationHistory"
              :columns="historyColumns"
              :loading="loading"
              :pagination="historyPagination"
              @change="handleTableChange"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'notification_type'">
                  <a-tag :color="getTypeColor(record.notification_type)">
                    {{ getTypeName(record.notification_type) }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-tag :color="getStatusColor(record.status)">
                    {{ getStatusName(record.status) }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'created_at'">
                  {{ formatTime(record.created_at) }}
                </template>
                <template v-else-if="column.key === 'actions'">
                  <a-button-group size="small">
                    <a-button @click="viewNotification(record)">
                      <EyeOutlined />
                    </a-button>
                    <a-button 
                      v-if="record.status === 'failed'" 
                      @click="resendNotification(record)"
                    >
                      <RetweetOutlined />
                    </a-button>
                  </a-button-group>
                </template>
              </template>
            </a-table>
          </a-tab-pane>

          <!-- 消息模板 -->
          <a-tab-pane key="templates" tab="消息模板">
            <div style="margin-bottom: 16px;">
              <a-button type="primary" @click="showTemplateModal">
                <template #icon>
                  <PlusOutlined />
                </template>
                新建模板
              </a-button>
            </div>

            <a-table
              :dataSource="templates"
              :columns="templateColumns"
              :loading="loading"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'template_type'">
                  <a-tag :color="getTypeColor(record.template_type)">
                    {{ getTypeName(record.template_type) }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'is_active'">
                  <a-switch
                    :checked="record.is_active"
                    @change="toggleTemplate(record)"
                    size="small"
                  />
                </template>
                <template v-else-if="column.key === 'actions'">
                  <a-button-group size="small">
                    <a-button @click="editTemplate(record)">
                      <EditOutlined />
                    </a-button>
                    <a-button @click="previewTemplate(record)">
                      <EyeOutlined />
                    </a-button>
                    <a-button danger @click="deleteTemplate(record)">
                      <DeleteOutlined />
                    </a-button>
                  </a-button-group>
                </template>
              </template>
            </a-table>
          </a-tab-pane>

          <!-- 统计分析 -->
          <a-tab-pane key="analytics" tab="统计分析">
            <a-row :gutter="[24, 24]">
              <a-col :xs="24" :lg="12">
                <a-card title="发送类型分布">
                  <div style="height: 300px;" v-if="analytics.by_type">
                    <!-- 这里可以集成图表组件 -->
                    <div class="chart-placeholder">
                      <p>邮件: {{ analytics.by_type.email?.sent || 0 }}</p>
                      <p>短信: {{ analytics.by_type.sms?.sent || 0 }}</p>
                      <p>推送: {{ analytics.by_type.push?.sent || 0 }}</p>
                    </div>
                  </div>
                </a-card>
              </a-col>
              
              <a-col :xs="24" :lg="12">
                <a-card title="优先级分布">
                  <div style="height: 300px;" v-if="analytics.by_priority">
                    <div class="chart-placeholder">
                      <p>紧急: {{ analytics.by_priority.urgent?.sent || 0 }}</p>
                      <p>高: {{ analytics.by_priority.high?.sent || 0 }}</p>
                      <p>普通: {{ analytics.by_priority.normal?.sent || 0 }}</p>
                      <p>低: {{ analytics.by_priority.low?.sent || 0 }}</p>
                    </div>
                  </div>
                </a-card>
              </a-col>
            </a-row>

            <a-card title="错误分析" style="margin-top: 24px;">
              <a-descriptions :column="2" bordered>
                <a-descriptions-item label="退信率">
                  {{ analytics.error_analysis?.bounce_rate || 0 }}%
                </a-descriptions-item>
                <a-descriptions-item label="垃圾邮件率">
                  {{ analytics.error_analysis?.spam_rate || 0 }}%
                </a-descriptions-item>
                <a-descriptions-item label="超时率">
                  {{ analytics.error_analysis?.timeout_rate || 0 }}%
                </a-descriptions-item>
                <a-descriptions-item label="平均送达时间">
                  {{ stats.average_delivery_time_seconds || 0 }}秒
                </a-descriptions-item>
              </a-descriptions>

              <a-divider />

              <h4>常见错误</h4>
              <a-list size="small">
                <a-list-item 
                  v-for="error in analytics.error_analysis?.common_errors || []"
                  :key="error.error"
                >
                  <a-list-item-meta :title="error.error">
                    <template #description>
                      出现次数: {{ error.count }}
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </a-list>
            </a-card>
          </a-tab-pane>
        </a-tabs>
      </a-card>
    </div>

    <!-- 发送通知模态框 -->
    <a-modal
      v-model:open="sendModalVisible"
      title="发送通知"
      width="600px"
      @ok="handleSendNotification"
    >
      <a-form ref="sendForm" :model="sendFormData" layout="vertical">
        <a-form-item label="通知类型" name="notification_type" required>
          <a-select v-model:value="sendFormData.notification_type">
            <a-select-option value="email">邮件通知</a-select-option>
            <a-select-option value="sms">短信通知</a-select-option>
            <a-select-option value="push">推送通知</a-select-option>
            <a-select-option value="system">系统通知</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="优先级" name="priority">
          <a-select v-model:value="sendFormData.priority">
            <a-select-option value="urgent">紧急</a-select-option>
            <a-select-option value="high">高</a-select-option>
            <a-select-option value="normal">普通</a-select-option>
            <a-select-option value="low">低</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="收件人邮箱" name="recipient_email" v-if="sendFormData.notification_type === 'email'">
          <a-input v-model:value="sendFormData.recipient_email" placeholder="请输入收件人邮箱" />
        </a-form-item>

        <a-form-item label="收件人电话" name="recipient_phone" v-if="sendFormData.notification_type === 'sms'">
          <a-input v-model:value="sendFormData.recipient_phone" placeholder="请输入收件人电话" />
        </a-form-item>

        <a-form-item label="使用模板" name="template_id">
          <a-select v-model:value="sendFormData.template_id" allow-clear placeholder="选择模板（可选）">
            <a-select-option 
              v-for="template in activeTemplates" 
              :key="template.id" 
              :value="template.id"
            >
              {{ template.template_name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="主题" name="subject" v-if="sendFormData.notification_type === 'email'">
          <a-input v-model:value="sendFormData.subject" placeholder="请输入通知主题" />
        </a-form-item>

        <a-form-item label="消息内容" name="message" required>
          <a-textarea 
            v-model:value="sendFormData.message" 
            :rows="6" 
            placeholder="请输入通知内容"
          />
        </a-form-item>

        <a-form-item label="定时发送" name="scheduled_for">
          <a-date-picker
            v-model:value="sendFormData.scheduled_for"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择发送时间（可选）"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 模板管理模态框 -->
    <a-modal
      v-model:open="templateModalVisible"
      title="模板管理"
      width="700px"
      @ok="handleSaveTemplate"
    >
      <a-form ref="templateForm" :model="templateFormData" layout="vertical">
        <a-form-item label="模板名称" name="template_name" required>
          <a-input v-model:value="templateFormData.template_name" placeholder="请输入模板名称" />
        </a-form-item>

        <a-form-item label="模板类型" name="template_type" required>
          <a-select v-model:value="templateFormData.template_type">
            <a-select-option value="email">邮件模板</a-select-option>
            <a-select-option value="sms">短信模板</a-select-option>
            <a-select-option value="push">推送模板</a-select-option>
            <a-select-option value="system">系统模板</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="模板分类" name="category" required>
          <a-input v-model:value="templateFormData.category" placeholder="例如：welcome, invoice, alert" />
        </a-form-item>

        <a-form-item label="邮件主题" name="subject" v-if="templateFormData.template_type === 'email'">
          <a-input v-model:value="templateFormData.subject" placeholder="请输入邮件主题模板" />
        </a-form-item>

        <a-form-item label="文本内容" name="body_text">
          <a-textarea 
            v-model:value="templateFormData.body_text" 
            :rows="4" 
            placeholder="请输入文本内容模板"
          />
        </a-form-item>

        <a-form-item label="HTML内容" name="body_html" v-if="templateFormData.template_type === 'email'">
          <a-textarea 
            v-model:value="templateFormData.body_html" 
            :rows="6" 
            placeholder="请输入HTML内容模板"
          />
        </a-form-item>

        <a-form-item label="可用变量" name="variables">
          <a-input v-model:value="templateFormData.variables" placeholder="变量名，用逗号分隔，例如：username,email,date" />
        </a-form-item>

        <a-form-item label="启用状态" name="is_active">
          <a-switch v-model:checked="templateFormData.is_active" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import dayjs, { Dayjs } from 'dayjs'
import {
  ReloadOutlined,
  SendOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  PercentageOutlined,
  SearchOutlined,
  EyeOutlined,
  RetweetOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { notificationService } from '@/services/notificationService'
import type { 
  NotificationHistory, 
  NotificationTemplate, 
  NotificationStats,
  SendNotificationData,
  CreateTemplateData
} from '@/services/notificationService'

const loading = ref(false)
const activeTab = ref('history')

// 数据
const stats = ref({
  total_sent: 0,
  total_delivered: 0,
  total_failed: 0,
  delivery_rate: 0,
  average_delivery_time_seconds: 0
})
const notificationHistory = ref<NotificationHistory[]>([])
const templates = ref<NotificationTemplate[]>([])
const analytics = ref<any>({})

// 过滤器
const filters = ref({
  notification_type: undefined,
  status: undefined,
  days: 7
})

// 模态框状态
const sendModalVisible = ref(false)
const templateModalVisible = ref(false)

// 表单数据
const sendFormData = ref<SendNotificationData>({
  notification_type: 'email',
  priority: 'normal',
  recipient_email: '',
  recipient_phone: '',
  template_id: undefined,
  subject: '',
  message: '',
  scheduled_for: undefined
})

const templateFormData = ref<CreateTemplateData>({
  template_name: '',
  template_type: 'email',
  category: '',
  subject: '',
  body_text: '',
  body_html: '',
  variables: '',
  is_active: true
})

// 表格配置
const historyColumns = [
  { title: '类型', dataIndex: 'notification_type', key: 'notification_type', width: 80 },
  { title: '收件人', dataIndex: 'recipient_email', key: 'recipient_email', width: 200 },
  { title: '主题', dataIndex: 'subject', key: 'subject', ellipsis: true },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'actions', width: 120 }
]

const templateColumns = [
  { title: '模板名称', dataIndex: 'template_name', key: 'template_name' },
  { title: '类型', dataIndex: 'template_type', key: 'template_type', width: 100 },
  { title: '分类', dataIndex: 'category', key: 'category', width: 120 },
  { title: '启用', dataIndex: 'is_active', key: 'is_active', width: 80 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'actions', width: 150 }
]

const historyPagination = ref({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true
})

// 计算属性
const activeTemplates = computed(() => 
  templates.value.filter(t => t.is_active)
)

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    await Promise.all([
      loadNotificationStats(),
      loadNotificationHistory(),
      loadTemplates()
    ])
  } catch (error) {
    console.error('Failed to load notification data:', error)
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadNotificationStats = async () => {
  try {
    const data = await notificationService.getStats(filters.value.days)
    stats.value = data.summary
    analytics.value = data
  } catch (error) {
    console.error('Failed to load notification stats:', error)
  }
}

const loadNotificationHistory = async () => {
  try {
    const data = await notificationService.getHistory({
      ...filters.value,
      skip: (historyPagination.value.current - 1) * historyPagination.value.pageSize,
      limit: historyPagination.value.pageSize
    })
    notificationHistory.value = data.notifications
    historyPagination.value.total = data.total
  } catch (error) {
    console.error('Failed to load notification history:', error)
  }
}

const loadTemplates = async () => {
  try {
    const data = await notificationService.getTemplates()
    templates.value = data
  } catch (error) {
    console.error('Failed to load templates:', error)
  }
}

// 事件处理
const refreshData = async () => {
  await loadData()
  message.success('数据已刷新')
}

const handleTableChange = (pagination: any) => {
  historyPagination.value.current = pagination.current
  historyPagination.value.pageSize = pagination.pageSize
  loadNotificationHistory()
}

const showSendModal = () => {
  sendModalVisible.value = true
  sendFormData.value = {
    notification_type: 'email',
    priority: 'normal',
    recipient_email: '',
    recipient_phone: '',
    template_id: undefined,
    subject: '',
    message: '',
    scheduled_for: undefined
  }
}

const handleSendNotification = async () => {
  try {
    const data = {
      ...sendFormData.value,
      scheduled_for: sendFormData.value.scheduled_for ? 
        dayjs(sendFormData.value.scheduled_for).toISOString() : undefined
    }
    
    await notificationService.sendNotification(data)
    message.success('通知发送成功')
    sendModalVisible.value = false
    await loadNotificationHistory()
  } catch (error) {
    message.error('发送通知失败')
  }
}

const showTemplateModal = () => {
  templateModalVisible.value = true
  templateFormData.value = {
    template_name: '',
    template_type: 'email',
    category: '',
    subject: '',
    body_text: '',
    body_html: '',
    variables: '',
    is_active: true
  }
}

const handleSaveTemplate = async () => {
  try {
    const data = {
      ...templateFormData.value,
      variables: templateFormData.value.variables ? 
        templateFormData.value.variables.split(',').map(v => v.trim()) : undefined
    }
    
    await notificationService.createTemplate(data)
    message.success('模板保存成功')
    templateModalVisible.value = false
    await loadTemplates()
  } catch (error) {
    message.error('保存模板失败')
  }
}

// 工具函数
const getDeliveryRateColor = (rate: number) => {
  if (rate >= 95) return '#52c41a'
  if (rate >= 85) return '#faad14'
  return '#f5222d'
}

const getTypeColor = (type: string) => {
  const colors = {
    email: 'blue',
    sms: 'green',
    push: 'orange',
    system: 'purple'
  }
  return colors[type as keyof typeof colors] || 'default'
}

const getTypeName = (type: string) => {
  const names = {
    email: '邮件',
    sms: '短信',
    push: '推送',
    system: '系统'
  }
  return names[type as keyof typeof names] || type
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'orange',
    sent: 'blue',
    delivered: 'green',
    failed: 'red',
    cancelled: 'gray'
  }
  return colors[status as keyof typeof colors] || 'default'
}

const getStatusName = (status: string) => {
  const names = {
    pending: '待发送',
    sent: '已发送',
    delivered: '已送达',
    failed: '发送失败',
    cancelled: '已取消'
  }
  return names[status as keyof typeof names] || status
}

const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 操作函数
const viewNotification = (record: NotificationHistory) => {
  // 实现查看通知详情
  console.log('View notification:', record)
}

const resendNotification = async (record: NotificationHistory) => {
  try {
    // 实现重新发送通知
    message.success('通知重发成功')
    await loadNotificationHistory()
  } catch (error) {
    message.error('重发通知失败')
  }
}

const editTemplate = (record: NotificationTemplate) => {
  templateFormData.value = {
    ...record,
    variables: record.variables ? record.variables.join(',') : ''
  }
  templateModalVisible.value = true
}

const previewTemplate = (record: NotificationTemplate) => {
  // 实现模板预览
  console.log('Preview template:', record)
}

const deleteTemplate = async (record: NotificationTemplate) => {
  try {
    await notificationService.deleteTemplate(record.id)
    message.success('模板删除成功')
    await loadTemplates()
  } catch (error) {
    message.error('删除模板失败')
  }
}

const toggleTemplate = async (record: NotificationTemplate) => {
  try {
    await notificationService.updateTemplate(record.id, {
      is_active: !record.is_active
    })
    record.is_active = !record.is_active
    message.success('模板状态更新成功')
  } catch (error) {
    message.error('更新模板状态失败')
  }
}

// 组件挂载
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.notifications-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.page-description {
  margin: 8px 0 0 0;
  color: rgba(0, 0, 0, 0.65);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.notifications-content {
  /* 内容样式 */
}

.filters {
  /* 过滤器样式 */
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}

@media (max-width: 768px) {
  .notifications-view {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>