<template>
  <div class="users-view">
    <div class="page-header">
      <h1>用户管理</h1>
      <p class="page-description">管理系统用户和权限</p>
    </div>
    
    <a-card>
      <!-- 搜索和操作栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索用户名或邮箱"
            style="width: 300px"
            @search="handleSearch"
          />
        </div>
        <div class="toolbar-right">
          <a-button type="primary">
            <template #icon>
              <PlusOutlined />
            </template>
            添加用户
          </a-button>
        </div>
      </div>
      
      <!-- 用户表格 -->
      <a-table
        :columns="columns"
        :data-source="users"
        :pagination="pagination"
        :loading="loading"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'red'">
              {{ record.status === 'active' ? '活跃' : '禁用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small">编辑</a-button>
              <a-button type="link" size="small" danger>删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import type { TableColumnsType } from 'ant-design-vue'

const searchText = ref('')
const loading = ref(false)

const columns: TableColumnsType = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
  },
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
  },
]

const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    status: 'active',
    created_at: '2024-01-15',
  },
  {
    id: 2,
    username: 'user1',
    email: 'user1@example.com',
    status: 'active',
    created_at: '2024-01-16',
  },
])

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 2,
})

const handleSearch = (value: string) => {
  console.log('搜索:', value)
}
</script>

<style scoped>
.users-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
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

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>