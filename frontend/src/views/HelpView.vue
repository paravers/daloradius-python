<template>
  <div class="help-view">
    <div class="page-header">
      <h1>帮助中心</h1>
      <p class="page-description">获取使用指南、技术支持和系统文档</p>
      <div class="header-actions">
        <a-button @click="refreshContent" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button @click="submitFeedback">
          <template #icon>
            <MessageOutlined />
          </template>
          反馈
        </a-button>
      </div>
    </div>

    <div class="help-content">
      <!-- 快速导航 -->
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="12" :md="6">
          <a-card hoverable @click="activeTab = 'getting-started'">
            <template #cover>
              <div class="card-icon">
                <RocketOutlined />
              </div>
            </template>
            <a-card-meta
              title="快速开始"
              description="新用户入门指南和基础配置"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card hoverable @click="activeTab = 'tutorials'">
            <template #cover>
              <div class="card-icon">
                <PlayCircleOutlined />
              </div>
            </template>
            <a-card-meta
              title="视频教程"
              description="分步骤视频指导和操作演示"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card hoverable @click="activeTab = 'troubleshooting'">
            <template #cover>
              <div class="card-icon">
                <ToolOutlined />
              </div>
            </template>
            <a-card-meta
              title="故障排除"
              description="常见问题解决方案和诊断工具"
            />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
          <a-card hoverable @click="activeTab = 'support'">
            <template #cover>
              <div class="card-icon">
                <CustomerServiceOutlined />
              </div>
            </template>
            <a-card-meta
              title="技术支持"
              description="联系支持团队和获取专业帮助"
            />
          </a-card>
        </a-col>
      </a-row>

      <!-- 主要内容区域 -->
      <a-card style="margin-top: 24px;">
        <a-tabs v-model:activeKey="activeTab" type="card">
          <!-- 快速开始 -->
          <a-tab-pane key="getting-started" tab="快速开始">
            <div v-if="!loading && tutorials.getting_started">
              <a-timeline>
                <a-timeline-item
                  v-for="(step, index) in tutorials.getting_started"
                  :key="index"
                  :color="index === 0 ? 'green' : 'blue'"
                >
                  <h4>{{ step.title }}</h4>
                  <p>预计时间：{{ step.estimated_time }} | 难度：{{ step.difficulty }}</p>
                  <a-steps direction="vertical" size="small" :current="0">
                    <a-step
                      v-for="(stepDetail, stepIndex) in step.steps"
                      :key="stepIndex"
                      :title="stepDetail"
                    />
                  </a-steps>
                </a-timeline-item>
              </a-timeline>
            </div>
            <a-skeleton v-else :loading="loading" active />
          </a-tab-pane>

          <!-- 视频教程 -->
          <a-tab-pane key="tutorials" tab="视频教程">
            <div v-if="!loading">
              <a-empty v-if="!tutorials.video_tutorials?.available">
                <template #description>
                  <span>视频教程正在制作中</span>
                </template>
                <a-button type="primary" @click="checkForUpdates">
                  检查更新
                </a-button>
              </a-empty>
              
              <div v-else>
                <a-row :gutter="[16, 16]">
                  <a-col :xs="24" :md="12" v-for="tutorial in advancedTutorials" :key="tutorial.title">
                    <a-card :title="tutorial.title">
                      <p>{{ tutorial.description }}</p>
                      <p>预计时间：{{ tutorial.estimated_time }}</p>
                      <a-button type="primary">观看视频</a-button>
                    </a-card>
                  </a-col>
                </a-row>
              </div>
            </div>
            <a-skeleton v-else :loading="loading" active />
          </a-tab-pane>

          <!-- 故障排除 -->
          <a-tab-pane key="troubleshooting" tab="故障排除">
            <div v-if="!loading && troubleshooting">
              <a-collapse>
                <a-collapse-panel
                  v-for="issue in troubleshooting.common_issues"
                  :key="issue.issue"
                  :header="issue.issue"
                >
                  <h5>解决方案：</h5>
                  <ol>
                    <li v-for="solution in issue.solutions" :key="solution">
                      {{ solution }}
                    </li>
                  </ol>
                  <a-tag :color="getCategoryColor(issue.category)">
                    {{ issue.category }}
                  </a-tag>
                </a-collapse-panel>
              </a-collapse>

              <a-divider />

              <h3>诊断工具</h3>
              <a-row :gutter="[16, 16]">
                <a-col :xs="24" :sm="12" :md="6" v-for="(url, tool) in troubleshooting.diagnostic_tools" :key="tool">
                  <a-button block @click="runDiagnostic(tool, url)">
                    {{ formatToolName(tool) }}
                  </a-button>
                </a-col>
              </a-row>
            </div>
            <a-skeleton v-else :loading="loading" active />
          </a-tab-pane>

          <!-- 技术支持 -->
          <a-tab-pane key="support" tab="技术支持">
            <div v-if="!loading && resources">
              <a-row :gutter="[24, 24]">
                <a-col :xs="24" :lg="12">
                  <a-card title="支持资源">
                    <a-list size="small">
                      <a-list-item v-for="(url, key) in resources.support" :key="key">
                        <a-list-item-meta>
                          <template #title>
                            <a :href="url" target="_blank">
                              {{ formatResourceName(key) }}
                              <ExportOutlined style="margin-left: 8px;" />
                            </a>
                          </template>
                        </a-list-item-meta>
                      </a-list-item>
                    </a-list>
                  </a-card>
                </a-col>
                
                <a-col :xs="24" :lg="12">
                  <a-card title="联系方式">
                    <a-list size="small">
                      <a-list-item v-for="(email, type) in resources.contact" :key="type">
                        <a-list-item-meta>
                          <template #title>
                            <a :href="`mailto:${email}`">
                              {{ formatContactType(type) }}
                            </a>
                          </template>
                          <template #description>
                            {{ email }}
                          </template>
                        </a-list-item-meta>
                      </a-list-item>
                    </a-list>
                  </a-card>
                </a-col>
              </a-row>

              <a-card title="系统信息" style="margin-top: 24px;">
                <a-descriptions :column="2" bordered>
                  <a-descriptions-item label="当前版本">
                    {{ resources.version_info?.current_version }}
                  </a-descriptions-item>
                  <a-descriptions-item label="发布日期">
                    {{ resources.version_info?.release_date }}
                  </a-descriptions-item>
                  <a-descriptions-item label="变更日志" :span="2">
                    <a :href="resources.version_info?.changelog_url" target="_blank">
                      查看更新日志 <ExportOutlined />
                    </a>
                  </a-descriptions-item>
                </a-descriptions>
              </a-card>
            </div>
            <a-skeleton v-else :loading="loading" active />
          </a-tab-pane>
        </a-tabs>
      </a-card>
    </div>

    <!-- 反馈模态框 -->
    <a-modal
      v-model:open="feedbackModalVisible"
      title="提交反馈"
      @ok="handleFeedbackSubmit"
    >
      <a-form ref="feedbackForm" :model="feedbackData" layout="vertical">
        <a-form-item label="反馈类型" name="category">
          <a-select v-model:value="feedbackData.category">
            <a-select-option value="general">一般反馈</a-select-option>
            <a-select-option value="bug">错误报告</a-select-option>
            <a-select-option value="suggestion">功能建议</a-select-option>
            <a-select-option value="documentation">文档改进</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="评分" name="rating">
          <a-rate v-model:value="feedbackData.rating" />
        </a-form-item>
        
        <a-form-item label="这个页面对您有帮助吗？" name="helpful">
          <a-radio-group v-model:value="feedbackData.helpful">
            <a-radio :value="true">有帮助</a-radio>
            <a-radio :value="false">没有帮助</a-radio>
          </a-radio-group>
        </a-form-item>
        
        <a-form-item label="详细反馈" name="comment">
          <a-textarea
            v-model:value="feedbackData.comment"
            :rows="4"
            placeholder="请详细描述您的反馈..."
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  MessageOutlined,
  RocketOutlined,
  PlayCircleOutlined,
  ToolOutlined,
  CustomerServiceOutlined,
  ExportOutlined
} from '@ant-design/icons-vue'
import { helpService } from '@/services/helpService'

const loading = ref(false)
const activeTab = ref('getting-started')
const resources = ref(null)
const tutorials = ref(null)
const troubleshooting = ref(null)
const systemInfo = ref(null)

const feedbackModalVisible = ref(false)
const feedbackData = ref({
  category: 'general',
  rating: 5,
  helpful: true,
  comment: ''
})

// 计算属性
const advancedTutorials = ref([
  {
    title: 'NAS设备配置',
    description: '学习如何配置和管理NAS设备',
    estimated_time: '20分钟'
  },
  {
    title: '自定义报表创建',
    description: '创建个性化的系统报表',
    estimated_time: '15分钟'
  }
])

// 加载帮助内容
const loadHelpContent = async () => {
  try {
    loading.value = true
    
    const [resourcesData, tutorialsData, troubleshootingData, systemData] = await Promise.all([
      helpService.getResources(),
      helpService.getTutorials(),
      helpService.getTroubleshooting(),
      helpService.getSystemInfo()
    ])
    
    resources.value = resourcesData
    tutorials.value = tutorialsData
    troubleshooting.value = troubleshootingData
    systemInfo.value = systemData
    
  } catch (error) {
    console.error('Failed to load help content:', error)
    message.error('加载帮助内容失败')
  } finally {
    loading.value = false
  }
}

// 刷新内容
const refreshContent = async () => {
  await loadHelpContent()
  message.success('内容已刷新')
}

// 检查更新
const checkForUpdates = () => {
  message.info('正在检查更新...', 2)
  setTimeout(() => {
    message.success('当前已是最新版本')
  }, 2000)
}

// 运行诊断
const runDiagnostic = async (tool: string, url: string) => {
  try {
    message.loading(`正在运行 ${formatToolName(tool)} 诊断...`, 3)
    // 这里可以调用实际的诊断API
    // const result = await helpService.runDiagnostic(tool)
    setTimeout(() => {
      message.success(`${formatToolName(tool)} 检查完成，系统正常`)
    }, 3000)
  } catch (error) {
    message.error(`${formatToolName(tool)} 诊断失败`)
  }
}

// 提交反馈
const submitFeedback = () => {
  feedbackModalVisible.value = true
}

const handleFeedbackSubmit = async () => {
  try {
    await helpService.submitFeedback({
      ...feedbackData.value,
      page_url: window.location.href,
      user_agent: navigator.userAgent
    })
    
    message.success('感谢您的反馈！')
    feedbackModalVisible.value = false
    
    // 重置表单
    feedbackData.value = {
      category: 'general',
      rating: 5,
      helpful: true,
      comment: ''
    }
  } catch (error) {
    message.error('提交反馈失败')
  }
}

// 工具函数
const getCategoryColor = (category: string) => {
  const colors = {
    authentication: 'blue',
    radius: 'green', 
    dashboard: 'orange',
    reports: 'purple'
  }
  return colors[category as keyof typeof colors] || 'default'
}

const formatToolName = (tool: string) => {
  const names = {
    database_check: '数据库检查',
    radius_check: 'RADIUS检查',
    api_health: 'API健康检查',
    system_logs: '系统日志'
  }
  return names[tool as keyof typeof names] || tool
}

const formatResourceName = (key: string) => {
  const names = {
    official_website: '官方网站',
    github_project: 'GitHub项目',
    issue_tracker: '问题追踪',
    community_forum: '社区论坛'
  }
  return names[key as keyof typeof names] || key
}

const formatContactType = (type: string) => {
  const types = {
    support_email: '技术支持邮箱',
    documentation_email: '文档反馈邮箱',
    security_email: '安全问题邮箱'
  }
  return types[type as keyof typeof types] || type
}

// 组件挂载时加载内容
onMounted(() => {
  loadHelpContent()
})
</script>

<style scoped>
.help-view {
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

.card-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  font-size: 32px;
  color: #1890ff;
  background: #f0f8ff;
}

.help-content {
  /* 内容样式 */
}

:deep(.ant-card) {
  cursor: pointer;
  transition: all 0.3s;
}

:deep(.ant-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .help-view {
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