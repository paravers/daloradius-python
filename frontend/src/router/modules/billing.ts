import type { RouteRecordRaw } from 'vue-router'

/**
 * 计费管理模块路由配置
 */
export const billingRoutes: RouteRecordRaw[] = [
  {
    path: '/billing',
    name: 'Billing',
    redirect: '/billing/plans',
    meta: {
      title: '计费管理',
      icon: 'CreditCard',
      requiresAuth: true,
      roles: ['admin', 'billing']
    },
    children: [
      // 计费计划管理
      {
        path: 'plans',
        name: 'BillingPlans',
        component: () => import('@/views/billing/BillingPlansView.vue'),
        meta: {
          title: '计费计划',
          icon: 'CreditCard',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 发票管理
      {
        path: 'invoices',
        name: 'Invoices',
        component: () => import('@/views/billing/InvoicesView.vue'),
        meta: {
          title: '发票管理',
          icon: 'FileText',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 支付管理
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/billing/PaymentsView.vue'),
        meta: {
          title: '支付管理',
          icon: 'DollarSign',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 退款管理
      {
        path: 'refunds',
        name: 'Refunds',
        component: () => import('@/views/billing/RefundsView.vue'),
        meta: {
          title: '退款管理',
          icon: 'RotateCcw',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 计费历史
      {
        path: 'history',
        name: 'BillingHistory',
        component: () => import('@/views/billing/BillingHistoryView.vue'),
        meta: {
          title: '计费历史',
          icon: 'Clock',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 计费报表
      {
        path: 'reports',
        name: 'BillingReports',
        component: () => import('@/views/billing/BillingReportsView.vue'),
        meta: {
          title: '计费报表',
          icon: 'BarChart3',
          requiresAuth: true,
          keepAlive: true
        }
      },
      // 计费设置
      {
        path: 'settings',
        name: 'BillingSettings',
        component: () => import('@/views/billing/BillingSettingsView.vue'),
        meta: {
          title: '计费设置',
          icon: 'Settings',
          requiresAuth: true
        }
      }
    ]
  }
]

export default billingRoutes