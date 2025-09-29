<template>
  <a-modal
    :visible="visible"
    :title="modalTitle"
    :width="600"
    @ok="handleSubmit"
    @cancel="handleCancel"
    :confirm-loading="submitting"
    destroy-on-close
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
    >
      <a-form-item label="属性类型" name="type">
        <a-radio-group
          v-model:value="formData.type"
          :disabled="mode === 'edit'"
          @change="handleTypeChange"
        >
          <a-radio value="check">RadCheck (认证)</a-radio>
          <a-radio value="reply">RadReply (授权)</a-radio>
        </a-radio-group>
      </a-form-item>

      <a-form-item label="用户名" name="username">
        <a-auto-complete
          v-model:value="formData.username"
          :options="userOptions"
          placeholder="请输入或选择用户名"
          allow-clear
          :filter-option="filterOption"
        />
      </a-form-item>

      <a-form-item label="属性名" name="attribute">
        <a-auto-complete
          v-model:value="formData.attribute"
          :options="attributeOptions"
          placeholder="请输入或选择属性名"
          allow-clear
          :filter-option="filterOption"
          @change="handleAttributeChange"
        >
          <template #option="{ value, label }">
            <div class="attribute-option">
              <div class="attribute-name">{{ label }}</div>
              <div class="attribute-description">{{ getAttributeDescription(value) }}</div>
            </div>
          </template>
        </a-auto-complete>
      </a-form-item>

      <a-form-item label="操作符" name="op">
        <a-select
          v-model:value="formData.op"
          placeholder="请选择操作符"
        >
          <a-select-option
            v-for="operator in radiusOperators"
            :key="operator"
            :value="operator"
          >
            <div class="operator-option">
              <span class="operator-symbol">{{ operator }}</span>
              <span class="operator-description">{{ getOperatorDescription(operator) }}</span>
            </div>
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="属性值" name="value">
        <component
          :is="getValueComponent()"
          v-model:value="formData.value"
          v-bind="getValueProps()"
        />
        
        <!-- Value hints -->
        <div v-if="valueHint" class="value-hint">
          <InfoCircleOutlined />
          {{ valueHint }}
        </div>
      </a-form-item>

      <!-- Quick Templates -->
      <a-form-item v-if="quickTemplates.length > 0" label="快速模板">
        <a-space wrap>
          <a-button
            v-for="template in quickTemplates"
            :key="template.name"
            size="small"
            type="dashed"
            @click="applyTemplate(template)"
          >
            {{ template.name }}
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import { InfoCircleOutlined } from '@ant-design/icons-vue';
import type { FormInstance, Rule } from 'ant-design-vue/es/form';
import type {
  RadCheck,
  RadReply,
  RadCheckCreate,
  RadReplyCreate,
  RadiusOperator,
  CommonCheckAttributes,
  CommonReplyAttributes
} from '@/types/radius';

// ===== Props & Emits =====
interface Props {
  visible: boolean;
  mode: 'create' | 'edit';
  attributeType: 'check' | 'reply';
  initialData?: RadCheck | RadReply | null;
  commonCheckAttributes?: CommonCheckAttributes | null;
  commonReplyAttributes?: CommonReplyAttributes | null;
  radiusOperators: RadiusOperator[];
}

interface Emits {
  (e: 'update:visible', visible: boolean): void;
  (e: 'submit', data: RadCheckCreate | RadReplyCreate): void;
  (e: 'cancel'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// ===== Local State =====
const formRef = ref<FormInstance>();
const submitting = ref(false);

const formData = reactive({
  type: 'check' as 'check' | 'reply',
  username: '',
  attribute: '',
  op: '==' as RadiusOperator,
  value: ''
});

// ===== Computed Properties =====
const modalTitle = computed(() => {
  const typeText = formData.type === 'check' ? 'RadCheck' : 'RadReply';
  return `${props.mode === 'create' ? '新建' : '编辑'} ${typeText} 属性`;
});

const userOptions = computed(() => {
  // TODO: Get users from a user service or prop
  return [];
});

const attributeOptions = computed(() => {
  const attributes = new Set<string>();
  
  if (formData.type === 'check' && props.commonCheckAttributes) {
    Object.values(props.commonCheckAttributes).flat().forEach(attr => attributes.add(attr));
  } else if (formData.type === 'reply' && props.commonReplyAttributes) {
    Object.values(props.commonReplyAttributes).flat().forEach(attr => attributes.add(attr));
  }
  
  return Array.from(attributes).map(attr => ({
    value: attr,
    label: attr
  }));
});

const quickTemplates = computed(() => {
  const templates: Array<{ name: string; data: Partial<typeof formData> }> = [];
  
  if (formData.type === 'check') {
    templates.push(
      { name: '明文密码', data: { attribute: 'Cleartext-Password', op: ':=', value: '' } },
      { name: '同时在线限制', data: { attribute: 'Simultaneous-Use', op: ':=', value: '1' } },
      { name: 'PAP认证', data: { attribute: 'Auth-Type', op: ':=', value: 'PAP' } }
    );
  } else {
    templates.push(
      { name: '会话超时1小时', data: { attribute: 'Session-Timeout', op: ':=', value: '3600' } },
      { name: '空闲超时15分钟', data: { attribute: 'Idle-Timeout', op: ':=', value: '900' } },
      { name: '固定IP地址', data: { attribute: 'Framed-IP-Address', op: ':=', value: '192.168.1.100' } }
    );
  }
  
  return templates;
});

const valueHint = computed(() => {
  const attribute = formData.attribute;
  
  if (!attribute) return '';
  
  const hints: Record<string, string> = {
    'Session-Timeout': '会话超时时间，单位：秒 (例如：3600 = 1小时)',
    'Idle-Timeout': '空闲超时时间，单位：秒 (例如：900 = 15分钟)',
    'Simultaneous-Use': '同时在线数量限制 (例如：1)',
    'Framed-IP-Address': 'IP地址 (例如：192.168.1.100)',
    'Framed-IP-Netmask': '子网掩码 (例如：255.255.255.0)',
    'WISPr-Bandwidth-Max-Down': '下行带宽限制，单位：bps (例如：1000000 = 1Mbps)',
    'WISPr-Bandwidth-Max-Up': '上行带宽限制，单位：bps (例如：512000 = 512Kbps)'
  };
  
  return hints[attribute] || '';
});

// ===== Form Rules =====
const formRules: Record<string, Rule[]> = {
  username: [
    { required: true, message: '请输入用户名' },
    { pattern: /^[a-zA-Z0-9\-_@.]+$/, message: '用户名格式不正确' },
    { max: 64, message: '用户名长度不能超过64个字符' }
  ],
  attribute: [
    { required: true, message: '请输入属性名' },
    { max: 64, message: '属性名长度不能超过64个字符' }
  ],
  op: [
    { required: true, message: '请选择操作符' }
  ],
  value: [
    { required: true, message: '请输入属性值' },
    { max: 253, message: '属性值长度不能超过253个字符' }
  ]
};

// ===== Methods =====

/**
 * Initialize form data
 */
const initializeForm = () => {
  if (props.mode === 'edit' && props.initialData) {
    const data = props.initialData;
    formData.type = props.attributeType;
    formData.username = data.username;
    formData.attribute = data.attribute;
    formData.op = data.op;
    formData.value = data.value;
  } else {
    formData.type = props.attributeType;
    formData.username = '';
    formData.attribute = '';
    formData.op = '==';
    formData.value = '';
  }
};

/**
 * Handle type change
 */
const handleTypeChange = () => {
  formData.attribute = '';
  formData.value = '';
};

/**
 * Handle attribute change
 */
const handleAttributeChange = (value: string) => {
  // Auto-set operator based on attribute type
  if (value.includes('Password') || value.includes('Auth-Type')) {
    formData.op = ':=';
  } else if (value.includes('Timeout') || value.includes('Use')) {
    formData.op = ':=';
  } else {
    formData.op = '==';
  }
};

/**
 * Get appropriate input component for value field
 */
const getValueComponent = () => {
  const attribute = formData.attribute;
  
  if (attribute.includes('Password')) {
    return 'a-input-password';
  } else if (attribute.includes('Timeout') || attribute.includes('Use') || attribute.includes('Bandwidth')) {
    return 'a-input-number';
  } else if (attribute.includes('IP')) {
    return 'a-input';
  } else {
    return 'a-input';
  }
};

/**
 * Get props for value input component
 */
const getValueProps = () => {
  const attribute = formData.attribute;
  
  if (attribute.includes('Timeout') || attribute.includes('Use')) {
    return {
      min: 0,
      placeholder: '请输入数值'
    };
  } else if (attribute.includes('Bandwidth')) {
    return {
      min: 0,
      placeholder: '请输入带宽值(bps)'
    };
  } else if (attribute.includes('IP')) {
    return {
      placeholder: '例如：192.168.1.100'
    };
  } else {
    return {
      placeholder: '请输入属性值'
    };
  }
};

/**
 * Get attribute description
 */
const getAttributeDescription = (attribute: string): string => {
  const descriptions: Record<string, string> = {
    'User-Password': '用户密码',
    'Cleartext-Password': '明文密码',
    'Session-Timeout': '会话超时',
    'Idle-Timeout': '空闲超时',
    'Framed-IP-Address': '分配IP地址',
    'Auth-Type': '认证类型',
    'Simultaneous-Use': '同时在线限制'
  };
  
  return descriptions[attribute] || '';
};

/**
 * Get operator description
 */
const getOperatorDescription = (operator: string): string => {
  const descriptions: Record<string, string> = {
    '==': '等于',
    '!=': '不等于',
    ':=': '设置为',
    '+=': '添加到',
    '<': '小于',
    '<=': '小于等于',
    '>': '大于',
    '>=': '大于等于',
    '=~': '正则匹配',
    '!~': '正则不匹配'
  };
  
  return descriptions[operator] || '';
};

/**
 * Apply quick template
 */
const applyTemplate = (template: { name: string; data: Partial<typeof formData> }) => {
  Object.assign(formData, template.data);
};

/**
 * Filter option for auto-complete
 */
const filterOption = (inputValue: string, option: any) => {
  return option.value.toLowerCase().includes(inputValue.toLowerCase());
};

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
    
    submitting.value = true;
    
    const submitData = {
      username: formData.username,
      attribute: formData.attribute,
      op: formData.op,
      value: formData.value
    };
    
    emit('submit', submitData);
  } catch (err) {
    console.error('Form validation failed:', err);
  } finally {
    submitting.value = false;
  }
};

/**
 * Handle cancel
 */
const handleCancel = () => {
  emit('cancel');
};

// ===== Watchers =====
watch(() => props.visible, (visible) => {
  if (visible) {
    nextTick(() => {
      initializeForm();
    });
  }
});

watch(() => props.attributeType, (type) => {
  formData.type = type;
});
</script>

<style scoped lang="less">
.attribute-option {
  .attribute-name {
    font-weight: 500;
  }
  
  .attribute-description {
    font-size: 12px;
    color: #8c8c8c;
  }
}

.operator-option {
  display: flex;
  justify-content: space-between;
  
  .operator-symbol {
    font-family: monospace;
    font-weight: 600;
  }
  
  .operator-description {
    color: #8c8c8c;
    font-size: 12px;
  }
}

.value-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #1890ff;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>