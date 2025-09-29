// 系统配置相关类型定义
export interface SystemConfig {
  id: string;
  category: ConfigCategory;
  key: string;
  value: any;
  type: ConfigValueType;
  label: string;
  description?: string;
  defaultValue?: any;
  options?: ConfigOption[];
  validation?: ConfigValidation;
  isRequired: boolean;
  isEditable: boolean;
  updateTime: string;
  updatedBy: string;
}

export enum ConfigCategory {
  GENERAL = 'general',
  DATABASE = 'database',
  RADIUS = 'radius',
  EMAIL = 'email',
  SECURITY = 'security',
  BACKUP = 'backup',
  LOGGING = 'logging',
  INTERFACE = 'interface',
  PERFORMANCE = 'performance',
  INTEGRATION = 'integration'
}

export enum ConfigValueType {
  STRING = 'string',
  NUMBER = 'number',
  BOOLEAN = 'boolean',
  JSON = 'json',
  PASSWORD = 'password',
  EMAIL = 'email',
  URL = 'url',
  FILE_PATH = 'file_path',
  SELECT = 'select',
  TEXTAREA = 'textarea',
  COLOR = 'color'
}

export interface ConfigOption {
  label: string;
  value: any;
  disabled?: boolean;
}

export interface ConfigValidation {
  min?: number;
  max?: number;
  pattern?: string;
  required?: boolean;
  custom?: (value: any) => string | null;
}

export interface ConfigGroup {
  category: ConfigCategory;
  title: string;
  description: string;
  icon: string;
  configs: SystemConfig[];
}

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  connectionPool: {
    min: number;
    max: number;
    timeout: number;
  };
  ssl: {
    enabled: boolean;
    cert?: string;
    key?: string;
  };
}

export interface RadiusConfig {
  server: {
    host: string;
    authPort: number;
    acctPort: number;
    secret: string;
  };
  client: {
    timeout: number;
    retries: number;
    deadtime: number;
  };
  dictionary: {
    path: string;
    vendor?: string[];
  };
}

export interface EmailConfig {
  smtp: {
    host: string;
    port: number;
    secure: boolean;
    username: string;
    password: string;
  };
  from: {
    name: string;
    address: string;
  };
  templates: {
    [key: string]: {
      subject: string;
      template: string;
    };
  };
}

export interface SecurityConfig {
  authentication: {
    sessionTimeout: number;
    maxLoginAttempts: number;
    lockoutDuration: number;
    passwordPolicy: {
      minLength: number;
      requireUppercase: boolean;
      requireLowercase: boolean;
      requireNumbers: boolean;
      requireSymbols: boolean;
    };
  };
  encryption: {
    algorithm: string;
    keySize: number;
  };
  cors: {
    enabled: boolean;
    origins: string[];
    credentials: boolean;
  };
}

export interface BackupConfig {
  schedule: {
    enabled: boolean;
    cron: string;
    timezone: string;
  };
  storage: {
    type: 'local' | 's3' | 'ftp';
    path: string;
    credentials?: Record<string, any>;
  };
  retention: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  compression: {
    enabled: boolean;
    algorithm: 'gzip' | 'bzip2' | 'xz';
  };
}

export interface LoggingConfig {
  level: 'error' | 'warn' | 'info' | 'debug';
  targets: {
    file: {
      enabled: boolean;
      path: string;
      maxSize: string;
      maxFiles: number;
    };
    database: {
      enabled: boolean;
      table: string;
    };
    syslog: {
      enabled: boolean;
      host: string;
      port: number;
      facility: string;
    };
  };
  audit: {
    enabled: boolean;
    events: string[];
  };
}

export interface UpdateConfigRequest {
  configs: {
    key: string;
    value: any;
  }[];
}

export interface ConfigTestRequest {
  category: ConfigCategory;
  configs: Record<string, any>;
}

export interface ConfigTestResult {
  success: boolean;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ConfigBackup {
  id: string;
  name: string;
  description?: string;
  configs: SystemConfig[];
  createTime: string;
  createdBy: string;
  size: number;
}

export interface CreateConfigBackupRequest {
  name: string;
  description?: string;
  categories?: ConfigCategory[];
}

export interface RestoreConfigRequest {
  backupId: string;
  categories?: ConfigCategory[];
  overwrite: boolean;
}

// 预定义配置项
export const DEFAULT_CONFIGS: Record<ConfigCategory, Partial<SystemConfig>[]> = {
  [ConfigCategory.GENERAL]: [
    {
      key: 'app_name',
      label: '应用名称',
      type: ConfigValueType.STRING,
      defaultValue: 'daloRADIUS',
      description: '系统显示的应用程序名称',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'app_version',
      label: '应用版本',
      type: ConfigValueType.STRING,
      defaultValue: '1.0.0',
      description: '当前应用程序版本号',
      isRequired: false,
      isEditable: false
    },
    {
      key: 'timezone',
      label: '时区',
      type: ConfigValueType.SELECT,
      defaultValue: 'Asia/Shanghai',
      description: '系统默认时区设置',
      isRequired: true,
      isEditable: true,
      options: [
        { label: '北京时间 (UTC+8)', value: 'Asia/Shanghai' },
        { label: '东京时间 (UTC+9)', value: 'Asia/Tokyo' },
        { label: '纽约时间 (UTC-5)', value: 'America/New_York' },
        { label: '伦敦时间 (UTC+0)', value: 'Europe/London' }
      ]
    },
    {
      key: 'language',
      label: '默认语言',
      type: ConfigValueType.SELECT,
      defaultValue: 'zh-CN',
      description: '系统界面默认语言',
      isRequired: true,
      isEditable: true,
      options: [
        { label: '简体中文', value: 'zh-CN' },
        { label: 'English', value: 'en-US' },
        { label: '繁體中文', value: 'zh-TW' },
        { label: '日本語', value: 'ja-JP' }
      ]
    }
  ],
  [ConfigCategory.DATABASE]: [
    {
      key: 'db_host',
      label: '数据库主机',
      type: ConfigValueType.STRING,
      defaultValue: 'localhost',
      description: '数据库服务器地址',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'db_port',
      label: '数据库端口',
      type: ConfigValueType.NUMBER,
      defaultValue: 3306,
      description: '数据库连接端口',
      isRequired: true,
      isEditable: true,
      validation: { min: 1, max: 65535 }
    },
    {
      key: 'db_name',
      label: '数据库名称',
      type: ConfigValueType.STRING,
      defaultValue: 'radius',
      description: 'RADIUS数据库名称',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'db_username',
      label: '数据库用户名',
      type: ConfigValueType.STRING,
      defaultValue: 'radius',
      description: '数据库连接用户名',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'db_password',
      label: '数据库密码',
      type: ConfigValueType.PASSWORD,
      defaultValue: '',
      description: '数据库连接密码',
      isRequired: true,
      isEditable: true
    }
  ],
  [ConfigCategory.EMAIL]: [
    {
      key: 'smtp_host',
      label: 'SMTP服务器',
      type: ConfigValueType.STRING,
      defaultValue: '',
      description: '邮件发送服务器地址',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'smtp_port',
      label: 'SMTP端口',
      type: ConfigValueType.NUMBER,
      defaultValue: 587,
      description: 'SMTP服务器端口',
      isRequired: true,
      isEditable: true
    },
    {
      key: 'smtp_secure',
      label: '启用SSL/TLS',
      type: ConfigValueType.BOOLEAN,
      defaultValue: true,
      description: '是否启用邮件加密传输',
      isRequired: false,
      isEditable: true
    }
  ],
  [ConfigCategory.SECURITY]: [
    {
      key: 'session_timeout',
      label: '会话超时时间',
      type: ConfigValueType.NUMBER,
      defaultValue: 3600,
      description: '用户会话超时时间（秒）',
      isRequired: true,
      isEditable: true,
      validation: { min: 300, max: 86400 }
    },
    {
      key: 'max_login_attempts',
      label: '最大登录尝试次数',
      type: ConfigValueType.NUMBER,
      defaultValue: 5,
      description: '账户锁定前的最大登录失败次数',
      isRequired: true,
      isEditable: true,
      validation: { min: 3, max: 10 }
    }
  ],
  [ConfigCategory.BACKUP]: [],
  [ConfigCategory.LOGGING]: [],
  [ConfigCategory.INTERFACE]: [],
  [ConfigCategory.PERFORMANCE]: [],
  [ConfigCategory.INTEGRATION]: [],
  [ConfigCategory.RADIUS]: []
};

export const CONFIG_CATEGORY_OPTIONS = [
  { label: '常规设置', value: ConfigCategory.GENERAL, icon: 'setting' },
  { label: '数据库配置', value: ConfigCategory.DATABASE, icon: 'database' },
  { label: 'RADIUS配置', value: ConfigCategory.RADIUS, icon: 'wifi' },
  { label: '邮件配置', value: ConfigCategory.EMAIL, icon: 'mail' },
  { label: '安全配置', value: ConfigCategory.SECURITY, icon: 'safety' },
  { label: '备份配置', value: ConfigCategory.BACKUP, icon: 'save' },
  { label: '日志配置', value: ConfigCategory.LOGGING, icon: 'file-text' },
  { label: '界面配置', value: ConfigCategory.INTERFACE, icon: 'layout' },
  { label: '性能配置', value: ConfigCategory.PERFORMANCE, icon: 'dashboard' },
  { label: '集成配置', value: ConfigCategory.INTEGRATION, icon: 'api' }
];