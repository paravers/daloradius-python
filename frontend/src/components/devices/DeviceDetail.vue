<!-- 设备详情组件 -->
<template>
  <div class="device-detail">
    <!-- 基本信息 -->
    <div class="detail-section">
      <h3>基本信息</h3>
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="设备名称">
          {{ device.name }}
        </a-descriptions-item>
        <a-descriptions-item label="设备类型">
          <a-tag color="blue">{{ getTypeText(device.type) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="IP地址">
          {{ device.ipAddress }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(device.status)">
            {{ getStatusText(device.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="NAS名称">
          {{ device.nasName }}
        </a-descriptions-item>
        <a-descriptions-item label="短名称">
          {{ device.shortName }}
        </a-descriptions-item>
        <a-descriptions-item label="端口">
          {{ device.ports || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="社区字符串">
          {{ device.community || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">
          {{ device.description || '-' }}
        </a-descriptions-item>
      </a-descriptions>
    </div>

    <!-- NAS特有信息 -->
    <div v-if="device.type === 'nas'" class="detail-section">
      <h3>NAS配置</h3>
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="认证端口">
          {{ (device as NasDevice).authPort || 1812 }}
        </a-descriptions-item>
        <a-descriptions-item label="计费端口">
          {{ (device as NasDevice).acctPort || 1813 }}
        </a-descriptions-item>
        <a-descriptions-item label="RADIUS密钥">
          <a-input-password 
            :value="(device as NasDevice).radiusSecret || device.secret" 
            :bordered="false"
            readonly
          />
        </a-descriptions-item>
        <a-descriptions-item label="最大会话数">
          {{ (device as NasDevice).maxSessions || '无限制' }}
        </a-descriptions-item>
        <a-descriptions-item label="超时时间">
          {{ (device as NasDevice).timeout || 30 }}秒
        </a-descriptions-item>
      </a-descriptions>
    </div>

    <!-- 时间信息 -->
    <div class="detail-section">
      <h3>时间信息</h3>
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="创建时间">
          {{ device.createTime }}
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          {{ device.updateTime }}
        </a-descriptions-item>
      </a-descriptions>
    </div>

    <!-- 连接测试 -->
    <div class="detail-section">
      <h3>连接测试</h3>
      <div class="connection-test">
        <a-button 
          type="primary" 
          @click="testConnection"
          :loading="testing"
        >
          <template #icon><WifiOutlined /></template>
          测试连接
        </a-button>
        
        <div v-if="testResult" class="test-result">
          <a-alert
            :type="testResult.success ? 'success' : 'error'"
            :message="testResult.success ? '连接成功' : '连接失败'"
            :description="getTestDescription()"
            show-icon
            closable
            @close="testResult = null"
          />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="detail-actions">
      <a-button type="primary" @click="$emit('edit', device)">
        <template #icon><EditOutlined /></template>
        编辑设备
      </a-button>
      <a-button @click="handleReboot" :loading="rebooting">
        <template #icon><ReloadOutlined /></template>
        重启设备
      </a-button>
      <a-button danger @click="handleDelete">
        <template #icon><DeleteOutlined /></template>
        删除设备
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  WifiOutlined,
  EditOutlined,
  ReloadOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';
import type { Device, NasDevice, DeviceTestResult, DeviceType, DeviceStatus } from '@/types/device';
import { useDeviceConnections } from '@/composables/useDeviceManagement';
import { deviceService } from '@/services/deviceService';

interface Props {
  device: Device;
}

interface Emits {
  (e: 'edit', device: Device): void;
  (e: 'delete', deviceId: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { testConnection: testDeviceConnection } = useDeviceConnections();

// 响应式状态
const testing = ref(false);
const rebooting = ref(false);
const testResult = ref<DeviceTestResult | null>(null);

// 测试连接
const testConnection = async () => {
  try {
    testing.value = true;
    testResult.value = await testDeviceConnection(props.device.id);
  } catch (error) {
    console.error(error);
  } finally {
    testing.value = false;
  }
};

// 重启设备
const handleReboot = () => {
  Modal.confirm({
    title: '确认重启',
    content: '确定要重启这个设备吗？重启过程可能需要几分钟时间。',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        rebooting.value = true;
        await deviceService.rebootDevice(props.device.id);
        message.success('设备重启指令已发送');
      } catch (error) {
        message.error('设备重启失败');
      } finally {
        rebooting.value = false;
      }
    }
  });
};

// 删除设备
const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个设备吗？删除后无法恢复。',
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => emit('delete', props.device.id)
  });
};

// 工具函数
const getTypeText = (type: DeviceType): string => {
  const textMap = {
    nas: 'NAS服务器',
    switch: '交换机',
    router: '路由器',
    access_point: '接入点',
    firewall: '防火墙'
  };
  return textMap[type] || type;
};

const getStatusColor = (status: DeviceStatus): string => {
  const colorMap = {
    online: 'green',
    offline: 'red',
    maintenance: 'orange',
    error: 'red'
  };
  return colorMap[status] || 'default';
};

const getStatusText = (status: DeviceStatus): string => {
  const textMap = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
    error: '错误'
  };
  return textMap[status] || status;
};

const getTestDescription = (): string => {
  if (!testResult.value) return '';
  
  if (testResult.value.success) {
    return `延迟: ${testResult.value.latency}ms，测试时间: ${new Date(testResult.value.timestamp).toLocaleString()}`;
  } else {
    return testResult.value.error || '连接测试失败';
  }
};
</script>

<style scoped>
.device-detail {
  padding: 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.connection-test {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-result {
  margin-top: 16px;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.detail-actions .ant-btn {
  flex: 1;
}
</style>