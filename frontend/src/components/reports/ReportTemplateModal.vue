<template>
  <a-modal v-model:open="isVisible" title="报表模板" width="800px" :footer="null">
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane key="my" tab="我的模板">
        <a-list :data-source="myTemplates" :loading="loading">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #title>
                  <a @click="selectTemplate(item)">{{ item.name }}</a>
                </template>
                <template #description>
                  {{ item.description }}
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="link" size="small" @click="selectTemplate(item)"> 使用 </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-tab-pane>

      <a-tab-pane key="public" tab="公共模板">
        <a-list :data-source="publicTemplates" :loading="loading">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #title>
                  <a @click="selectTemplate(item)">{{ item.name }}</a>
                </template>
                <template #description>
                  {{ item.description }}
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="link" size="small" @click="selectTemplate(item)"> 使用 </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-tab-pane>
    </a-tabs>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { message } from 'ant-design-vue'

interface Template {
  id: number
  name: string
  description?: string
  report_type: string
}

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'template-selected', template: Template): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isVisible = ref(props.visible)
const activeKey = ref('my')
const loading = ref(false)

// Mock data
const myTemplates = ref<Template[]>([
  {
    id: 1,
    name: '每日在线用户报表',
    description: '显示每日在线用户统计数据',
    report_type: 'online_users',
  },
  {
    id: 2,
    name: '月度流量报表',
    description: '按月统计用户流量使用情况',
    report_type: 'top_users',
  },
])

const publicTemplates = ref<Template[]>([
  {
    id: 10,
    name: '标准在线用户报表',
    description: '系统预置的在线用户报表模板',
    report_type: 'online_users',
  },
  {
    id: 11,
    name: '标准历史报表',
    description: '系统预置的历史会话报表模板',
    report_type: 'history',
  },
])

watch(
  () => props.visible,
  (val) => {
    isVisible.value = val
  },
)

watch(isVisible, (val) => {
  emit('update:visible', val)
})

const selectTemplate = (template: Template) => {
  emit('template-selected', template)
  message.success(`已选择模板: ${template.name}`)
  isVisible.value = false
}
</script>
