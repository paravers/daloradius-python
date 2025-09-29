// 系统配置管理服务
import type {
  SystemConfig,
  ConfigCategory,
  ConfigGroup,
  UpdateConfigRequest,
  ConfigTestRequest,
  ConfigTestResult,
  ConfigBackup,
  CreateConfigBackupRequest,
  RestoreConfigRequest
} from '@/types/config';
import { DEFAULT_CONFIGS } from '@/types/config';

// 模拟配置数据
const mockConfigs: SystemConfig[] = [];

// 初始化默认配置
const initDefaultConfigs = () => {
  let id = 1;
  for (const [category, configs] of Object.entries(DEFAULT_CONFIGS)) {
    for (const config of configs) {
      mockConfigs.push({
        id: (id++).toString(),
        category: category as ConfigCategory,
        key: config.key!,
        value: config.defaultValue,
        type: config.type!,
        label: config.label!,
        description: config.description,
        defaultValue: config.defaultValue,
        options: config.options,
        validation: config.validation,
        isRequired: config.isRequired!,
        isEditable: config.isEditable!,
        updateTime: new Date().toISOString(),
        updatedBy: 'system'
      });
    }
  }
};

// 初始化配置
if (mockConfigs.length === 0) {
  initDefaultConfigs();
}

// 模拟备份数据
const mockBackups: ConfigBackup[] = [
  {
    id: '1',
    name: '系统初始配置',
    description: '系统部署时的初始配置备份',
    configs: [...mockConfigs],
    createTime: '2024-09-01 10:00:00',
    createdBy: 'admin',
    size: 1024 * 50 // 50KB
  },
  {
    id: '2',
    name: '生产环境配置',
    description: '切换到生产环境前的配置备份',
    configs: [...mockConfigs],
    createTime: '2024-09-15 14:30:00',
    createdBy: 'admin',
    size: 1024 * 48
  }
];

class ConfigService {
  private baseUrl = '/api/configs';

  // 获取所有配置
  async getAllConfigs(): Promise<SystemConfig[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 400));
      return [...mockConfigs];
    } catch (error) {
      console.error('获取系统配置失败:', error);
      throw new Error('获取系统配置失败');
    }
  }

  // 按分类获取配置
  async getConfigsByCategory(category: ConfigCategory): Promise<SystemConfig[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      return mockConfigs.filter(config => config.category === category);
    } catch (error) {
      console.error('获取配置分类失败:', error);
      throw new Error('获取配置分类失败');
    }
  }

  // 获取配置分组
  async getConfigGroups(): Promise<ConfigGroup[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const groups: ConfigGroup[] = [
        {
          category: ConfigCategory.GENERAL,
          title: '常规设置',
          description: '应用程序的基本配置选项',
          icon: 'setting',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.GENERAL)
        },
        {
          category: ConfigCategory.DATABASE,
          title: '数据库配置',
          description: '数据库连接和性能设置',
          icon: 'database',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.DATABASE)
        },
        {
          category: ConfigCategory.RADIUS,
          title: 'RADIUS配置',
          description: 'RADIUS服务器连接设置',
          icon: 'wifi',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.RADIUS)
        },
        {
          category: ConfigCategory.EMAIL,
          title: '邮件配置',
          description: 'SMTP邮件发送设置',
          icon: 'mail',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.EMAIL)
        },
        {
          category: ConfigCategory.SECURITY,
          title: '安全配置',
          description: '系统安全和认证设置',
          icon: 'safety',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.SECURITY)
        },
        {
          category: ConfigCategory.BACKUP,
          title: '备份配置',
          description: '数据备份和恢复设置',
          icon: 'save',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.BACKUP)
        },
        {
          category: ConfigCategory.LOGGING,
          title: '日志配置',
          description: '系统日志记录设置',
          icon: 'file-text',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.LOGGING)
        },
        {
          category: ConfigCategory.INTERFACE,
          title: '界面配置',
          description: '用户界面显示设置',
          icon: 'layout',
          configs: mockConfigs.filter(c => c.category === ConfigCategory.INTERFACE)
        }
      ];
      
      return groups;
    } catch (error) {
      console.error('获取配置分组失败:', error);
      throw new Error('获取配置分组失败');
    }
  }

  // 更新配置
  async updateConfigs(request: UpdateConfigRequest): Promise<SystemConfig[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const updatedConfigs: SystemConfig[] = [];
      
      for (const { key, value } of request.configs) {
        const configIndex = mockConfigs.findIndex(c => c.key === key);
        if (configIndex !== -1) {
          const updatedConfig = {
            ...mockConfigs[configIndex],
            value,
            updateTime: new Date().toISOString(),
            updatedBy: 'admin' // 实际应该从当前用户获取
          };
          
          mockConfigs[configIndex] = updatedConfig;
          updatedConfigs.push(updatedConfig);
        }
      }
      
      return updatedConfigs;
    } catch (error) {
      console.error('更新配置失败:', error);
      throw new Error('更新配置失败');
    }
  }

  // 重置配置为默认值
  async resetConfigs(keys: string[]): Promise<SystemConfig[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      
      const resetConfigs: SystemConfig[] = [];
      
      for (const key of keys) {
        const configIndex = mockConfigs.findIndex(c => c.key === key);
        if (configIndex !== -1) {
          const config = mockConfigs[configIndex];
          const resetConfig = {
            ...config,
            value: config.defaultValue,
            updateTime: new Date().toISOString(),
            updatedBy: 'admin'
          };
          
          mockConfigs[configIndex] = resetConfig;
          resetConfigs.push(resetConfig);
        }
      }
      
      return resetConfigs;
    } catch (error) {
      console.error('重置配置失败:', error);
      throw new Error('重置配置失败');
    }
  }

  // 测试配置连接
  async testConfig(request: ConfigTestRequest): Promise<ConfigTestResult> {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 模拟配置测试
      const success = Math.random() > 0.2; // 80%成功率
      
      let message = '';
      let details: Record<string, any> = {};
      
      switch (request.category) {
        case ConfigCategory.DATABASE:
          message = success ? '数据库连接测试成功' : '数据库连接失败：连接超时';
          details = {
            host: request.configs.db_host,
            port: request.configs.db_port,
            database: request.configs.db_name,
            latency: success ? Math.floor(Math.random() * 100) + 10 : undefined
          };
          break;
          
        case ConfigCategory.EMAIL:
          message = success ? 'SMTP连接测试成功' : 'SMTP连接失败：认证失败';
          details = {
            host: request.configs.smtp_host,
            port: request.configs.smtp_port,
            secure: request.configs.smtp_secure
          };
          break;
          
        case ConfigCategory.RADIUS:
          message = success ? 'RADIUS服务器连接正常' : 'RADIUS服务器连接失败：无响应';
          details = {
            server: request.configs.radius_host,
            authPort: request.configs.radius_auth_port,
            acctPort: request.configs.radius_acct_port
          };
          break;
          
        default:
          message = success ? '配置测试成功' : '配置测试失败';
      }
      
      return {
        success,
        message,
        details,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('配置测试失败:', error);
      throw new Error('配置测试失败');
    }
  }

  // 获取配置备份列表
  async getConfigBackups(): Promise<ConfigBackup[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      return [...mockBackups].sort((a, b) => 
        new Date(b.createTime).getTime() - new Date(a.createTime).getTime()
      );
    } catch (error) {
      console.error('获取配置备份列表失败:', error);
      throw new Error('获取配置备份列表失败');
    }
  }

  // 创建配置备份
  async createConfigBackup(request: CreateConfigBackupRequest): Promise<ConfigBackup> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      let configsToBackup = [...mockConfigs];
      
      // 如果指定了分类，只备份指定分类的配置
      if (request.categories && request.categories.length > 0) {
        configsToBackup = mockConfigs.filter(c => 
          request.categories!.includes(c.category)
        );
      }
      
      const backup: ConfigBackup = {
        id: Date.now().toString(),
        name: request.name,
        description: request.description,
        configs: configsToBackup,
        createTime: new Date().toLocaleString('zh-CN'),
        createdBy: 'admin',
        size: JSON.stringify(configsToBackup).length
      };
      
      mockBackups.unshift(backup);
      return backup;
    } catch (error) {
      console.error('创建配置备份失败:', error);
      throw new Error('创建配置备份失败');
    }
  }

  // 恢复配置备份
  async restoreConfigBackup(request: RestoreConfigRequest): Promise<SystemConfig[]> {
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const backup = mockBackups.find(b => b.id === request.backupId);
      if (!backup) {
        throw new Error('备份不存在');
      }
      
      let configsToRestore = backup.configs;
      
      // 如果指定了分类，只恢复指定分类的配置
      if (request.categories && request.categories.length > 0) {
        configsToRestore = backup.configs.filter(c => 
          request.categories!.includes(c.category)
        );
      }
      
      const restoredConfigs: SystemConfig[] = [];
      
      for (const backupConfig of configsToRestore) {
        const configIndex = mockConfigs.findIndex(c => c.key === backupConfig.key);
        
        if (configIndex !== -1) {
          if (request.overwrite) {
            // 覆盖现有配置
            const restoredConfig = {
              ...mockConfigs[configIndex],
              value: backupConfig.value,
              updateTime: new Date().toISOString(),
              updatedBy: 'admin'
            };
            
            mockConfigs[configIndex] = restoredConfig;
            restoredConfigs.push(restoredConfig);
          }
        } else {
          // 添加新配置
          const newConfig = {
            ...backupConfig,
            id: Date.now().toString() + Math.random(),
            updateTime: new Date().toISOString(),
            updatedBy: 'admin'
          };
          
          mockConfigs.push(newConfig);
          restoredConfigs.push(newConfig);
        }
      }
      
      return restoredConfigs;
    } catch (error) {
      console.error('恢复配置备份失败:', error);
      throw error;
    }
  }

  // 删除配置备份
  async deleteConfigBackup(id: string): Promise<void> {
    try {
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const backupIndex = mockBackups.findIndex(b => b.id === id);
      if (backupIndex === -1) {
        throw new Error('备份不存在');
      }
      
      mockBackups.splice(backupIndex, 1);
    } catch (error) {
      console.error('删除配置备份失败:', error);
      throw error;
    }
  }

  // 导出配置
  async exportConfigs(categories?: ConfigCategory[]): Promise<Blob> {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      let configsToExport = [...mockConfigs];
      
      if (categories && categories.length > 0) {
        configsToExport = mockConfigs.filter(c => categories.includes(c.category));
      }
      
      const exportData = {
        exportTime: new Date().toISOString(),
        version: '1.0.0',
        configs: configsToExport
      };
      
      const content = JSON.stringify(exportData, null, 2);
      return new Blob([content], { type: 'application/json' });
    } catch (error) {
      console.error('导出配置失败:', error);
      throw new Error('导出配置失败');
    }
  }

  // 导入配置
  async importConfigs(file: File, overwrite: boolean = false): Promise<SystemConfig[]> {
    try {
      const content = await file.text();
      const importData = JSON.parse(content);
      
      if (!importData.configs || !Array.isArray(importData.configs)) {
        throw new Error('配置文件格式不正确');
      }
      
      const importedConfigs: SystemConfig[] = [];
      
      for (const configData of importData.configs) {
        const existingIndex = mockConfigs.findIndex(c => c.key === configData.key);
        
        if (existingIndex !== -1) {
          if (overwrite) {
            const updatedConfig = {
              ...mockConfigs[existingIndex],
              value: configData.value,
              updateTime: new Date().toISOString(),
              updatedBy: 'admin'
            };
            
            mockConfigs[existingIndex] = updatedConfig;
            importedConfigs.push(updatedConfig);
          }
        } else {
          const newConfig: SystemConfig = {
            ...configData,
            id: Date.now().toString() + Math.random(),
            updateTime: new Date().toISOString(),
            updatedBy: 'admin'
          };
          
          mockConfigs.push(newConfig);
          importedConfigs.push(newConfig);
        }
      }
      
      return importedConfigs;
    } catch (error) {
      console.error('导入配置失败:', error);
      throw new Error('导入配置失败: ' + (error as Error).message);
    }
  }

  // 获取系统信息
  async getSystemInfo(): Promise<Record<string, any>> {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        application: {
          name: 'daloRADIUS',
          version: '1.0.0',
          buildTime: '2024-09-29 10:00:00',
          environment: 'production'
        },
        server: {
          os: 'Ubuntu 22.04 LTS',
          nodejs: 'v18.17.0',
          memory: {
            total: '8 GB',
            used: '2.5 GB',
            free: '5.5 GB'
          },
          cpu: {
            model: 'Intel Xeon E5-2686 v4',
            cores: 4,
            usage: '15.2%'
          },
          disk: {
            total: '100 GB',
            used: '35 GB',
            free: '65 GB'
          }
        },
        database: {
          type: 'MySQL',
          version: '8.0.35',
          size: '450 MB',
          tables: 15,
          connections: {
            active: 3,
            max: 100
          }
        },
        uptime: {
          application: '15 天 8 小时',
          system: '45 天 12 小时'
        }
      };
    } catch (error) {
      console.error('获取系统信息失败:', error);
      throw new Error('获取系统信息失败');
    }
  }
}

export const configService = new ConfigService();