<template>
  <div class="radcheck-table">
    <DataTable
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      @page-change="$emit('page-change', $event.page, $event.size)"
    >
      <!-- Username Column -->
      <template #username="{ record }">
        <a-typography-text copyable>{{ record.username }}</a-typography-text>
      </template>

      <!-- Attribute Column -->
      <template #attribute="{ record }">
        <a-tag :color="getAttributeColor(record.attribute)">
          {{ record.attribute }}
        </a-tag>
      </template>

      <!-- Operator Column -->
      <template #op="{ record }">
        <a-tag color="blue">{{ record.op }}</a-tag>
      </template>

      <!-- Value Column -->
      <template #value="{ record }">
        <a-typography-text
          :copyable="!isPasswordAttribute(record.attribute)"
          :ellipsis="{ tooltip: record.value }"
          style="max-width: 200px"
        >
          {{ isPasswordAttribute(record.attribute) ? '••••••••' : record.value }}
        </a-typography-text>
      </template>

      <!-- Created At Column -->
      <template #created_at="{ record }">
        <Time :value="record.created_at" format="YYYY-MM-DD HH:mm" />
      </template>

      <!-- Actions Column -->
      <template #actions="{ record }">
        <a-space>
          <a-button
            type="link"
            size="small"
            @click="$emit('edit', record)"
          >
            编辑
          </a-button>
          <a-button
            type="link"
            size="small"
            danger
            @click="$emit('delete', record)"
          >
            删除
          </a-button>
          <a-dropdown>
            <template #overlay>
              <a-menu @click="handleMenuClick($event, record)">
                <a-menu-item key="duplicate">复制属性</a-menu-item>
                <a-menu-item key="view-user">查看用户</a-menu-item>
                <a-menu-item key="export">导出数据</a-menu-item>
              </a-menu>
            </template>
            <a-button type="link" size="small">
              更多
              <DownOutlined />
            </a-button>
          </a-dropdown>
        </a-space>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';
import { message } from 'ant-design-vue';
import { DownOutlined } from '@ant-design/icons-vue';
import DataTable from '@/components/common/DataTable.vue';
import Time from '@/components/common/Time.vue';
import type { RadCheck } from '@/types/radius';
import type { TableColumn } from '@/types/common';

// ===== Props & Emits =====
interface Props {
  data: RadCheck[];
  loading?: boolean;
  pagination?: any;
}

interface Emits {
  (e: 'edit', record: RadCheck): void;
  (e: 'delete', record: RadCheck): void;
  (e: 'page-change', page: number, size: number): void;
}

defineProps<Props>();
defineEmits<Emits>();

// ===== Table Columns =====
const columns: TableColumn[] = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 120,
    fixed: 'left',
    sorter: true,
    slots: { customRender: 'username' }
  },
  {
    title: '属性名',
    dataIndex: 'attribute',
    key: 'attribute',
    width: 150,
    sorter: true,
    slots: { customRender: 'attribute' }
  },
  {
    title: '操作符',
    dataIndex: 'op',
    key: 'op',
    width: 80,
    align: 'center',
    slots: { customRender: 'op' }
  },
  {
    title: '属性值',
    dataIndex: 'value',
    key: 'value',
    width: 200,
    ellipsis: true,
    slots: { customRender: 'value' }
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
    sorter: true,
    slots: { customRender: 'created_at' }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    slots: { customRender: 'actions' }
  }
];

// ===== Methods =====

/**
 * Get color for different attribute types
 */
const getAttributeColor = (attribute: string): string => {
  if (attribute.includes('Password')) return 'red';
  if (attribute.includes('Timeout')) return 'orange';
  if (attribute.includes('IP')) return 'blue';
  if (attribute.includes('Auth')) return 'purple';
  return 'default';
};

/**
 * Check if attribute is a password type
 */
const isPasswordAttribute = (attribute: string): boolean => {
  const passwordAttrs = [
    'User-Password',
    'Cleartext-Password',
    'Crypt-Password',
    'MD5-Password',
    'SHA-Password',
    'NT-Password',
    'LM-Password'
  ];
  return passwordAttrs.includes(attribute);
};

/**
 * Handle dropdown menu clicks
 */
const handleMenuClick = ({ key }: { key: string }, record: RadCheck) => {
  switch (key) {
    case 'duplicate':
      // TODO: Implement duplicate functionality
      message.info('复制功能将在后续版本中实现');
      break;
    case 'view-user':
      // TODO: Navigate to user detail
      message.info(`查看用户 ${record.username} 的详细信息`);
      break;
    case 'export':
      // TODO: Implement export functionality
      message.info('导出功能将在后续版本中实现');
      break;
  }
};
</script>

<style scoped lang="less">
.radcheck-table {
  .ant-tag {
    margin: 0;
  }
  
  .ant-typography {
    margin-bottom: 0;
  }
}
</style>