# daloRADIUS 重构项目目录结构

## 完整项目结构

```
daloradius-modern/
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── Makefile
│
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用入口
│   │   ├── config.py                 # 配置管理
│   │   ├── dependencies.py           # 依赖注入
│   │   │
│   │   ├── api/                      # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # API 依赖
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py           # 认证相关
│   │   │   │   ├── users.py          # 用户管理
│   │   │   │   ├── accounting.py     # 计费记录
│   │   │   │   ├── billing.py        # 账单管理
│   │   │   │   ├── nas.py            # NAS 设备
│   │   │   │   ├── reports.py        # 报表统计
│   │   │   │   ├── system.py         # 系统配置
│   │   │   │   └── hotspots.py       # 热点管理
│   │   │   └── middleware.py         # 中间件
│   │   │
│   │   ├── core/                     # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 认证授权
│   │   │   ├── security.py           # 安全相关
│   │   │   ├── exceptions.py         # 异常处理
│   │   │   ├── logging.py            # 日志配置
│   │   │   └── events.py             # 事件处理
│   │   │
│   │   ├── db/                       # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # 基础配置
│   │   │   ├── session.py            # 会话管理
│   │   │   ├── migrations/           # 数据库迁移
│   │   │   │   └── alembic/
│   │   │   └── init_db.py            # 初始化脚本
│   │   │
│   │   ├── models/                   # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # 基础模型类
│   │   │   ├── user.py               # 用户相关模型
│   │   │   ├── radius.py             # RADIUS 相关模型
│   │   │   ├── accounting.py         # 计费记录模型
│   │   │   ├── billing.py            # 账单模型
│   │   │   ├── nas.py                # NAS 设备模型
│   │   │   ├── system.py             # 系统配置模型
│   │   │   └── hotspot.py            # 热点模型
│   │   │
│   │   ├── schemas/                  # Pydantic 模式
│   │   │   ├── __init__.py
│   │   │   ├── common.py             # 通用模式
│   │   │   ├── user.py               # 用户模式
│   │   │   ├── auth.py               # 认证模式
│   │   │   ├── accounting.py         # 计费模式
│   │   │   ├── billing.py            # 账单模式
│   │   │   ├── nas.py                # NAS 模式
│   │   │   ├── reports.py            # 报表模式
│   │   │   └── system.py             # 系统模式
│   │   │
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # 基础服务类
│   │   │   ├── auth_service.py       # 认证服务
│   │   │   ├── user_service.py       # 用户服务
│   │   │   ├── accounting_service.py # 计费服务
│   │   │   ├── billing_service.py    # 账单服务
│   │   │   ├── nas_service.py        # NAS 服务
│   │   │   ├── report_service.py     # 报表服务
│   │   │   ├── system_service.py     # 系统服务
│   │   │   └── notification_service.py # 通知服务
│   │   │
│   │   ├── repositories/             # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # 基础仓储
│   │   │   ├── user_repo.py          # 用户仓储
│   │   │   ├── accounting_repo.py    # 计费仓储
│   │   │   ├── billing_repo.py       # 账单仓储
│   │   │   ├── nas_repo.py           # NAS 仓储
│   │   │   └── system_repo.py        # 系统仓储
│   │   │
│   │   ├── utils/                    # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── crypto.py             # 加密工具
│   │   │   ├── validators.py         # 验证工具
│   │   │   ├── formatters.py         # 格式化工具
│   │   │   ├── exporters.py          # 导出工具
│   │   │   └── radius_client.py      # RADIUS 客户端
│   │   │
│   │   └── tasks/                    # 后台任务
│   │       ├── __init__.py
│   │       ├── celery_app.py         # Celery 配置
│   │       ├── accounting_tasks.py   # 计费任务
│   │       ├── billing_tasks.py      # 账单任务
│   │       ├── report_tasks.py       # 报表任务
│   │       └── cleanup_tasks.py      # 清理任务
│   │
│   ├── tests/                        # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py               # pytest 配置
│   │   ├── test_auth.py              # 认证测试
│   │   ├── test_users.py             # 用户测试
│   │   ├── test_accounting.py        # 计费测试
│   │   ├── test_billing.py           # 账单测试
│   │   ├── test_nas.py               # NAS 测试
│   │   ├── test_reports.py           # 报表测试
│   │   └── integration/              # 集成测试
│   │       ├── test_api_integration.py
│   │       └── test_db_integration.py
│   │
│   ├── scripts/                      # 脚本工具
│   │   ├── migrate_data.py           # 数据迁移
│   │   ├── init_admin.py             # 初始化管理员
│   │   ├── backup_db.py              # 数据库备份
│   │   └── health_check.py           # 健康检查
│   │
│   ├── requirements.txt              # Python 依赖
│   ├── requirements-dev.txt          # 开发依赖
│   ├── Dockerfile                    # Docker 镜像
│   ├── .env.example                  # 环境变量示例
│   ├── alembic.ini                   # 数据库迁移配置
│   ├── pytest.ini                    # 测试配置
│   └── pyproject.toml                # 项目配置
│
├── frontend/                         # Vue 3 前端
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── assets/
│   │
│   ├── src/
│   │   ├── main.ts                   # 应用入口
│   │   ├── App.vue                   # 根组件
│   │   ├── env.d.ts                  # 类型声明
│   │   │
│   │   ├── api/                      # API 调用
│   │   │   ├── index.ts              # API 配置
│   │   │   ├── auth.ts               # 认证API
│   │   │   ├── users.ts              # 用户API
│   │   │   ├── accounting.ts         # 计费API
│   │   │   ├── billing.ts            # 账单API
│   │   │   ├── nas.ts                # NAS API
│   │   │   ├── reports.ts            # 报表API
│   │   │   └── system.ts             # 系统API
│   │   │
│   │   ├── components/               # 通用组件
│   │   │   ├── common/               # 基础组件
│   │   │   │   ├── AppLayout.vue     # 布局组件
│   │   │   │   ├── DataTable.vue     # 数据表格
│   │   │   │   ├── SearchForm.vue    # 搜索表单
│   │   │   │   ├── ExportButton.vue  # 导出按钮
│   │   │   │   └── PageHeader.vue    # 页面头部
│   │   │   │
│   │   │   ├── charts/               # 图表组件
│   │   │   │   ├── LineChart.vue     # 折线图
│   │   │   │   ├── PieChart.vue      # 饼图
│   │   │   │   ├── BarChart.vue      # 柱状图
│   │   │   │   └── GaugeChart.vue    # 仪表盘
│   │   │   │
│   │   │   ├── forms/                # 表单组件
│   │   │   │   ├── UserForm.vue      # 用户表单
│   │   │   │   ├── NasForm.vue       # NAS 表单
│   │   │   │   ├── BillingForm.vue   # 账单表单
│   │   │   │   └── HotspotForm.vue   # 热点表单
│   │   │   │
│   │   │   └── widgets/              # 小部件
│   │   │       ├── StatCard.vue      # 统计卡片
│   │   │       ├── QuickActions.vue  # 快捷操作
│   │   │       ├── RecentActivity.vue # 最近活动
│   │   │       └── SystemStatus.vue  # 系统状态
│   │   │
│   │   ├── views/                    # 页面视图
│   │   │   ├── auth/                 # 认证页面
│   │   │   │   ├── Login.vue         # 登录页
│   │   │   │   ├── Register.vue      # 注册页
│   │   │   │   └── ForgotPassword.vue # 忘记密码
│   │   │   │
│   │   │   ├── dashboard/            # 仪表板
│   │   │   │   ├── Dashboard.vue     # 主仪表板
│   │   │   │   ├── Overview.vue      # 概览
│   │   │   │   └── Statistics.vue    # 统计
│   │   │   │
│   │   │   ├── users/                # 用户管理
│   │   │   │   ├── UserList.vue      # 用户列表
│   │   │   │   ├── UserDetail.vue    # 用户详情
│   │   │   │   ├── UserCreate.vue    # 新建用户
│   │   │   │   └── UserBatch.vue     # 批量操作
│   │   │   │
│   │   │   ├── accounting/           # 计费管理
│   │   │   │   ├── AccountingList.vue # 计费记录
│   │   │   │   ├── ActiveSessions.vue # 活跃会话
│   │   │   │   └── UsageStats.vue    # 使用统计
│   │   │   │
│   │   │   ├── billing/              # 账单管理
│   │   │   │   ├── InvoiceList.vue   # 发票列表
│   │   │   │   ├── PaymentList.vue   # 支付记录
│   │   │   │   ├── BillingPlans.vue  # 计费计划
│   │   │   │   └── Rates.vue         # 费率管理
│   │   │   │
│   │   │   ├── nas/                  # NAS 管理
│   │   │   │   ├── NasList.vue       # NAS 列表
│   │   │   │   ├── NasDetail.vue     # NAS 详情
│   │   │   │   └── NasMonitor.vue    # NAS 监控
│   │   │   │
│   │   │   ├── reports/              # 报表中心
│   │   │   │   ├── ReportCenter.vue  # 报表中心
│   │   │   │   ├── UsageReports.vue  # 使用报表
│   │   │   │   ├── BillingReports.vue # 账单报表
│   │   │   │   └── SystemReports.vue # 系统报表
│   │   │   │
│   │   │   ├── system/               # 系统管理
│   │   │   │   ├── SystemConfig.vue  # 系统配置
│   │   │   │   ├── UserRoles.vue     # 用户角色
│   │   │   │   ├── Logs.vue          # 系统日志
│   │   │   │   └── Backup.vue        # 备份管理
│   │   │   │
│   │   │   └── hotspots/             # 热点管理
│   │   │       ├── HotspotList.vue   # 热点列表
│   │   │       ├── HotspotMap.vue    # 热点地图
│   │   │       └── HotspotDetail.vue # 热点详情
│   │   │
│   │   ├── router/                   # 路由配置
│   │   │   ├── index.ts              # 路由主文件
│   │   │   ├── guards.ts             # 路由守卫
│   │   │   └── routes.ts             # 路由定义
│   │   │
│   │   ├── stores/                   # Pinia 状态管理
│   │   │   ├── index.ts              # 状态管理入口
│   │   │   ├── auth.ts               # 认证状态
│   │   │   ├── user.ts               # 用户状态
│   │   │   ├── system.ts             # 系统状态
│   │   │   └── settings.ts           # 设置状态
│   │   │
│   │   ├── utils/                    # 工具函数
│   │   │   ├── index.ts              # 工具入口
│   │   │   ├── request.ts            # 请求封装
│   │   │   ├── auth.ts               # 认证工具
│   │   │   ├── validators.ts         # 验证工具
│   │   │   ├── formatters.ts         # 格式化工具
│   │   │   ├── constants.ts          # 常量定义
│   │   │   └── permissions.ts        # 权限工具
│   │   │
│   │   ├── types/                    # TypeScript 类型
│   │   │   ├── index.ts              # 类型入口
│   │   │   ├── api.ts                # API 类型
│   │   │   ├── auth.ts               # 认证类型
│   │   │   ├── user.ts               # 用户类型
│   │   │   ├── accounting.ts         # 计费类型
│   │   │   ├── billing.ts            # 账单类型
│   │   │   └── system.ts             # 系统类型
│   │   │
│   │   ├── styles/                   # 样式文件
│   │   │   ├── index.css             # 主样式
│   │   │   ├── variables.css         # CSS 变量
│   │   │   ├── components.css        # 组件样式
│   │   │   └── themes/               # 主题
│   │   │       ├── light.css         # 浅色主题
│   │   │       └── dark.css          # 深色主题
│   │   │
│   │   └── assets/                   # 静态资源
│   │       ├── images/               # 图片资源
│   │       ├── icons/                # 图标资源
│   │       └── fonts/                # 字体资源
│   │
│   ├── tests/                        # 前端测试
│   │   ├── unit/                     # 单元测试
│   │   │   ├── components/           # 组件测试
│   │   │   └── utils/                # 工具测试
│   │   │
│   │   └── e2e/                      # E2E 测试
│   │       ├── auth.spec.ts          # 认证测试
│   │       ├── users.spec.ts         # 用户测试
│   │       └── dashboard.spec.ts     # 仪表板测试
│   │
│   ├── package.json                  # 依赖管理
│   ├── package-lock.json             # 锁定版本
│   ├── tsconfig.json                 # TypeScript 配置
│   ├── vite.config.ts                # Vite 配置
│   ├── tailwind.config.js            # Tailwind 配置
│   ├── .eslintrc.js                  # ESLint 配置
│   ├── .prettierrc                   # Prettier 配置
│   ├── vitest.config.ts              # 测试配置
│   └── Dockerfile                    # Docker 镜像
│
├── shared/                           # 共享代码
│   ├── types/                        # 共享类型定义
│   │   ├── api.ts                    # API 接口类型
│   │   ├── models.ts                 # 模型类型
│   │   └── enums.ts                  # 枚举定义
│   │
│   └── constants/                    # 共享常量
│       ├── api.ts                    # API 常量
│       ├── routes.ts                 # 路由常量
│       └── messages.ts               # 消息常量
│
├── docs/                             # 项目文档
│   ├── README.md                     # 项目说明
│   ├── API.md                        # API 文档
│   ├── DEPLOYMENT.md                 # 部署文档
│   ├── DEVELOPMENT.md                # 开发文档
│   ├── ARCHITECTURE.md               # 架构文档
│   └── MIGRATION.md                  # 迁移文档
│
├── deployment/                       # 部署配置
│   ├── docker/                       # Docker 配置
│   │   ├── backend.Dockerfile        # 后端镜像
│   │   ├── frontend.Dockerfile       # 前端镜像
│   │   └── nginx.conf                # Nginx 配置
│   │
│   ├── k8s/                          # Kubernetes 配置
│   │   ├── namespace.yaml            # 命名空间
│   │   ├── backend-deployment.yaml   # 后端部署
│   │   ├── frontend-deployment.yaml  # 前端部署
│   │   ├── database-deployment.yaml  # 数据库部署
│   │   └── ingress.yaml              # 入口配置
│   │
│   └── scripts/                      # 部署脚本
│       ├── deploy.sh                 # 部署脚本
│       ├── backup.sh                 # 备份脚本
│       └── restore.sh                # 恢复脚本
│
├── monitoring/                       # 监控配置
│   ├── prometheus/                   # Prometheus 配置
│   │   ├── prometheus.yml            # 主配置
│   │   └── rules/                    # 告警规则
│   │
│   ├── grafana/                      # Grafana 配置
│   │   ├── dashboards/               # 仪表板
│   │   └── datasources/              # 数据源
│   │
│   └── alerting/                     # 告警配置
│       ├── alertmanager.yml          # 告警管理器
│       └── templates/                # 告警模板
│
└── tools/                            # 开发工具
    ├── data-migration/               # 数据迁移工具
    │   ├── migrate.py                # 迁移脚本
    │   ├── validate.py               # 验证脚本
    │   └── rollback.py               # 回滚脚本
    │
    ├── load-testing/                 # 性能测试
    │   ├── locustfile.py             # Locust 测试
    │   └── scenarios/                # 测试场景
    │
    └── development/                  # 开发工具
        ├── mock-data.py              # 模拟数据
        ├── db-seeds.py               # 数据种子
        └── api-client.py             # API 客户端
```

## 关键目录说明

### 后端架构特点
- **分层架构**: API -> Service -> Repository -> Model
- **依赖注入**: 使用 FastAPI 的依赖注入系统
- **异步处理**: 支持异步 I/O 和后台任务
- **测试驱动**: 完整的测试覆盖

### 前端架构特点
- **组件化设计**: 可复用的组件库
- **状态管理**: 集中式状态管理
- **类型安全**: 完整的 TypeScript 支持
- **模块化**: 按功能模块组织代码

### 部署架构特点
- **容器化**: Docker 容器化部署
- **微服务**: 支持微服务架构
- **监控完整**: 完整的监控告警体系
- **CI/CD**: 自动化部署流程

这个目录结构遵循现代软件开发的最佳实践，支持团队协作和项目维护。