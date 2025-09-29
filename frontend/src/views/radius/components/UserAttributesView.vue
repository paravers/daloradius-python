<template>
  <div class="user-attributes-view">
    <div v-if="!userAttributes" class="empty-state">
      <a-empty
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
        description="请选择一个用户查看其RADIUS属性"
      >
        <a-button type="primary" @click="$emit('select-user')">
          选择用户
        </a-button>
      </a-empty>
    </div>

    <div v-else class="user-content">
      <!-- User Info Header -->
      <div class="user-header">
        <div class="user-info">
          <h3>
            <UserOutlined />
            {{ userAttributes.username }}
          </h3>
          <p class="user-summary">
            总共 {{ userAttributes.total_attributes }} 个属性
            ({{ userAttributes.check_attributes.length }} 个认证属性，
            {{ userAttributes.reply_attributes.length }} 个授权属性)
          </p>
        </div>
        
        <div class="user-actions">
          <a-button
            type="primary"
            ghost
            :icon="h(KeyOutlined)"
            @click="showPasswordModal"
          >
            设置密码
          </a-button>
          <a-button
            :icon="h(ReloadOutlined)"
            @click="$emit('refresh')"
            :loading="loading"
          >
            刷新
          </a-button>
        </div>
      </div>

      <!-- Attributes Cards -->
      <a-row :gutter="[24, 24]">
        <!-- RadCheck Attributes -->
        <a-col :xs="24" :lg="12">
          <a-card
            title="认证属性 (RadCheck)"
            :bordered="false"
            class="attributes-card"
          >
            <template #extra>
              <a-badge
                :count="userAttributes.check_attributes.length"
                :number-style="{ backgroundColor: '#1890ff' }"
              />
            </template>
            
            <div v-if="userAttributes.check_attributes.length === 0" class="empty-attributes">
              <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE" description="暂无认证属性" />
            </div>
            
            <div v-else class="attributes-list">
              <div
                v-for="attr in userAttributes.check_attributes"
                :key="attr.id"
                class="attribute-item"
              >
                <div class="attribute-header">
                  <a-tag :color="getAttributeColor(attr.attribute)">
                    {{ attr.attribute }}
                  </a-tag>
                  <a-tag color="blue" size="small">{{ attr.op }}</a-tag>
                </div>
                <div class="attribute-value">
                  <a-typography-text
                    :copyable="!isPasswordAttribute(attr.attribute)"
                    :ellipsis="{ tooltip: true }"
                  >
                    {{ isPasswordAttribute(attr.attribute) ? '••••••••' : attr.value }}
                  </a-typography-text>
                </div>
                <div class="attribute-meta">
                  <Time :value="attr.created_at" format="YYYY-MM-DD HH:mm" />
                </div>
              </div>
            </div>
          </a-card>
        </a-col>

        <!-- RadReply Attributes -->
        <a-col :xs="24" :lg="12">
          <a-card
            title="授权属性 (RadReply)"
            :bordered="false"
            class="attributes-card"
          >
            <template #extra>
              <a-badge
                :count="userAttributes.reply_attributes.length"
                :number-style="{ backgroundColor: '#52c41a' }"
              />
            </template>
            
            <div v-if="userAttributes.reply_attributes.length === 0" class="empty-attributes">
              <a-empty :image="Empty.PRESENTED_IMAGE_SIMPLE" description="暂无授权属性" />
            </div>
            
            <div v-else class="attributes-list">
              <div
                v-for="attr in userAttributes.reply_attributes"
                :key="attr.id"
                class="attribute-item"
              >
                <div class="attribute-header">
                  <a-tag :color="getAttributeColor(attr.attribute)">
                    {{ attr.attribute }}
                  </a-tag>
                  <a-tag color="green" size="small">{{ attr.op }}</a-tag>
                </div>
                <div class="attribute-value">
                  <a-typography-text
                    copyable
                    :ellipsis="{ tooltip: true }"
                  >
                    {{ formatAttributeValue(attr.attribute, attr.value) }}
                  </a-typography-text>
                </div>
                <div class="attribute-meta">
                  <Time :value="attr.created_at" format="YYYY-MM-DD HH:mm" />
                </div>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>

      <!-- Password Modal -->
      <a-modal
        v-model:visible="passwordModalVisible"
        title="设置用户密码"
        @ok="handlePasswordSubmit"
        @cancel="handlePasswordCancel"
      >
        <a-form
          :model="passwordForm"
          :rules="passwordRules"
          layout="vertical"
        >
          <a-form-item label="密码" name="password">
            <a-input-password
              v-model:value="passwordForm.password"
              placeholder="请输入新密码"
              autocomplete="new-password"
            />
          </a-form-item>
          
          <a-form-item label="密码类型" name="passwordType">
            <a-select v-model:value="passwordForm.passwordType">
              <a-select-option value="Cleartext-Password">明文密码</a-select-option>
              <a-select-option value="Crypt-Password">Crypt 加密</a-select-option>
              <a-select-option value="MD5-Password">MD5 加密</a-select-option>
              <a-select-option value="SHA-Password">SHA 加密</a-select-option>
              <a-select-option value="NT-Password">NT 加密</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h } from 'vue';
import { message, Empty } from 'ant-design-vue';
import {
  UserOutlined,
  KeyOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue';
import Time from '@/components/common/Time.vue';
import type { UserAttributes } from '@/types/radius';

// ===== Props & Emits =====
interface Props {
  userAttributes: UserAttributes | null;
  loading?: boolean;
}

interface Emits {
  (e: 'set-password', data: { username: string; password: string; passwordType?: string }): void;
  (e: 'refresh'): void;
  (e: 'select-user'): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

// ===== Local State =====
const passwordModalVisible = ref(false);
const passwordForm = reactive({
  password: '',
  passwordType: 'Cleartext-Password'
});

const passwordRules = {
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码长度至少6位' }
  ]
};

// ===== Methods =====

/**
 * Show password setting modal
 */
const showPasswordModal = () => {
  passwordForm.password = '';
  passwordForm.passwordType = 'Cleartext-Password';
  passwordModalVisible.value = true;
};

/**
 * Handle password form submission
 */
const handlePasswordSubmit = () => {
  if (!passwordForm.password) {
    message.error('请输入密码');
    return;
  }
  
  if (passwordForm.password.length < 6) {
    message.error('密码长度至少6位');
    return;
  }
  
  emit('set-password', {
    username: props.userAttributes!.username,
    password: passwordForm.password,
    passwordType: passwordForm.passwordType
  });
  
  passwordModalVisible.value = false;
};

/**
 * Handle password modal cancel
 */
const handlePasswordCancel = () => {
  passwordModalVisible.value = false;
};

/**
 * Get color for different attribute types
 */
const getAttributeColor = (attribute: string): string => {
  if (attribute.includes('Password')) return 'red';
  if (attribute.includes('Timeout')) return 'orange';
  if (attribute.includes('IP')) return 'blue';
  if (attribute.includes('Auth')) return 'purple';
  if (attribute.includes('Service')) return 'cyan';
  if (attribute.includes('Bandwidth')) return 'magenta';
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
 * Format attribute value for display
 */
const formatAttributeValue = (attribute: string, value: string): string => {
  // Format timeout values
  if (attribute.includes('Timeout')) {
    const seconds = parseInt(value);
    if (!isNaN(seconds)) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const remainingSeconds = seconds % 60;
      
      if (hours > 0) {
        return `${hours}h ${minutes}m ${remainingSeconds}s`;
      } else if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`;
      } else {
        return `${remainingSeconds}s`;
      }
    }
  }
  
  // Format bandwidth values
  if (attribute.includes('Bandwidth') || attribute.includes('Speed')) {
    const bytes = parseInt(value);
    if (!isNaN(bytes)) {
      if (bytes >= 1000000) {
        return `${(bytes / 1000000).toFixed(2)} Mbps`;
      } else if (bytes >= 1000) {
        return `${(bytes / 1000).toFixed(2)} Kbps`;
      }
    }
  }
  
  return value;
};
</script>

<style scoped lang="less">
.user-attributes-view {
  .empty-state {
    padding: 60px 0;
    text-align: center;
  }
  
  .user-content {
    .user-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 24px 0;
      border-bottom: 1px solid #f0f0f0;
      margin-bottom: 24px;
      
      .user-info {
        h3 {
          margin: 0 0 8px 0;
          font-size: 20px;
          font-weight: 600;
          color: #262626;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .user-summary {
          margin: 0;
          color: #8c8c8c;
          font-size: 14px;
        }
      }
      
      .user-actions {
        display: flex;
        gap: 8px;
      }
    }
    
    .attributes-card {
      height: 100%;
      
      :deep(.ant-card-body) {
        padding: 16px;
      }
    }
    
    .empty-attributes {
      padding: 20px 0;
      text-align: center;
    }
    
    .attributes-list {
      .attribute-item {
        padding: 12px;
        border: 1px solid #f0f0f0;
        border-radius: 6px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: #d9d9d9;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .attribute-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .attribute-value {
          margin-bottom: 4px;
          
          .ant-typography {
            margin-bottom: 0;
          }
        }
        
        .attribute-meta {
          font-size: 12px;
          color: #8c8c8c;
        }
      }
    }
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .user-attributes-view {
    .user-content {
      .user-header {
        flex-direction: column;
        gap: 16px;
        
        .user-actions {
          width: 100%;
          justify-content: flex-start;
        }
      }
    }
  }
}
</style>