<template>
  <a-layout class="layout-container">
    <!-- 顶部导航 -->
    <a-layout-header class="layout-header">
      <AppHeader />
    </a-layout-header>

    <a-layout has-sider>
      <!-- 侧边栏 -->
      <a-layout-sider
        v-model:collapsed="appStore.sidebarCollapsed"
        :trigger="null"
        collapsible
        class="layout-sider"
        :width="240"
        :collapsed-width="80"
      >
        <AppSidebar />
      </a-layout-sider>

      <!-- 主内容区 -->
      <a-layout>
        <a-layout-content class="layout-content">
          <!-- 面包屑导航 -->
          <AppBreadcrumb v-if="appStore.breadcrumbs.length > 0" />
          
          <!-- 页面内容 -->
          <div class="content-wrapper">
            <RouterView />
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'

const appStore = useAppStore()
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  height: 64px;
  line-height: 64px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.layout-sider {
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow: auto;
}

.layout-content {
  min-height: calc(100vh - 64px);
  background: #f0f2f5;
}

.content-wrapper {
  padding: 24px;
  min-height: calc(100vh - 64px - 48px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .layout-sider {
    position: fixed;
    z-index: 999;
    height: 100vh;
    top: 0;
  }
  
  .content-wrapper {
    padding: 16px;
  }
}

/* 暗色主题 */
:deep([data-theme='dark']) {
  .layout-header {
    background: #001529;
    border-bottom-color: #303030;
  }
  
  .layout-content {
    background: #141414;
  }
}
</style>