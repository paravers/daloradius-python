<template>
  <div class="config-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1>系统配置</h1>
          <p class="page-description">系统参数和配置管理</p>
        </div>
        <div class="header-actions">
          <a-badge :count="modificationCount" :show-zero="false">
            <a-button 
              type="primary" 
              :disabled="!hasModifications"
              :loading="saving"
              @click="handleSave"
            >
              <template #icon><SaveOutlined /></template>
              保存配置
            </a-button>
          </a-badge>
          <a-button 
            :disabled="!hasModifications"
            @click="handleCancel"
          >
            取消修改
          </a-button>
          <a-dropdown>
            <a-button>
              更多操作
              <DownOutlined />
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="showBackupModal = true">
                  <SaveOutlined /> 创建备份
                </a-menu-item>
                <a-menu-item @click="showRestoreModal = true">
                  <ReloadOutlined /> 恢复备份
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="handleExport">
                  <ExportOutlined /> 导出配置
                </a-menu-item>
                <a-menu-item @click="showImportModal = true">
                  <ImportOutlined /> 导入配置
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="showSystemInfoModal = true">
                  <InfoCircleOutlined /> 系统信息
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>
      
      <!-- 修改提示 -->
      <div v-if="hasModifications" class="modification-alert">
        <a-alert
          :message="`您有 ${modificationCount} 项未保存的配置修改`"
          type="warning"
          show-icon
          closable
          @close="handleCancel"
        >
          <template #action>
            <a-space>
              <a-button size="small" @click="handleCancel">取消</a-button>
              <a-button size="small" type="primary" @click="handleSave">保存</a-button>
            </a-space>
          </template>
        </a-alert>
      </div>
    </div>

    <div class="config-content">
      <!-- 左侧分类菜单 -->
      <div class="config-sidebar">
        <a-menu
          v-model:selectedKeys="selectedKeys"
          mode="inline"
          @select="handleCategorySelect"
        >
          <a-menu-item 
            v-for="group in configGroups" 
            :key="group.category"
          >
            <template #icon>
              <component :is="getIcon(group.icon)" />
            </template>
            {{ group.title }}
          </a-menu-item>
        </a-menu>
      </div>

      <!-- 右侧配置表单 -->
      <div class="config-main">
        <a-spin :spinning="loading">
          <div v-if="currentCategoryConfigs.length > 0" class="config-form-container">
            <!-- 分类标题和描述 -->
            <div class="category-header">
              <h2>{{ currentGroupTitle }}</h2>
              <p class="category-description">{{ currentGroupDescription }}</p>
              
              <!-- 分类操作按钮 -->
              <div class="category-actions">
                <a-button 
                  @click="handleTestConfig" 
                  :loading="testing"
                  :disabled="!canTestConfig"
                >
                  <template #icon><ExperimentOutlined /></template>
                  测试连接
                </a-button>
                <a-button @click="handleResetCategory">
                  <template #icon><RedoOutlined /></template>
                  重置为默认值
                </a-button>
              </div>
            </div>

            <!-- 配置表单 -->
            <a-form
              :model="formData"
              :label-col="{ span: 6 }"
              :wrapper-col="{ span: 18 }"
              class="config-form"
            >
              <div
                v-for="config in currentCategoryConfigs"
                :key="config.key"
                class="config-item"
                :class="{ 'config-modified': isConfigModified(config.key) }"
              >
                <!-- 字符串输入 -->
                <a-form-item
                  v-if="config.type === 'string'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-input
                    :value="getConfigValue(config.key)"
                    @input="(e) => updateConfigValue(config.key, e.target.value)"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 密码输入 -->
                <a-form-item
                  v-else-if="config.type === 'password'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-input-password
                    :value="getConfigValue(config.key)"
                    @input="(e) => updateConfigValue(config.key, e.target.value)"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                    autocomplete="new-password"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 数字输入 -->
                <a-form-item
                  v-else-if="config.type === 'number'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-input-number
                    :value="getConfigValue(config.key)"
                    @change="(value) => updateConfigValue(config.key, value)"
                    :min="config.validation?.min"
                    :max="config.validation?.max"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                    style="width: 100%"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 布尔值选择 -->
                <a-form-item
                  v-else-if="config.type === 'boolean'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-switch
                    :checked="getConfigValue(config.key)"
                    @change="(checked) => updateConfigValue(config.key, checked)"
                    :disabled="!config.isEditable"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 选择器 -->
                <a-form-item
                  v-else-if="config.type === 'select'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-select
                    :value="getConfigValue(config.key)"
                    @change="(value) => updateConfigValue(config.key, value)"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                  >
                    <a-select-option
                      v-for="option in config.options"
                      :key="option.value"
                      :value="option.value"
                      :disabled="option.disabled"
                    >
                      {{ option.label }}
                    </a-select-option>
                  </a-select>
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 文本域 -->
                <a-form-item
                  v-else-if="config.type === 'textarea'"
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-textarea
                    :value="getConfigValue(config.key)"
                    @input="(e) => updateConfigValue(config.key, e.target.value)"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                    :rows="4"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>

                <!-- 默认输入 -->
                <a-form-item
                  v-else
                  :label="config.label"
                  :required="config.isRequired"
                >
                  <a-input
                    :value="getConfigValue(config.key)"
                    @input="(e) => updateConfigValue(config.key, e.target.value)"
                    :placeholder="config.description"
                    :disabled="!config.isEditable"
                  />
                  <div v-if="config.description" class="config-help">
                    {{ config.description }}
                  </div>
                </a-form-item>
              </div>
            </a-form>
          </div>
          
          <div v-else class="empty-config">
            <a-empty description="该分类暂无配置项" />
          </div>
        </a-spin>
      </div>
    </div>

    <!-- 创建备份模态框 -->
    <a-modal
      v-model:open="showBackupModal"
      title="创建配置备份"
      :width="600"
      @ok="handleCreateBackup"
      @cancel="showBackupModal = false"
    >
      <ConfigBackupForm
        ref="backupFormRef"
        @submit="handleCreateBackup"
      />
    </a-modal>

    <!-- 恢复备份模态框 -->
    <a-modal
      v-model:open="showRestoreModal"
      title="恢复配置备份"
      :width="800"
      :footer="null"
    >
      <ConfigRestoreForm
        @submit="handleRestoreBackup"
        @cancel="showRestoreModal = false"
      />
    </a-modal>

    <!-- 导入配置模态框 -->
    <a-modal
      v-model:open="showImportModal"
      title="导入配置"
      :width="600"
      @ok="handleImport"
      @cancel="showImportModal = false"
    >
      <ConfigImportForm
        ref="importFormRef"
        @submit="handleImport"
      />
    </a-modal>

    <!-- 系统信息模态框 -->
    <a-modal
      v-model:open="showSystemInfoModal"
      title="系统信息"
      :width="900"
      :footer="null"
    >
      <SystemInfo />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  SaveOutlined,
  ExportOutlined,
  ImportOutlined,
  ReloadOutlined,
  RedoOutlined,
  ExperimentOutlined,
  InfoCircleOutlined,
  DownOutlined,
  SettingOutlined,
  DatabaseOutlined,
  WifiOutlined,
  MailOutlined,
  SafetyOutlined,
  FileTextOutlined,
  LayoutOutlined,
  DashboardOutlined,
  ApiOutlined
} from '@ant-design/icons-vue';
import ConfigBackupForm from '@/components/config/ConfigBackupForm.vue';
import ConfigRestoreForm from '@/components/config/ConfigRestoreForm.vue';
import ConfigImportForm from '@/components/config/ConfigImportForm.vue';
import SystemInfo from '@/components/config/SystemInfo.vue';
import { 
  useConfigManagement, 
  useConfigBackup, 
  useConfigImportExport 
} from '@/composables/useConfigManagement';
import type { ConfigCategory } from '@/types/config';

// 组合式函数
const {
  configGroups,
  loading,
  saving,
  testing,
  activeCategory,
  hasModifications,
  currentCategoryConfigs,
  modificationCount,
  fetchConfigGroups,
  updateConfigValue,
  saveConfigs,
  resetConfigs,
  testConfig,
  switchCategory,
  cancelModifications,
  getConfigValue,
  isConfigModified
} = useConfigManagement();

const { exportConfigs } = useConfigImportExport();

// 响应式状态
const showBackupModal = ref(false);
const showRestoreModal = ref(false);
const showImportModal = ref(false);
const showSystemInfoModal = ref(false);
const backupFormRef = ref();
const importFormRef = ref();

// 选中的菜单项
const selectedKeys = ref<string[]>([]);

// 表单数据（用于表单验证）
const formData = ref({});

// 计算属性
const currentGroupTitle = computed(() => {
  const group = configGroups.value.find(g => g.category === activeCategory.value);
  return group ? group.title : '';
});

const currentGroupDescription = computed(() => {
  const group = configGroups.value.find(g => g.category === activeCategory.value);
  return group ? group.description : '';
});

const canTestConfig = computed(() => {
  // 只有数据库、邮件、RADIUS等配置支持测试连接
  const testableCategories = ['database', 'email', 'radius'];
  return testableCategories.includes(activeCategory.value);
});

// 事件处理
const handleCategorySelect = ({ key }: { key: string }) => {
  switchCategory(key as ConfigCategory);
};

const handleSave = async () => {
  try {
    await saveConfigs();
  } catch (error) {
    console.error(error);
  }
};

const handleCancel = () => {
  Modal.confirm({
    title: '确认取消修改',
    content: '确定要取消所有未保存的修改吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: cancelModifications
  });
};

const handleTestConfig = async () => {
  try {
    await testConfig(activeCategory.value);
  } catch (error) {
    console.error(error);
  }
};

const handleResetCategory = () => {
  const categoryConfigs = currentCategoryConfigs.value;
  const configKeys = categoryConfigs.map(c => c.key);
  
  Modal.confirm({
    title: '确认重置配置',
    content: `确定要将当前分类的所有配置重置为默认值吗？这将影响 ${configKeys.length} 项配置。`,
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => resetConfigs(configKeys)
  });
};

const handleCreateBackup = async () => {
  if (backupFormRef.value) {
    await backupFormRef.value.submit();
    showBackupModal.value = false;
  }
};

const handleRestoreBackup = () => {
  showRestoreModal.value = false;
  // 恢复后刷新配置
  fetchConfigGroups();
};

const handleExport = () => {
  exportConfigs();
};

const handleImport = async () => {
  if (importFormRef.value) {
    await importFormRef.value.submit();
    showImportModal.value = false;
    // 导入后刷新配置
    fetchConfigGroups();
  }
};

// 工具函数
const getIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    setting: SettingOutlined,
    database: DatabaseOutlined,
    wifi: WifiOutlined,
    mail: MailOutlined,
    safety: SafetyOutlined,
    save: SaveOutlined,
    'file-text': FileTextOutlined,
    layout: LayoutOutlined,
    dashboard: DashboardOutlined,
    api: ApiOutlined
  };
  return iconMap[iconName] || SettingOutlined;
};

// 监听分类变化
watch(activeCategory, (newCategory) => {
  selectedKeys.value = [newCategory];
}, { immediate: true });

// 生命周期
onMounted(() => {
  fetchConfigGroups();
});
</script>

<style scoped>
.config-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.page-description {
  margin: 8px 0 0 0;
  color: rgba(0, 0, 0, 0.65);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.modification-alert {
  margin-top: 16px;
}

.config-content {
  display: flex;
  gap: 24px;
  min-height: 600px;
}

.config-sidebar {
  width: 240px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.config-main {
  flex: 1;
  background: #fff;
  border-radius: 6px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.config-form-container {
  max-width: 800px;
}

.category-header {
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.category-header h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 500;
}

.category-description {
  margin: 0 0 16px 0;
  color: rgba(0, 0, 0, 0.65);
}

.category-actions {
  display: flex;
  gap: 12px;
}

.config-form {
  margin-top: 24px;
}

.config-item {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 6px;
  transition: all 0.3s;
}

.config-item:hover {
  background: #fafafa;
}

.config-modified {
  background: #fff7e6;
  border: 1px solid #ffd591;
}

.config-help {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.4;
}

.empty-config {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

:deep(.ant-menu-inline) {
  border-right: none;
}

:deep(.ant-form-item-label > label) {
  font-weight: 500;
}

:deep(.ant-input-number) {
  width: 100%;
}
</style>