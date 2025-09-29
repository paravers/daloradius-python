<template>
  <div class="radius-attributes-view">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <RadiusIcon />
          RADIUS 属性管理
        </h1>
        <p class="page-description">
          管理用户的 RADIUS 认证和授权属性，包括检查属性 (RadCheck) 和回复属性 (RadReply)
        </p>
      </div>
      
      <!-- Action Buttons -->
      <div class="header-actions">
        <a-button
          type="primary"
          :icon="h(PlusOutlined)"
          @click="showCreateModal"
        >
          新建属性
        </a-button>
        <a-button
          :icon="h(ReloadOutlined)"
          @click="refreshData"
          :loading="isLoading"
        >
          刷新
        </a-button>
        <a-dropdown>
          <template #overlay>
            <a-menu @click="handleExportAction">
              <a-menu-item key="export-check">导出 RadCheck</a-menu-item>
              <a-menu-item key="export-reply">导出 RadReply</a-menu-item>
              <a-menu-item key="export-all">导出全部</a-menu-item>
            </a-menu>
          </template>
          <a-button>
            <DownloadOutlined />
            导出
            <DownOutlined />
          </a-button>
        </a-dropdown>
      </div>
    </div>

    <!-- Search and Filter Section -->
    <div class="search-section">
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-input
            v-model:value="searchForm.search"
            placeholder="搜索用户名、属性名或值"
            allow-clear
            @change="handleSearch"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-select
            v-model:value="searchForm.username"
            placeholder="选择用户"
            allow-clear
            show-search
            :filter-option="filterOption"
            @change="handleUsernameFilter"
          >
            <a-select-option
              v-for="user in uniqueUsers"
              :key="user"
              :value="user"
            >
              {{ user }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-select
            v-model:value="searchForm.attribute"
            placeholder="选择属性类型"
            allow-clear
            @change="handleAttributeFilter"
          >
            <a-select-option
              v-for="attr in commonAttributes"
              :key="attr"
              :value="attr"
            >
              {{ attr }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-button-group>
            <a-button
              :type="activeTab === 'check' ? 'primary' : 'default'"
              @click="setActiveTab('check')"
            >
              RadCheck ({{ checkPagination.total }})
            </a-button>
            <a-button
              :type="activeTab === 'reply' ? 'primary' : 'default'"
              @click="setActiveTab('reply')"
            >
              RadReply ({{ replyPagination.total }})
            </a-button>
          </a-button-group>
        </a-col>
      </a-row>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-section" v-if="showStats">
      <a-row :gutter="[16, 16]">
        <a-col :xs="12" :sm="6">
          <StatCard
            title="RadCheck 属性"
            :value="checkPagination.total"
            :loading="loadingCheck"
            color="#1890ff"
          />
        </a-col>
        <a-col :xs="12" :sm="6">
          <StatCard
            title="RadReply 属性"
            :value="replyPagination.total"
            :loading="loadingReply"
            color="#52c41a"
          />
        </a-col>
        <a-col :xs="12" :sm="6">
          <StatCard
            title="总属性数"
            :value="totalAttributes"
            :loading="isLoading"
            color="#722ed1"
          />
        </a-col>
        <a-col :xs="12" :sm="6">
          <StatCard
            title="用户数"
            :value="uniqueUsers.length"
            :loading="isLoading"
            color="#fa8c16"
          />
        </a-col>
      </a-row>
    </div>

    <!-- Main Content Tabs -->
    <div class="content-section">
      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <!-- RadCheck Tab -->
        <a-tab-pane key="check" tab="RadCheck 认证属性">
          <RadCheckTable
            :data="radCheckAttributes"
            :loading="loadingCheck"
            :pagination="checkPagination"
            @edit="handleEditCheck"
            @delete="handleDeleteCheck"
            @page-change="handleCheckPaginationChange"
          />
        </a-tab-pane>

        <!-- RadReply Tab -->
        <a-tab-pane key="reply" tab="RadReply 授权属性">
          <RadReplyTable
            :data="radReplyAttributes"
            :loading="loadingReply"
            :pagination="replyPagination"
            @edit="handleEditReply"
            @delete="handleDeleteReply"
            @page-change="handleReplyPaginationChange"
          />
        </a-tab-pane>

        <!-- User Attributes Tab -->
        <a-tab-pane key="user" tab="用户属性视图">
          <UserAttributesView
            :user-attributes="userAttributes"
            :loading="loading"
            @set-password="handleSetPassword"
            @refresh="loadUserAttributesData"
          />
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- Create/Edit Modal -->
    <RadiusAttributeModal
      v-model:visible="modalVisible"
      :mode="modalMode"
      :attribute-type="modalAttributeType"
      :initial-data="currentEditingAttribute"
      :common-check-attributes="commonCheckAttributes"
      :common-reply-attributes="commonReplyAttributes"
      :radius-operators="radiusOperators"
      @submit="handleModalSubmit"
      @cancel="handleModalCancel"
    />

    <!-- User Selection Modal -->
    <UserSelectionModal
      v-model:visible="userModalVisible"
      @select="handleUserSelect"
    />

    <!-- Bulk Operations Modal -->
    <BulkOperationsModal
      v-model:visible="bulkModalVisible"
      :selected-items="selectedItems"
      @complete="handleBulkComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  DownloadOutlined,
  DownOutlined
} from '@ant-design/icons-vue';

// Components
import StatCard from '@/components/common/StatCard.vue';
import RadCheckTable from './components/RadCheckTable.vue';
import RadReplyTable from './components/RadReplyTable.vue';
import UserAttributesView from './components/UserAttributesView.vue';
import RadiusAttributeModal from './components/RadiusAttributeModal.vue';
import UserSelectionModal from './components/UserSelectionModal.vue';
import BulkOperationsModal from './components/BulkOperationsModal.vue';
import RadiusIcon from '@/components/common/Icon.vue';

// Composables
import { useRadiusManagement } from '@/composables/useRadiusManagement';

// Types
import type {
  RadCheck,
  RadReply,
  RadCheckCreate,
  RadReplyCreate,
  RadiusOperator
} from '@/types/radius';

// ===== Composables =====
const {
  // State
  loading,
  loadingCheck,
  loadingReply,
  radCheckAttributes,
  radReplyAttributes,
  userAttributes,
  checkPagination,
  replyPagination,
  commonCheckAttributes,
  commonReplyAttributes,
  radiusOperators,
  error,
  
  // Computed
  totalAttributes,
  isLoading,
  
  // Methods
  loadRadCheckAttributes,
  loadRadReplyAttributes,
  loadUserAttributes,
  createRadCheckAttribute,
  createRadReplyAttribute,
  updateRadCheckAttribute,
  updateRadReplyAttribute,
  deleteRadCheckAttribute,
  deleteRadReplyAttribute,
  setUserPassword,
  handleCheckPaginationChange,
  handleReplyPaginationChange,
  searchAttributes,
  filterByUsername,
  filterByAttribute,
  loadCommonData,
  resetSearch
} = useRadiusManagement();

// ===== Local State =====
const activeTab = ref<'check' | 'reply' | 'user'>('check');
const showStats = ref(true);
const modalVisible = ref(false);
const userModalVisible = ref(false);
const bulkModalVisible = ref(false);

const modalMode = ref<'create' | 'edit'>('create');
const modalAttributeType = ref<'check' | 'reply'>('check');
const currentEditingAttribute = ref<RadCheck | RadReply | null>(null);
const selectedItems = ref<(RadCheck | RadReply)[]>([]);

// Search form
const searchForm = reactive({
  search: '',
  username: undefined as string | undefined,
  attribute: undefined as string | undefined
});

// ===== Computed Properties =====
const uniqueUsers = computed(() => {
  const users = new Set<string>();
  radCheckAttributes.value.forEach(attr => users.add(attr.username));
  radReplyAttributes.value.forEach(attr => users.add(attr.username));
  return Array.from(users).sort();
});

const commonAttributes = computed(() => {
  const attrs = new Set<string>();
  
  if (commonCheckAttributes.value) {
    Object.values(commonCheckAttributes.value).flat().forEach(attr => attrs.add(attr));
  }
  
  if (commonReplyAttributes.value) {
    Object.values(commonReplyAttributes.value).flat().forEach(attr => attrs.add(attr));
  }
  
  radCheckAttributes.value.forEach(attr => attrs.add(attr.attribute));
  radReplyAttributes.value.forEach(attr => attrs.add(attr.attribute));
  
  return Array.from(attrs).sort();
});

// ===== Methods =====

/**
 * Initialize page data
 */
const initializeData = async () => {
  try {
    await Promise.all([
      loadCommonData(),
      loadRadCheckAttributes(),
      loadRadReplyAttributes()
    ]);
  } catch (err) {
    console.error('Failed to initialize data:', err);
  }
};

/**
 * Refresh all data
 */
const refreshData = async () => {
  await initializeData();
  message.success('数据已刷新');
};

/**
 * Handle search input
 */
const handleSearch = async () => {
  if (searchForm.search.trim()) {
    await searchAttributes(searchForm.search.trim());
  } else {
    await refreshData();
  }
};

/**
 * Handle username filter
 */
const handleUsernameFilter = async () => {
  if (searchForm.username) {
    await filterByUsername(searchForm.username);
  } else {
    await refreshData();
  }
};

/**
 * Handle attribute filter
 */
const handleAttributeFilter = async () => {
  if (searchForm.attribute) {
    await filterByAttribute(searchForm.attribute);
  } else {
    await refreshData();
  }
};

/**
 * Handle tab change
 */
const handleTabChange = (key: string) => {
  activeTab.value = key as 'check' | 'reply' | 'user';
};

/**
 * Set active tab
 */
const setActiveTab = (tab: 'check' | 'reply' | 'user') => {
  activeTab.value = tab;
};

/**
 * Show create modal
 */
const showCreateModal = () => {
  modalMode.value = 'create';
  modalAttributeType.value = activeTab.value === 'reply' ? 'reply' : 'check';
  currentEditingAttribute.value = null;
  modalVisible.value = true;
};

/**
 * Handle edit RadCheck attribute
 */
const handleEditCheck = (attribute: RadCheck) => {
  modalMode.value = 'edit';
  modalAttributeType.value = 'check';
  currentEditingAttribute.value = attribute;
  modalVisible.value = true;
};

/**
 * Handle edit RadReply attribute
 */
const handleEditReply = (attribute: RadReply) => {
  modalMode.value = 'edit';
  modalAttributeType.value = 'reply';
  currentEditingAttribute.value = attribute;
  modalVisible.value = true;
};

/**
 * Handle delete RadCheck attribute
 */
const handleDeleteCheck = (attribute: RadCheck) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${attribute.username}" 的属性 "${attribute.attribute}" 吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      if (attribute.id) {
        await deleteRadCheckAttribute(attribute.id);
      }
    }
  });
};

/**
 * Handle delete RadReply attribute
 */
const handleDeleteReply = (attribute: RadReply) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${attribute.username}" 的属性 "${attribute.attribute}" 吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      if (attribute.id) {
        await deleteRadReplyAttribute(attribute.id);
      }
    }
  });
};

/**
 * Handle modal submit
 */
const handleModalSubmit = async (data: RadCheckCreate | RadReplyCreate) => {
  try {
    if (modalMode.value === 'create') {
      if (modalAttributeType.value === 'check') {
        await createRadCheckAttribute(data as RadCheckCreate);
      } else {
        await createRadReplyAttribute(data as RadReplyCreate);
      }
    } else {
      // Edit mode
      const id = currentEditingAttribute.value?.id;
      if (id) {
        if (modalAttributeType.value === 'check') {
          await updateRadCheckAttribute(id, data as RadCheckCreate);
        } else {
          await updateRadReplyAttribute(id, data as RadReplyCreate);
        }
      }
    }
    
    modalVisible.value = false;
    currentEditingAttribute.value = null;
  } catch (err) {
    // Error handling is done in the composable
    console.error('Modal submit failed:', err);
  }
};

/**
 * Handle modal cancel
 */
const handleModalCancel = () => {
  modalVisible.value = false;
  currentEditingAttribute.value = null;
};

/**
 * Handle user select for user attributes view
 */
const handleUserSelect = async (username: string) => {
  userModalVisible.value = false;
  await loadUserAttributes(username);
  activeTab.value = 'user';
};

/**
 * Handle set password
 */
const handleSetPassword = async (data: { username: string; password: string; passwordType?: string }) => {
  await setUserPassword(data.username, data.password, data.passwordType);
};

/**
 * Load user attributes data
 */
const loadUserAttributesData = async () => {
  if (userAttributes.value?.username) {
    await loadUserAttributes(userAttributes.value.username);
  }
};

/**
 * Handle export actions
 */
const handleExportAction = ({ key }: { key: string }) => {
  // TODO: Implement export functionality
  message.info(`导出功能 "${key}" 将在后续版本中实现`);
};

/**
 * Handle bulk operations complete
 */
const handleBulkComplete = async () => {
  bulkModalVisible.value = false;
  selectedItems.value = [];
  await refreshData();
};

/**
 * Filter option for select components
 */
const filterOption = (input: string, option: any) => {
  return option.value.toLowerCase().includes(input.toLowerCase());
};

// ===== Lifecycle =====
onMounted(() => {
  initializeData();
});
</script>

<style scoped lang="less">
.radius-attributes-view {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    padding: 24px 0 0;
    
    .header-content {
      flex: 1;
      
      .page-title {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: #262626;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .page-description {
        margin: 0;
        color: #8c8c8c;
        font-size: 14px;
        line-height: 1.5;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .search-section {
    background: #fafafa;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 24px;
  }
  
  .stats-section {
    margin-bottom: 24px;
  }
  
  .content-section {
    background: white;
    border-radius: 6px;
    padding: 0;
    
    :deep(.ant-tabs-content-holder) {
      padding: 24px;
    }
    
    :deep(.ant-tabs-nav) {
      padding: 0 24px;
      margin-bottom: 0;
    }
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .radius-attributes-view {
    .page-header {
      flex-direction: column;
      gap: 16px;
      
      .header-actions {
        width: 100%;
        justify-content: flex-start;
      }
    }
    
    .search-section {
      padding: 12px;
    }
    
    .content-section {
      :deep(.ant-tabs-content-holder) {
        padding: 16px;
      }
      
      :deep(.ant-tabs-nav) {
        padding: 0 16px;
      }
    }
  }
}
</style>