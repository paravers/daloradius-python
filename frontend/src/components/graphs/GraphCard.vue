<template>
  <div class="graph-card">
    <div class="card-header">
      <div class="card-title-section">
        <h3 class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </div>
      
      <div class="card-controls">
        <slot name="controls"></slot>
        
        <button 
          @click="handleRefresh"
          :disabled="loading"
          class="refresh-btn"
          :title="loading ? '加载中...' : '刷新数据'"
        >
          <i 
            :class="['fas fa-sync-alt', { 'fa-spin': loading }]"
          ></i>
        </button>
      </div>
    </div>
    
    <div class="card-content">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p class="loading-text">数据加载中...</p>
        </div>
      </div>
      
      <div v-else-if="error" class="error-container">
        <div class="error-content">
          <i class="fas fa-exclamation-triangle error-icon"></i>
          <h4 class="error-title">加载失败</h4>
          <p class="error-message">{{ error }}</p>
          <button @click="handleRefresh" class="retry-btn">
            <i class="fas fa-redo"></i>
            重试
          </button>
        </div>
      </div>
      
      <div v-else class="chart-container">
        <slot></slot>
      </div>
    </div>
    
    <div v-if="showFooter" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  subtitle?: string
  loading?: boolean
  error?: string | null
  showFooter?: boolean
}

interface Emits {
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '',
  loading: false,
  error: null,
  showFooter: false
})

const emit = defineEmits<Emits>()

const handleRefresh = () => {
  if (!props.loading) {
    emit('refresh')
  }
}
</script>

<style scoped>
.graph-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.graph-card:hover {
  box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 24px;
}

.card-title-section {
  flex: 1;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.card-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.refresh-btn {
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.refresh-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #f8fafc;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn i {
  font-size: 0.875rem;
}

.card-content {
  padding: 0 24px 24px 24px;
  min-height: 200px;
  position: relative;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.error-content {
  text-align: center;
  max-width: 300px;
}

.error-icon {
  font-size: 3rem;
  color: #ef4444;
  margin-bottom: 16px;
}

.error-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.error-message {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.retry-btn {
  padding: 8px 16px;
  border: 1px solid #3b82f6;
  border-radius: 6px;
  background: white;
  color: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.retry-btn:hover {
  background: #3b82f6;
  color: white;
}

.retry-btn i {
  margin-right: 6px;
}

.chart-container {
  position: relative;
  width: 100%;
  min-height: 300px;
}

.card-footer {
  padding: 16px 24px;
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
}

/* Responsive design */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .card-controls {
    justify-content: flex-end;
  }
  
  .card-content {
    padding: 0 16px 16px 16px;
  }
  
  .loading-container,
  .error-container {
    min-height: 250px;
  }
  
  .chart-container {
    min-height: 250px;
  }
}

@media (max-width: 480px) {
  .card-header {
    padding: 16px 16px 0 16px;
  }
  
  .card-title {
    font-size: 1.125rem;
  }
  
  .card-subtitle {
    font-size: 0.8rem;
  }
  
  .card-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .refresh-btn {
    align-self: flex-end;
  }
}</style>