<template>
  <a-modal
    :visible="visible"
    title="批量操作"
    @ok="handleComplete"
    @cancel="handleCancel"
    :width="600"
  >
    <div class="bulk-operations">
      <p>已选择 {{ selectedItems.length }} 个属性项</p>
      
      <a-space direction="vertical" style="width: 100%;">
        <a-button block type="primary" danger @click="bulkDelete">
          批量删除
        </a-button>
        
        <a-button block @click="bulkExport">
          批量导出
        </a-button>
        
        <a-button block @click="bulkModify">
          批量修改
        </a-button>
      </a-space>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { message } from 'ant-design-vue';
import type { RadCheck, RadReply } from '@/types/radius';

// ===== Props & Emits =====
interface Props {
  visible: boolean;
  selectedItems: (RadCheck | RadReply)[];
}

interface Emits {
  (e: 'update:visible', visible: boolean): void;
  (e: 'complete'): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

// ===== Methods =====
const bulkDelete = () => {
  // TODO: Implement bulk delete
  message.info('批量删除功能将在后续版本中实现');
  handleComplete();
};

const bulkExport = () => {
  // TODO: Implement bulk export
  message.info('批量导出功能将在后续版本中实现');
  handleComplete();
};

const bulkModify = () => {
  // TODO: Implement bulk modify
  message.info('批量修改功能将在后续版本中实现');
  handleComplete();
};

const handleComplete = () => {
  emit('complete');
};

const handleCancel = () => {
  emit('update:visible', false);
};
</script>