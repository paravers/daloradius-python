/**
 * Vue Router 配置
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
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: {
          title: '仪表板',
          icon: 'DashboardOutlined',
          requiresAuth: true,
        } as RouteMeta,
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/users/UsersLayout.vue'),
        meta: {
          title: '用户管理',
          icon: 'UserOutlined',
          requiresAuth: true,
          permissions: ['users.view'],
        } as RouteMeta,
        children: [
          {
            path: '',
            name: 'UsersList',
            component: () => import('@/views/users/UsersList.vue'),
            meta: {
              title: '用户列表',
              requiresAuth: true,
              permissions: ['users.view'],
            } as RouteMeta,
          },
          {
            path: 'create',
            name: 'UsersCreate',
            component: () => import('@/views/users/UsersForm.vue'),
            meta: {
              title: '创建用户',
              requiresAuth: true,
              permissions: ['users.create'],
            } as RouteMeta,
          },
          {
            path: ':id/edit',
            name: 'UsersEdit',
            component: () => import('@/views/users/UsersForm.vue'),
            meta: {
              title: '编辑用户',
              requiresAuth: true,
              permissions: ['users.update'],
            } as RouteMeta,
          },
        ],
      },
      {
        path: '/billing',
        name: 'Billing',
        component: () => import('@/views/billing/BillingLayout.vue'),
        meta: {
          title: '计费管理',
          icon: 'CreditCardOutlined',
          requiresAuth: true,
          permissions: ['billing.view'],
        } as RouteMeta,
        children: [
          {
            path: 'plans',
            name: 'BillingPlans',
            component: () => import('@/views/billing/PlansList.vue'),
            meta: {
              title: '计费计划',
              requiresAuth: true,
              permissions: ['billing.plans.view'],
            } as RouteMeta,
          },
          {
            path: 'history',
            name: 'BillingHistory',
            component: () => import('@/views/billing/BillingHistory.vue'),
            meta: {
              title: '账单历史',
              requiresAuth: true,
              permissions: ['billing.history.view'],
            } as RouteMeta,
          },
        ],
      },
      {
        path: '/devices',
        name: 'Devices',
        component: () => import('@/views/devices/DevicesLayout.vue'),
        meta: {
          title: '设备管理',
          icon: 'LaptopOutlined',
          requiresAuth: true,
          permissions: ['devices.view'],
        } as RouteMeta,
        children: [
          {
            path: '',
            name: 'DevicesList',
            component: () => import('@/views/devices/DevicesList.vue'),
            meta: {
              title: '设备列表',
              requiresAuth: true,
              permissions: ['devices.view'],
            } as RouteMeta,
          },
        ],
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/reports/ReportsLayout.vue'),
        meta: {
          title: '报表中心',
          icon: 'BarChartOutlined',
          requiresAuth: true,
          permissions: ['reports.view'],
        } as RouteMeta,
        children: [
          {
            path: 'usage',
            name: 'UsageReports',
            component: () => import('@/views/reports/UsageReports.vue'),
            meta: {
              title: '使用统计',
              requiresAuth: true,
              permissions: ['reports.usage.view'],
            } as RouteMeta,
          },
          {
            path: 'revenue',
            name: 'RevenueReports',
            component: () => import('@/views/reports/RevenueReports.vue'),
            meta: {
              title: '收入报表',
              requiresAuth: true,
              permissions: ['reports.revenue.view'],
            } as RouteMeta,
          },
        ],
      },
    ],
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '无权限访问',
      hidden: true,
    } as RouteMeta,
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面未找到',
      hidden: true,
    } as RouteMeta,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态（仅在首次访问时）
  if (!authStore.token && !authStore.user) {
    authStore.initializeAuth()
  }

  // 检查是否需要认证
  if (to.meta?.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 检查权限
    if (to.meta?.permissions) {
      const hasPermission = authStore.hasAnyPermission(to.meta.permissions as string[])
      if (!hasPermission) {
        next({ name: 'Forbidden' })
        return
      }
    }

    // 检查角色
    if (to.meta?.roles) {
      const hasRole = (to.meta.roles as string[]).some(role => authStore.hasRole(role))
      if (!hasRole) {
        next({ name: 'Forbidden' })
        return
      }
    }
  }

  // 已登录用户访问登录页时，重定向到仪表板
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

// 路由后置守卫，设置页面标题
router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} - daloRADIUS` : 'daloRADIUS'
})

export default router
