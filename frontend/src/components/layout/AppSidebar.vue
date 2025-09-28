<template>
  <div class="app-sidebar">
    <div class="sidebar-content">
      <!-- Logo区域 -->
      <div class="sidebar-logo">
        <RouterLink to="/" class="logo-link">
          <span class="logo-text">dR</span>
        </RouterLink>
      </div>
      
      <!-- 菜单区域 -->
      <a-menu
        v-model:selected-keys="selectedKeys"
        mode="inline"
        theme="dark"
        :inline-collapsed="appStore.sidebarCollapsed"
        @click="handleMenuClick"
      >
        <a-menu-item key="dashboard">
          <template #icon>
            <DashboardOutlined />
          </template>
          <span>仪表板</span>
        </a-menu-item>
        
        <a-sub-menu key="users">
          <template #icon>
            <UserOutlined />
          </template>
          <template #title>用户管理</template>
          <a-menu-item key="users-list">用户列表</a-menu-item>
          <a-menu-item key="users-create">创建用户</a-menu-item>
        </a-sub-menu>
        
        <a-sub-menu key="billing">
          <template #icon>
            <CreditCardOutlined />
          </template>
          <template #title>计费管理</template>
          <a-menu-item key="billing-plans">计费计划</a-menu-item>
          <a-menu-item key="billing-history">账单历史</a-menu-item>
        </a-sub-menu>
        
        <a-menu-item key="devices">
          <template #icon>
            <LaptopOutlined />
          </template>
          <span>设备管理</span>
        </a-menu-item>
        
        <a-sub-menu key="reports">
          <template #icon>
            <BarChartOutlined />
          </template>
          <template #title>报表中心</template>
          <a-menu-item key="reports-usage">使用统计</a-menu-item>
          <a-menu-item key="reports-revenue">收入报表</a-menu-item>
        </a-sub-menu>
      </a-menu>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  UserOutlined,
  CreditCardOutlined,
  LaptopOutlined,
  BarChartOutlined,
} from '@ant-design/icons-vue'
import { useAppStore } from '@/stores'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const selectedKeys = ref(['dashboard'])

const menuRoutes: Record<string, string> = {
  'dashboard': '/dashboard',
  'users-list': '/users',
  'users-create': '/users/create',
  'billing-plans': '/billing/plans',
  'billing-history': '/billing/history',
  'devices': '/devices',
  'reports-usage': '/reports/usage',
  'reports-revenue': '/reports/revenue',
}

const handleMenuClick = (event: { key: string }) => {
  const routePath = menuRoutes[event.key]
  if (routePath) {
    router.push(routePath)
  }
}
</script>

<style scoped>
.app-sidebar {
  height: 100%;
  background: #001529;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  margin: 16px;
  border-radius: 6px;
}

.logo-link {
  text-decoration: none;
  color: #fff;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
}

:deep(.ant-menu-dark) {
  background: transparent;
}

:deep(.ant-menu-inline-collapsed) {
  width: 80px;
}
</style>