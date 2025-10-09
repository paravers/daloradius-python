<template>
  <input
    v-model="internalValue"
    class="input"
    :class="inputClass"
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    :readonly="readonly"
    @input="handleInput"
    @blur="handleBlur"
    @focus="handleFocus"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  modelValue?: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  error?: boolean
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'input', value: string | number): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
})

const emit = defineEmits<Emits>()

const internalValue = ref(props.modelValue || '')

watch(
  () => props.modelValue,
  (newValue) => {
    internalValue.value = newValue || ''
  },
)

const inputClass = computed(() => {
  return {
    'input--error': props.error,
    'input--disabled': props.disabled,
    'input--readonly': props.readonly,
    [`input--${props.size}`]: true,
  }
})

const handleInput = () => {
  emit('update:modelValue', internalValue.value)
  emit('input', internalValue.value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}
</script>

<style scoped>
.input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input--sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.input--md {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.input--lg {
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.input--error {
  border-color: #ef4444;
}

.input--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.input--disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
}

.input--readonly {
  background-color: #f9fafb;
  cursor: default;
}
</style>
