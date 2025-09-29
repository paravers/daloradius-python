// 系统配置管理组合式函数
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import { configService } from '@/services/configService';
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

export function useConfigManagement() {
  // 响应式状态
  const configs = ref<SystemConfig[]>([]);
  const configGroups = ref<ConfigGroup[]>([]);
  const loading = ref(false);
  const saving = ref(false);
  const testing = ref(false);

  // 当前激活的分类
  const activeCategory = ref<ConfigCategory>(ConfigCategory.GENERAL);

  // 修改状态跟踪
  const modifiedConfigs = reactive<Map<string, any>>(new Map());
  const originalValues = reactive<Map<string, any>>(new Map());

  // 计算属性
  const hasModifications = computed(() => modifiedConfigs.size > 0);

  const currentCategoryConfigs = computed(() => {
    const group = configGroups.value.find(g => g.category === activeCategory.value);
    return group ? group.configs : [];
  });

  const modificationCount = computed(() => modifiedConfigs.size);

  // 获取所有配置
  const fetchConfigs = async () => {
    try {
      loading.value = true;
      const result = await configService.getAllConfigs();
      configs.value = result;
      
      // 保存原始值用于比较
      originalValues.clear();
      result.forEach(config => {
        originalValues.set(config.key, config.value);
      });
    } catch (error) {
      message.error('获取系统配置失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 获取配置分组
  const fetchConfigGroups = async () => {
    try {
      loading.value = true;
      const result = await configService.getConfigGroups();
      configGroups.value = result;
    } catch (error) {
      message.error('获取配置分组失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 更新配置值
  const updateConfigValue = (key: string, value: any) => {
    const originalValue = originalValues.get(key);
    
    if (JSON.stringify(value) !== JSON.stringify(originalValue)) {
      modifiedConfigs.set(key, value);
    } else {
      modifiedConfigs.delete(key);
    }
  };

  // 保存配置
  const saveConfigs = async () => {
    if (!hasModifications.value) {
      message.warning('没有配置需要保存');
      return;
    }

    try {
      saving.value = true;
      
      const updateRequest: UpdateConfigRequest = {
        configs: Array.from(modifiedConfigs.entries()).map(([key, value]) => ({
          key,
          value
        }))
      };
      
      await configService.updateConfigs(updateRequest);
      
      // 更新本地数据
      modifiedConfigs.forEach((value, key) => {
        const config = configs.value.find(c => c.key === key);
        if (config) {
          config.value = value;
          config.updateTime = new Date().toISOString();
        }
        originalValues.set(key, value);
      });
      
      // 更新配置分组中的数据
      configGroups.value.forEach(group => {
        group.configs.forEach(config => {
          if (modifiedConfigs.has(config.key)) {
            config.value = modifiedConfigs.get(config.key);
            config.updateTime = new Date().toISOString();
          }
        });
      });
      
      modifiedConfigs.clear();
      message.success(`成功保存 ${updateRequest.configs.length} 项配置`);
    } catch (error) {
      message.error('保存配置失败');
      throw error;
    } finally {
      saving.value = false;
    }
  };

  // 重置配置
  const resetConfigs = async (keys?: string[]) => {
    const keysToReset = keys || Array.from(modifiedConfigs.keys());
    
    if (keysToReset.length === 0) {
      message.warning('没有配置需要重置');
      return;
    }

    try {
      loading.value = true;
      await configService.resetConfigs(keysToReset);
      
      // 更新本地数据
      keysToReset.forEach(key => {
        const config = configs.value.find(c => c.key === key);
        if (config) {
          config.value = config.defaultValue;
          config.updateTime = new Date().toISOString();
        }
        
        // 更新配置分组
        configGroups.value.forEach(group => {
          const groupConfig = group.configs.find(c => c.key === key);
          if (groupConfig) {
            groupConfig.value = groupConfig.defaultValue;
            groupConfig.updateTime = new Date().toISOString();
          }
        });
        
        originalValues.set(key, config?.defaultValue);
        modifiedConfigs.delete(key);
      });
      
      message.success(`成功重置 ${keysToReset.length} 项配置`);
    } catch (error) {
      message.error('重置配置失败');
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // 测试配置
  const testConfig = async (category: ConfigCategory): Promise<ConfigTestResult> => {
    try {
      testing.value = true;
      
      // 获取当前分类的配置
      const categoryConfigs = currentCategoryConfigs.value;
      const configMap: Record<string, any> = {};
      
      categoryConfigs.forEach(config => {
        const value = modifiedConfigs.has(config.key) 
          ? modifiedConfigs.get(config.key)
          : config.value;
        configMap[config.key] = value;
      });
      
      const request: ConfigTestRequest = {
        category,
        configs: configMap
      };
      
      const result = await configService.testConfig(request);
      
      if (result.success) {
        message.success(result.message);
      } else {
        message.error(result.message);
      }
      
      return result;
    } catch (error) {
      message.error('配置测试失败');
      throw error;
    } finally {
      testing.value = false;
    }
  };

  // 切换分类
  const switchCategory = (category: ConfigCategory) => {
    activeCategory.value = category;
  };

  // 取消修改
  const cancelModifications = () => {
    modifiedConfigs.clear();
    message.info('已取消所有未保存的修改');
  };

  // 获取配置值（考虑修改状态）
  const getConfigValue = (key: string) => {
    if (modifiedConfigs.has(key)) {
      return modifiedConfigs.get(key);
    }
    
    const config = configs.value.find(c => c.key === key);
    return config ? config.value : undefined;
  };

  // 判断配置是否被修改
  const isConfigModified = (key: string) => {
    return modifiedConfigs.has(key);
  };

  return {
    // 状态
    configs,
    configGroups,
    loading,
    saving,
    testing,
    activeCategory,
    modifiedConfigs,
    
    // 计算属性
    hasModifications,
    currentCategoryConfigs,
    modificationCount,
    
    // 方法
    fetchConfigs,
    fetchConfigGroups,
    updateConfigValue,
    saveConfigs,
    resetConfigs,
    testConfig,
    switchCategory,
    cancelModifications,
    getConfigValue,
    isConfigModified
  };
}

// 配置备份管理
export function useConfigBackup() {
  const backups = ref<ConfigBackup[]>([]);
  const loading = ref(false);
  const creating = ref(false);
  const restoring = ref(false);

  // 获取备份列表
  const fetchBackups = async () => {
    try {
      loading.value = true;
      const result = await configService.getConfigBackups();
      backups.value = result;
    } catch (error) {
      message.error('获取配置备份列表失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  // 创建备份
  const createBackup = async (request: CreateConfigBackupRequest) => {
    try {
      creating.value = true;
      const backup = await configService.createConfigBackup(request);
      backups.value.unshift(backup);
      message.success('配置备份创建成功');
      return backup;
    } catch (error) {
      message.error('创建配置备份失败');
      throw error;
    } finally {
      creating.value = false;
    }
  };

  // 恢复备份
  const restoreBackup = async (request: RestoreConfigRequest) => {
    try {
      restoring.value = true;
      const restoredConfigs = await configService.restoreConfigBackup(request);
      message.success(`成功恢复 ${restoredConfigs.length} 项配置`);
      return restoredConfigs;
    } catch (error) {
      message.error('恢复配置备份失败');
      throw error;
    } finally {
      restoring.value = false;
    }
  };

  // 删除备份
  const deleteBackup = async (id: string) => {
    try {
      await configService.deleteConfigBackup(id);
      const index = backups.value.findIndex(b => b.id === id);
      if (index !== -1) {
        backups.value.splice(index, 1);
      }
      message.success('配置备份删除成功');
    } catch (error) {
      message.error('删除配置备份失败');
      throw error;
    }
  };

  return {
    backups,
    loading,
    creating,
    restoring,
    fetchBackups,
    createBackup,
    restoreBackup,
    deleteBackup
  };
}

// 配置导入导出
export function useConfigImportExport() {
  const exporting = ref(false);
  const importing = ref(false);

  // 导出配置
  const exportConfigs = async (categories?: ConfigCategory[]) => {
    try {
      exporting.value = true;
      const blob = await configService.exportConfigs(categories);
      
      // 下载文件
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      const categoryText = categories && categories.length > 0 
        ? categories.join('_') 
        : 'all';
      a.download = `config_export_${categoryText}_${new Date().toISOString().split('T')[0]}.json`;
      
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      message.success('配置导出成功');
    } catch (error) {
      message.error('配置导出失败');
      throw error;
    } finally {
      exporting.value = false;
    }
  };

  // 导入配置
  const importConfigs = async (file: File, overwrite: boolean = false) => {
    try {
      importing.value = true;
      const importedConfigs = await configService.importConfigs(file, overwrite);
      message.success(`成功导入 ${importedConfigs.length} 项配置`);
      return importedConfigs;
    } catch (error) {
      message.error('配置导入失败');
      throw error;
    } finally {
      importing.value = false;
    }
  };

  return {
    exporting,
    importing,
    exportConfigs,
    importConfigs
  };
}

// 系统信息
export function useSystemInfo() {
  const systemInfo = ref<Record<string, any>>({});
  const loading = ref(false);

  // 获取系统信息
  const fetchSystemInfo = async () => {
    try {
      loading.value = true;
      const result = await configService.getSystemInfo();
      systemInfo.value = result;
    } catch (error) {
      message.error('获取系统信息失败');
      console.error(error);
    } finally {
      loading.value = false;
    }
  };

  return {
    systemInfo,
    loading,
    fetchSystemInfo
  };
}