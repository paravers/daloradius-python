<template>
  <div class="users-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>用户管理</h1>
      <p class="page-description">管理系统用户和权限</p>
    </div>
    
    <!-- 搜索表单 -->
    <SearchForm
      :fields="searchFields"
      :loading="loading"
      @search="handleSearch"
      @reset="handleSearchReset"
    />
    
    <!-- 数据表格 -->
    <DataTable
      :data-source="dataSource"
      :columns="tableColumns"
      :show-selection="true"
      :show-export="true"
      :show-refresh="true"
      :action-buttons="actionButtons"
      :batch-actions="batchActions"
      :custom-actions="customActions"
      :pagination="paginationConfig"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      @refresh="handleRefresh"
      @export="handleExport"
      @sort="handleSort"
      @filter="handleFilter"
    />
    
    <!-- 用户表单对话框 -->
    <a-modal
      v-model:visible="formVisible"
      :title="formTitle"
      :width="800"
      @ok="handleFormSubmit"
      @cancel="handleFormCancel"
    >
      <DynamicForm
        ref="formRef"
        :fields="formFields"
        :model-value="formModel"
        :columns="2"
        :show-submit-button="false"
        :show-reset-button="false"
        @update:model-value="formModel = $event"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import DynamicForm from '@/components/common/DynamicForm.vue'
import UserImportModal from '@/components/users/UserImportModal.vue'
import OnlineUsersMonitor from '@/components/users/OnlineUsersMonitor.vue'
import { useUserManagement } from '@/composables/useUserManagement'
import { useUserForm } from '@/composables/useUserForm'
import type { 
  ITableColumn,
  IFormField,
  IActionButton,
  IBatchAction,
  IExportConfig
} from '@/types/common'
import type { User } from '@/types'

// 使用组合式函数
const {
  loading,
  dataSource,
  selectedRowKeys,
  selectedRows,
  hasSelectedRows,
  selectedCount,
  fetchUsers,
  refreshUsers,
  searchUsers,
  handlePageChange,
  handleSort,
  handleSelectionChange,
  deleteUser,
  batchDeleteUsers,
  batchUpdateStatus,
  exportUsers,
  resetQuery
} = useUserManagement()

const {
  visible: formVisible,
  loading: formLoading,
  formRef,
  formModel,
  title: formTitle,
  isReadonly,
  openCreateForm,
  openEditForm,
  openViewForm,
  closeForm,
  submitForm,
  getFormFields
} = useUserForm()

// 搜索表单字段配置
const searchFields: IFormField[] = [
  {
    name: 'username',
    type: 'input',
    label: '用户名',
    placeholder: '请输入用户名',
    span: 6
  },
  {
    name: 'email',
    type: 'email',
    label: '邮箱',
    placeholder: '请输入邮箱地址',
    span: 6
  },
  {
    name: 'status',
    type: 'select',
    label: '状态',
    placeholder: '请选择状态',
    span: 6,
    options: [
      { label: '活跃', value: 'active' },
      { label: '非活跃', value: 'inactive' },
      { label: '已暂停', value: 'suspended' }
    ]
  },
  {
    name: 'dateRange',
    type: 'daterange',
    label: '创建时间',
    placeholder: ['开始日期', '结束日期'],
    span: 6,
    advanced: true
  }
]

// 动态获取表单字段配置
const formFields = computed(() => getFormFields())

// 表格列配置
const tableColumns: ITableColumn<User>[] = [
  {
    key: 'id',
    title: 'ID',
    dataIndex: 'id',
    width: 80,
    sortable: true
  },
  {
    key: 'username',
    title: '用户名',
    dataIndex: 'username',
    sortable: true,
    filterable: true
  },
  {
    key: 'email',
    title: '邮箱',
    dataIndex: 'email',
    sortable: true,
    filterable: true
  },
  {
    key: 'fullName',
    title: '姓名',
    dataIndex: 'fullName',
    ellipsis: true
  },
  {
    key: 'status',
    title: '状态',
    dataIndex: 'status',
    width: 100,
    render: (value: string) => {
      const statusConfig = {
        active: { color: 'green', text: '活跃' },
        inactive: { color: 'orange', text: '非活跃' },
        suspended: { color: 'red', text: '已暂停' }
      }
      const config = statusConfig[value as keyof typeof statusConfig]
      return `<a-tag color="${config.color}">${config.text}</a-tag>`
    }
  },
  {
    key: 'roles',
    title: '角色',
    dataIndex: 'roles',
    width: 120,
    render: (roles: string[]) => {
      return roles.map(role => `<a-tag>${role}</a-tag>`).join('')
    }
  },
  {
    key: 'lastLoginAt',
    title: '最后登录',
    dataIndex: 'lastLoginAt',
    width: 150,
    sortable: true
  },
  {
    key: 'createdAt',
    title: '创建时间',
    dataIndex: 'createdAt',
    width: 150,
    sortable: true
  }
]

// 表格操作按钮配置

const actionButtons: IActionButton[] = [
  {
    key: 'view',
    label: '查看',
    type: 'link',
    icon: 'EyeOutlined',
    onClick: (record: User) => openViewForm(record)
  },
  {
    key: 'edit',
    label: '编辑',
    type: 'link',
    icon: 'EditOutlined',
    onClick: (record: User) => openEditForm(record)
  },
  {
    key: 'delete',
    label: '删除',
    type: 'link',
    icon: 'DeleteOutlined',
    onClick: (record: User) => handleDeleteUser(record),
    disabled: (record: User) => record.username === 'admin'
  }
]

const batchActions: IBatchAction[] = [
  {
    key: 'activate',
    label: '批量激活',
    type: 'default',
    icon: 'UnlockOutlined',
    onClick: () => handleBatchUpdateStatus('active')
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'default',
    icon: 'LockOutlined',
    onClick: () => handleBatchUpdateStatus('inactive')
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'DeleteOutlined',
    confirmText: '确认删除选中的用户？此操作不可撤销！',
    onClick: () => handleBatchDelete()
  }
]

const customActions: IActionButton[] = [
  {
    key: 'create',
    label: '添加用户',
    type: 'primary',
    icon: 'PlusOutlined',
    onClick: () => openCreateForm()
  },
  {
    key: 'import',
    label: '批量导入',
    type: 'default',
    icon: 'ImportOutlined',
    onClick: () => openImportModal()
  },
  {
    key: 'monitor',
    label: '在线监控',
    type: 'default',
    icon: 'EyeOutlined',
    onClick: () => openOnlineMonitor()
  }
]

// 导入和监控弹窗状态
const importVisible = ref(false)
const monitorVisible = ref(false)

// 分页配置
const paginationConfig = computed(() => ({
  current: 1, // 这将由 useUserManagement 管理
  pageSize: 10,
  total: dataSource.total,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: true,
  onChange: handlePageChange
}))

// 业务处理函数
const handleSearchUsers = (searchParams: Record<string, any>) => {
  searchUsers(searchParams)
}

const handleSearchReset = () => {
  resetQuery()
}

const handleDeleteUser = (record: User) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${record.username}" 吗？此操作不可撤销！`,
    onOk: async () => {
      const success = await deleteUser(record.id)
      if (success) {
        message.success('删除成功')
      } else {
        message.error('删除失败')
      }
    }
  })
}

const handleBatchDelete = () => {
  if (!hasSelectedRows.value) {
    message.warning('请先选择要删除的用户')
    return
  }

  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedCount.value} 个用户吗？此操作不可撤销！`,
    onOk: async () => {
      const success = await batchDeleteUsers()
      if (success) {
        message.success(`成功删除 ${selectedCount.value} 个用户`)
      } else {
        message.error('批量删除失败')
      }
    }
  })
}

const handleBatchUpdateStatus = async (status: User['status']) => {
  if (!hasSelectedRows.value) {
    message.warning('请先选择要操作的用户')
    return
  }

  const success = await batchUpdateStatus(status)
  if (success) {
    const statusText = status === 'active' ? '激活' : '禁用'
    message.success(`成功${statusText} ${selectedCount.value} 个用户`)
  } else {
    message.error('批量操作失败')
  }
}

const handleFormSubmit = async () => {
  try {
    const result = await submitForm()
    if (result) {
      message.success('操作成功')
      await refreshUsers()
    }
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const handleExport = async (config?: IExportConfig) => {
  const success = await exportUsers(config?.format || 'xlsx')
  if (success) {
    message.success('导出成功')
  } else {
    message.error('导出失败')
  }
}

const handleFilter = (filters: Record<string, any>) => {
  console.log('过滤条件:', filters)
}

const handleRowClick = (record: User, index: number) => {
  console.log('点击行:', record, index)
}

// 打开导入弹窗
const openImportModal = () => {
  importVisible.value = true
}

// 打开在线监控
const openOnlineMonitor = () => {
  monitorVisible.value = true
}

// 处理导入成功
const handleImportSuccess = () => {
  refreshUsers()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="users-view">
    <!-- 页面头部 -->
    <div class="mb-6">
      <h2 class="text-2xl font-semibold text-gray-900">用户管理</h2>
      <p class="text-gray-600 mt-2">管理系统用户，包括添加、编辑、删除、权限分配等操作</p>
    </div>

    <!-- 搜索表单 -->
    <div class="mb-4">
      <SearchForm
        :fields="searchFields"
        :loading="loading"
        @search="handleSearchUsers"
        @reset="handleSearchReset"
      />
    </div>

    <!-- 数据表格 -->
    <DataTable
      :data-source="dataSource"
      :columns="tableColumns"
      :action-buttons="actionButtons"
      :batch-actions="batchActions"
      :custom-actions="customActions"
      :pagination="paginationConfig"
      :selected-keys="selectedRowKeys"
      row-key="id"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      @refresh="refreshUsers"
      @export="handleExport"
      @sort="handleSort"
      @filter="handleFilter"
    />

    <!-- 用户表单弹窗 -->
    <a-modal
      v-model:open="formVisible"
      :title="formTitle"
      :width="600"
      :footer="isReadonly ? null : undefined"
      @cancel="closeForm"
    >
      <template v-if="!isReadonly" #footer>
        <a-space>
          <a-button @click="closeForm">取消</a-button>
          <a-button type="primary" :loading="formLoading" @click="handleFormSubmit">
            保存
          </a-button>
        </a-space>
      </template>

      <DynamicForm
        ref="formRef"
        :fields="formFields"
        :model="formModel"
        :readonly="isReadonly"
        layout="vertical"
        @submit="handleFormSubmit"
      />
    </a-modal>

    <!-- 用户导入弹窗 -->
    <UserImportModal
      v-model:visible="importVisible"
      @success="handleImportSuccess"
    />

    <!-- 在线用户监控弹窗 -->
    <a-modal
      v-model:open="monitorVisible"
      title="在线用户监控"
      :width="1200"
      :footer="null"
      :body-style="{ padding: 0 }"
    >
      <OnlineUsersMonitor />
    </a-modal>
  </div>
</template>

<style scoped>
.users-view {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.users-view h2 {
  margin-bottom: 8px;
}

.users-view p {
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-view {
    padding: 16px;
  }
  
  .users-view h2 {
    font-size: 1.5rem;
  }
}
</style>