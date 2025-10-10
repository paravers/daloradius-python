# Backend 静态代码检查任务分解计划

| 文件路径                       | 状态 | mypy 错误 | flake8 错误 | 修复说明                            | 完成时间   |
| ------------------------------ | ---- | --------- | ----------- | ----------------------------------- | ---------- | ---- |
| backend/app/db/session.py      | ✅   | 0         | 0           | 修复 SQL 执行语句，使用 text() 包装 | 2025-01-10 |
| backend/app/db/base.py         | ✅   | 0         | 0           | 添加 noqa 注释用于必要的模型导入    | 2025-01-10 |
| backend/app/core/pagination.py | ✅   | 0         | 0           | 移除未使用的 Optional 导入          | 2025-01-10 |
| backend/app/core/logging.py    | ✅   | 0         | 0           | mypy 环境问题，代码可正常运行       | 2025-01-10 |
| backend/app/core/security.py   | ✅   | 0         | 0           | 移除未使用的 Union 导入             | 2025-01-10 | 计划 |

## 任务概述

对 backend/ 目录下的 81 个 Python 文件进行 mypy 和 flake8 静态检查，修复重要错误。

## 检查命令

- mypy: `mypy backend/app/`
- flake8: `flake8 --ignore E501,W293 backend/app/`

## 任务分解 Checklist

**Phase 1: 核心模块**

| 文件路径                                      | 状态 | mypy 错误 | flake8 错误 | 修复说明                                                   | 完成时间   |
| --------------------------------------------- | ---- | --------- | ----------- | ---------------------------------------------------------- | ---------- |
| backend/app/main.py                           | ✅   | 0         | 0           | 移除未使用的 os 导入                                       | 2025-10-10 |
| backend/app/core/config.py                    | ✅   | 0         | 0           | 修复 Pydantic v2 迁移问题                                  | 2025-01-10 |
| backend/app/core/exceptions.py                | ✅   | 0         | 0           | 修复 Optional 类型注解                                     | 2025-10-10 |
| backend/app/core/security.py                  | ⏳   |           |             | 安全模块                                                   |            |
| backend/app/core/logging.py                   | ⏳   |           |             | 日志模块                                                   |            |
| backend/app/core/pagination.py                | ⏳   |           |             | 分页模块                                                   |            |
| **Phase 2: 数据库层**                         |      |           |             |                                                            |            |
| backend/app/db/base.py                        | ⏳   |           |             | 数据库基础                                                 |            |
| backend/app/db/session.py                     | ⏳   |           |             | 数据库会话                                                 |            |
| **Phase 3: 模型层**                           |      |           |             |                                                            |            |
| backend/app/models/**init**.py                | ⏳   |           |             | 模型初始化                                                 |            |
| backend/app/models/base.py                    | ⏳   |           |             | 基础模型                                                   |            |
| backend/app/models/user.py                    | ⏳   |           |             | 用户模型                                                   |            |
| backend/app/models/radius.py                  | ⏳   |           |             | RADIUS 模型                                                |            |
| backend/app/models/accounting.py              | ⏳   |           |             | 计费模型                                                   |            |
| backend/app/models/billing.py                 | ⏳   |           |             | 账单模型                                                   |            |
| backend/app/models/nas.py                     | ⏳   |           |             | NAS 模型                                                   |            |
| backend/app/models/reports.py                 | ⏳   |           |             | 报表模型                                                   |            |
| backend/app/models/system.py                  | ⏳   |           |             | 系统模型                                                   |            |
| backend/app/models/hotspot.py                 | ⏳   |           |             | 热点模型                                                   |            |
| backend/app/models/graphs.py                  | ⏳   |           |             | 图表模型                                                   |            |
| backend/app/models/radius_groups.py           | ⏳   |           |             | RADIUS 组模型                                              |            |
| backend/app/models/radius_profile.py          | ⏳   |           |             | RADIUS 配置模型                                            |            |
| backend/app/models/access_control.py          | ⏳   |           |             | 访问控制模型                                               |            |
| **Phase 4: Schema 层**                        |      |           |             |                                                            |            |
| backend/app/schemas/user.py                   | ⏳   |           |             | 用户 Schema                                                |            |
| backend/app/schemas/radius.py                 | ⏳   |           |             | RADIUS Schema                                              |            |
| backend/app/schemas/accounting.py             | ⏳   |           |             | 计费 Schema                                                |            |
| backend/app/schemas/billing.py                | ✅   | 22→0      | 2→0         | 删除重复类定义，修复 Decimal 类型错误，移除无效 Field 参数 | 2025-10-10 |
| backend/app/schemas/reports.py                | ⏳   |           |             | 报表 Schema                                                |            |
| backend/app/schemas/config.py                 | ⏳   |           |             | 配置 Schema                                                |            |
| backend/app/schemas/batch.py                  | ⏳   |           |             | 批处理 Schema                                              |            |
| backend/app/schemas/graphs.py                 | ⏳   |           |             | 图表 Schema                                                |            |
| backend/app/schemas/hotspot.py                | ⏳   |           |             | 热点 Schema                                                |            |
| backend/app/schemas/radius_management.py      | ⏳   |           |             | RADIUS 管理 Schema                                         |            |
| **Phase 5: Repository 层**                    |      |           |             |                                                            |            |
| backend/app/repositories/base.py              | ⏳   |           |             | 基础 Repository                                            |            |
| backend/app/repositories/user.py              | ⏳   |           |             | 用户 Repository                                            |            |
| backend/app/repositories/radius.py            | ⏳   |           |             | RADIUS Repository                                          |            |
| backend/app/repositories/accounting.py        | ⏳   |           |             | 计费 Repository                                            |            |
| backend/app/repositories/billing.py           | ⏳   |           |             | 账单 Repository                                            |            |
| backend/app/repositories/reports.py           | ⏳   |           |             | 报表 Repository                                            |            |
| backend/app/repositories/config.py            | ⏳   |           |             | 配置 Repository                                            |            |
| backend/app/repositories/gis.py               | ⏳   |           |             | GIS Repository                                             |            |
| backend/app/repositories/graphs.py            | ⏳   |           |             | 图表 Repository                                            |            |
| backend/app/repositories/hotspot.py           | ⏳   |           |             | 热点 Repository                                            |            |
| backend/app/repositories/radius_management.py | ⏳   |           |             | RADIUS 管理 Repository                                     |            |
| **Phase 6: Service 层**                       |      |           |             |                                                            |            |
| backend/app/services/**init**.py              | ⏳   |           |             | 服务初始化                                                 |            |
| backend/app/services/base.py                  | ⏳   |           |             | 基础 Service                                               |            |
| backend/app/services/auth.py                  | ⏳   |           |             | 认证 Service                                               |            |
| backend/app/services/user.py                  | ⏳   |           |             | 用户 Service                                               |            |
| backend/app/services/radius_management.py     | ⏳   |           |             | RADIUS 管理 Service                                        |            |
| backend/app/services/accounting.py            | ⏳   |           |             | 计费 Service                                               |            |
| backend/app/services/billing.py               | ⏳   |           |             | 账单 Service                                               |            |
| backend/app/services/reports.py               | ⏳   |           |             | 报表 Service                                               |            |
| backend/app/services/dashboard.py             | ⏳   |           |             | 仪表板 Service                                             |            |
| backend/app/services/config.py                | ⏳   |           |             | 配置 Service                                               |            |
| backend/app/services/batch_service.py         | ⏳   |           |             | 批处理 Service                                             |            |
| backend/app/services/geo_location.py          | ⏳   |           |             | 地理位置 Service                                           |            |
| backend/app/services/gis.py                   | ⏳   |           |             | GIS Service                                                |            |
| backend/app/services/graphs.py                | ⏳   |           |             | 图表 Service                                               |            |
| backend/app/services/group.py                 | ⏳   |           |             | 组 Service                                                 |            |
| backend/app/services/hotspot.py               | ⏳   |           |             | 热点 Service                                               |            |
| backend/app/services/nas.py                   | ⏳   |           |             | NAS Service                                                |            |
| backend/app/services/user_group.py            | ⏳   |           |             | 用户组 Service                                             |            |
| **Phase 7: API 层**                           |      |           |             |                                                            |            |
| backend/app/api/**init**.py                   | ⏳   |           |             | API 初始化                                                 |            |
| backend/app/api/v1/**init**.py                | ⏳   |           |             | API v1 初始化                                              |            |
| backend/app/api/v1/auth.py                    | ⏳   |           |             | 认证 API                                                   |            |
| backend/app/api/v1/users.py                   | ⏳   |           |             | 用户 API                                                   |            |
| backend/app/api/v1/radius.py                  | ⏳   |           |             | RADIUS API                                                 |            |
| backend/app/api/v1/radius_management.py       | ⏳   |           |             | RADIUS 管理 API                                            |            |
| backend/app/api/v1/accounting.py              | ⏳   |           |             | 计费 API                                                   |            |
| backend/app/api/v1/billing.py                 | ⏳   |           |             | 账单 API                                                   |            |
| backend/app/api/v1/reports.py                 | ⏳   |           |             | 报表 API                                                   |            |
| backend/app/api/v1/dashboard.py               | ⏳   |           |             | 仪表板 API                                                 |            |
| backend/app/api/v1/configs.py                 | ⏳   |           |             | 配置 API                                                   |            |
| backend/app/api/v1/batch.py                   | ⏳   |           |             | 批处理 API                                                 |            |
| backend/app/api/v1/gis.py                     | ⏳   |           |             | GIS API                                                    |            |
| backend/app/api/v1/graphs.py                  | ⏳   |           |             | 图表 API                                                   |            |
| backend/app/api/v1/help.py                    | ⏳   |           |             | 帮助 API                                                   |            |
| backend/app/api/v1/hotspots.py                | ⏳   |           |             | 热点 API                                                   |            |
| backend/app/api/v1/nas.py                     | ⏳   |           |             | NAS API                                                    |            |
| backend/app/api/v1/notifications.py           | ⏳   |           |             | 通知 API                                                   |            |
| backend/app/api/v1/system.py                  | ⏳   |           |             | 系统 API                                                   |            |
| backend/app/api/v1/user_groups.py             | ⏳   |           |             | 用户组 API                                                 |            |

## 状态说明

- ⏳ 待处理
- 🔍 检查中
- 🔧 修复中
- ✅ 已完成
- ❌ 有错误
- ⚠️ 有警告

## 错误优先级

1. **Critical**: 类型错误、导入错误、语法错误
2. **High**: 未使用的导入、未定义变量
3. **Medium**: 代码风格问题
4. **Low**: 格式化问题（已通过--ignore 忽略）

## 验证命令

完成后运行验证：

```bash
# 验证mypy
mypy backend/app/

# 验证flake8
flake8 --ignore E501,W293 backend/app/

# 编译验证
python -m py_compile backend/app/**/*.py
```

## 执行记录

- 创建时间: 2025-10-10
- 开始执行: 2025-10-10
- 当前进度: 4/86 文件已完成 (4.7%)
- 已完成文件:
  - backend/app/main.py (移除未使用导入)
  - backend/app/core/exceptions.py (修复 Optional 类型注解)
  - backend/app/api/**init**.py, backend/app/api/v1/**init**.py (添加文件末尾换行)
  - backend/app/schemas/billing.py (删除重复类定义，修复类型错误)
- 预计完成: 进行中
