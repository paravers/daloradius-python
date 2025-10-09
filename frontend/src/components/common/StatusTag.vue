<template>
  <span class="status-tag" :class="statusClass">
    <span class="status-tag__dot"></span>
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'active' | 'inactive' | 'pending' | 'success' | 'error' | 'warning'
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

const statusClass = computed(() => {
  return {
    [`status-tag--${props.status}`]: true,
    [`status-tag--${props.size}`]: true,
  }
})
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  border-radius: 9999px;
  font-weight: 500;
  line-height: 1;
}

.status-tag--sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.status-tag--md {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.status-tag--lg {
  padding: 0.5rem 1rem;
  font-size: 1rem;
}

.status-tag__dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-tag--active {
  background-color: #d1fae5;
  color: #047857;
}

.status-tag--active .status-tag__dot {
  background-color: #10b981;
}

.status-tag--inactive {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-tag--inactive .status-tag__dot {
  background-color: #9ca3af;
}

.status-tag--pending {
  background-color: #fef3c7;
  color: #d97706;
}

.status-tag--pending .status-tag__dot {
  background-color: #f59e0b;
}

.status-tag--success {
  background-color: #d1fae5;
  color: #047857;
}

.status-tag--success .status-tag__dot {
  background-color: #10b981;
}

.status-tag--error {
  background-color: #fee2e2;
  color: #dc2626;
}

.status-tag--error .status-tag__dot {
  background-color: #ef4444;
}

.status-tag--warning {
  background-color: #fef3c7;
  color: #d97706;
}

.status-tag--warning .status-tag__dot {
  background-color: #f59e0b;
}
</style>
