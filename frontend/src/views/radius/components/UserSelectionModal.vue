<template>
  <a-modal
    :visible="visible"
    title="选择用户"
    @ok="handleSelect"
    @cancel="handleCancel"
    :width="500"
  >
    <a-input
      v-model:value="searchValue"
      placeholder="搜索用户名"
      allow-clear
    >
      <template #prefix>
        <SearchOutlined />
      </template>
    </a-input>
    
    <div class="user-list" style="margin-top: 16px; max-height: 300px; overflow-y: auto;">
      <a-list
        :data-source="filteredUsers"
        size="small"
      >
        <template #renderItem="{ item }">
          <a-list-item
            style="cursor: pointer;"
            @click="selectUser(item)"
          >
            <a-list-item-meta>
              <template #title>{{ item.username }}</template>
              <template #description>
                {{ item.attributeCount }} 个属性
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { SearchOutlined } from '@ant-design/icons-vue';

// ===== Props & Emits =====
interface Props {
  visible: boolean;
}

interface Emits {
  (e: 'update:visible', visible: boolean): void;
  (e: 'select', username: string): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

// ===== Local State =====
const searchValue = ref('');

// Mock user data - TODO: Replace with actual data from service
const users = [
  { username: 'testuser1', attributeCount: 5 },
  { username: 'testuser2', attributeCount: 3 },
  { username: 'admin', attributeCount: 8 }
];

// ===== Computed =====
const filteredUsers = computed(() => {
  if (!searchValue.value) return users;
  return users.filter(user => 
    user.username.toLowerCase().includes(searchValue.value.toLowerCase())
  );
});

// ===== Methods =====
const selectUser = (user: any) => {
  emit('select', user.username);
};

const handleSelect = () => {
  if (filteredUsers.value.length > 0) {
    selectUser(filteredUsers.value[0]);
  }
};

const handleCancel = () => {
  emit('update:visible', false);
};
</script>