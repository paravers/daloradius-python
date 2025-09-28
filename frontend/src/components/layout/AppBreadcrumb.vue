<template>
  <a-breadcrumb class="app-breadcrumb">
    <a-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
      <router-link v-if="item.path && !item.disabled" :to="item.path">
        {{ item.title }}
      </router-link>
      <span v-else>{{ item.title }}</span>
    </a-breadcrumb-item>
  </a-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  title: string
  path?: string
  disabled?: boolean
}

const route = useRoute()

const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  
  const breadcrumbItems: BreadcrumbItem[] = [
    {
      title: '首页',
      path: '/dashboard',
    },
  ]
  
  matched.forEach((item, index) => {
    if (item.path !== '/') {
      breadcrumbItems.push({
        title: (item.meta?.title as string) || item.name as string,
        path: index === matched.length - 1 ? undefined : item.path, // 最后一项不可点击
        disabled: index === matched.length - 1,
      })
    }
  })
  
  return breadcrumbItems
})
</script>

<style scoped>
.app-breadcrumb {
  margin: 16px 0;
}
</style>