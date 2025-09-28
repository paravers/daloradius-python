/**
 * Vue Router 配置 - 重新创建
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'
import type { RouteMeta } from '@/types'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
      hidden: true,
    } as RouteMeta,
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true,
    } as RouteMeta,
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          title: '仪表板',
          requiresAuth: true,
        } as RouteMeta,
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UsersView.vue'),
        meta: {
          title: '用户管理',
          icon: 'UserOutlined',
          requiresAuth: true,
          permissions: ['users.view'],
        } as RouteMeta,
      },
      {
        path: 'billing',
        name: 'Billing',
        component: () => import('@/views/billing/BillingView.vue'),
        meta: {
          title: '计费管理',
          icon: 'CreditCardOutlined',
          requiresAuth: true,
          permissions: ['billing.view'],
        } as RouteMeta,
      },
      {
        path: 'devices',
        name: 'Devices',
        component: () => import('@/views/devices/DevicesView.vue'),
        meta: {
          title: '设备管理',
          icon: 'LaptopOutlined',
          requiresAuth: true,
          permissions: ['devices.view'],
        } as RouteMeta,
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/reports/ReportsView.vue'),
        meta: {
          title: '报表中心',
          icon: 'BarChartOutlined',
          requiresAuth: true,
          permissions: ['reports.view'],
        } as RouteMeta,
      },
      {
        path: 'config',
        name: 'Config',
        component: () => import('@/views/config/ConfigView.vue'),
        meta: {
          title: '系统配置',
          icon: 'SettingOutlined',
          requiresAuth: true,
          permissions: ['config.view'],
        } as RouteMeta,
      },
    ],
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/DashboardView.vue'), // 临时使用仪表板
    meta: {
      title: '页面不存在',
      hidden: true,
    } as RouteMeta,
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 获取用户信息（如果已登录）
  if (authStore.token && !authStore.user) {
    try {
      // 临时注释掉，等待后端API准备好
      // await authStore.fetchUserInfo()
    } catch (error) {
      // Token 可能已失效，清除并跳转到登录页
      authStore.logout()
      next('/login')
      return
    }
  }
  
  // 检查是否需要认证
  if (to.meta?.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 暂时跳过权限检查，等待完整的权限系统
  // if (to.meta?.permissions && !authStore.hasPermission(to.meta.permissions[0])) {
  //   next('/403')
  //   return
  // }
  
  // 已登录用户访问登录页，重定向到仪表板
  if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

// 路由后置守卫 - 设置页面标题
router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} - daloRADIUS`
  }
})

export default router