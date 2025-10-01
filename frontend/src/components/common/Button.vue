<template>
  <button 
    class="button"
    :class="buttonClass"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span v-if="loading" class="button__loading">Loading...</span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
  block?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button'
})

const emit = defineEmits<Emits>()

const buttonClass = computed(() => {
  return {
    [`button--${props.variant}`]: true,
    [`button--${props.size}`]: true,
    'button--disabled': props.disabled,
    'button--loading': props.loading,
    'button--block': props.block
  }
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Variants */
.button--primary {
  background-color: #3b82f6;
  color: white;
}

.button--primary:hover:not(.button--disabled) {
  background-color: #2563eb;
}

.button--secondary {
  background-color: #6b7280;
  color: white;
}

.button--secondary:hover:not(.button--disabled) {
  background-color: #4b5563;
}

.button--danger {
  background-color: #ef4444;
  color: white;
}

.button--danger:hover:not(.button--disabled) {
  background-color: #dc2626;
}

.button--success {
  background-color: #10b981;
  color: white;
}

.button--success:hover:not(.button--disabled) {
  background-color: #059669;
}

.button--warning {
  background-color: #f59e0b;
  color: white;
}

.button--warning:hover:not(.button--disabled) {
  background-color: #d97706;
}

.button--ghost {
  background-color: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.button--ghost:hover:not(.button--disabled) {
  background-color: #f3f4f6;
}

/* Sizes */
.button--sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.button--md {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.button--lg {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

/* States */
.button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button--loading {
  cursor: wait;
}

.button--block {
  width: 100%;
}

.button__loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>