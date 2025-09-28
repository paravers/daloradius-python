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
import { ref, reactive, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { 
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  LockOutlined,
  UnlockOutlined
} from '@ant-design/icons-vue'
import DataTable from '@/components/common/DataTable.vue'
import SearchForm from '@/components/common/SearchForm.vue'
import DynamicForm from '@/components/common/DynamicForm.vue'
import { userService } from '@/services'
import type { 
  IDataSource,
  ITableColumn,
  IFormField,
  IActionButton,
  IBatchAction,
  IExportConfig,
  IPaginationConfig
} from '@/types/common'
import type { User } from '@/types'

// 响应式状态
const loading = ref(false)
const formVisible = ref(false)
const formMode = ref<'create' | 'edit' | 'view'>('create')
const formRef = ref()
const selectedRowKeys = ref<string[]>([])
const selectedRows = ref<User[]>([])

// 表单数据
const formModel = reactive<Partial<User>>({})

// 数据源
const dataSource = reactive<IDataSource<User>>({
  data: [],
  total: 0,
  loading: false,
  error: undefined
})

// 查询参数
const queryParams = reactive({
  page: 1,
  pageSize: 10,
  username: '',
  email: '',
  status: undefined,
  startDate: undefined,
  endDate: undefined,
  sortField: undefined,
  sortOrder: undefined
})

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

// 表单字段配置
const formFields: IFormField[] = [
  {
    name: 'username',
    type: 'input',
    label: '用户名',
    required: true,
    disabled: formMode.value === 'edit',
    rules: [
      { required: true, message: '请输入用户名' },
      { min: 3, max: 20, message: '用户名长度在3-20个字符之间' },
      { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' }
    ]
  },
  {
    name: 'email',
    type: 'email',
    label: '邮箱',
    required: true,
    rules: [
      { required: true, message: '请输入邮箱地址' },
      { type: 'email', message: '请输入正确的邮箱格式' }
    ]
  },
  {
    name: 'fullName',
    type: 'input',
    label: '姓名',
    placeholder: '请输入真实姓名'
  },
  {
    name: 'password',
    type: 'password',
    label: '密码',
    required: formMode.value === 'create',
    visible: formMode.value !== 'view',
    rules: [
      { 
        required: formMode.value === 'create', 
        message: '请输入密码' 
      },
      { min: 6, message: '密码长度至少6个字符' }
    ]
  },
  {
    name: 'roles',
    type: 'select',
    label: '角色',
    multiple: true,
    options: [
      { label: '管理员', value: 'admin' },
      { label: '操作员', value: 'operator' },
      { label: '用户', value: 'user' }
    ]
  },
  {
    name: 'status',
    type: 'radio',
    label: '状态',
    options: [
      { label: '活跃', value: 'active' },
      { label: '非活跃', value: 'inactive' },
      { label: '已暂停', value: 'suspended' }
    ]
  }
]

// 操作按钮配置
const actionButtons: IActionButton[] = [
  {
    key: 'view',
    label: '查看',
    type: 'link',
    icon: 'EyeOutlined',
    onClick: (record: User) => handleView(record)
  },
  {
    key: 'edit',
    label: '编辑',
    type: 'link',
    icon: 'EditOutlined',
    onClick: (record: User) => handleEdit(record)
  },
  {
    key: 'delete',
    label: '删除',
    type: 'link',
    icon: 'DeleteOutlined',
    onClick: (record: User) => handleDelete(record),
    disabled: (record: User) => record.username === 'admin'
  }
]

// 批量操作配置
const batchActions: IBatchAction[] = [
  {
    key: 'activate',
    label: '批量激活',
    type: 'default',
    icon: 'UnlockOutlined',
    onClick: (keys: string[], rows: User[]) => handleBatchActivate(keys, rows)
  },
  {
    key: 'deactivate',
    label: '批量禁用',
    type: 'default',
    icon: 'LockOutlined',
    onClick: (keys: string[], rows: User[]) => handleBatchDeactivate(keys, rows)
  },
  {
    key: 'delete',
    label: '批量删除',
    type: 'danger',
    icon: 'DeleteOutlined',
    confirmText: '确认删除选中的用户？此操作不可撤销！',
    onClick: (keys: string[], rows: User[]) => handleBatchDelete(keys, rows)
  }
]

// 自定义操作按钮
const customActions: IActionButton[] = [
  {
    key: 'create',
    label: '添加用户',
    type: 'primary',
    icon: 'PlusOutlined',
    onClick: () => handleCreate()
  }
]

// 分页配置
const paginationConfig = computed<IPaginationConfig>(() => ({
  current: queryParams.page,
  pageSize: queryParams.pageSize,
  total: dataSource.total,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: true,
  onChange: (page: number, pageSize: number) => {
    queryParams.page = page
    queryParams.pageSize = pageSize
    fetchUsers()
  }
}))

// 表单标题
const formTitle = computed(() => {
  const titles = {
    create: '添加用户',
    edit: '编辑用户',
    view: '查看用户'
  }
  return titles[formMode.value]
})

// 获取用户列表
const fetchUsers = async () => {
  try {
    dataSource.loading = true
    dataSource.error = undefined
    
    const response = await userService.getUsers({
      page: queryParams.page,
      pageSize: queryParams.pageSize,
      username: queryParams.username || undefined,
      email: queryParams.email || undefined,
      status: queryParams.status,
      sortField: queryParams.sortField,
      sortOrder: queryParams.sortOrder
    })
    
    dataSource.data = response.data
    dataSource.total = response.total
  } catch (error: any) {
    dataSource.error = error.message || '获取用户列表失败'
    message.error(dataSource.error)
  } finally {
    dataSource.loading = false
  }
}

// 处理搜索
const handleSearch = (values: Record<string, any>) => {
  Object.assign(queryParams, values, { page: 1 })
  fetchUsers()
}

// 处理搜索重置
const handleSearchReset = () => {
  Object.assign(queryParams, {
    page: 1,
    username: '',
    email: '',
    status: undefined,
    startDate: undefined,
    endDate: undefined
  })
  fetchUsers()
}

// 处理选择变化
const handleSelectionChange = (keys: string[], rows: User[]) => {
  selectedRowKeys.value = keys
  selectedRows.value = rows
}

// 处理行点击
const handleRowClick = (record: User, index: number) => {
  console.log('点击行:', record, index)
}

// 处理刷新
const handleRefresh = () => {
  fetchUsers()
}

// 处理导出
const handleExport = (config?: IExportConfig) => {
  console.log('导出配置:', config)
  message.success('导出功能开发中...')
}

// 处理排序
const handleSort = (field: string, order: 'ascend' | 'descend' | null) => {
  queryParams.sortField = field
  queryParams.sortOrder = order
  fetchUsers()
}

// 处理过滤
const handleFilter = (filters: Record<string, any>) => {
  console.log('过滤条件:', filters)
  // 这里处理表格列的过滤逻辑
}

// 处理创建用户
const handleCreate = () => {
  formMode.value = 'create'
  Object.assign(formModel, {
    username: '',
    email: '',
    fullName: '',
    password: '',
    roles: [],
    status: 'active'
  })
  formVisible.value = true
}

// 处理查看用户
const handleView = (record: User) => {
  formMode.value = 'view'
  Object.assign(formModel, record)
  formVisible.value = true
}

// 处理编辑用户
const handleEdit = (record: User) => {
  formMode.value = 'edit'
  Object.assign(formModel, record)
  formVisible.value = true
}

// 处理删除用户
const handleDelete = (record: User) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${record.username}" 吗？此操作不可撤销！`,
    onOk: async () => {
      try {
        await userService.deleteUser(record.id)
        message.success('删除成功')
        fetchUsers()
      } catch (error: any) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

// 处理表单提交
const handleFormSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    if (formMode.value === 'create') {
      await userService.createUser(formModel as any)
      message.success('用户创建成功')
    } else if (formMode.value === 'edit') {
      await userService.updateUser(formModel.id!, formModel as any)
      message.success('用户更新成功')
    }
    
    formVisible.value = false
    fetchUsers()
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      message.error('请检查表单填写')
    } else {
      // API 错误
      message.error(error.message || '操作失败')
    }
  }
}

// 处理表单取消
const handleFormCancel = () => {
  formVisible.value = false
}

// 批量激活
const handleBatchActivate = async (keys: string[], rows: User[]) => {
  try {
    await userService.batchUpdateUsers(keys, { status: 'active' })
    message.success(`成功激活 ${keys.length} 个用户`)
    fetchUsers()
  } catch (error: any) {
    message.error(error.message || '批量激活失败')
  }
}

// 批量禁用
const handleBatchDeactivate = async (keys: string[], rows: User[]) => {
  try {
    await userService.batchUpdateUsers(keys, { status: 'inactive' })
    message.success(`成功禁用 ${keys.length} 个用户`)
    fetchUsers()
  } catch (error: any) {
    message.error(error.message || '批量禁用失败')
  }
}

// 批量删除
const handleBatchDelete = async (keys: string[], rows: User[]) => {
  try {
    await userService.batchDeleteUsers(keys)
    message.success(`成功删除 ${keys.length} 个用户`)
    fetchUsers()
  } catch (error: any) {
    message.error(error.message || '批量删除失败')
  }
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
        @search="handleSearch"
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
      @refresh="handleRefresh"
      @export="handleExport"
      @sort="handleSort"
      @filter="handleFilter"
    />

    <!-- 用户表单弹窗 -->
    <a-modal
      v-model:open="formVisible"
      :title="formTitle"
      :width="600"
      :footer="formMode === 'view' ? null : undefined"
      @cancel="handleFormCancel"
    >
      <template v-if="formMode !== 'view'" #footer>
        <a-space>
          <a-button @click="handleFormCancel">取消</a-button>
          <a-button type="primary" :loading="loading" @click="handleFormSubmit">
            {{ formMode === 'create' ? '创建' : '更新' }}
          </a-button>
        </a-space>
      </template>

      <DynamicForm
        ref="formRef"
        :fields="formFields"
        :model="formModel"
        :readonly="formMode === 'view'"
        layout="vertical"
        @submit="handleFormSubmit"
      />
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