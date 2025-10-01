<template>
  <div class="stats-card">
    <div class="stats-card__icon" v-if="icon">
      <component :is="icon" class="w-6 h-6" />
    </div>
    <div class="stats-card__content">
      <div class="stats-card__value">{{ value }}</div>
      <div class="stats-card__label">{{ label }}</div>
      <div class="stats-card__change" v-if="change" :class="changeClass">
        {{ formatChange(change) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: string | number
  label: string
  change?: number
  icon?: any
  color?: 'primary' | 'success' | 'warning' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary'
})

const changeClass = computed(() => {
  if (!props.change) return ''
  return props.change > 0 ? 'stats-card__change--positive' : 'stats-card__change--negative'
})

const formatChange = (change: number) => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(1)}%`
}
</script>

<style scoped>
.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.stats-card__icon {
  margin-right: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background-color: #f3f4f6;
}

.stats-card__content {
  flex: 1;
}

.stats-card__value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stats-card__label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.stats-card__change {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0.25rem;
}

.stats-card__change--positive {
  color: #10b981;
}

.stats-card__change--negative {
  color: #ef4444;
}
</style>