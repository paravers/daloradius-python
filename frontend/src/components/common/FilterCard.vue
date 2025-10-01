<template>
  <Card class="filter-card">
    <template #header>
      <div class="filter-card__header">
        <Icon name="filter" />
        <span>{{ title || '过滤器' }}</span>
        <Button
          v-if="clearable && hasActiveFilters"
          variant="ghost"
          size="sm"
          @click="handleClear"
        >
          清除
        </Button>
      </div>
    </template>

    <div class="filter-card__content">
      <slot />
    </div>

    <template #footer v-if="showFooter">
      <div class="filter-card__footer">
        <Button
          variant="ghost"
          @click="handleReset"
        >
          重置
        </Button>
        <Button
          variant="primary"
          @click="handleApply"
        >
          应用
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from './Card.vue'
import Button from './Button.vue'
import Icon from './Icon.vue'

interface Props {
  title?: string
  clearable?: boolean
  showFooter?: boolean
  hasActiveFilters?: boolean
}

interface Emits {
  (e: 'clear'): void
  (e: 'reset'): void
  (e: 'apply'): void
}

withDefaults(defineProps<Props>(), {
  clearable: true,
  showFooter: true,
  hasActiveFilters: false
})

const emit = defineEmits<Emits>()

const handleClear = () => {
  emit('clear')
}

const handleReset = () => {
  emit('reset')
}

const handleApply = () => {
  emit('apply')
}
</script>

<style scoped>
.filter-card__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.filter-card__content {
  padding: 1rem 0;
}

.filter-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
</style>