<template>
  <div class="data-table-container">
    <!-- 表格工具栏 -->
    <TableToolbar
      v-if="showToolbar"
      :title="title"
      :show-selection="showSelection"
      :selected-row-keys="selectedRowKeys"
      :batch-actions="batchActions"
      :show-refresh="showRefresh"
      :show-export="showExport"
      :show-column-setting="showColumnSetting"
      :custom-actions="customActions"
      @refresh="handleRefresh"
      @export="handleExport"
      @column-setting-change="handleColumnSettingChange"
    />
    
    <!-- 数据表格 -->
    <a-table
      :columns="computedColumns"
      :data-source="dataSource.data"
      :loading="dataSource.loading"
      :row-key="rowKey"
      :row-selection="rowSelectionConfig"
      :pagination="paginationConfig"
      :bordered="bordered"
      :size="size"
      :scroll="scroll"
      @change="handleTableChange"
      @row-click="handleRowClick"
    >
      <!-- 自定义渲染插槽 -->
      <template v-for="column in columns" :key="column.key" #[`${column.key}`]="{ text, record, index }">
        <component 
          v-if="column.render"
          :is="column.render"
          :value="text"
          :record="record"
          :index="index"
        />
        <span v-else>{{ text }}</span>
      </template>
      
      <!-- 操作列插槽 -->
      <template #action="{ record, index }">
        <a-space>
          <template v-for="action in actionButtons" :key="action.key">
            <a-button
              v-if="isActionVisible(action, record)"
              :type="action.type || 'link'"
              :size="size"
              :disabled="isActionDisabled(action, record)"
              :loading="action.loading"
              @click="action.onClick(record)"
            >
              <template v-if="action.icon" #icon>
                <component :is="action.icon" />
              </template>
              {{ action.label }}
            </a-button>
          </template>
        </a-space>
      </template>
    </a-table>
    
    <!-- 错误提示 -->
    <a-alert
      v-if="dataSource.error"
      :message="dataSource.error"
      type="error"
      show-icon
      closable
      class="mt-3"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import TableToolbar from './TableToolbar.vue'
import type {
  IDataTableProps,
  ITableColumn,
  IActionButton,
  IBatchAction,
  IExportConfig,
  IPaginationConfig
} from '@/types/common'

// 组件属性定义
interface Props extends IDataTableProps {
  title?: string
  showToolbar?: boolean
  showColumnSetting?: boolean
  actionButtons?: IActionButton[]
  batchActions?: IBatchAction[]
  customActions?: IActionButton[]
  scroll?: { x?: number | string; y?: number | string }
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  showSelection: false,
  showPagination: true,
  showExport: true,
  showRefresh: true,
  showToolbar: true,
  showColumnSetting: true,
  bordered: false,
  size: 'middle',
  actionButtons: () => [],
  batchActions: () => [],
  customActions: () => []
})

// 组件事件定义
const emit = defineEmits<{
  selectionChange: [selectedRowKeys: string[], selectedRows: any[]]
  rowClick: [record: any, index: number]
  sort: [field: string, order: 'ascend' | 'descend' | null]
  filter: [filters: Record<string, any>]
  refresh: []
  export: [config?: IExportConfig]
  columnSettingChange: [columns: string[]]
}>()

// 响应式状态
const selectedRowKeys = ref<string[]>([])
const selectedRows = ref<any[]>([])
const visibleColumns = ref<string[]>([])

// 初始化可见列
watch(() => props.columns, (newColumns) => {
  visibleColumns.value = newColumns.map(col => col.key)
}, { immediate: true })

// 计算属性 - 处理后的列配置
const computedColumns = computed(() => {
  const columns = props.columns.filter(col => visibleColumns.value.includes(col.key))
  
  // 添加操作列
  if (props.actionButtons && props.actionButtons.length > 0) {
    columns.push({
      key: 'action',
      title: '操作',
      dataIndex: 'action',
      width: 200,
      fixed: 'right'
    } as ITableColumn)
  }
  
  return columns.map(col => ({
    ...col,
    sorter: col.sortable ? true : false,
    filterable: col.filterable || false,
    ellipsis: col.ellipsis !== false,
  }))
})

// 计算属性 - 行选择配置
const rowSelectionConfig = computed(() => {
  if (!props.showSelection) return undefined
  
  return {
    selectedRowKeys: selectedRowKeys.value,
    onChange: (keys: string[], rows: any[]) => {
      selectedRowKeys.value = keys
      selectedRows.value = rows
      emit('selectionChange', keys, rows)
    },
    onSelectAll: (selected: boolean, selectedRows: any[], changeRows: any[]) => {
      // 全选/取消全选逻辑
    },
    getCheckboxProps: (record: any) => ({
      disabled: record.disabled,
    })
  }
})

// 计算属性 - 分页配置
const paginationConfig = computed(() => {
  if (!props.showPagination) return false
  
  const defaultPagination: IPaginationConfig = {
    current: 1,
    pageSize: 10,
    total: props.dataSource.total,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: true,
    pageSizeOptions: ['10', '20', '50', '100'],
    onChange: (page: number, pageSize: number) => {
      if (props.pagination?.onChange) {
        props.pagination.onChange(page, pageSize)
      }
    }
  }
  
  return { ...defaultPagination, ...props.pagination }
})

// 表格变化处理
const handleTableChange = (pagination: any, filters: any, sorter: any) => {
  // 处理分页变化
  if (pagination && props.pagination?.onChange) {
    props.pagination.onChange(pagination.current, pagination.pageSize)
  }
  
  // 处理排序变化
  if (sorter && sorter.field) {
    emit('sort', sorter.field, sorter.order)
  }
  
  // 处理过滤变化
  if (filters && Object.keys(filters).length > 0) {
    emit('filter', filters)
  }
}

// 行点击处理
const handleRowClick = (record: any, index: number) => {
  emit('rowClick', record, index)
}

// 刷新处理
const handleRefresh = () => {
  emit('refresh')
}

// 导出处理
const handleExport = (config?: IExportConfig) => {
  const exportData = selectedRowKeys.value.length > 0 ? selectedRows.value : props.dataSource.data
  
  if (exportData.length === 0) {
    message.warning('没有数据可导出')
    return
  }
  
  emit('export', { ...config, customData: exportData })
}

// 列设置变化处理
const handleColumnSettingChange = (columns: string[]) => {
  visibleColumns.value = columns
  emit('columnSettingChange', columns)
}

// 判断操作按钮是否可见
const isActionVisible = (action: IActionButton, record: any): boolean => {
  if (typeof action.visible === 'function') {
    return action.visible(record)
  }
  return action.visible !== false
}

// 判断操作按钮是否禁用
const isActionDisabled = (action: IActionButton, record: any): boolean => {
  if (typeof action.disabled === 'function') {
    return action.disabled(record)
  }
  return action.disabled || false
}

// 清空选择
const clearSelection = () => {
  selectedRowKeys.value = []
  selectedRows.value = []
}

// 获取选中的行
const getSelectedRows = () => {
  return {
    keys: selectedRowKeys.value,
    rows: selectedRows.value
  }
}

// 暴露给父组件的方法
defineExpose({
  clearSelection,
  getSelectedRows
})
</script>

<style scoped>
.data-table-container {
  background: #fff;
  border-radius: 6px;
  padding: 16px;
}

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}

:deep(.ant-table-row-selected) {
  background-color: #e6f7ff;
}

:deep(.ant-pagination) {
  margin-top: 16px;
  text-align: right;
}
</style>