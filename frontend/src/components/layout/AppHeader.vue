<template>
  <div class="app-header">
    <div class="header-left">
      <!-- 侧边栏折叠按钮 -->
      <a-button
        type="text"
        class="trigger-btn"
        @click="appStore.toggleSidebar"
      >
        <MenuFoldOutlined v-if="!appStore.sidebarCollapsed" />
        <MenuUnfoldOutlined v-else />
      </a-button>

      <!-- Logo和标题 -->
      <div class="logo-section">
        <RouterLink to="/" class="logo-link">
          <span class="logo-text">daloRADIUS</span>
        </RouterLink>
      </div>
    </div>

    <div class="header-right">
      <!-- 搜索 -->
      <div class="search-section">
        <a-input-search
          v-model:value="searchValue"
          placeholder="搜索功能..."
          style="width: 200px"
          @search="handleSearch"
        />
      </div>

      <!-- 全屏切换 -->
      <a-tooltip title="全屏">
        <a-button
          type="text"
          class="header-action"
          @click="toggleFullscreen"
        >
          <FullscreenOutlined v-if="!isFullscreen" />
          <FullscreenExitOutlined v-else />
        </a-button>
      </a-tooltip>

      <!-- 主题切换 -->
      <a-tooltip :title="appStore.isDarkTheme ? '浅色主题' : '深色主题'">
        <a-button
          type="text"
          class="header-action"
          @click="appStore.toggleTheme"
        >
          <BulbOutlined v-if="appStore.isDarkTheme" />
          <BulbFilled v-else />
        </a-button>
      </a-tooltip>

      <!-- 通知 -->
      <a-dropdown placement="bottomRight">
        <a-badge :count="notificationCount" :offset="[10, 0]">
          <a-button type="text" class="header-action">
            <BellOutlined />
          </a-button>
        </a-badge>
        <template #overlay>
          <a-menu style="width: 300px; max-height: 400px; overflow-y: auto;">
            <a-menu-item-group title="最新通知">
              <a-menu-item v-for="notification in notifications" :key="notification.id">
                <div class="notification-item">
                  <div class="notification-title">{{ notification.title }}</div>
                  <div class="notification-time">{{ notification.time }}</div>
                </div>
              </a-menu-item>
            </a-menu-item-group>
            <a-menu-divider />
            <a-menu-item class="text-center">
              <a-button type="link" size="small">查看全部通知</a-button>
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>

      <!-- 用户菜单 -->
      <a-dropdown placement="bottomRight">
        <div class="user-profile">
          <a-avatar :size="32" :src="authStore.user?.avatar">
            <template #icon><UserOutlined /></template>
          </a-avatar>
          <span v-if="!appStore.sidebarCollapsed" class="user-name">
            {{ authStore.userName }}
          </span>
          <DownOutlined class="down-icon" />
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="profile" @click="handleProfile">
              <UserOutlined />
              个人资料
            </a-menu-item>
            <a-menu-item key="settings" @click="handleSettings">
              <SettingOutlined />
              系统设置
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="logout" @click="handleLogout">
              <LogoutOutlined />
              退出登录
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SearchOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  BulbOutlined,
  BulbFilled,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
} from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useAuthStore, useAppStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const searchValue = ref('')
const isFullscreen = ref(false)
const notificationCount = ref(5)

// 模拟通知数据
const notifications = ref([
  { id: 1, title: '新用户注册通知', time: '2分钟前' },
  { id: 2, title: '系统维护提醒', time: '30分钟前' },
  { id: 3, title: '账单生成完成', time: '1小时前' },
  { id: 4, title: '设备连接异常', time: '2小时前' },
  { id: 5, title: '流量使用报告', time: '3小时前' },
])

// 搜索处理
const handleSearch = (value: string) => {
  console.log('Search:', value)
  // TODO: 实现全局搜索功能
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 监听全屏状态变化
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

// 个人资料
const handleProfile = () => {
  router.push('/profile')
}

// 系统设置
const handleSettings = () => {
  router.push('/settings')
}

// 退出登录
const handleLogout = () => {
  Modal.confirm({
    title: '确认退出',
    content: '确定要退出登录吗？',
    okText: '确认',
    cancelText: '取消',
    async onOk() {
      await authStore.logout()
      router.push('/login')
    },
  })
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trigger-btn {
  font-size: 18px;
  line-height: 64px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger-btn:hover {
  color: #1890ff;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-section {
  margin-right: 16px;
}

.header-action {
  width: 40px;
  height: 40px;
  font-size: 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-profile:hover {
  background-color: #f5f5f5;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.down-icon {
  font-size: 12px;
  color: #999;
}

.notification-item {
  padding: 4px 0;
}

.notification-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.text-center {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }
  
  .search-section {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}

/* 暗色主题 */
:deep([data-theme='dark']) {
  .app-header {
    background: #001529;
    border-bottom: 1px solid #303030;
  }
  
  .logo-text {
    color: #fff;
  }
  
  .user-profile:hover {
    background-color: #262626;
  }
  
  .user-name {
    color: rgba(255, 255, 255, 0.85);
  }
}
</style>