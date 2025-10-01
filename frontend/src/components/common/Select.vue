<template>
  <select 
    v-model="internalValue" 
    class="select"
    :class="selectClass"
    :disabled="disabled"
    @change="handleChange"
  >
    <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
    <option 
      v-for="option in options" 
      :key="getOptionValue(option)" 
      :value="getOptionValue(option)"
    >
      {{ getOptionLabel(option) }}
    </option>
  </select>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Option {
  label: string
  value: string | number
  disabled?: boolean
}

interface Props {
  modelValue?: string | number
  options: Option[] | string[] | number[]
  placeholder?: string
  disabled?: boolean
  error?: boolean
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const emit = defineEmits<Emits>()

const internalValue = ref(props.modelValue || '')

watch(() => props.modelValue, (newValue) => {
  internalValue.value = newValue || ''
})

const selectClass = computed(() => {
  return {
    'select--error': props.error,
    'select--disabled': props.disabled,
    [`select--${props.size}`]: true
  }
})

const getOptionValue = (option: Option | string | number): string | number => {
  if (typeof option === 'object') {
    return option.value
  }
  return option
}

const getOptionLabel = (option: Option | string | number): string => {
  if (typeof option === 'object') {
    return option.label
  }
  return String(option)
}

const handleChange = () => {
  emit('update:modelValue', internalValue.value)
  emit('change', internalValue.value)
}
</script>

<style scoped>
.select {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select--sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.select--md {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.select--lg {
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.select--error {
  border-color: #ef4444;
}

.select--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.select--disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}
</style>