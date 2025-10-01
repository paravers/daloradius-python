<template>
  <input 
    v-model="internalValue"
    type="date"
    class="date-picker"
    :class="pickerClass"
    :disabled="disabled"
    :min="min"
    :max="max"
    @change="handleChange"
  >
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  modelValue?: string
  disabled?: boolean
  min?: string
  max?: string
  error?: boolean
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const emit = defineEmits<Emits>()

const internalValue = ref(props.modelValue || '')

watch(() => props.modelValue, (newValue) => {
  internalValue.value = newValue || ''
})

const pickerClass = computed(() => {
  return {
    'date-picker--error': props.error,
    'date-picker--disabled': props.disabled,
    [`date-picker--${props.size}`]: true
  }
})

const handleChange = () => {
  emit('update:modelValue', internalValue.value)
  emit('change', internalValue.value)
}
</script>

<style scoped>
.date-picker {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.date-picker:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.date-picker--sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.date-picker--md {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.date-picker--lg {
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.date-picker--error {
  border-color: #ef4444;
}

.date-picker--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.date-picker--disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}
</style>