<template>
  <nav class="pagination" v-if="totalPages > 1">
    <div class="pagination__info">
      显示第 {{ startItem }} - {{ endItem }} 项，共 {{ total }} 项
    </div>
    
    <div class="pagination__controls">
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage === 1"
        @click="handlePageChange(1)"
      >
        首页
      </Button>
      
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage === 1"
        @click="handlePageChange(currentPage - 1)"
      >
        上一页
      </Button>
      
      <div class="pagination__pages">
        <Button
          v-for="page in visiblePages"
          :key="page"
          :variant="page === currentPage ? 'primary' : 'ghost'"
          size="sm"
          @click="handlePageChange(page)"
        >
          {{ page }}
        </Button>
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage === totalPages"
        @click="handlePageChange(currentPage + 1)"
      >
        下一页
      </Button>
      
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage === totalPages"
        @click="handlePageChange(totalPages)"
      >
        末页
      </Button>
    </div>
    
    <div class="pagination__size-selector" v-if="showSizeSelector">
      <Select
        :modelValue="pageSize.toString()"
        @update:modelValue="handlePageSizeChange"
        size="sm"
      >
        <option value="10">10 条/页</option>
        <option value="20">20 条/页</option>
        <option value="50">50 条/页</option>
        <option value="100">100 条/页</option>
      </Select>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from './Button.vue'
import Select from './Select.vue'

interface Props {
  currentPage: number
  pageSize: number
  total: number
  showSizeSelector?: boolean
  maxVisiblePages?: number
}

interface Emits {
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
}

const props = withDefaults(defineProps<Props>(), {
  showSizeSelector: true,
  maxVisiblePages: 7
})

const emit = defineEmits<Emits>()

const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize)
})

const startItem = computed(() => {
  return (props.currentPage - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  return Math.min(props.currentPage * props.pageSize, props.total)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = props.currentPage
  const max = props.maxVisiblePages

  if (total <= max) {
    // 如果总页数小于等于最大显示页数，显示所有页
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 否则计算需要显示的页码
    const half = Math.floor(max / 2)
    let start = Math.max(1, current - half)
    let end = Math.min(total, start + max - 1)

    // 调整起始位置
    if (end - start + 1 < max) {
      start = Math.max(1, end - max + 1)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return pages
})

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('page-change', page)
  }
}

const handlePageSizeChange = (value: string) => {
  const size = parseInt(value, 10)
  emit('size-change', size)
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  border-top: 1px solid #e5e7eb;
}

.pagination__info {
  color: #6b7280;
  font-size: 0.875rem;
}

.pagination__controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination__pages {
  display: flex;
  gap: 0.25rem;
}

.pagination__size-selector {
  min-width: 120px;
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .pagination__controls {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination__info {
    order: 2;
  }
}
</style>