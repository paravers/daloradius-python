/**
 * 应用状态管理
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { AppState, BreadcrumbItem, MenuItemConfig } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const locale = ref('zh-CN')
  const breadcrumbs = ref<BreadcrumbItem[]>([])
  const pageTitle = ref('')

  // 计算属性
  const isDarkTheme = computed(() => theme.value === 'dark')

  // 设置加载状态
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  // 切换侧边栏折叠状态
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebar_collapsed', String(sidebarCollapsed.value))
  }

  // 设置侧边栏折叠状态
  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
    localStorage.setItem('sidebar_collapsed', String(collapsed))
  }

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('app_theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 设置主题
  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    localStorage.setItem('app_theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  // 切换语言
  const setLocale = (newLocale: string) => {
    locale.value = newLocale
    localStorage.setItem('app_locale', newLocale)
  }

  // 设置面包屑
  const setBreadcrumbs = (items: BreadcrumbItem[]) => {
    breadcrumbs.value = items
  }

  // 添加面包屑项
  const addBreadcrumb = (item: BreadcrumbItem) => {
    const exists = breadcrumbs.value.find(crumb => crumb.path === item.path)
    if (!exists) {
      breadcrumbs.value.push(item)
    }
  }

  // 清除面包屑
  const clearBreadcrumbs = () => {
    breadcrumbs.value = []
  }

  // 设置页面标题
  const setPageTitle = (title: string) => {
    pageTitle.value = title
    document.title = title ? `${title} - daloRADIUS` : 'daloRADIUS'
  }

  // 初始化应用状态
  const initializeApp = () => {
    // 恢复侧边栏状态
    const savedCollapsed = localStorage.getItem('sidebar_collapsed')
    if (savedCollapsed !== null) {
      sidebarCollapsed.value = savedCollapsed === 'true'
    }

    // 恢复主题设置
    const savedTheme = localStorage.getItem('app_theme') as 'light' | 'dark'
    if (savedTheme) {
      theme.value = savedTheme
      document.documentElement.setAttribute('data-theme', savedTheme)
    }

    // 恢复语言设置
    const savedLocale = localStorage.getItem('app_locale')
    if (savedLocale) {
      locale.value = savedLocale
    }
  }

  // 重置应用状态
  const resetAppState = () => {
    loading.value = false
    sidebarCollapsed.value = false
    theme.value = 'light'
    locale.value = 'zh-CN'
    breadcrumbs.value = []
    pageTitle.value = ''
  }

  return {
    // 状态
    loading,
    sidebarCollapsed,
    theme,
    locale,
    breadcrumbs,
    pageTitle,

    // 计算属性
    isDarkTheme,

    // 方法
    setLoading,
    toggleSidebar,
    setSidebarCollapsed,
    toggleTheme,
    setTheme,
    setLocale,
    setBreadcrumbs,
    addBreadcrumb,
    clearBreadcrumbs,
    setPageTitle,
    initializeApp,
    resetAppState,
  }
})