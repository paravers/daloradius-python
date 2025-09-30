&lt;template&gt;
  &lt;div v-if="show" class="modal-overlay" @click.self="handleCancel"&gt;
    &lt;div class="modal-content"&gt;
      &lt;div class="modal-header"&gt;
        &lt;h3 class="modal-title"&gt;{{ title || '确认操作' }}&lt;/h3&gt;
      &lt;/div&gt;
      &lt;div class="modal-body"&gt;
        &lt;p&gt;{{ message || '您确定要执行此操作吗？' }}&lt;/p&gt;
      &lt;/div&gt;
      &lt;div class="modal-footer"&gt;
        &lt;button @click="handleCancel" class="btn btn-secondary"&gt;
          {{ cancelText || '取消' }}
        &lt;/button&gt;
        &lt;button @click="handleConfirm" class="btn" :class="confirmButtonClass"&gt;
          {{ confirmText || '确认' }}
        &lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script setup lang="ts"&gt;
import { computed } from 'vue'

interface Props {
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info' | 'primary'
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps&lt;Props&gt;(), {
  type: 'primary'
})

const emit = defineEmits&lt;Emits&gt;()

const confirmButtonClass = computed(() => {
  switch (props.type) {
    case 'danger':
      return 'btn-danger'
    case 'warning':
      return 'btn-warning'
    case 'info':
      return 'btn-info'
    default:
      return 'btn-primary'
  }
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
&lt;/script&gt;

&lt;style scoped&gt;
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
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-body {
  padding: 1rem;
}

.modal-body p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background-color: #d97706;
}

.btn-info {
  background-color: #06b6d4;
  color: white;
}

.btn-info:hover {
  background-color: #0891b2;
}
&lt;/style&gt;