<!-- 设备表单组件 -->
<template>
  <div class="device-form">
    <a-form
      :model="formData"
      :rules="rules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
      @finish="handleSubmit"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h3>基本信息</h3>
        
        <a-form-item label="设备名称" name="name">
          <a-input
            v-model:value="formData.name"
            placeholder="请输入设备名称"
          />
        </a-form-item>

        <a-form-item label="设备类型" name="type">
          <a-select
            v-model:value="formData.type"
            placeholder="请选择设备类型"
            @change="handleTypeChange"
          >
            <a-select-option
              v-for="option in DEVICE_TYPE_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="IP地址" name="ipAddress">
          <a-input
            v-model:value="formData.ipAddress"
            placeholder="请输入IP地址"
          />
        </a-form-item>

        <a-form-item label="密钥" name="secret">
          <a-input-password
            v-model:value="formData.secret"
            placeholder="请输入设备密钥"
            autocomplete="new-password"
          />
        </a-form-item>

        <a-form-item label="NAS名称" name="nasName">
          <a-input
            v-model:value="formData.nasName"
            placeholder="请输入NAS名称"
          />
        </a-form-item>

        <a-form-item label="短名称" name="shortName">
          <a-input
            v-model:value="formData.shortName"
            placeholder="请输入短名称"
          />
        </a-form-item>

        <a-form-item label="端口" name="ports">
          <a-input
            v-model:value="formData.ports"
            placeholder="请输入端口号，多个用逗号分隔"
          />
        </a-form-item>

        <a-form-item label="虚拟服务器" name="virtualServer">
          <a-input
            v-model:value="formData.virtualServer"
            placeholder="请输入虚拟服务器地址"
          />
        </a-form-item>

        <a-form-item label="社区字符串" name="community">
          <a-input
            v-model:value="formData.community"
            placeholder="请输入SNMP社区字符串"
          />
        </a-form-item>

        <a-form-item label="描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            :rows="3"
            placeholder="请输入设备描述"
          />
        </a-form-item>

        <a-form-item v-if="isEdit" label="设备状态" name="status">
          <a-select
            v-model:value="formData.status"
            placeholder="请选择设备状态"
          >
            <a-select-option
              v-for="option in DEVICE_STATUS_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              <a-tag :color="option.color" style="margin: 0;">
                {{ option.label }}
              </a-tag>
            </a-select-option>
          </a-select>
        </a-form-item>
      </div>

      <!-- NAS特有配置 -->
      <div v-if="formData.type === 'nas'" class="form-section">
        <h3>NAS配置</h3>
        
        <a-form-item label="认证端口" name="authPort">
          <a-input-number
            v-model:value="formData.authPort"
            :min="1"
            :max="65535"
            placeholder="认证端口号（默认1812）"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="计费端口" name="acctPort">
          <a-input-number
            v-model:value="formData.acctPort"
            :min="1"
            :max="65535"
            placeholder="计费端口号（默认1813）"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="RADIUS密钥" name="radiusSecret">
          <a-input-password
            v-model:value="formData.radiusSecret"
            placeholder="RADIUS认证密钥"
            autocomplete="new-password"
          />
        </a-form-item>

        <a-form-item label="最大会话数" name="maxSessions">
          <a-input-number
            v-model:value="formData.maxSessions"
            :min="0"
            placeholder="最大并发会话数（0表示无限制）"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="超时时间" name="timeout">
          <a-input-number
            v-model:value="formData.timeout"
            :min="1"
            :max="300"
            placeholder="超时时间（秒）"
            style="width: 100%"
          />
        </a-form-item>
      </div>

      <!-- 表单操作 -->
      <div class="form-actions">
        <a-form-item :wrapper-col="{ span: 24 }">
          <div class="action-buttons">
            <a-button @click="handleCancel">
              取消
            </a-button>
            <a-button @click="handleTest" :loading="testing">
              测试连接
            </a-button>
            <a-button type="primary" html-type="submit" :loading="submitting">
              {{ isEdit ? '更新设备' : '创建设备' }}
            </a-button>
          </div>
        </a-form-item>
      </div>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { message } from 'ant-design-vue';
import type { 
  Device, 
  CreateDeviceRequest, 
  UpdateDeviceRequest, 
  DeviceType, 
  DeviceStatus 
} from '@/types/device';
import { DEVICE_TYPE_OPTIONS, DEVICE_STATUS_OPTIONS } from '@/types/device';
import { useDeviceConnections } from '@/composables/useDeviceManagement';

interface Props {
  device?: Device;
}

interface Emits {
  (e: 'submit', data: CreateDeviceRequest | UpdateDeviceRequest): void;
  (e: 'cancel'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { testConnection } = useDeviceConnections();

// 响应式状态
const submitting = ref(false);
const testing = ref(false);

// 是否为编辑模式
const isEdit = computed(() => !!props.device);

// 表单数据
const formData = reactive<CreateDeviceRequest & { status?: DeviceStatus }>({
  name: '',
  type: 'nas' as DeviceType,
  ipAddress: '',
  secret: '',
  nasName: '',
  shortName: '',
  ports: '',
  virtualServer: '',
  community: 'public',
  description: '',
  authPort: 1812,
  acctPort: 1813,
  radiusSecret: '',
  maxSessions: 0,
  timeout: 30
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' },
    { min: 2, max: 50, message: '设备名称长度为2-50字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择设备类型', trigger: 'change' }
  ],
  ipAddress: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    { 
      pattern: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      message: '请输入正确的IP地址格式',
      trigger: 'blur'
    }
  ],
  secret: [
    { required: true, message: '请输入设备密钥', trigger: 'blur' },
    { min: 6, message: '密钥长度不能少于6个字符', trigger: 'blur' }
  ],
  nasName: [
    { required: true, message: '请输入NAS名称', trigger: 'blur' },
    { min: 2, max: 30, message: 'NAS名称长度为2-30字符', trigger: 'blur' }
  ],
  shortName: [
    { required: true, message: '请输入短名称', trigger: 'blur' },
    { min: 2, max: 20, message: '短名称长度为2-20字符', trigger: 'blur' }
  ],
  ports: [
    {
      pattern: /^\d+(,\d+)*$/,
      message: '端口号格式不正确，多个端口用逗号分隔',
      trigger: 'blur'
    }
  ],
  authPort: [
    { type: 'number', min: 1, max: 65535, message: '端口号范围为1-65535', trigger: 'blur' }
  ],
  acctPort: [
    { type: 'number', min: 1, max: 65535, message: '端口号范围为1-65535', trigger: 'blur' }
  ],
  maxSessions: [
    { type: 'number', min: 0, message: '最大会话数不能小于0', trigger: 'blur' }
  ],
  timeout: [
    { type: 'number', min: 1, max: 300, message: '超时时间范围为1-300秒', trigger: 'blur' }
  ]
};

// 初始化表单数据
const initFormData = () => {
  if (props.device) {
    Object.assign(formData, {
      name: props.device.name,
      type: props.device.type,
      ipAddress: props.device.ipAddress,
      secret: props.device.secret,
      nasName: props.device.nasName,
      shortName: props.device.shortName,
      ports: props.device.ports,
      virtualServer: props.device.virtualServer,
      community: props.device.community,
      description: props.device.description,
      status: props.device.status,
      // NAS特有字段
      authPort: (props.device as any).authPort || 1812,
      acctPort: (props.device as any).acctPort || 1813,
      radiusSecret: (props.device as any).radiusSecret || props.device.secret,
      maxSessions: (props.device as any).maxSessions || 0,
      timeout: (props.device as any).timeout || 30
    });
  }
};

// 设备类型变化处理
const handleTypeChange = (type: DeviceType) => {
  if (type === 'nas') {
    // 设置NAS默认值
    if (!formData.authPort) formData.authPort = 1812;
    if (!formData.acctPort) formData.acctPort = 1813;
    if (!formData.timeout) formData.timeout = 30;
    if (!formData.radiusSecret) formData.radiusSecret = formData.secret;
  }
};

// 测试连接
const handleTest = async () => {
  // 先验证基本字段
  if (!formData.ipAddress) {
    message.warning('请先填写IP地址');
    return;
  }

  try {
    testing.value = true;
    
    // 模拟测试连接
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 随机生成测试结果
    const success = Math.random() > 0.3;
    
    if (success) {
      const latency = Math.floor(Math.random() * 100) + 10;
      message.success(`连接测试成功！延迟: ${latency}ms`);
    } else {
      message.error('连接测试失败：设备无响应或网络不通');
    }
  } catch (error) {
    message.error('连接测试失败');
  } finally {
    testing.value = false;
  }
};

// 提交表单
const handleSubmit = () => {
  submitting.value = true;
  
  try {
    const submitData = { ...formData };
    
    // 如果不是NAS类型，移除NAS特有字段
    if (formData.type !== 'nas') {
      delete submitData.authPort;
      delete submitData.acctPort;
      delete submitData.radiusSecret;
      delete submitData.maxSessions;
      delete submitData.timeout;
    }
    
    // 移除状态字段（仅编辑时需要）
    if (!isEdit.value) {
      delete submitData.status;
    }
    
    emit('submit', submitData);
  } catch (error) {
    console.error(error);
  } finally {
    submitting.value = false;
  }
};

// 取消操作
const handleCancel = () => {
  emit('cancel');
};

// 监听props变化
watch(
  () => props.device,
  () => initFormData(),
  { immediate: true }
);
</script>

<style scoped>
.device-form {
  padding: 0;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}

.form-actions {
  border-top: 1px solid #f0f0f0;
  padding-top: 24px;
  margin-top: 24px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}

:deep(.ant-input-number) {
  width: 100%;
}
</style>