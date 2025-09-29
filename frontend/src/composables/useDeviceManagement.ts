// 设备管理组合式函数
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import { deviceService } from '@/services/deviceService';
import type {
  Device,
  DeviceSearchParams,
  CreateDeviceRequest,
  UpdateDeviceRequest,
  DeviceStatistics,
  DeviceConnection,
  DeviceTestResult,
  DeviceStatus,
  DeviceType
} from '@/types/device';

export function useDeviceManagement() {
  // 响应式状态
  const devices = ref<Device[]>([]);
  const loading = ref(false);
  const total = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);
  
  // 搜索参数
  const searchParams = reactive<DeviceSearchParams>({
    name: '',
    type: undefined,
    status: undefined,
    ipAddress: '',
    page: 1,
    pageSize: 10,
    sortBy: 'createTime',
    sortOrder: 'desc'
  });

  // 选中的设备
  const selectedDevices = ref<string[]>([]);
  const selectedDevice = ref<Device | null>(null);

  // 计算属性
  const hasSelection = computed(() => selectedDevices.value.length > 0);
  const selectionCount = computed(() => selectedDevices.value.length);

  // 获取设备列表
  const fetchDevices = async (params?: Partial<DeviceSearchParams>) => {
    try {
      loading.value = true;
      const queryParams = { ...searchParams, ...params };
      const response = await deviceService.getDevices(queryParams);
      
      devices.value = response.devices;
      total.value = response.total;
      currentPage.value = response.page;
      pageSize.value = response.pageSize;
    } catch (error) {
      message.error('获取设备列表失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 获取设备详情
  const fetchDevice = async (id: string) => {
    try {
      loading.value = true;
      const device = await deviceService.getDevice(id);
      selectedDevice.value = device;
      return device;
    } catch (error) {
      message.error('获取设备详情失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 创建设备
  const createDevice = async (data: CreateDeviceRequest) => {
    try {
      loading.value = true;
      const device = await deviceService.createDevice(data);
      message.success('设备创建成功');
      await fetchDevices(); // 刷新列表
      return device;
    } catch (error) {
      message.error('设备创建失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 更新设备
  const updateDevice = async (id: string, data: UpdateDeviceRequest) => {
    try {
      loading.value = true;
      const device = await deviceService.updateDevice(id, data);
      message.success('设备更新成功');
      await fetchDevices(); // 刷新列表
      return device;
    } catch (error) {
      message.error('设备更新失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 删除设备
  const deleteDevice = async (id: string) => {
    try {
      loading.value = true;
      await deviceService.deleteDevice(id);
      message.success('设备删除成功');
      await fetchDevices(); // 刷新列表
    } catch (error) {
      message.error('设备删除失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 批量删除设备
  const deleteSelectedDevices = async () => {
    if (selectedDevices.value.length === 0) {
      message.warning('请先选择要删除的设备');
      return;
    }

    try {
      loading.value = true;
      await deviceService.deleteDevices(selectedDevices.value);
      message.success(`成功删除 ${selectedDevices.value.length} 个设备`);
      selectedDevices.value = [];
      await fetchDevices(); // 刷新列表
    } catch (error) {
      message.error('批量删除设备失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 搜索设备
  const searchDevices = async () => {
    searchParams.page = 1;
    await fetchDevices();
  };

  // 重置搜索
  const resetSearch = () => {
    Object.assign(searchParams, {
      name: '',
      type: undefined,
      status: undefined,
      ipAddress: '',
      page: 1,
      pageSize: 10,
      sortBy: 'createTime',
      sortOrder: 'desc'
    });
    fetchDevices();
  };

  // 分页变化
  const onPageChange = (page: number, size: number) => {
    searchParams.page = page;
    searchParams.pageSize = size;
    fetchDevices();
  };

  // 排序变化
  const onSortChange = (sortBy: string, sortOrder: 'asc' | 'desc') => {
    searchParams.sortBy = sortBy;
    searchParams.sortOrder = sortOrder;
    fetchDevices();
  };

  // 选择设备
  const toggleDeviceSelection = (deviceId: string) => {
    const index = selectedDevices.value.indexOf(deviceId);
    if (index > -1) {
      selectedDevices.value.splice(index, 1);
    } else {
      selectedDevices.value.push(deviceId);
    }
  };

  // 全选/取消全选
  const toggleAllSelection = (checked: boolean) => {
    selectedDevices.value = checked ? devices.value.map(d => d.id) : [];
  };

  // 清空选择
  const clearSelection = () => {
    selectedDevices.value = [];
  };

  return {
    // 状态
    devices,
    loading,
    total,
    currentPage,
    pageSize,
    searchParams,
    selectedDevices,
    selectedDevice,
    
    // 计算属性
    hasSelection,
    selectionCount,
    
    // 方法
    fetchDevices,
    fetchDevice,
    createDevice,
    updateDevice,
    deleteDevice,
    deleteSelectedDevices,
    searchDevices,
    resetSearch,
    onPageChange,
    onSortChange,
    toggleDeviceSelection,
    toggleAllSelection,
    clearSelection
  };
}

// 设备连接状态管理
export function useDeviceConnections() {
  const connections = ref<DeviceConnection[]>([]);
  const loading = ref(false);
  const autoRefresh = ref(false);
  const refreshInterval = ref<number | null>(null);

  // 获取连接状态
  const fetchConnections = async () => {
    try {
      loading.value = true;
      const result = await deviceService.getDeviceConnections();
      connections.value = result;
    } catch (error) {
      message.error('获取设备连接状态失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 测试设备连接
  const testConnection = async (deviceId: string): Promise<DeviceTestResult> => {
    try {
      const result = await deviceService.testDeviceConnection(deviceId);
      
      if (result.success) {
        message.success(`设备连接正常，延迟: ${result.latency}ms`);
      } else {
        message.error(`设备连接失败: ${result.error}`);
      }
      
      return result;
    } catch (error) {
      message.error('测试设备连接失败');
      throw error;
    }
  };

  // 开始自动刷新
  const startAutoRefresh = (interval = 30000) => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value);
    }
    
    autoRefresh.value = true;
    refreshInterval.value = window.setInterval(() => {
      fetchConnections();
    }, interval);
  };

  // 停止自动刷新
  const stopAutoRefresh = () => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value);
      refreshInterval.value = null;
    }
    autoRefresh.value = false;
  };

  // 组件卸载时清理定时器
  const cleanup = () => {
    stopAutoRefresh();
  };

  return {
    connections,
    loading,
    autoRefresh,
    fetchConnections,
    testConnection,
    startAutoRefresh,
    stopAutoRefresh,
    cleanup
  };
}

// 设备统计信息管理
export function useDeviceStatistics() {
  const statistics = ref<DeviceStatistics[]>([]);
  const loading = ref(false);

  // 获取统计信息
  const fetchStatistics = async (deviceId?: string) => {
    try {
      loading.value = true;
      const result = await deviceService.getDeviceStatistics(deviceId);
      statistics.value = result;
    } catch (error) {
      message.error('获取设备统计信息失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 格式化流量
  const formatTraffic = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

  // 格式化时间
  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) {
      return `${days}天 ${hours}小时`;
    } else if (hours > 0) {
      return `${hours}小时 ${minutes}分钟`;
    } else {
      return `${minutes}分钟`;
    }
  };

  return {
    statistics,
    loading,
    fetchStatistics,
    formatTraffic,
    formatUptime
  };
}