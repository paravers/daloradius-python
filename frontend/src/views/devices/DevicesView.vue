<template>
  <div class="devices-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1>设备管理</h1>
          <p class="page-description">管理网络设备和NAS服务器</p>
        </div>
        <div class="header-actions">
          <a-button type="primary" @click="showCreateModal = true">
            <template #icon><PlusOutlined /></template>
            添加设备
          </a-button>
          <a-button @click="handleExportConfig" :loading="exporting">
            <template #icon><ExportOutlined /></template>
            导出配置
          </a-button>
          <a-upload
            :show-upload-list="false"
            :before-upload="handleImportConfig"
            accept=".json"
          >
            <a-button>
              <template #icon><ImportOutlined /></template>
              导入配置
            </a-button>
          </a-upload>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        title="总设备数"
        :value="total"
        :loading="loading"
        color="blue"
        icon="desktop"
      />
      <StatCard
        title="在线设备"
        :value="onlineDevicesCount"
        :loading="loading"
        color="green"
        icon="check-circle"
      />
      <StatCard
        title="离线设备"
        :value="offlineDevicesCount"
        :loading="loading"
        color="red"
        icon="close-circle"
      />
      <StatCard
        title="维护中"
        :value="maintenanceDevicesCount"
        :loading="loading"
        color="orange"
        icon="tool"
      />
    </div>

    <!-- 搜索和工具栏 -->
    <a-card class="search-card">
      <SearchForm
        v-model:values="searchParams"
        :fields="searchFields"
        @search="searchDevices"
        @reset="resetSearch"
      />
      
      <div class="table-toolbar">
        <div class="toolbar-left">
          <span v-if="hasSelection" class="selection-info">
            已选择 {{ selectionCount }} 项
          </span>
        </div>
        <div class="toolbar-right">
          <a-button
            v-if="hasSelection"
            danger
            @click="handleBatchDelete"
            :loading="loading"
          >
            <template #icon><DeleteOutlined /></template>
            批量删除
          </a-button>
          <a-button @click="fetchDevices" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 设备列表 -->
    <a-card title="设备列表">
      <DataTable
        :columns="columns"
        :data="devices"
        :loading="loading"
        :pagination="{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 项，共 ${total} 项`
        }"
        :row-selection="{
          selectedRowKeys: selectedDevices,
          onChange: (keys) => selectedDevices = keys,
          onSelectAll: toggleAllSelection
        }"
        @change="handleTableChange"
      >
        <!-- 设备状态 -->
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>

        <!-- 设备类型 -->
        <template #type="{ record }">
          <a-tag color="blue">
            {{ getTypeText(record.type) }}
          </a-tag>
        </template>

        <!-- IP地址 -->
        <template #ipAddress="{ record }">
          <a-button
            type="link"
            size="small"
            @click="testDeviceConnection(record.id)"
          >
            {{ record.ipAddress }}
          </a-button>
        </template>

        <!-- 操作列 -->
        <template #actions="{ record }">
          <div class="action-buttons">
            <a-button
              type="link"
              size="small"
              @click="viewDevice(record)"
            >
              查看
            </a-button>
            <a-button
              type="link"
              size="small"
              @click="editDevice(record)"
            >
              编辑
            </a-button>
            <a-dropdown>
              <a-button type="link" size="small">
                更多
                <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="testDeviceConnection(record.id)">
                    <WifiOutlined /> 测试连接
                  </a-menu-item>
                  <a-menu-item @click="rebootDevice(record.id)">
                    <ReloadOutlined /> 重启设备
                  </a-menu-item>
                  <a-menu-item @click="viewStatistics(record.id)">
                    <BarChartOutlined /> 查看统计
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="deleteDevice(record.id)" danger>
                    <DeleteOutlined /> 删除
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </template>
      </DataTable>
    </a-card>

    <!-- 设备详情抽屉 -->
    <a-drawer
      v-model:open="showDetailDrawer"
      title="设备详情"
      :width="600"
      placement="right"
    >
      <DeviceDetail
        v-if="selectedDevice"
        :device="selectedDevice"
        @edit="editDevice"
        @delete="deleteDevice"
      />
    </a-drawer>

    <!-- 创建设备模态框 -->
    <a-modal
      v-model:open="showCreateModal"
      title="添加设备"
      :width="800"
      :footer="null"
    >
      <DeviceForm
        @submit="handleCreateDevice"
        @cancel="showCreateModal = false"
      />
    </a-modal>

    <!-- 编辑设备模态框 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑设备"
      :width="800"
      :footer="null"
    >
      <DeviceForm
        v-if="editingDevice"
        :device="editingDevice"
        @submit="handleUpdateDevice"
        @cancel="showEditModal = false"
      />
    </a-modal>

    <!-- 统计信息模态框 -->
    <a-modal
      v-model:open="showStatisticsModal"
      title="设备统计"
      :width="900"
      :footer="null"
    >
      <DeviceStatistics
        v-if="statisticsDeviceId"
        :device-id="statisticsDeviceId"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ExportOutlined,
  ImportOutlined,
  DownOutlined,
  WifiOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue';
import DataTable from '@/components/common/DataTable.vue';
import SearchForm from '@/components/common/SearchForm.vue';
import StatCard from '@/components/common/StatCard.vue';
import DeviceDetail from '@/components/devices/DeviceDetail.vue';
import DeviceForm from '@/components/devices/DeviceForm.vue';
import DeviceStatistics from '@/components/devices/DeviceStatistics.vue';
import { useDeviceManagement, useDeviceConnections } from '@/composables/useDeviceManagement';
import { deviceService } from '@/services/deviceService';
import type { Device, DeviceStatus, DeviceType, CreateDeviceRequest, UpdateDeviceRequest } from '@/types/device';
import { DEVICE_TYPE_OPTIONS, DEVICE_STATUS_OPTIONS } from '@/types/device';

// 组合式函数
const {
  devices,
  loading,
  total,
  currentPage,
  pageSize,
  searchParams,
  selectedDevices,
  selectedDevice,
  hasSelection,
  selectionCount,
  fetchDevices,
  fetchDevice,
  createDevice,
  updateDevice,
  deleteDevice: deleteDeviceById,
  deleteSelectedDevices,
  searchDevices,
  resetSearch,
  onPageChange,
  toggleAllSelection,
  clearSelection
} = useDeviceManagement();

const { testConnection } = useDeviceConnections();

// 响应式状态
const showDetailDrawer = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showStatisticsModal = ref(false);
const editingDevice = ref<Device | null>(null);
const statisticsDeviceId = ref<string | null>(null);
const exporting = ref(false);

// 计算属性
const onlineDevicesCount = computed(() => 
  devices.value.filter(d => d.status === 'online').length
);

const offlineDevicesCount = computed(() => 
  devices.value.filter(d => d.status === 'offline').length
);

const maintenanceDevicesCount = computed(() => 
  devices.value.filter(d => d.status === 'maintenance').length
);

// 搜索字段配置
const searchFields = [
  {
    key: 'name',
    label: '设备名称',
    type: 'input',
    placeholder: '请输入设备名称'
  },
  {
    key: 'type',
    label: '设备类型',
    type: 'select',
    options: DEVICE_TYPE_OPTIONS
  },
  {
    key: 'status',
    label: '设备状态',
    type: 'select',
    options: DEVICE_STATUS_OPTIONS
  },
  {
    key: 'ipAddress',
    label: 'IP地址',
    type: 'input',
    placeholder: '请输入IP地址'
  }
];

// 表格列配置
const columns = [
  {
    title: '设备名称',
    dataIndex: 'name',
    key: 'name',
    sorter: true,
    width: 150
  },
  {
    title: '设备类型',
    dataIndex: 'type',
    key: 'type',
    slots: { customRender: 'type' },
    width: 120
  },
  {
    title: 'IP地址',
    dataIndex: 'ipAddress',
    key: 'ipAddress',
    slots: { customRender: 'ipAddress' },
    width: 140
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' },
    width: 100
  },
  {
    title: '短名称',
    dataIndex: 'shortName',
    key: 'shortName',
    width: 100
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    key: 'updateTime',
    sorter: true,
    width: 160
  },
  {
    title: '操作',
    key: 'actions',
    slots: { customRender: 'actions' },
    width: 150,
    fixed: 'right'
  }
];

// 事件处理
const handleTableChange = ({ current, pageSize: size, sorter }: any) => {
  if (sorter) {
    onPageChange(current, size);
  } else {
    onPageChange(current, size);
  }
};

const viewDevice = async (device: Device) => {
  selectedDevice.value = device;
  showDetailDrawer.value = true;
};

const editDevice = (device: Device) => {
  editingDevice.value = device;
  showEditModal.value = true;
};

const handleCreateDevice = async (data: CreateDeviceRequest) => {
  try {
    await createDevice(data);
    showCreateModal.value = false;
  } catch (error) {
    console.error(error);
  }
};

const handleUpdateDevice = async (data: UpdateDeviceRequest) => {
  if (!editingDevice.value) return;
  
  try {
    await updateDevice(editingDevice.value.id, data);
    showEditModal.value = false;
    editingDevice.value = null;
  } catch (error) {
    console.error(error);
  }
};

const deleteDevice = (deviceId: string) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个设备吗？删除后无法恢复。',
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => deleteDeviceById(deviceId)
  });
};

const handleBatchDelete = () => {
  if (selectedDevices.value.length === 0) {
    message.warning('请先选择要删除的设备');
    return;
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedDevices.value.length} 个设备吗？删除后无法恢复。`,
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: deleteSelectedDevices
  });
};

const testDeviceConnection = async (deviceId: string) => {
  try {
    await testConnection(deviceId);
  } catch (error) {
    console.error(error);
  }
};

const rebootDevice = (deviceId: string) => {
  Modal.confirm({
    title: '确认重启',
    content: '确定要重启这个设备吗？重启过程可能需要几分钟时间。',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await deviceService.rebootDevice(deviceId);
        message.success('设备重启指令已发送');
        await fetchDevices();
      } catch (error) {
        message.error('设备重启失败');
      }
    }
  });
};

const viewStatistics = (deviceId: string) => {
  statisticsDeviceId.value = deviceId;
  showStatisticsModal.value = true;
};

const handleExportConfig = async () => {
  if (selectedDevices.value.length === 0) {
    message.warning('请先选择要导出配置的设备');
    return;
  }

  try {
    exporting.value = true;
    
    for (const deviceId of selectedDevices.value) {
      const blob = await deviceService.exportDeviceConfig(deviceId);
      const device = devices.value.find(d => d.id === deviceId);
      
      // 下载文件
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `device-${device?.name || deviceId}-config.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
    
    message.success('配置导出成功');
  } catch (error) {
    message.error('配置导出失败');
  } finally {
    exporting.value = false;
  }
};

const handleImportConfig = async (file: File) => {
  try {
    const importedDevices = await deviceService.importDeviceConfig(file);
    message.success(`成功导入 ${importedDevices.length} 个设备配置`);
    await fetchDevices();
  } catch (error) {
    message.error('配置导入失败');
  }
  return false; // 阻止默认上传行为
};

// 工具函数
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

// 生命周期
onMounted(() => {
  fetchDevices();
});

onUnmounted(() => {
  clearSelection();
});
</script>

<style scoped>
.devices-view {
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
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.search-card {
  margin-bottom: 24px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-info {
  color: #1890ff;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .ant-btn-link {
  padding: 0;
  height: auto;
}
</style>