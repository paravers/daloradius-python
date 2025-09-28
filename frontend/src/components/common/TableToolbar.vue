<template>
  <div class="table-toolbar">
    <div class="toolbar-left">
      <!-- 标题 -->
      <h3 v-if="title" class="toolbar-title">{{ title }}</h3>
      
      <!-- 批量操作区域 -->
      <div v-if="showSelection && selectedRowKeys.length > 0" class="batch-actions">
        <span class="selection-info">
          已选择 <strong>{{ selectedRowKeys.length }}</strong> 项
          <a @click="clearSelection" class="clear-selection">清空</a>
        </span>
        
        <a-space class="ml-3">
          <template v-for="action in batchActions" :key="action.key">
            <a-button
              :type="action.type || 'default'"
              :disabled="action.disabled"
              :loading="action.loading"
              @click="handleBatchAction(action)"
            >
              <template v-if="action.icon" #icon>
                <component :is="action.icon" />
              </template>
              {{ action.label }}
            </a-button>
          </template>
        </a-space>
      </div>
    </div>
    
    <div class="toolbar-right">
      <!-- 自定义操作按钮 -->
      <a-space>
        <template v-for="action in customActions" :key="action.key">
          <a-button
            :type="action.type || 'default'"
            :disabled="isActionDisabled(action)"
            :loading="action.loading"
            @click="action.onClick"
          >
            <template v-if="action.icon" #icon>
              <component :is="action.icon" />
            </template>
            {{ action.label }}
          </a-button>
        </template>
        
        <!-- 刷新按钮 -->
        <a-button
          v-if="showRefresh"
          type="text"
          @click="handleRefresh"
          title="刷新"
        >
          <template #icon>
            <ReloadOutlined />
          </template>
        </a-button>
        
        <!-- 导出按钮 -->
        <a-dropdown v-if="showExport">
          <a-button type="text" title="导出">
            <template #icon>
              <ExportOutlined />
            </template>
          </a-button>
          <template #overlay>
            <a-menu @click="handleExportMenuClick">
              <a-menu-item key="xlsx">
                <FileExcelOutlined />
                导出 Excel
              </a-menu-item>
              <a-menu-item key="csv">
                <FileCsvOutlined />
                导出 CSV
              </a-menu-item>
              <a-menu-item key="pdf">
                <FilePdfOutlined />
                导出 PDF
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
        
        <!-- 列设置按钮 -->
        <a-dropdown v-if="showColumnSetting" placement="bottomRight">
          <a-button type="text" title="列设置">
            <template #icon>
              <SettingOutlined />
            </template>
          </a-button>
          <template #overlay>
            <div class="column-setting-panel">
              <div class="column-setting-header">
                <span>列设置</span>
                <a-button type="link" size="small" @click="resetColumnSetting">
                  重置
                </a-button>
              </div>
              <a-checkbox-group
                v-model:value="visibleColumns"
                @change="handleColumnChange"
              >
                <div v-for="column in allColumns" :key="column.key" class="column-setting-item">
                  <a-checkbox :value="column.key">
                    {{ column.title }}
                  </a-checkbox>
                </div>
              </a-checkbox-group>
            </div>
          </template>
        </a-dropdown>
      </a-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Modal } from 'ant-design-vue'
import {
  ReloadOutlined,
  ExportOutlined,
  SettingOutlined,
  FileExcelOutlined,
  FileCsvOutlined,
  FilePdfOutlined,
} from '@ant-design/icons-vue'
import type {
  ITableToolbarProps,
  IBatchAction,
  IActionButton,
  IExportConfig,
  ITableColumn
} from '@/types/common'

// 组件属性定义
interface Props extends ITableToolbarProps {
  allColumns?: ITableColumn[]
}

const props = withDefaults(defineProps<Props>(), {
  selectedRowKeys: () => [],
  batchActions: () => [],
  customActions: () => [],
  allColumns: () => []
})

// 组件事件定义
const emit = defineEmits<{
  refresh: []
  export: [config?: IExportConfig]
  columnSettingChange: [columns: string[]]
  clearSelection: []
}>()

// 响应式状态
const visibleColumns = ref<string[]>([])

// 初始化可见列
watch(() => props.allColumns, (columns) => {
  visibleColumns.value = columns.map(col => col.key)
}, { immediate: true })

// 处理批量操作
const handleBatchAction = (action: IBatchAction) => {
  if (action.confirmText) {
    Modal.confirm({
      title: '确认操作',
      content: action.confirmText,
      onOk: () => {
        action.onClick(props.selectedRowKeys, [])
      }
    })
  } else {
    action.onClick(props.selectedRowKeys, [])
  }
}

// 处理刷新
const handleRefresh = () => {
  emit('refresh')
}

// 处理导出菜单点击
const handleExportMenuClick = ({ key }: { key: string }) => {
  const config: IExportConfig = {
    format: key as 'xlsx' | 'csv' | 'pdf',
    filename: `export_${new Date().toISOString().split('T')[0]}`
  }
  emit('export', config)
}

// 处理列设置变化
const handleColumnChange = (checkedValues: string[]) => {
  emit('columnSettingChange', checkedValues)
}

// 重置列设置
const resetColumnSetting = () => {
  const allKeys = props.allColumns.map(col => col.key)
  visibleColumns.value = allKeys
  emit('columnSettingChange', allKeys)
}

// 清空选择
const clearSelection = () => {
  emit('clearSelection')
}

// 判断操作按钮是否禁用
const isActionDisabled = (action: IActionButton): boolean => {
  if (typeof action.disabled === 'function') {
    return action.disabled({})
  }
  return action.disabled || false
}
</script>

<style scoped>
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.toolbar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.batch-actions {
  display: flex;
  align-items: center;
  margin-left: 24px;
}

.selection-info {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
}

.clear-selection {
  margin-left: 8px;
  color: #1890ff;
  cursor: pointer;
}

.clear-selection:hover {
  color: #40a9ff;
}

.column-setting-panel {
  width: 200px;
  padding: 8px 0;
}

.column-setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 8px;
}

.column-setting-item {
  padding: 4px 12px;
}

.column-setting-item:hover {
  background: #f5f5f5;
}

:deep(.ant-checkbox-group) {
  width: 100%;
}

:deep(.ant-checkbox-wrapper) {
  width: 100%;
  margin-left: 0;
}
</style>