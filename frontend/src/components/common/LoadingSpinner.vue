<template>
  <div class="loading-spinner" :class="spinnerClass">
    <div class="loading-spinner__spinner"></div>
    <div v-if="text" class="loading-spinner__text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  overlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  overlay: false
})

const spinnerClass = computed(() => {
  return {
    [`loading-spinner--${props.size}`]: true,
    'loading-spinner--overlay': props.overlay
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loading-spinner--overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.loading-spinner__spinner {
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: loading-spinner-spin 1s linear infinite;
}

.loading-spinner--sm .loading-spinner__spinner {
  width: 1rem;
  height: 1rem;
}

.loading-spinner--md .loading-spinner__spinner {
  width: 1.5rem;
  height: 1.5rem;
}

.loading-spinner--lg .loading-spinner__spinner {
  width: 2rem;
  height: 2rem;
}

.loading-spinner__text {
  color: #6b7280;
  font-size: 0.875rem;
}

.loading-spinner--overlay .loading-spinner__text {
  color: white;
}

@keyframes loading-spinner-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>