/**
 * 菜单徽章配置
 */
export interface MenuBadge {
  type: 'dot' | 'count' | 'text'
  count?: number
  text?: string
  color?: 'red' | 'green' | 'blue' | 'orange' | 'purple' | 'gray'
}

/**
 * 菜单项信息
 */
export interface MenuInfo {
  key: string
  label: string
  icon?: string
  path?: string
  badge?: MenuBadge | null
  children?: MenuInfo[]
  disabled?: boolean
  hidden?: boolean
  roles?: string[]
  permissions?: string[]
}

/**
 * 面包屑导航项
 */
export interface BreadcrumbItem {
  key: string
  label: string
  path?: string
  icon?: string
}

/**
 * 导航标签页信息
 */
export interface TabInfo {
  key: string
  label: string
  path: string
  icon?: string
  closable?: boolean
  active?: boolean
}