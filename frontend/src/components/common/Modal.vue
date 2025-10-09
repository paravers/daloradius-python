<template>
  <teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="handleOverlayClick">
      <div class="modal-content" :class="modalClass">
        <div class="modal-header" v-if="title || $slots.header">
          <h3 class="modal-title" v-if="title">{{ title }}</h3>
          <slot name="header" />
          <button v-if="closable" class="modal-close" @click="handleClose">×</button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div class="modal-footer" v-if="$slots.footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  show: boolean
  title?: string
  closable?: boolean
  closeOnOverlay?: boolean
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

interface Emits {
  (e: 'close'): void
  (e: 'update:show', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  closable: true,
  closeOnOverlay: true,
  size: 'md',
})

const emit = defineEmits<Emits>()

const modalClass = computed(() => {
  return {
    [`modal-content--${props.size}`]: true,
  }
})

const handleClose = () => {
  emit('close')
  emit('update:show', false)
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleClose()
  }
}

// Prevent body scroll when modal is open
watch(
  () => props.show,
  (show) => {
    if (show) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  },
)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
  width: 100%;
}

.modal-content--sm {
  max-width: 28rem;
}

.modal-content--md {
  max-width: 32rem;
}

.modal-content--lg {
  max-width: 48rem;
}

.modal-content--xl {
  max-width: 64rem;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}
</style>
