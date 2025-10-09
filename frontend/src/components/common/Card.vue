<template>
  <div class="card" :class="cardClass">
    <div class="card__header" v-if="title || $slots.header">
      <h3 class="card__title" v-if="title">{{ title }}</h3>
      <slot name="header" />
    </div>
    <div class="card__body">
      <slot />
    </div>
    <div class="card__footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  border?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'sm',
  border: true,
  padding: 'md',
})

const cardClass = computed(() => {
  return {
    [`card--shadow-${props.shadow}`]: props.shadow !== 'none',
    'card--no-border': !props.border,
    [`card--padding-${props.padding}`]: true,
  }
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.card--shadow-sm {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card--shadow-md {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card--shadow-lg {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.card:not(.card--no-border) {
  border: 1px solid #e5e7eb;
}

.card__header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.card__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.card__body {
  padding: 1rem;
}

.card--padding-none .card__body {
  padding: 0;
}

.card--padding-sm .card__body {
  padding: 0.5rem;
}

.card--padding-lg .card__body {
  padding: 1.5rem;
}

.card__footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}
</style>
