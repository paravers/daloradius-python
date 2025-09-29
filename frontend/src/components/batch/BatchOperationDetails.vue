<template>
  <div class="batch-operation-details">
    <!-- Basic Information -->
    <div class="section">
      <h4>基本信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <label>操作ID:</label>
          <span>{{ operation.id }}</span>
        </div>
        <div class="info-item">
          <label>操作名称:</label>
          <span>{{ operation.batch_name }}</span>
        </div>
        <div class="info-item">
          <label>操作类型:</label>
          <span>{{ getOperationTypeLabel(operation.operation_type) }}</span>
        </div>
        <div class="info-item">
          <label>状态:</label>
          <StatusTag :status="operation.status" />
        </div>
        <div class="info-item">
          <label>Hotspot ID:</label>
          <span>{{ operation.hotspot_id || '无' }}</span>
        </div>
      </div>
      
      <div v-if="operation.batch_description" class="description">
        <label>描述:</label>
        <p>{{ operation.batch_description }}</p>
      </div>
    </div>

    <!-- Progress Information -->
    <div class="section">
      <h4>执行进度</h4>
      <div class="progress-info">
        <div class="progress-stats">
          <div class="stat-item">
            <div class="stat-value">{{ operation.total_count }}</div>
            <div class="stat-label">总计</div>
          </div>
          <div class="stat-item success">
            <div class="stat-value">{{ operation.success_count }}</div>
            <div class="stat-label">成功</div>
          </div>
          <div class="stat-item failure">
            <div class="stat-value">{{ operation.failure_count }}</div>
            <div class="stat-label">失败</div>
          </div>
        </div>
        
        <div class="progress-bar">
          <div class="progress-track">
            <div 
              class="progress-fill success"
              :style="{ width: `${successPercentage}%` }"
            ></div>
            <div 
              class="progress-fill failure"
              :style="{ width: `${failurePercentage}%`, left: `${successPercentage}%` }"
            ></div>
          </div>
          <div class="progress-labels">
            <span class="success">成功: {{ successPercentage.toFixed(1) }}%</span>
            <span class="failure">失败: {{ failurePercentage.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Time Information -->
    <div class="section">
      <h4>时间信息</h4>
      <div class="info-grid">
        <div class="info-item">
          <label>创建时间:</label>
          <span>{{ formatDateTime(operation.created_at) }}</span>
        </div>
        <div class="info-item">
          <label>更新时间:</label>
          <span>{{ formatDateTime(operation.updated_at) }}</span>
        </div>
        <div v-if="operation.started_at" class="info-item">
          <label>开始时间:</label>
          <span>{{ formatDateTime(operation.started_at) }}</span>
        </div>
        <div v-if="operation.completed_at" class="info-item">
          <label>完成时间:</label>
          <span>{{ formatDateTime(operation.completed_at) }}</span>
        </div>
      </div>
      
      <div v-if="executionDuration" class="info-item">
        <label>执行时长:</label>
        <span>{{ executionDuration }}</span>
      </div>
    </div>

    <!-- Operation Details -->
    <div v-if="operation.operation_details" class="section">
      <h4>操作详情</h4>
      <div class="details-content">
        <div v-if="operation.operation_details.executed_by" class="info-item">
          <label>执行者:</label>
          <span>{{ operation.operation_details.executed_by }}</span>
        </div>
        
        <div v-if="operation.operation_details.target_ids" class="info-item">
          <label>目标对象 ({{ operation.operation_details.target_ids.length }} 个):</label>
          <div class="target-ids">
            <Tag 
              v-for="id in displayTargetIds" 
              :key="id" 
              class="target-tag"
            >
              {{ id }}
            </Tag>
            <Tag 
              v-if="hiddenTargetCount > 0" 
              class="more-tag"
              @click="showAllTargets = !showAllTargets"
            >
              {{ showAllTargets ? '收起' : `+${hiddenTargetCount} 更多` }}
            </Tag>
          </div>
        </div>
        
        <div v-if="operation.operation_details.operation_data" class="info-item">
          <label>操作数据:</label>
          <pre class="json-display">{{ JSON.stringify(operation.operation_details.operation_data, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- Error Information -->
    <div v-if="operation.error_message" class="section error-section">
      <h4>错误信息</h4>
      <div class="error-message">
        <Icon name="exclamation-circle" class="error-icon" />
        <span>{{ operation.error_message }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions">
      <Button v-if="canRetry" @click="handleRetry" type="primary">
        <Icon name="redo" />
        重试操作
      </Button>
      <Button v-if="canCancel" @click="handleCancel" danger>
        <Icon name="stop" />
        取消操作
      </Button>
      <Button @click="handleDownloadLog">
        <Icon name="download" />
        下载日志
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { BatchHistoryResponse } from '@/types/batch'
import StatusTag from '@/components/common/StatusTag.vue'
import Tag from '@/components/common/Tag.vue'
import Button from '@/components/common/Button.vue'
import Icon from '@/components/common/Icon.vue'

interface Props {
  operation: BatchHistoryResponse
}

const props = defineProps<Props>()
const showAllTargets = ref(false)

// Computed
const successPercentage = computed(() => {
  if (props.operation.total_count === 0) return 0
  return (props.operation.success_count / props.operation.total_count) * 100
})

const failurePercentage = computed(() => {
  if (props.operation.total_count === 0) return 0
  return (props.operation.failure_count / props.operation.total_count) * 100
})

const executionDuration = computed(() => {
  if (!props.operation.started_at || !props.operation.completed_at) return null
  
  const start = new Date(props.operation.started_at)
  const end = new Date(props.operation.completed_at)
  const duration = end.getTime() - start.getTime()
  
  const seconds = Math.floor(duration / 1000) % 60
  const minutes = Math.floor(duration / (1000 * 60)) % 60
  const hours = Math.floor(duration / (1000 * 60 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds}s`
  } else {
    return `${seconds}s`
  }
})

const displayTargetIds = computed(() => {
  const targetIds = props.operation.operation_details?.target_ids || []
  if (showAllTargets.value || targetIds.length <= 10) {
    return targetIds
  }
  return targetIds.slice(0, 10)
})

const hiddenTargetCount = computed(() => {
  const targetIds = props.operation.operation_details?.target_ids || []
  return Math.max(0, targetIds.length - 10)
})

const canRetry = computed(() => {
  return ['failed', 'cancelled'].includes(props.operation.status)
})

const canCancel = computed(() => {
  return ['pending', 'running'].includes(props.operation.status)
})

// Methods
const getOperationTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'user_create': '用户创建',
    'user_delete': '用户删除',
    'user_update': '用户更新',
    'user_activate': '用户激活',
    'user_deactivate': '用户停用',
    'nas_delete': 'NAS删除',
    'nas_update': 'NAS更新',
    'group_delete': '组删除',
    'group_update': '组更新',
    'group_add_users': '组添加用户',
    'group_remove_users': '组移除用户'
  }
  return typeMap[type] || type
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const handleRetry = () => {
  // TODO: Implement retry logic
  console.log('Retrying operation:', props.operation.id)
}

const handleCancel = () => {
  // TODO: Implement cancel logic
  console.log('Cancelling operation:', props.operation.id)
}

const handleDownloadLog = () => {
  // TODO: Implement download log logic
  console.log('Downloading log for operation:', props.operation.id)
}
</script>

<style scoped>
.batch-operation-details {
  padding: 20px 0;
}

.section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-weight: 500;
  color: #595959;
  font-size: 13px;
}

.info-item span {
  color: #262626;
  font-size: 14px;
}

.description {
  margin-top: 16px;
}

.description label {
  font-weight: 500;
  color: #595959;
  font-size: 13px;
  display: block;
  margin-bottom: 8px;
}

.description p {
  margin: 0;
  color: #262626;
  line-height: 1.6;
  background: #fafafa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
}

.stat-item.success .stat-value {
  color: #52c41a;
}

.stat-item.failure .stat-value {
  color: #ff4d4f;
}

.progress-bar {
  width: 100%;
}

.progress-track {
  position: relative;
  width: 100%;
  height: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  position: absolute;
  top: 0;
  height: 100%;
  transition: all 0.3s ease;
}

.progress-fill.success {
  background: #52c41a;
  left: 0;
}

.progress-fill.failure {
  background: #ff4d4f;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
}

.progress-labels .success {
  color: #52c41a;
}

.progress-labels .failure {
  color: #ff4d4f;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.target-ids {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.target-tag {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #389e0d;
}

.more-tag {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #0958d9;
  cursor: pointer;
}

.more-tag:hover {
  background: #bae7ff;
}

.json-display {
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 12px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  color: #262626;
  white-space: pre-wrap;
  word-break: break-all;
}

.error-section {
  border-color: #ffccc7;
  background: #fff2f0;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #ffccc7;
}

.error-section h4 {
  color: #cf1322;
}

.error-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #cf1322;
  font-size: 14px;
  line-height: 1.6;
}

.error-icon {
  color: #ff4d4f;
  margin-top: 2px;
  flex-shrink: 0;
}

.actions {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .batch-operation-details {
    padding: 16px 0;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .progress-stats {
    gap: 20px;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>