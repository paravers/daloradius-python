<template>
  <div class="dashboard-view">
    <div class="page-header">
      <h1>仪表板</h1>
      <p class="page-description">系统概览和关键指标</p>
    </div>
    
    <div class="dashboard-content">
      <!-- 统计卡片 -->
      <a-row :gutter="[16, 16]">
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="在线用户"
              :value="123"
              :value-style="{ color: '#3f8600' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="总用户数"
              :value="1234"
              :value-style="{ color: '#1890ff' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="今日收入"
              :value="5678.90"
              prefix="¥"
              :precision="2"
              :value-style="{ color: '#cf1322' }"
            />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic
              title="活跃设备"
              :value="456"
              :value-style="{ color: '#722ed1' }"
            />
          </a-card>
        </a-col>
      </a-row>
      
      <!-- 图表区域 -->
      <a-row :gutter="[16, 16]" style="margin-top: 16px;">
        <a-col :span="12">
          <a-card title="用户活跃度趋势">
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              图表组件待实现
            </div>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="收入统计">
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999;">
              图表组件待实现
            </div>
          </a-card>
        </a-col>
      </a-row>
      
      <!-- 快速操作 -->
      <a-card title="快速操作" style="margin-top: 16px;">
        <a-space>
          <a-button type="primary">
            <template #icon>
              <UserAddOutlined />
            </template>
            添加用户
          </a-button>
          <a-button>
            <template #icon>
              <FileTextOutlined />
            </template>
            生成报表
          </a-button>
          <a-button>
            <template #icon>
              <SettingOutlined />
            </template>
            系统配置
          </a-button>
        </a-space>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  UserAddOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'
</script>

<style scoped>
.dashboard-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.page-description {
  margin: 8px 0 0 0;
  color: rgba(0, 0, 0, 0.65);
}

.dashboard-content {
  /* 内容样式 */
}
</style>