import { ref, computed, readonly } from 'vue'
import type { User, UserQueryParams, UserListResponse } from '@/types/user'
import { userService } from '@/services/userService'
import { batchService } from '@/services/batchService'

/**
 * 用户管理组合式函数
 * 提供用户列表管理的完整功能
 */
export function useUserManagement() {
  // 状态管理
  const loading = ref(false)
  const users = ref<User[]>([])
  const total = ref(0)
  const error = ref<string>()
  
  // 查询参数
  const queryParams = ref<UserQueryParams>({
    page: 1,
    pageSize: 10,
    sortField: 'createdAt',
    sortOrder: 'descend'
  })

  // 选择状态
  const selectedRowKeys = ref<string[]>([])
  const selectedRows = ref<User[]>([])

  // 计算属性
  const dataSource = computed(() => ({
    data: users.value,
    total: total.value,
    loading: loading.value,
    error: error.value
  }))

  const hasSelectedRows = computed(() => selectedRowKeys.value.length > 0)
  const selectedCount = computed(() => selectedRowKeys.value.length)

  // 获取用户列表
  const fetchUsers = async (params?: Partial<UserQueryParams>) => {
    try {
      loading.value = true
      error.value = undefined
      
      const mergedParams = { ...queryParams.value, ...params }
      const response: UserListResponse = await userService.getUsers(mergedParams)
      
      users.value = response.data
      total.value = response.total
      
      // 更新查询参数
      Object.assign(queryParams.value, mergedParams)
    } catch (err: any) {
      error.value = err.message || '获取用户列表失败'
      console.error('获取用户列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 刷新数据
  const refreshUsers = () => {
    fetchUsers()
  }

  // 重置查询
  const resetQuery = () => {
    queryParams.value = {
      page: 1,
      pageSize: 10,
      sortField: 'createdAt',
      sortOrder: 'descend'
    }
    fetchUsers()
  }

  // 搜索用户
  const searchUsers = (searchParams: Record<string, unknown>) => {
    const { dateRange, ...otherParams } = searchParams
    
    const params: Partial<UserQueryParams> = {
      ...otherParams,
      page: 1 // 重置到第一页
    }
    
    // 处理日期范围
    if (dateRange && dateRange.length === 2) {
      params.startDate = dateRange[0]
      params.endDate = dateRange[1]
    }
    
    fetchUsers(params)
  }

  // 分页处理
  const handlePageChange = (page: number, pageSize: number) => {
    fetchUsers({ page, pageSize })
  }

  // 排序处理
  const handleSort = (field: string, order: 'ascend' | 'descend' | null) => {
    fetchUsers({
      sortField: field,
      sortOrder: order || undefined
    })
  }

  // 选择处理
  const handleSelectionChange = (keys: string[], rows: User[]) => {
    selectedRowKeys.value = keys
    selectedRows.value = rows
  }

  // 清空选择
  const clearSelection = () => {
    selectedRowKeys.value = []
    selectedRows.value = []
  }

  // 删除用户
  const deleteUser = async (id: string) => {
    try {
      loading.value = true
      await userService.deleteUser(id)
      await fetchUsers() // 重新获取数据
      return true
    } catch (err: any) {
      error.value = err.message || '删除用户失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 批量删除
  const batchDeleteUsers = async (ids?: string[]) => {
    const userIds = ids || selectedRowKeys.value
    if (userIds.length === 0) return false

    try {
      loading.value = true
      // Use batch service with history tracking
      const numericIds = userIds.map(id => parseInt(id))
      const result = await batchService.batchDeleteUsersWithHistory(numericIds, {
        batchName: `批量删除 ${numericIds.length} 个用户`,
        description: `通过用户管理界面执行的批量删除操作`
      })
      
      clearSelection()
      await fetchUsers() // 重新获取数据
      
      // Return success if no failures
      return result.failure_count === 0
    } catch (err: any) {
      error.value = err.message || '批量删除失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 批量更新状态
  const batchUpdateStatus = async (status: User['status'], ids?: string[]) => {
    const userIds = ids || selectedRowKeys.value
    if (userIds.length === 0) return false

    try {
      loading.value = true
      // Use batch service with history tracking
      const numericIds = userIds.map(id => parseInt(id))
      const result = await batchService.batchUpdateUserStatusWithHistory(
        numericIds, 
        status as 'active' | 'inactive',
        {
          batchName: `批量${status === 'active' ? '激活' : '停用'} ${numericIds.length} 个用户`,
          description: `通过用户管理界面执行的批量状态更新操作`
        }
      )
      
      clearSelection()
      await fetchUsers() // 重新获取数据
      
      // Return success if no failures
      return result.failure_count === 0
    } catch (err: any) {
      error.value = err.message || '批量更新状态失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 导出用户数据
  const exportUsers = async (format: 'xlsx' | 'csv' = 'xlsx') => {
    try {
      // 这里应该调用实际的导出API
      console.log('导出用户数据:', format)
      
      // 模拟导出逻辑
      const exportData = users.value.map(user => ({
        ID: user.id,
        用户名: user.username,
        邮箱: user.email,
        姓名: user.fullName || '',
        状态: user.status,
        角色: user.roles.join(', '),
        最后登录: user.lastLoginAt || '',
        创建时间: user.createdAt
      }))

      // 实际项目中这里会调用文件下载
      console.log('导出数据:', exportData)
      return true
    } catch (err: any) {
      error.value = err.message || '导出数据失败'
      return false
    }
  }

  return {
    // 状态
    loading: readonly(loading),
    users: readonly(users),
    total: readonly(total),
    error: readonly(error),
    queryParams: readonly(queryParams),
    selectedRowKeys: readonly(selectedRowKeys),
    selectedRows: readonly(selectedRows),
    
    // 计算属性
    dataSource,
    hasSelectedRows,
    selectedCount,
    
    // 方法
    fetchUsers,
    refreshUsers,
    resetQuery,
    searchUsers,
    handlePageChange,
    handleSort,
    handleSelectionChange,
    clearSelection,
    deleteUser,
    batchDeleteUsers,
    batchUpdateStatus,
    exportUsers
  }
}