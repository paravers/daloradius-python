<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ backgroundColor: color }">
      <Icon :name="icon" />
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-title">{{ title }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from './Icon.vue'

interface Props {
  title: string
  value: string | number
  icon: string
  color?: string
}

withDefaults(defineProps<Props>(), {
  color: '#1890ff'
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: #d9d9d9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  color: white;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: #8c8c8c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
    gap: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-title {
    font-size: 12px;
  }
}
</style>