<template>
  <Card class="batch-operation-details">
    <template #header>
      <div class="batch-operation-details__header">
        <h3>{{ title }}</h3>
        <span class="batch-operation-details__count">
          已选择 {{ selectedCount }} 项
        </span>
      </div>
    </template>

    <div class="batch-operation-details__content">
      <div class="batch-operation-details__actions">
        <slot name="actions" />
      </div>

      <div v-if="items.length > 0" class="batch-operation-details__items">
        <div class="batch-operation-details__items-header">
          <span>操作项目：</span>
        </div>
        <div class="batch-operation-details__items-list">
          <div 
            v-for="(item, index) in displayItems" 
            :key="index"
            class="batch-operation-details__item"
          >
            {{ formatItem(item) }}
          </div>
          <div v-if="hasMoreItems" class="batch-operation-details__more">
            还有 {{ items.length - maxDisplayItems }} 项...
          </div>
        </div>
      </div>
    </div>

    <template #footer v-if="showFooter">
      <div class="batch-operation-details__footer">
        <Button variant="ghost" @click="handleCancel">
          取消
        </Button>
        <Button 
          variant="primary" 
          :loading="loading"
          @click="handleConfirm"
        >
          确认操作
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from './Card.vue'
import Button from './Button.vue'

interface Props {
  title: string
  items: unknown[]
  selectedCount?: number
  loading?: boolean
  showFooter?: boolean
  maxDisplayItems?: number
  itemFormatter?: (item: unknown) => string
}

interface Emits {
  (e: 'cancel'): void
  (e: 'confirm'): void
}

const props = withDefaults(defineProps<Props>(), {
  selectedCount: 0,
  loading: false,
  showFooter: true,
  maxDisplayItems: 10
})

const emit = defineEmits<Emits>()

const displayItems = computed(() => {
  return props.items.slice(0, props.maxDisplayItems)
})

const hasMoreItems = computed(() => {
  return props.items.length > props.maxDisplayItems
})

const formatItem = (item: unknown): string => {
  if (props.itemFormatter) {
    return props.itemFormatter(item)
  }
  if (typeof item === 'string') {
    return item
  }
  if (typeof item === 'object' && item !== null && 'toString' in item) {
    return (item as { toString(): string }).toString()
  }
  return String(item)
}

const handleCancel = () => {
  emit('cancel')
}

const handleConfirm = () => {
  emit('confirm')
}
</script>

<style scoped>
.batch-operation-details__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-operation-details__header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.batch-operation-details__count {
  background-color: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.batch-operation-details__content {
  padding: 1rem 0;
}

.batch-operation-details__actions {
  margin-bottom: 1rem;
}

.batch-operation-details__items-header {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.batch-operation-details__items-list {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.75rem;
  max-height: 200px;
  overflow-y: auto;
}

.batch-operation-details__item {
  padding: 0.25rem 0;
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 0.875rem;
}

.batch-operation-details__item:last-child {
  border-bottom: none;
}

.batch-operation-details__more {
  color: #9ca3af;
  font-style: italic;
  font-size: 0.875rem;
  padding-top: 0.5rem;
}

.batch-operation-details__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
</style>