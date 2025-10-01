<template>
  <span class="tag" :class="tagClass">
    <slot />
    <button v-if="closable" class="tag__close" @click="handleClose">×</button>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  closable?: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md'
})

const emit = defineEmits<Emits>()

const tagClass = computed(() => {
  return {
    [`tag--${props.variant}`]: true,
    [`tag--${props.size}`]: true,
    'tag--closable': props.closable
  }
})

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  border-radius: 9999px;
  font-weight: 500;
  line-height: 1;
}

.tag--sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.tag--md {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.tag--lg {
  padding: 0.5rem 1rem;
  font-size: 1rem;
}

.tag--default {
  background-color: #f3f4f6;
  color: #374151;
}

.tag--primary {
  background-color: #dbeafe;
  color: #1e40af;
}

.tag--success {
  background-color: #d1fae5;
  color: #047857;
}

.tag--warning {
  background-color: #fef3c7;
  color: #d97706;
}

.tag--danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.tag--info {
  background-color: #e0f2fe;
  color: #0284c7;
}

.tag__close {
  background: none;
  border: none;
  padding: 0;
  margin-left: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.7;
}

.tag__close:hover {
  opacity: 1;
}
</style>