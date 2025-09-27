# daloRADIUS 现代化重构架构设计

## 1. 项目概述

### 1.1 重构目标
将传统PHP架构的daloRADIUS系统重构为现代化的前后端分离架构，实现：
- 轻量化单机部署
- 现代化技术栈
- 高可维护性
- 良好的用户体验

### 1.2 技术栈选择
- **后端**: FastAPI + SQLAlchemy ORM + PostgreSQL
- **前端**: Vue3 + TypeScript + Ant Design Vue + Vite
- **测试**: pytest (TDD驱动开发)
- **部署**: Docker + Docker Compose (单机编排)

## 2. 系统架构设计

### 2.1 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                Nginx (Reverse Proxy)                        │
├─────────────────────┬───────────────────┬───────────────────┤
│                     │                   │                   │
▼                     ▼                   ▼                   ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Vue3 Frontend│ │FastAPI Backend│ │ PostgreSQL │ │   Redis     │
│             │ │             │ │  Database   │ │   Cache     │
│- TypeScript │ │- SQLAlchemy │ │             │ │             │
│- Ant Design │ │- JWT Auth   │ │             │ │             │
│- Pinia      │ │- Pydantic   │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 2.2 模块架构
```
Backend (FastAPI)
├── auth/           # 认证授权模块
├── users/          # 用户管理模块  
├── accounting/     # 计费会计模块
├── nas/            # NAS设备管理
├── hotspots/       # 热点管理
├── billing/        # 账单管理
├── reports/        # 报表统计
└── config/         # 系统配置

Frontend (Vue3)
├── auth/           # 登录认证页面
├── dashboard/      # 仪表板
├── users/          # 用户管理页面
├── accounting/     # 计费统计页面
├── nas/            # 设备管理页面
├── hotspots/       # 热点管理页面
├── billing/        # 账单管理页面
├── reports/        # 报表页面
└── settings/       # 系统设置页面
```

## 3. 数据库设计

### 3.1 核心表结构
基于现有daloRADIUS的MySQL schema，迁移到PostgreSQL：

```sql
-- 用户认证表
CREATE TABLE radcheck (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    attribute VARCHAR(64) NOT NULL,
    op CHAR(2) NOT NULL DEFAULT '==',
    value VARCHAR(253) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户回复属性表
CREATE TABLE radreply (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    attribute VARCHAR(64) NOT NULL,
    op CHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 计费记录表
CREATE TABLE radacct (
    radacctid BIGSERIAL PRIMARY KEY,
    acctsessionid VARCHAR(64) NOT NULL,
    acctuniqueid VARCHAR(32) NOT NULL,
    username VARCHAR(64) NOT NULL,
    realm VARCHAR(64),
    nasipaddress INET NOT NULL,
    nasportid VARCHAR(32),
    nasporttype VARCHAR(32),
    acctstarttime TIMESTAMP WITH TIME ZONE,
    acctupdatetime TIMESTAMP WITH TIME ZONE,
    acctstoptime TIMESTAMP WITH TIME ZONE,
    acctinterval INTEGER,
    acctsessiontime INTEGER,
    acctauthentic VARCHAR(32),
    connectinfo_start VARCHAR(128),
    connectinfo_stop VARCHAR(128),
    acctinputoctets BIGINT,
    acctoutputoctets BIGINT,
    calledstationid VARCHAR(50),
    callingstationid VARCHAR(50),
    acctterminatecause VARCHAR(32),
    servicetype VARCHAR(32),
    framedprotocol VARCHAR(32),
    framedipaddress INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NAS设备表
CREATE TABLE nas (
    id SERIAL PRIMARY KEY,
    nasname VARCHAR(128) NOT NULL UNIQUE,
    shortname VARCHAR(32),
    type VARCHAR(30) DEFAULT 'other',
    ports INTEGER,
    secret VARCHAR(60) NOT NULL,
    server VARCHAR(64),
    community VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户信息表
CREATE TABLE userinfo (
    id SERIAL PRIMARY KEY,
    username VARCHAR(128) NOT NULL UNIQUE,
    firstname VARCHAR(200),
    lastname VARCHAR(200),
    email VARCHAR(200),
    department VARCHAR(200),
    company VARCHAR(200),
    workphone VARCHAR(200),
    homephone VARCHAR(200),
    mobilephone VARCHAR(200),
    address VARCHAR(200),
    city VARCHAR(200),
    state VARCHAR(200),
    country VARCHAR(100),
    zip VARCHAR(200),
    notes TEXT,
    changeuserinfo VARCHAR(128),
    portalloginpassword VARCHAR(128),
    enableportallogin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 操作员表
CREATE TABLE operators (
    id SERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    firstname VARCHAR(32),
    lastname VARCHAR(32),
    title VARCHAR(32),
    department VARCHAR(32),
    company VARCHAR(32),
    phone1 VARCHAR(32),
    phone2 VARCHAR(32),
    email1 VARCHAR(32),
    email2 VARCHAR(32),
    messenger1 VARCHAR(32),
    messenger2 VARCHAR(32),
    notes VARCHAR(128),
    lastlogin TIMESTAMP,
    creationdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creationby VARCHAR(128),
    updatedate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updateby VARCHAR(128)
);
```

## 4. API接口设计

### 4.1 RESTful API规范
采用标准的RESTful设计，所有API统一前缀：`/api/v1`

```yaml
# 认证相关
POST   /api/v1/auth/login          # 用户登录
POST   /api/v1/auth/logout         # 用户登出
POST   /api/v1/auth/refresh        # 刷新Token
GET    /api/v1/auth/me             # 获取当前用户信息

# 用户管理
GET    /api/v1/users               # 获取用户列表
POST   /api/v1/users               # 创建用户
GET    /api/v1/users/{id}          # 获取用户详情
PUT    /api/v1/users/{id}          # 更新用户
DELETE /api/v1/users/{id}          # 删除用户
POST   /api/v1/users/batch         # 批量操作

# 计费会计
GET    /api/v1/accounting/sessions # 获取会话记录
GET    /api/v1/accounting/online   # 获取在线用户
GET    /api/v1/accounting/stats    # 获取统计数据

# NAS设备管理
GET    /api/v1/nas                 # 获取NAS列表
POST   /api/v1/nas                 # 创建NAS
GET    /api/v1/nas/{id}            # 获取NAS详情
PUT    /api/v1/nas/{id}            # 更新NAS
DELETE /api/v1/nas/{id}           # 删除NAS

# 报表统计
GET    /api/v1/reports/users       # 用户报表
GET    /api/v1/reports/traffic     # 流量报表
GET    /api/v1/reports/revenue     # 收入报表
GET    /api/v1/reports/dashboard   # 仪表板数据
```

### 4.2 响应格式标准
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-09-26T10:00:00Z"
}
```

## 5. 前端设计

### 5.1 页面结构
```
App.vue
├── LoginView.vue                 # 登录页面
└── MainLayout.vue               # 主布局
    ├── Header.vue               # 顶部导航
    ├── Sidebar.vue              # 侧边栏菜单
    └── RouterView
        ├── DashboardView.vue    # 仪表板
        ├── UsersView.vue        # 用户管理
        ├── AccountingView.vue   # 计费统计
        ├── NasView.vue          # 设备管理
        ├── ReportsView.vue      # 报表统计
        └── SettingsView.vue     # 系统设置
```

### 5.2 状态管理 (Pinia)
```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false
  }),
  actions: {
    async login(credentials) { ... },
    async logout() { ... },
    async refreshToken() { ... }
  }
})

// stores/users.ts
export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    pagination: { ... }
  }),
  actions: {
    async fetchUsers() { ... },
    async createUser() { ... },
    async updateUser() { ... },
    async deleteUser() { ... }
  }
})
```

## 6. 项目目录结构

```
daloradius-modern/
├── backend/                     # FastAPI后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI应用入口
│   │   ├── api/                # API路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── accounting.py
│   │   │   │   ├── nas.py
│   │   │   │   └── reports.py
│   │   │   └── deps.py         # 依赖注入
│   │   ├── core/               # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # 配置文件
│   │   │   ├── security.py     # 安全相关
│   │   │   └── database.py     # 数据库连接
│   │   ├── db/                 # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # 基础模型
│   │   │   └── session.py      # 数据库会话
│   │   ├── models/             # SQLAlchemy模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── radius.py
│   │   │   ├── nas.py
│   │   │   └── operator.py
│   │   ├── schemas/            # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── accounting.py
│   │   │   └── common.py
│   │   ├── services/           # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   └── accounting_service.py
│   │   ├── utils/              # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py
│   │   │   └── validators.py
│   │   └── tests/              # 测试代码
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_auth.py
│   │       ├── test_users.py
│   │       └── test_accounting.py
│   ├── alembic/                # 数据库迁移
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── requirements.txt         # Python依赖
│   ├── pyproject.toml          # 项目配置
│   └── Dockerfile              # Docker配置
├── frontend/                   # Vue3前端
│   ├── src/
│   │   ├── main.ts             # 入口文件
│   │   ├── App.vue             # 根组件
│   │   ├── components/         # 通用组件
│   │   │   ├── common/
│   │   │   ├── charts/
│   │   │   └── forms/
│   │   ├── views/              # 页面组件
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── users/
│   │   │   ├── accounting/
│   │   │   ├── nas/
│   │   │   ├── reports/
│   │   │   └── settings/
│   │   ├── router/             # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/             # Pinia状态管理
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   └── app.ts
│   │   ├── services/           # API服务
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   └── accounting.ts
│   │   ├── utils/              # 工具函数
│   │   │   ├── request.ts
│   │   │   ├── helpers.ts
│   │   │   └── constants.ts
│   │   ├── types/              # TypeScript类型
│   │   │   ├── api.ts
│   │   │   ├── user.ts
│   │   │   └── common.ts
│   │   └── assets/             # 静态资源
│   │       ├── styles/
│   │       └── images/
│   ├── tests/                  # 前端测试
│   │   ├── unit/
│   │   └── e2e/
│   ├── public/                 # 公共文件
│   ├── package.json            # Node依赖
│   ├── vite.config.ts         # Vite配置
│   ├── tsconfig.json          # TypeScript配置
│   └── Dockerfile             # Docker配置
├── docs/                       # 项目文档
│   ├── api.md                 # API文档
│   ├── deployment.md          # 部署文档
│   └── development.md         # 开发文档
├── docker-compose.yml          # Docker编排
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目说明
```

## 7. 开发流程

### 7.1 TDD开发流程
1. **编写测试** - 先写失败的测试用例
2. **实现功能** - 编写最小化代码让测试通过
3. **重构代码** - 优化代码结构和性能
4. **重复循环** - 继续下一个功能

### 7.2 Git工作流
- `main` - 生产分支
- `develop` - 开发分支  
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

## 8. 部署方案

### 8.1 单机Docker部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: daloradius
      POSTGRES_USER: daloradius
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://daloradius:password@postgres:5432/daloradius
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

## 9. 性能优化

### 9.1 后端优化
- 数据库连接池
- Redis缓存热点数据
- 异步处理长时间任务
- 分页查询大数据集

### 9.2 前端优化
- 路由懒加载
- 组件按需加载
- 图片懒加载
- 打包体积优化

## 10. 安全考虑

### 10.1 认证授权
- JWT Token认证
- RBAC权限控制
- 密码加密存储
- 会话超时机制

### 10.2 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF防护
- 敏感数据加密

---

*本架构设计将作为后续开发的指导文档*