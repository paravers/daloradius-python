<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore, useAppStore } from '@/stores'

const authStore = useAuthStore()
const appStore = useAppStore()

onMounted(() => {
  // 初始化应用状态
  appStore.initializeApp()
  authStore.initializeAuth()
})
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
}
</style>
