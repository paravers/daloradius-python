// 设备管理服务
import type {
  Device,
  DeviceListResponse,
  CreateDeviceRequest,
  UpdateDeviceRequest,
  DeviceSearchParams,
  DeviceStatistics,
  DeviceConnection,
  DeviceTestResult,
  DeviceBackup,
  DeviceMonitorData,
  DeviceType,
  DeviceStatus
} from '@/types/device';

// 模拟数据
const mockDevices: Device[] = [
  {
    id: '1',
    name: 'NAS-001',
    type: DeviceType.NAS,
    ipAddress: '192.168.1.10',
    secret: 'radius_secret_001',
    description: '主要NAS服务器',
    status: DeviceStatus.ONLINE,
    nasName: 'nas001',
    shortName: 'nas001',
    ports: '1812,1813',
    virtualServer: '',
    community: 'public',
    createTime: '2024-01-15 10:00:00',
    updateTime: '2024-09-29 14:30:00'
  },
  {
    id: '2',
    name: 'Switch-001',
    type: DeviceType.SWITCH,
    ipAddress: '192.168.1.20',
    secret: 'switch_secret_001',
    description: '核心交换机',
    status: DeviceStatus.ONLINE,
    nasName: 'switch001',
    shortName: 'sw001',
    ports: '161,162',
    virtualServer: '',
    community: 'public',
    createTime: '2024-02-01 09:00:00',
    updateTime: '2024-09-28 16:45:00'
  },
  {
    id: '3',
    name: 'Router-001',
    type: DeviceType.ROUTER,
    ipAddress: '192.168.1.1',
    secret: 'router_secret_001',
    description: '边界路由器',
    status: DeviceStatus.MAINTENANCE,
    nasName: 'router001',
    shortName: 'rt001',
    ports: '22,23,161',
    virtualServer: '',
    community: 'private',
    createTime: '2024-01-01 08:00:00',
    updateTime: '2024-09-29 10:00:00'
  },
  {
    id: '4',
    name: 'AP-001',
    type: DeviceType.ACCESS_POINT,
    ipAddress: '192.168.1.100',
    secret: 'ap_secret_001',
    description: '办公区接入点',
    status: DeviceStatus.OFFLINE,
    nasName: 'ap001',
    shortName: 'ap001',
    ports: '161,162',
    virtualServer: '',
    community: 'public',
    createTime: '2024-03-01 14:00:00',
    updateTime: '2024-09-27 18:20:00'
  }
];

const mockStatistics: DeviceStatistics[] = [
  {
    deviceId: '1',
    deviceName: 'NAS-001',
    totalUsers: 156,
    activeUsers: 45,
    totalSessions: 2340,
    activeSessions: 45,
    totalTraffic: {
      upload: 1024 * 1024 * 1024 * 50, // 50GB
      download: 1024 * 1024 * 1024 * 200 // 200GB
    },
    lastActivity: '2024-09-29 14:30:00',
    uptime: 86400 * 15 // 15天
  },
  {
    deviceId: '2',
    deviceName: 'Switch-001',
    totalUsers: 89,
    activeUsers: 32,
    totalSessions: 1560,
    activeSessions: 32,
    totalTraffic: {
      upload: 1024 * 1024 * 1024 * 30,
      download: 1024 * 1024 * 1024 * 120
    },
    lastActivity: '2024-09-29 14:25:00',
    uptime: 86400 * 8
  }
];

class DeviceService {
  private baseUrl = '/api/devices';

  // 获取设备列表
  async getDevices(params: DeviceSearchParams = {}): Promise<DeviceListResponse> {
    try {
      // 模拟API请求延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      
      let filteredDevices = [...mockDevices];
      
      // 应用过滤条件
      if (params.name) {
        filteredDevices = filteredDevices.filter(device => 
          device.name.toLowerCase().includes(params.name!.toLowerCase())
        );
      }
      
      if (params.type) {
        filteredDevices = filteredDevices.filter(device => device.type === params.type);
      }
      
      if (params.status) {
        filteredDevices = filteredDevices.filter(device => device.status === params.status);
      }
      
      if (params.ipAddress) {
        filteredDevices = filteredDevices.filter(device => 
          device.ipAddress.includes(params.ipAddress!)
        );
      }
      
      // 排序
      if (params.sortBy) {
        filteredDevices.sort((a, b) => {
          const aValue = (a as any)[params.sortBy!];
          const bValue = (b as any)[params.sortBy!];
          const order = params.sortOrder === 'desc' ? -1 : 1;
          
          if (aValue < bValue) return -1 * order;
          if (aValue > bValue) return 1 * order;
          return 0;
        });
      }
      
      // 分页
      const page = params.page || 1;
      const pageSize = params.pageSize || 10;
      const startIndex = (page - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedDevices = filteredDevices.slice(startIndex, endIndex);
      
      return {
        devices: paginatedDevices,
        total: filteredDevices.length,
        page,
        pageSize
      };
    } catch (error) {
      console.error('获取设备列表失败:', error);
      throw new Error('获取设备列表失败');
    }
  }

  // 获取设备详情
  async getDevice(id: string): Promise<Device> {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const device = mockDevices.find(d => d.id === id);
      if (!device) {
        throw new Error('设备不存在');
      }
      
      return device;
    } catch (error) {
      console.error('获取设备详情失败:', error);
      throw error;
    }
  }

  // 创建设备
  async createDevice(data: CreateDeviceRequest): Promise<Device> {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const newDevice: Device = {
        id: Date.now().toString(),
        ...data,
        status: DeviceStatus.OFFLINE,
        createTime: new Date().toLocaleString('zh-CN'),
        updateTime: new Date().toLocaleString('zh-CN')
      };
      
      mockDevices.unshift(newDevice);
      return newDevice;
    } catch (error) {
      console.error('创建设备失败:', error);
      throw new Error('创建设备失败');
    }
  }

  // 更新设备
  async updateDevice(id: string, data: UpdateDeviceRequest): Promise<Device> {
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      const deviceIndex = mockDevices.findIndex(d => d.id === id);
      if (deviceIndex === -1) {
        throw new Error('设备不存在');
      }
      
      const updatedDevice = {
        ...mockDevices[deviceIndex],
        ...data,
        updateTime: new Date().toLocaleString('zh-CN')
      };
      
      mockDevices[deviceIndex] = updatedDevice;
      return updatedDevice;
    } catch (error) {
      console.error('更新设备失败:', error);
      throw error;
    }
  }

  // 删除设备
  async deleteDevice(id: string): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const deviceIndex = mockDevices.findIndex(d => d.id === id);
      if (deviceIndex === -1) {
        throw new Error('设备不存在');
      }
      
      mockDevices.splice(deviceIndex, 1);
    } catch (error) {
      console.error('删除设备失败:', error);
      throw error;
    }
  }

  // 批量删除设备
  async deleteDevices(ids: string[]): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      for (const id of ids) {
        const deviceIndex = mockDevices.findIndex(d => d.id === id);
        if (deviceIndex !== -1) {
          mockDevices.splice(deviceIndex, 1);
        }
      }
    } catch (error) {
      console.error('批量删除设备失败:', error);
      throw new Error('批量删除设备失败');
    }
  }

  // 测试设备连接
  async testDeviceConnection(id: string): Promise<DeviceTestResult> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const device = mockDevices.find(d => d.id === id);
      if (!device) {
        throw new Error('设备不存在');
      }
      
      // 模拟测试结果
      const success = Math.random() > 0.2; // 80%成功率
      
      return {
        success,
        latency: success ? Math.floor(Math.random() * 100) + 10 : undefined,
        error: success ? undefined : '连接超时或设备无响应',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('测试设备连接失败:', error);
      throw error;
    }
  }

  // 获取设备统计信息
  async getDeviceStatistics(id?: string): Promise<DeviceStatistics[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 400));
      
      if (id) {
        const stats = mockStatistics.filter(s => s.deviceId === id);
        return stats;
      }
      
      return mockStatistics;
    } catch (error) {
      console.error('获取设备统计信息失败:', error);
      throw new Error('获取设备统计信息失败');
    }
  }

  // 获取设备连接状态
  async getDeviceConnections(): Promise<DeviceConnection[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return mockDevices.map(device => ({
        deviceId: device.id,
        isConnected: device.status === DeviceStatus.ONLINE,
        latency: device.status === DeviceStatus.ONLINE ? Math.floor(Math.random() * 100) + 10 : undefined,
        lastPing: new Date().toISOString(),
        connectionStatus: device.status === DeviceStatus.ONLINE ? 'connected' : 'disconnected'
      }));
    } catch (error) {
      console.error('获取设备连接状态失败:', error);
      throw new Error('获取设备连接状态失败');
    }
  }

  // 重启设备
  async rebootDevice(id: string): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const device = mockDevices.find(d => d.id === id);
      if (!device) {
        throw new Error('设备不存在');
      }
      
      // 模拟重启过程
      device.status = DeviceStatus.MAINTENANCE;
      device.updateTime = new Date().toLocaleString('zh-CN');
      
      // 3秒后恢复在线状态
      setTimeout(() => {
        device.status = DeviceStatus.ONLINE;
        device.updateTime = new Date().toLocaleString('zh-CN');
      }, 3000);
    } catch (error) {
      console.error('重启设备失败:', error);
      throw error;
    }
  }

  // 导出设备配置
  async exportDeviceConfig(id: string): Promise<Blob> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const device = mockDevices.find(d => d.id === id);
      if (!device) {
        throw new Error('设备不存在');
      }
      
      const config = JSON.stringify(device, null, 2);
      return new Blob([config], { type: 'application/json' });
    } catch (error) {
      console.error('导出设备配置失败:', error);
      throw error;
    }
  }

  // 导入设备配置
  async importDeviceConfig(file: File): Promise<Device[]> {
    try {
      const content = await file.text();
      const devices = JSON.parse(content);
      
      if (!Array.isArray(devices)) {
        throw new Error('配置文件格式不正确');
      }
      
      const importedDevices: Device[] = [];
      
      for (const deviceData of devices) {
        const newDevice: Device = {
          ...deviceData,
          id: Date.now().toString() + Math.random(),
          createTime: new Date().toLocaleString('zh-CN'),
          updateTime: new Date().toLocaleString('zh-CN')
        };
        
        mockDevices.push(newDevice);
        importedDevices.push(newDevice);
      }
      
      return importedDevices;
    } catch (error) {
      console.error('导入设备配置失败:', error);
      throw new Error('导入设备配置失败: ' + (error as Error).message);
    }
  }
}

export const deviceService = new DeviceService();