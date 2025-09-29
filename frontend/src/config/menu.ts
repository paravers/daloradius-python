import type { MenuInfo } from '@/types/menu'

/**
 * 应用程序主导航菜单配置
 */
export const mainMenu: MenuInfo[] = [
  // 仪表盘
  {
    key: 'dashboard',
    label: '仪表盘',
    icon: 'LayoutDashboard',
    path: '/dashboard',
    badge: null
  },
  
  // 用户管理
  {
    key: 'users',
    label: '用户管理',
    icon: 'Users',
    path: '/users',
    children: [
      {
        key: 'users-list',
        label: '用户列表',
        icon: 'List',
        path: '/users/list'
      },
      {
        key: 'users-groups',
        label: '用户组',
        icon: 'Users',
        path: '/users/groups'
      },
      {
        key: 'users-online',
        label: '在线用户',
        icon: 'Activity',
        path: '/users/online',
        badge: { type: 'dot', color: 'green' }
      },
      {
        key: 'users-import',
        label: '批量导入',
        icon: 'Upload',
        path: '/users/import'
      }
    ]
  },
  
  // 计费管理
  {
    key: 'billing',
    label: '计费管理',
    icon: 'CreditCard',
    path: '/billing',
    children: [
      {
        key: 'billing-plans',
        label: '计费计划',
        icon: 'CreditCard',
        path: '/billing/plans'
      },
      {
        key: 'billing-invoices',
        label: '发票管理',
        icon: 'FileText',
        path: '/billing/invoices'
      },
      {
        key: 'billing-payments',
        label: '支付管理',
        icon: 'DollarSign',
        path: '/billing/payments'
      },
      {
        key: 'billing-refunds',
        label: '退款管理',
        icon: 'RotateCcw',
        path: '/billing/refunds'
      },
      {
        key: 'billing-history',
        label: '计费历史',
        icon: 'Clock',
        path: '/billing/history'
      },
      {
        key: 'billing-reports',
        label: '计费报表',
        icon: 'BarChart3',
        path: '/billing/reports'
      },
      {
        key: 'billing-settings',
        label: '计费设置',
        icon: 'Settings',
        path: '/billing/settings'
      }
    ]
  },
  
  // 网络监控
  {
    key: 'monitoring',
    label: '网络监控',
    icon: 'Activity',
    path: '/monitoring',
    children: [
      {
        key: 'monitoring-dashboard',
        label: '监控面板',
        icon: 'LayoutDashboard',
        path: '/monitoring/dashboard'
      },
      {
        key: 'monitoring-sessions',
        label: '会话监控',
        icon: 'Monitor',
        path: '/monitoring/sessions'
      },
      {
        key: 'monitoring-traffic',
        label: '流量统计',
        icon: 'TrendingUp',
        path: '/monitoring/traffic'
      },
      {
        key: 'monitoring-bandwidth',
        label: '带宽监控',
        icon: 'Wifi',
        path: '/monitoring/bandwidth'
      },
      {
        key: 'monitoring-alerts',
        label: '告警管理',
        icon: 'AlertTriangle',
        path: '/monitoring/alerts',
        badge: { type: 'count', count: 3, color: 'red' }
      }
    ]
  },
  
  // 设备管理
  {
    key: 'devices',
    label: '设备管理',
    icon: 'Router',
    path: '/devices',
    children: [
      {
        key: 'devices-nas',
        label: 'NAS 设备',
        icon: 'Router',
        path: '/devices/nas'
      },
      {
        key: 'devices-switches',
        label: '交换机',
        icon: 'Network',
        path: '/devices/switches'
      },
      {
        key: 'devices-access-points',
        label: '接入点',
        icon: 'Wifi',
        path: '/devices/access-points'
      },
      {
        key: 'devices-topology',
        label: '网络拓扑',
        icon: 'Sitemap',
        path: '/devices/topology'
      }
    ]
  },
  
  // 认证管理
  {
    key: 'authentication',
    label: '认证管理',
    icon: 'Shield',
    path: '/authentication',
    children: [
      {
        key: 'auth-radius',
        label: 'RADIUS 配置',
        icon: 'Shield',
        path: '/authentication/radius'
      },
      {
        key: 'auth-policies',
        label: '认证策略',
        icon: 'FileShield',
        path: '/authentication/policies'
      },
      {
        key: 'auth-certificates',
        label: '证书管理',
        icon: 'Award',
        path: '/authentication/certificates'
      },
      {
        key: 'auth-ldap',
        label: 'LDAP 集成',
        icon: 'Users',
        path: '/authentication/ldap'
      }
    ]
  },
  
  // 报表分析
  {
    key: 'reports',
    label: '报表分析',
    icon: 'BarChart3',
    path: '/reports',
    children: [
      {
        key: 'reports-usage',
        label: '使用量报表',
        icon: 'TrendingUp',
        path: '/reports/usage'
      },
      {
        key: 'reports-revenue',
        label: '收入报表',
        icon: 'DollarSign',
        path: '/reports/revenue'
      },
      {
        key: 'reports-performance',
        label: '性能报表',
        icon: 'Gauge',
        path: '/reports/performance'
      },
      {
        key: 'reports-custom',
        label: '自定义报表',
        icon: 'FileBarChart',
        path: '/reports/custom'
      }
    ]
  },
  
  // 系统配置
  {
    key: 'system',
    label: '系统配置',
    icon: 'Settings',
    path: '/system',
    children: [
      {
        key: 'system-general',
        label: '基础设置',
        icon: 'Settings',
        path: '/system/general'
      },
      {
        key: 'system-database',
        label: '数据库配置',
        icon: 'Database',
        path: '/system/database'
      },
      {
        key: 'system-backup',
        label: '备份管理',
        icon: 'HardDrive',
        path: '/system/backup'
      },
      {
        key: 'system-logs',
        label: '系统日志',
        icon: 'FileText',
        path: '/system/logs'
      },
      {
        key: 'system-maintenance',
        label: '系统维护',
        icon: 'Wrench',
        path: '/system/maintenance'
      }
    ]
  },
  
  // 管理员
  {
    key: 'admin',
    label: '管理员',
    icon: 'UserCog',
    path: '/admin',
    children: [
      {
        key: 'admin-users',
        label: '管理员账号',
        icon: 'UserCog',
        path: '/admin/users'
      },
      {
        key: 'admin-roles',
        label: '角色权限',
        icon: 'Key',
        path: '/admin/roles'
      },
      {
        key: 'admin-audit',
        label: '操作审计',
        icon: 'Eye',
        path: '/admin/audit'
      },
      {
        key: 'admin-sessions',
        label: '登录会话',
        icon: 'Clock',
        path: '/admin/sessions'
      }
    ]
  }
]

/**
 * 快捷操作菜单
 */
export const quickActions: MenuInfo[] = [
  {
    key: 'quick-add-user',
    label: '添加用户',
    icon: 'UserPlus',
    path: '/users/add'
  },
  {
    key: 'quick-create-plan',
    label: '创建计费计划',
    icon: 'Plus',
    path: '/billing/plans/create'
  },
  {
    key: 'quick-generate-invoice',
    label: '生成发票',
    icon: 'FileText',
    path: '/billing/invoices/generate'
  },
  {
    key: 'quick-view-alerts',
    label: '查看告警',
    icon: 'AlertTriangle',
    path: '/monitoring/alerts'
  },
  {
    key: 'quick-backup',
    label: '创建备份',
    icon: 'Download',
    path: '/system/backup/create'
  }
]

/**
 * 用户菜单（右上角用户头像菜单）
 */
export const userMenu: MenuInfo[] = [
  {
    key: 'user-profile',
    label: '个人资料',
    icon: 'User',
    path: '/profile'
  },
  {
    key: 'user-settings',
    label: '个人设置',
    icon: 'Settings',
    path: '/settings'
  },
  {
    key: 'user-security',
    label: '安全设置',
    icon: 'Shield',
    path: '/security'
  },
  {
    key: 'user-help',
    label: '帮助中心',
    icon: 'HelpCircle',
    path: '/help'
  },
  {
    key: 'user-logout',
    label: '退出登录',
    icon: 'LogOut',
    path: '/logout'
  }
]

export default {
  mainMenu,
  quickActions,
  userMenu
}