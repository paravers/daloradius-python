// 设备管理相关类型定义
export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  ipAddress: string;
  secret: string;
  description?: string;
  status: DeviceStatus;
  nasName: string;
  shortName: string;
  ports?: string;
  virtualServer?: string;
  community?: string;
  createTime: string;
  updateTime: string;
}

export enum DeviceType {
  NAS = 'nas',
  SWITCH = 'switch',
  ROUTER = 'router',
  ACCESS_POINT = 'access_point',
  FIREWALL = 'firewall'
}

export enum DeviceStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  ERROR = 'error'
}

export interface NasDevice extends Device {
  type: DeviceType.NAS;
  authPort: number;
  acctPort: number;
  radiusSecret: string;
  maxSessions: number;
  timeout: number;
}

export interface DeviceStatistics {
  deviceId: string;
  deviceName: string;
  totalUsers: number;
  activeUsers: number;
  totalSessions: number;
  activeSessions: number;
  totalTraffic: {
    upload: number;
    download: number;
  };
  lastActivity: string;
  uptime: number;
}

export interface DeviceConnection {
  deviceId: string;
  isConnected: boolean;
  latency?: number;
  lastPing: string;
  connectionStatus: 'connected' | 'disconnected' | 'timeout' | 'error';
  errorMessage?: string;
}

export interface CreateDeviceRequest {
  name: string;
  type: DeviceType;
  ipAddress: string;
  secret: string;
  description?: string;
  nasName: string;
  shortName: string;
  ports?: string;
  virtualServer?: string;
  community?: string;
  authPort?: number;
  acctPort?: number;
  radiusSecret?: string;
  maxSessions?: number;
  timeout?: number;
}

export interface UpdateDeviceRequest {
  name?: string;
  ipAddress?: string;
  secret?: string;
  description?: string;
  nasName?: string;
  shortName?: string;
  ports?: string;
  virtualServer?: string;
  community?: string;
  status?: DeviceStatus;
  authPort?: number;
  acctPort?: number;
  radiusSecret?: string;
  maxSessions?: number;
  timeout?: number;
}

export interface DeviceSearchParams {
  name?: string;
  type?: DeviceType;
  status?: DeviceStatus;
  ipAddress?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface DeviceListResponse {
  devices: Device[];
  total: number;
  page: number;
  pageSize: number;
}

// 设备测试连接结果
export interface DeviceTestResult {
  success: boolean;
  latency?: number;
  error?: string;
  timestamp: string;
}

// 设备配置备份
export interface DeviceBackup {
  id: string;
  deviceId: string;
  deviceName: string;
  backupData: Record<string, any>;
  createTime: string;
  description?: string;
}

// 设备监控数据
export interface DeviceMonitorData {
  deviceId: string;
  timestamp: string;
  cpuUsage?: number;
  memoryUsage?: number;
  networkTraffic?: {
    inbound: number;
    outbound: number;
  };
  temperature?: number;
  powerStatus?: 'on' | 'off' | 'unknown';
}

export const DEVICE_TYPE_OPTIONS = [
  { label: 'NAS服务器', value: DeviceType.NAS },
  { label: '交换机', value: DeviceType.SWITCH },
  { label: '路由器', value: DeviceType.ROUTER },
  { label: '接入点', value: DeviceType.ACCESS_POINT },
  { label: '防火墙', value: DeviceType.FIREWALL }
];

export const DEVICE_STATUS_OPTIONS = [
  { label: '在线', value: DeviceStatus.ONLINE, color: 'green' },
  { label: '离线', value: DeviceStatus.OFFLINE, color: 'red' },
  { label: '维护中', value: DeviceStatus.MAINTENANCE, color: 'orange' },
  { label: '错误', value: DeviceStatus.ERROR, color: 'red' }
];