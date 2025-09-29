import { ref, computed, reactive } from 'vue'
import type {
  BillingPlan,
  BillingRate,
  CreateBillingPlanRequest,
  UpdateBillingPlanRequest,
  BillingPlanQueryParams,
  BillingPlanListResponse,
  Money,
  UsageData,
  ValidationResult
} from '@/types/billing'
import { billingPlanService, type IBillingPlanService } from '@/services/billingPlanService'

/**
 * 计费管理 - 计费计划组合式函数
 * 提供计费计划的完整管理功能
 */
export function useBillingPlans(service: IBillingPlanService = billingPlanService) {
  // 状态管理
  const loading = ref(false)
  const plans = ref<BillingPlan[]>([])
  const total = ref(0)
  const error = ref<string | null>(null)

  // 查询参数
  const queryParams = reactive<BillingPlanQueryParams>({
    page: 1,
    pageSize: 10,
    name: '',
    type: undefined,
    active: undefined
  })

  // 计算属性
  const hasPlans = computed(() => plans.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / queryParams.pageSize))
  const activePlans = computed(() => plans.value.filter(plan => plan.active))
  const inactivePlans = computed(() => plans.value.filter(plan => !plan.active))

  /**
   * 获取计费计划列表
   */
  async function fetchPlans(params?: Partial<BillingPlanQueryParams>) {
    try {
      loading.value = true
      error.value = null
      
      // 合并查询参数
      const searchParams = { ...queryParams, ...params }
      Object.assign(queryParams, searchParams)
      
      const response: BillingPlanListResponse = await service.getPlans(searchParams)
      
      plans.value = response.data
      total.value = response.total
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取计费计划失败'
      console.error('获取计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个计费计划详情
   */
  async function fetchPlan(id: string) {
    try {
      loading.value = true
      error.value = null
      
      const plan = await service.getPlan(id)
      
      // 更新列表中的对应计划
      const index = plans.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plans.value[index] = plan
      }
      
      return plan
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取计费计划详情失败'
      console.error('获取计费计划详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建计费计划
   */
  async function createPlan(data: CreateBillingPlanRequest) {
    try {
      loading.value = true
      error.value = null
      
      const newPlan = await service.createPlan(data)
      
      // 添加到列表开头
      plans.value.unshift(newPlan)
      total.value += 1
      
      return newPlan
    } catch (err) {
      error.value = err instanceof Error ? err.message : '创建计费计划失败'
      console.error('创建计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新计费计划
   */
  async function updatePlan(id: string, data: UpdateBillingPlanRequest) {
    try {
      loading.value = true
      error.value = null
      
      const updatedPlan = await service.updatePlan(id, data)
      
      // 更新列表中的对应计划
      const index = plans.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plans.value[index] = updatedPlan
      }
      
      return updatedPlan
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新计费计划失败'
      console.error('更新计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除计费计划
   */
  async function deletePlan(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.deletePlan(id)
      
      // 从列表中移除
      const index = plans.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plans.value.splice(index, 1)
        total.value -= 1
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除计费计划失败'
      console.error('删除计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 激活计费计划
   */
  async function activatePlan(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.activatePlan(id)
      
      // 更新本地状态
      const plan = plans.value.find(p => p.id === id)
      if (plan) {
        plan.active = true
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '激活计费计划失败'
      console.error('激活计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 停用计费计划
   */
  async function deactivatePlan(id: string) {
    try {
      loading.value = true
      error.value = null
      
      await service.deactivatePlan(id)
      
      // 更新本地状态
      const plan = plans.value.find(p => p.id === id)
      if (plan) {
        plan.active = false
      }
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '停用计费计划失败'
      console.error('停用计费计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 搜索计费计划
   */
  function searchPlans(searchTerm: string) {
    queryParams.name = searchTerm
    queryParams.page = 1 // 重置到第一页
    return fetchPlans()
  }

  /**
   * 筛选计费计划
   */
  function filterPlans(filters: Partial<BillingPlanQueryParams>) {
    Object.assign(queryParams, filters)
    queryParams.page = 1 // 重置到第一页
    return fetchPlans()
  }

  /**
   * 分页
   */
  function changePage(page: number) {
    queryParams.page = page
    return fetchPlans()
  }

  /**
   * 改变页面大小
   */
  function changePageSize(pageSize: number) {
    queryParams.pageSize = pageSize
    queryParams.page = 1 // 重置到第一页
    return fetchPlans()
  }

  /**
   * 重置查询条件
   */
  function resetFilters() {
    Object.assign(queryParams, {
      page: 1,
      pageSize: 10,
      name: '',
      type: undefined,
      active: undefined
    })
    return fetchPlans()
  }

  /**
   * 刷新计划列表
   */
  function refreshPlans() {
    return fetchPlans()
  }

  /**
   * 批量删除计费计划
   */
  async function deletePlans(ids: string[]) {
    const results = await Promise.allSettled(
      ids.map(id => deletePlan(id))
    )
    
    const failed = results
      .map((result, index) => ({ result, id: ids[index] }))
      .filter(({ result }) => result.status === 'rejected')
    
    if (failed.length > 0) {
      const failedIds = failed.map(({ id }) => id)
      throw new Error(`删除失败的计划: ${failedIds.join(', ')}`)
    }
    
    return true
  }

  /**
   * 验证计划数据
   */
  function validatePlanData(data: CreateBillingPlanRequest): ValidationResult {
    return service.validatePlanData(data)
  }

  return {
    // 状态
    loading: readonly(loading),
    plans: readonly(plans),
    total: readonly(total),
    error: readonly(error),
    queryParams: readonly(queryParams),
    
    // 计算属性
    hasPlans,
    totalPages,
    activePlans,
    inactivePlans,
    
    // 方法
    fetchPlans,
    fetchPlan,
    createPlan,
    updatePlan,
    deletePlan,
    activatePlan,
    deactivatePlan,
    searchPlans,
    filterPlans,
    changePage,
    changePageSize,
    resetFilters,
    refreshPlans,
    deletePlans,
    validatePlanData
  }
}

/**
 * 计费管理 - 计费计算组合式函数
 */
export function useBillingCalculation(service: IBillingPlanService = billingPlanService) {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 计算使用费用
   */
  async function calculateCost(planId: string, usage: UsageData): Promise<Money> {
    try {
      loading.value = true
      error.value = null
      
      return await service.calculateCost(planId, usage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '费用计算失败'
      console.error('费用计算失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 测试计费计算
   */
  async function testCalculation(planId: string, testUsage: UsageData): Promise<Money> {
    try {
      loading.value = true
      error.value = null
      
      return await service.testPlanCalculation(planId, testUsage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '测试计算失败'
      console.error('测试计算失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取计划费率
   */
  async function getPlanRates(planId: string): Promise<BillingRate[]> {
    try {
      loading.value = true
      error.value = null
      
      return await service.getPlanRates(planId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取费率失败'
      console.error('获取费率失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新计划费率
   */
  async function updatePlanRates(planId: string, rates: Partial<BillingRate>[]): Promise<BillingRate[]> {
    try {
      loading.value = true
      error.value = null
      
      return await service.updatePlanRates(planId, rates)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新费率失败'
      console.error('更新费率失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    calculateCost,
    testCalculation,
    getPlanRates,
    updatePlanRates
  }
}

/**
 * 计费管理 - 用户计划分配组合式函数
 */
export function useBillingAssignment(service: IBillingPlanService = billingPlanService) {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 为用户分配计费计划
   */
  async function assignPlanToUser(planId: string, userId: string): Promise<void> {
    try {
      loading.value = true
      error.value = null
      
      await service.assignPlanToUser(planId, userId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '分配计划失败'
      console.error('分配计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取用户的当前计费计划
   */
  async function getUserPlan(userId: string): Promise<BillingPlan | null> {
    try {
      loading.value = true
      error.value = null
      
      return await service.getUserPlan(userId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取用户计划失败'
      console.error('获取用户计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量分配计费计划
   */
  async function assignPlanToUsers(planId: string, userIds: string[]): Promise<void> {
    const results = await Promise.allSettled(
      userIds.map(userId => assignPlanToUser(planId, userId))
    )
    
    const failed = results
      .map((result, index) => ({ result, userId: userIds[index] }))
      .filter(({ result }) => result.status === 'rejected')
    
    if (failed.length > 0) {
      const failedIds = failed.map(({ userId }) => userId)
      throw new Error(`分配失败的用户: ${failedIds.join(', ')}`)
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    assignPlanToUser,
    getUserPlan,
    assignPlanToUsers
  }
}

// 导入 readonly 函数
import { readonly } from 'vue'