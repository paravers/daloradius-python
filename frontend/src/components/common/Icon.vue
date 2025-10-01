<template>
  <component :is="iconComponent" :class="iconClass" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  name: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const iconComponent = computed(() => {
  // Simple placeholder - in a real app you'd map to actual icon components
  return 'div'
})

const iconClass = computed(() => {
  return {
    'icon': true,
    [`icon--${props.size}`]: true,
    [`text-${props.color}`]: props.color
  }
})
</script>

<style scoped>
.icon {
  display: inline-block;
  flex-shrink: 0;
}

.icon--xs {
  width: 0.75rem;
  height: 0.75rem;
}

.icon--sm {
  width: 1rem;
  height: 1rem;
}

.icon--md {
  width: 1.25rem;
  height: 1.25rem;
}

.icon--lg {
  width: 1.5rem;
  height: 1.5rem;
}

.icon--xl {
  width: 2rem;
  height: 2rem;
}
</style>