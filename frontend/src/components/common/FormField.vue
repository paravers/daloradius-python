<template>
  <div class="form-field" :class="fieldClass">
    <label v-if="label" class="form-field__label" :for="inputId">
      {{ label }}
      <span v-if="required" class="form-field__required">*</span>
    </label>
    <div class="form-field__input">
      <slot />
    </div>
    <div v-if="error" class="form-field__error">{{ error }}</div>
    <div v-if="help" class="form-field__help">{{ help }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label?: string
  error?: string
  help?: string
  required?: boolean
  disabled?: boolean
  inputId?: string
}

const props = defineProps<Props>()

const fieldClass = computed(() => {
  return {
    'form-field--error': !!props.error,
    'form-field--disabled': props.disabled
  }
})
</script>

<style scoped>
.form-field {
  margin-bottom: 1rem;
}

.form-field__label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-field__required {
  color: #ef4444;
  margin-left: 0.25rem;
}

.form-field__input {
  position: relative;
}

.form-field__error {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.form-field__help {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.form-field--disabled .form-field__label {
  color: #9ca3af;
}
</style>