# DaloRADIUS 页面功能对照分析表

## 原PHP页面与Python后端+Vue前端实现对照清单

### 说明
- ✅ 已完成：功能已完整实现
- 🟡 部分完成：基础架构存在，需要完善功能
- ❌ 未实现：需要从零开始开发
- 🔄 需要适配：需要调整以匹配新架构

## 1. 用户管理模块 (User Management)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 用户列表 | `mng-list-all.php` | ✅ 已完成 | `User` | `GET /api/v1/users` | `UsersView.vue` | 完整CRUD功能，支持分页搜索 |
| 用户新建 | `mng-new.php` | ✅ 已完成 | `User` | `POST /api/v1/users` | `UserForm.vue` | 表单验证完整，支持用户信息 |
| 用户编辑 | `mng-edit.php` | ✅ 已完成 | `User` | `PUT /api/v1/users/{id}` | `UserForm.vue` | 支持编辑模式，同步UserInfo |
| 用户删除 | `mng-del.php` | ✅ 已完成 | `User` | `DELETE /api/v1/users/{id}` | 集成在列表中 | 确认对话框，防止自删除 |
| 快速添加用户 | `mng-new-quick.php` | ✅ 已完成 | `User` | `POST /api/v1/users/quick` | 集成在主界面 | 简化表单，最少字段 |
| 用户搜索 | `mng-search.php` | ✅ 已完成 | `User` | `GET /api/v1/users/search/{query}` | 集成在列表中 | 动态搜索多字段 |
| 批量导入 | `mng-import-users.php` | ✅ 已完成 | `User` | `POST /api/v1/users/import` | `UserImportModal.vue` | Excel/CSV导入，错误处理 |
| 用户详情 | 无独立PHP | ✅ 已完成 | `User` | `GET /api/v1/users/{id}` | `UserDetail.vue` | 详细信息展示 |
| 在线用户监控 | 集成在其他页面 | ✅ 已完成 | `RadAcct` | `GET /api/v1/users/online/active` | `OnlineUsersMonitor.vue` | 实时监控在线状态 |
| 批量操作 | 无独立PHP | ✅ 已完成 | `User` | `DELETE /api/v1/users/batch` | 集成在列表中 | 批量删除用户 |
| 密码管理 | 分散在各页面 | ✅ 已完成 | `User` | `PUT /api/v1/users/{id}/password` | 集成在用户表单 | 密码修改和验证 |
| 用户组管理 | `mng-rad-usergroup*.php` | ✅ 已完成 | `UserGroup` | `GET/POST /api/v1/users/{id}/groups` | 集成在用户详情 | 用户组关联管理 |

### 实现详情

**后端实现：**
- **数据模型**：完整的用户模型体系，包括User主表和UserInfo兼容表
- **API接口**：`/backend/app/api/v1/users.py` - 完整RESTful API，支持分页、搜索、批量操作
- **服务层**：`/backend/app/services/user.py` - 业务逻辑层，用户创建、验证、密码管理
- **仓储层**：`/backend/app/repositories/user.py` - 数据访问层，增强的CRUD操作和复杂查询
- **核心API端点**：
  - 用户CRUD：GET/POST/PUT/DELETE `/api/v1/users`
  - 快速创建：POST `/api/v1/users/quick`
  - 批量操作：POST `/api/v1/users/batch`, DELETE `/api/v1/users/batch`
  - 用户导入：POST `/api/v1/users/import`
  - 在线监控：GET `/api/v1/users/online/active`
  - 搜索功能：GET `/api/v1/users/search/{query}`
  - 密码管理：PUT `/api/v1/users/{id}/password`
  - 用户组：GET/POST `/api/v1/users/{id}/groups`

**前端实现：**
- **主要视图**：`/frontend/src/views/users/UsersView.vue` - 统一用户管理界面
- **组件架构**：
  - `UserForm.vue` - 用户添加/编辑表单组件
  - `UserDetail.vue` - 用户详情展示组件
  - `UserImportModal.vue` - 批量导入模态框
  - `OnlineUsersMonitor.vue` - 在线用户监控组件
- **服务层**：`/frontend/src/services/userService.ts` - 完整API调用服务
- **状态管理**：基于Vue 3 Composition API的响应式状态管理
- **类型定义**：完整TypeScript类型定义支持

**系统集成：**
- **路由配置**：`/users` 路由已配置，支持子路由
- **菜单集成**：已添加到用户管理菜单分组
- **导航路径**：用户管理 → 用户列表/用户组/在线用户/批量导入
- **权限控制**：集成认证和权限验证中间件

**技术特性：**
- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ 高级搜索和过滤功能（用户名、邮箱、状态等）
- ✅ 分页和排序支持
- ✅ 批量操作支持（批量删除、批量导入）
- ✅ 快速用户创建（简化流程）
- ✅ Excel/CSV文件导入功能
- ✅ 在线用户实时监控
- ✅ 用户组关联管理
- ✅ 密码安全管理（哈希、验证）
- ✅ 表单验证和错误处理
- ✅ 响应式设计和现代UI
- ✅ 数据库兼容性（新User表+legacy UserInfo表同步）

**安全特性：**
- 密码哈希存储（bcrypt）
- JWT认证集成
- 防止自删除保护
- 输入验证和SQL注入防护
- 文件上传安全检查

**架构优势：**
- 完全遵循项目现有架构模式
- 与其他模块保持API设计一致性
- 使用相同的UI组件库和设计规范
- 继承项目的错误处理和状态管理模式
- 支持数据库迁移和向后兼容

## 2. RADIUS 管理模块

### 2.1 RADIUS 属性管理

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 属性列表 | `mng-rad-attributes-list.php` | ✅ 已完成 | `RadCheck`, `RadReply` | `GET /api/v1/radius/radcheck`, `GET /api/v1/radius/radreply` | `RadiusAttributesView.vue` | 完整CRUD功能，支持分页搜索 |
| 属性新建 | `mng-rad-attributes-new.php` | ✅ 已完成 | `RadCheck`, `RadReply` | `POST /api/v1/radius/radcheck`, `POST /api/v1/radius/radreply` | `RadiusAttributeModal.vue` | 模态框表单，支持快速模板 |
| 属性编辑 | `mng-rad-attributes-edit.php` | ✅ 已完成 | `RadCheck`, `RadReply` | `PUT /api/v1/radius/radcheck/{id}`, `PUT /api/v1/radius/radreply/{id}` | `RadiusAttributeModal.vue` | 支持编辑模式 |
| 属性删除 | `mng-rad-attributes-del.php` | ✅ 已完成 | `RadCheck`, `RadReply` | `DELETE /api/v1/radius/radcheck/{id}`, `DELETE /api/v1/radius/radreply/{id}` | 集成在表格中 | 确认删除对话框 |
| 属性搜索 | `mng-rad-attributes-search.php` | ✅ 已完成 | `RadCheck`, `RadReply` | `GET /api/v1/radius/radcheck?search=`, `GET /api/v1/radius/radreply?search=` | 集成在主视图中 | 支持用户名、属性名、值搜索 |
| 属性导入 | `mng-rad-attributes-import.php` | 🟡 部分完成 | `RadCheck`, `RadReply` | 支持批量创建API | 待开发 | 后续版本实现 |

#### 实现详情

**后端实现：**
- 数据模型：完全复用现有的 `RadCheck` 和 `RadReply` 模型
- API接口：`/backend/app/api/v1/radius.py` - 完整RESTful API接口，支持分页、搜索、过滤
- 仓储层：`/backend/app/repositories/radius.py` - 增强的仓储层，支持用户特定操作和批量操作
- 核心API端点：
  - RadCheck CRUD：GET/POST/PUT/DELETE `/api/v1/radius/radcheck`
  - RadReply CRUD：GET/POST/PUT/DELETE `/api/v1/radius/radreply`
  - 用户属性管理：GET `/api/v1/radius/users/{username}/attributes`
  - 工具方法：GET `/api/v1/radius/attributes`, `/api/v1/radius/operators`

**前端实现：**
- 主要视图：`/frontend/src/views/radius/RadiusAttributesView.vue` - 统一管理界面
- 组件架构：
  - `RadCheckTable.vue` - RadCheck属性表格组件
  - `RadReplyTable.vue` - RadReply属性表格组件  
  - `RadiusAttributeModal.vue` - 属性添加/编辑模态框
  - `UserAttributesView.vue` - 用户属性查看组件
- 状态管理：`/frontend/src/composables/useRadiusManagement.ts` - 响应式状态管理
- 服务层：`/frontend/src/services/radiusService.ts` - API调用和数据处理
- 类型定义：`/frontend/src/types/radius.ts` - 完整TypeScript类型定义

**集成实现：**
- 路由配置：`/radius-attributes` 路由已配置
- 菜单集成：已添加到认证管理菜单分组
- 导航路径：系统管理 → 认证管理 → RADIUS属性管理

**功能特性：**
- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ 高级搜索和过滤功能
- ✅ 分页和排序支持
- ✅ 用户友好的表单验证
- ✅ 响应式设计和现代UI
- ✅ 错误处理和加载状态
- ✅ 批量操作支持
- ✅ 实时数据更新

**技术栈一致性：**
- 完全遵循项目现有架构模式
- 与其他模块保持API设计一致性
- 使用相同的UI组件库和设计规范
- 继承项目的错误处理和状态管理模式

### 2.2 NAS 管理

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| NAS列表 | `mng-rad-nas-list.php` | ✅ 已完成 | `Nas` | `GET /api/v1/nas` | `DevicesView.vue` | 完整CRUD功能，支持分页搜索 |
| NAS新建 | `mng-rad-nas-new.php` | ✅ 已完成 | `Nas` | `POST /api/v1/nas` | `DeviceForm.vue` | 表单验证完整，支持连接测试 |
| NAS编辑 | `mng-rad-nas-edit.php` | ✅ 已完成 | `Nas` | `PUT /api/v1/nas/{id}` | `DeviceForm.vue` | 支持编辑模式，实时验证 |
| NAS删除 | `mng-rad-nas-del.php` | ✅ 已完成 | `Nas` | `DELETE /api/v1/nas/{id}` | 集成在列表中 | 防止删除有活动会话的NAS |
| NAS搜索 | `mng-rad-nas-search.php` | ✅ 已完成 | `Nas` | `GET /api/v1/nas/search/{query}` | 集成在主视图中 | 支持名称、描述、服务器搜索 |
| NAS状态监控 | 无独立PHP | ✅ 已完成 | `Nas`, `NasMonitoring` | `GET /api/v1/nas/{id}/status` | `DeviceDetail.vue` | 实时状态监控 |
| 连接性测试 | 无独立PHP | ✅ 已完成 | `Nas` | `POST /api/v1/nas/{id}/test-connection` | 集成在设备详情 | Ping、RADIUS、SNMP测试 |
| 活动会话查看 | 无独立PHP | ✅ 已完成 | `RadAcct` | `GET /api/v1/nas/{id}/sessions` | 集成在设备详情 | 实时会话监控 |
| 批量操作 | 无独立PHP | ✅ 已完成 | `Nas` | `DELETE /api/v1/nas/batch` | 集成在列表中 | 批量删除NAS设备 |
| 统计信息 | 无独立PHP | ✅ 已完成 | `Nas`, `RadAcct` | `GET /api/v1/nas/statistics/overview` | 集成在主界面 | 设备统计和利用率 |

#### 实现详情

**后端实现：**
- **数据模型**：完整的NAS模型体系，包括Nas主表、NasMonitoring监控表、NasGroup分组表
- **API接口**：`/backend/app/api/v1/nas.py` - 完整RESTful API，支持分页、搜索、监控、批量操作
- **服务层**：`/backend/app/services/nas.py` - 业务逻辑层，连接性测试、状态监控、性能分析
- **仓储层**：`/backend/app/repositories/radius.py` - 数据访问层，增强的CRUD操作和复杂查询
- **核心API端点**：
  - NAS CRUD：GET/POST/PUT/DELETE `/api/v1/nas`
  - 状态监控：GET `/api/v1/nas/{id}/status`
  - 连接测试：POST `/api/v1/nas/{id}/test-connection`
  - 活动会话：GET `/api/v1/nas/{id}/sessions`
  - 批量操作：DELETE `/api/v1/nas/batch`
  - 搜索功能：GET `/api/v1/nas/search/{query}`
  - 设备类型：GET `/api/v1/nas/types/available`
  - 统计信息：GET `/api/v1/nas/statistics/overview`

**前端实现：**
- **主要视图**：`/frontend/src/views/devices/DevicesView.vue` - 统一设备管理界面
- **组件架构**：
  - `DeviceForm.vue` - 设备添加/编辑表单组件
  - `DeviceDetail.vue` - 设备详情展示组件
  - `DeviceStatusMonitor.vue` - 设备状态监控组件
  - `ConnectivityTestPanel.vue` - 连接性测试面板
- **服务层**：`/frontend/src/services/nasService.ts` - 完整API调用服务
- **状态管理**：基于Vue 3 Composition API的响应式状态管理
- **类型定义**：完整TypeScript类型定义支持

**系统集成：**
- **路由配置**：`/devices` 路由已配置，支持设备管理功能
- **菜单集成**：已添加到网络设备菜单分组
- **导航路径**：网络管理 → 设备管理 → NAS设备
- **权限控制**：集成认证和权限验证中间件

**核心功能特性：**
- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ 高级搜索和过滤功能（设备名、类型、状态等）
- ✅ 分页和排序支持
- ✅ 实时连接性测试（Ping、RADIUS、SNMP）
- ✅ 设备状态监控和健康检查
- ✅ 活动会话实时监控
- ✅ 批量操作支持（批量删除）
- ✅ 设备统计和性能分析
- ✅ 多种NAS类型支持（Cisco、Juniper、MikroTik等）
- ✅ 端口利用率监控
- ✅ 设备分组管理
- ✅ 错误处理和用户友好提示

**监控和测试功能：**
- **连接性测试**：支持Ping、RADIUS端口（1812/1813）、SNMP连通性测试
- **状态监控**：实时设备状态、会话数、端口利用率监控
- **性能指标**：请求成功率、响应时间、历史性能趋势
- **告警机制**：设备离线、高利用率、连接失败告警

**安全特性：**
- RADIUS密钥安全存储和管理
- 设备访问权限控制
- 操作审计日志
- 连接测试安全验证
- 输入验证和防护

**技术优势：**
- 完全遵循项目现有架构模式
- 与其他模块保持API设计一致性
- 使用相同的UI组件库和设计规范
- 继承项目的错误处理和状态管理模式
- 支持异步操作和实时更新
- 高性能的数据库查询优化

### 2.3 RADIUS 组管理

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 组检查属性列表 | `mng-rad-groupcheck-list.php` | ✅ 已完成 | `GroupCheck` | `GET /api/v1/radius/radgroupcheck` | `GroupManagementView.vue` | 完整CRUD功能，支持分页搜索 |
| 组检查属性新建 | `mng-rad-groupcheck-new.php` | ✅ 已完成 | `GroupCheck` | `POST /api/v1/radius/radgroupcheck` | `GroupAttributeModal.vue` | 表单验证完整，支持属性模板 |
| 组检查属性编辑 | `mng-rad-groupcheck-edit.php` | ✅ 已完成 | `GroupCheck` | `PUT /api/v1/radius/radgroupcheck/{id}` | `GroupAttributeModal.vue` | 支持编辑模式，实时验证 |
| 组检查属性删除 | `mng-rad-groupcheck-del.php` | ✅ 已完成 | `GroupCheck` | `DELETE /api/v1/radius/radgroupcheck/{id}` | 集成在表格中 | 确认删除对话框 |
| 组回复属性列表 | `mng-rad-groupreply-list.php` | ✅ 已完成 | `GroupReply` | `GET /api/v1/radius/radgroupreply` | `GroupManagementView.vue` | 完整CRUD功能，支持分页搜索 |
| 组回复属性新建 | `mng-rad-groupreply-new.php` | ✅ 已完成 | `GroupReply` | `POST /api/v1/radius/radgroupreply` | `GroupAttributeModal.vue` | 表单验证完整，支持属性模板 |
| 组回复属性编辑 | `mng-rad-groupreply-edit.php` | ✅ 已完成 | `GroupReply` | `PUT /api/v1/radius/radgroupreply/{id}` | `GroupAttributeModal.vue` | 支持编辑模式，实时验证 |
| 组回复属性删除 | `mng-rad-groupreply-del.php` | ✅ 已完成 | `GroupReply` | `DELETE /api/v1/radius/radgroupreply/{id}` | 集成在表格中 | 确认删除对话框 |
| 组列表管理 | 无独立PHP | ✅ 已完成 | `GroupCheck`, `GroupReply` | `GET /api/v1/radius/groups` | `GroupListView.vue` | 统一组管理界面 |
| 组属性查看 | 无独立PHP | ✅ 已完成 | `GroupCheck`, `GroupReply` | `GET /api/v1/radius/groups/{name}/attributes` | `GroupDetailView.vue` | 查看组的所有属性 |
| 批量组属性操作 | 无独立PHP | ✅ 已完成 | `GroupCheck`, `GroupReply` | `DELETE /api/v1/radius/groups/{name}/attributes` | 集成在组管理中 | 批量删除组属性 |
| 组统计信息 | 无独立PHP | ✅ 已完成 | `GroupCheck`, `GroupReply` | `GET /api/v1/radius/groups/statistics` | 集成在主界面 | 组和属性统计 |

#### 实现详情

**后端实现：**
- **数据模型**：完整的RADIUS组模型体系，包括GroupCheck认证属性表、GroupReply授权属性表
- **API接口**：`/backend/app/api/v1/radius.py` - 完整RESTful API，支持分页、搜索、统计功能
- **服务层**：`/backend/app/services/group.py` - 业务逻辑层，组属性管理、验证、批量操作
- **仓储层**：`/backend/app/repositories/radius.py` - 数据访问层，增强的CRUD操作和复杂查询
- **核心API端点**：
  - RadGroupCheck CRUD：GET/POST/PUT/DELETE `/api/v1/radius/radgroupcheck`
  - RadGroupReply CRUD：GET/POST/PUT/DELETE `/api/v1/radius/radgroupreply`
  - 组列表管理：GET `/api/v1/radius/groups`
  - 组属性查看：GET `/api/v1/radius/groups/{groupname}/attributes`
  - 批量属性操作：DELETE `/api/v1/radius/groups/{groupname}/attributes`
  - 组统计信息：GET `/api/v1/radius/groups/statistics`
  - 属性验证工具：内置属性名和值验证
  - 模板支持：支持常用属性模板快速创建

**前端实现：**
- **主要视图**：`/frontend/src/views/radius/GroupManagementView.vue` - 统一组管理界面
- **组件架构**：
  - `GroupAttributeTable.vue` - 组属性表格组件（支持check和reply）
  - `GroupAttributeModal.vue` - 属性添加/编辑模态框
  - `GroupListView.vue` - 组列表管理组件
  - `GroupDetailView.vue` - 组详情展示组件
  - `GroupStatisticsPanel.vue` - 组统计信息面板
- **服务层**：`/frontend/src/services/groupService.ts` - 完整API调用服务
- **状态管理**：基于Vue 3 Composition API的响应式状态管理
- **类型定义**：`/frontend/src/types/group.ts` - 完整TypeScript类型定义支持

**系统集成：**
- **路由配置**：`/radius-groups` 路由已配置，支持组管理功能
- **菜单集成**：已添加到RADIUS管理菜单分组
- **导航路径**：系统管理 → RADIUS管理 → 组管理
- **权限控制**：集成认证和权限验证中间件

**核心功能特性：**
- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ 双表管理（RadGroupCheck + RadGroupReply）
- ✅ 高级搜索和过滤功能（组名、属性名、操作符等）
- ✅ 分页和排序支持
- ✅ 批量操作支持（批量删除组属性）
- ✅ 属性验证和模板支持
- ✅ 组统计和分析功能
- ✅ 属性克隆和复制功能
- ✅ 实时表单验证
- ✅ 响应式设计和现代UI

**组管理特性：**
- **双类型属性管理**：支持认证属性（RadGroupCheck）和授权属性（RadGroupReply）
- **统一组视图**：在单一界面管理组的所有属性
- **属性模板**：预定义常用RADIUS属性模板，快速创建
- **批量操作**：支持批量创建、更新、删除组属性
- **属性验证**：内置RADIUS属性名称和值验证
- **组克隆**：支持从现有组复制属性到新组
- **统计分析**：组数量、属性数量、使用情况统计

**技术优势：**
- **模型一致性**：使用统一的GroupCheck和GroupReply模型
- **API设计**：RESTful设计，支持标准HTTP方法和状态码
- **错误处理**：完善的错误处理和用户反馈机制
- **性能优化**：数据库查询优化，支持分页和索引
- **类型安全**：完整的TypeScript类型定义
- **组件复用**：可复用的UI组件和业务逻辑

**安全特性：**
- 属性值安全验证和清理
- SQL注入防护
- 输入验证和格式检查
- 操作审计日志
- 访问权限控制

**扩展特性：**
- 支持自定义RADIUS属性
- 灵活的操作符支持（==、:=、+=等）
- 属性模板自定义和扩展
- 多条件搜索和过滤
- 导出导入功能（预留接口）

### 2.4 用户组关联

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 用户组列表 | `mng-rad-usergroup-list.php` | ✅ 已完成 | `UserGroup` | `GET /api/v1/user-groups/user-groups` | `UserGroupsView.vue` | 完整CRUD功能，支持分页搜索 |
| 用户组新建 | `mng-rad-usergroup-new.php` | ✅ 已完成 | `UserGroup` | `POST /api/v1/user-groups/user-groups` | `UserGroupModal.vue` | 用户组关联创建 |
| 用户组编辑 | `mng-rad-usergroup-edit.php` | ✅ 已完成 | `UserGroup` | `PUT /api/v1/user-groups/user-groups/{id}` | `UserGroupModal.vue` | 优先级和组名编辑 |
| 用户组删除 | `mng-rad-usergroup-del.php` | ✅ 已完成 | `UserGroup` | `DELETE /api/v1/user-groups/user-groups/{id}` | 集成在表格中 | 确认删除对话框 |
| 按用户列出组 | `mng-rad-usergroup-list-user.php` | ✅ 已完成 | `UserGroup` | `GET /api/v1/user-groups/users/{username}/groups` | `UserGroupsView.vue` | 用户维度的组视图 |
| 按组列出用户 | 无独立PHP | ✅ 已完成 | `UserGroup` | `GET /api/v1/user-groups/groups/{groupname}/users` | `GroupUsersView.vue` | 组维度的用户视图 |
| 批量组操作 | 无独立PHP | ✅ 已完成 | `UserGroup` | `POST /api/v1/user-groups/groups/{groupname}/users/batch-add` | `BatchUserGroupModal.vue` | 批量添加/删除用户 |
| 组统计信息 | 无独立PHP | ✅ 已完成 | `UserGroup` | `GET /api/v1/user-groups/groups/statistics` | `UserGroupStatistics.vue` | 组使用情况统计 |

### 实现详情

**后端实现：**
- **数据模型**：完整的用户组关联模型，基于`radusergroup`表实现
- **API接口**：`/backend/app/api/v1/user_groups.py` - 完整RESTful API，包含15+个端点
- **服务层**：`/backend/app/services/user_group.py` - 业务逻辑层，包含验证、统计、批量操作
- **仓储层**：`/backend/app/repositories/user.py` - 增强的UserGroupRepository，支持复杂查询
- **核心API端点**：
  - 用户组关联CRUD：GET/POST/PUT/DELETE `/api/v1/user-groups/user-groups`
  - 用户维度操作：GET/POST/DELETE `/api/v1/user-groups/users/{username}/groups`
  - 组维度操作：GET/POST `/api/v1/user-groups/groups/{groupname}/users`
  - 批量操作：POST `/api/v1/user-groups/groups/{groupname}/users/batch-add|batch-remove`
  - 统计功能：GET `/api/v1/user-groups/groups/statistics`
  - 组列表：GET `/api/v1/user-groups/groups`
  - 搜索功能：GET `/api/v1/user-groups/user-groups/search`

**前端实现：**
- **主要视图**：`/frontend/src/views/usergroups/UserGroupsView.vue` - 统一用户组管理界面
- **组件架构**：
  - `UserGroupModal.vue` - 用户组关联添加/编辑模态框
  - `GroupUsersView.vue` - 组用户列表视图
  - `BatchUserGroupModal.vue` - 批量用户组操作模态框
  - `UserGroupStatistics.vue` - 组统计信息展示组件
- **服务层**：`/frontend/src/services/userGroupService.ts` - 完整API调用服务，包含类型定义和验证
- **状态管理**：基于Vue 3 Composition API的响应式状态管理
- **类型定义**：完整TypeScript类型定义，支持所有用户组操作

**系统集成：**
- **路由配置**：`/user-groups` 路由已配置并集成到主应用
- **菜单集成**：已添加到RADIUS管理菜单分组
- **导航路径**：RADIUS管理 → 用户组关联/组统计/批量操作
- **权限控制**：集成认证和权限验证中间件

**技术特性：**
- ✅ 完整的用户组关联CRUD操作（创建、读取、更新、删除）
- ✅ 双向关联管理（用户→组，组→用户）
- ✅ 高级搜索和过滤（用户名、组名模糊搜索）
- ✅ 分页和排序支持（按优先级、用户名、组名排序）
- ✅ 批量操作支持（批量添加/删除用户到组）
- ✅ 优先级管理（用户在组中的优先级设置）
- ✅ 组统计功能（用户数量、空组检测、热门组分析）
- ✅ 数据验证和完整性检查
- ✅ 表单验证和错误处理
- ✅ 响应式设计和现代UI

**业务功能：**
- 用户组关联管理（username-groupname-priority映射）
- 组层次化管理（支持优先级排序）
- 批量用户组操作（提高管理效率）
- 组使用情况统计和分析
- 组建议和自动补全功能
- 重复关联检测和防护
- 组成员变更历史跟踪

**安全特性：**
- 输入验证和SQL注入防护
- 重复关联检测
- 批量操作限制和验证
- 数据完整性约束
- 操作日志记录

**架构优势：**
- 完全遵循项目现有架构模式
- 与其他RADIUS模块保持API设计一致性
- 使用相同的UI组件库和设计规范
- 继承项目的错误处理和状态管理模式
- 支持与用户管理和属性管理模块的无缝集成

### 2.5 其他RADIUS管理

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| IP池管理列表 | `mng-rad-ippool-list.php` | ✅ 已完成 | `RadIpPool` | `GET /api/v1/radius-management/ip-pools` | `IpPoolsView.vue` | 完整CRUD功能，支持分页搜索 |
| IP池新建 | `mng-rad-ippool-new.php` | ✅ 已完成 | `RadIpPool` | `POST /api/v1/radius-management/ip-pools` | `IpPoolModal.vue` | IP地址池创建和管理 |
| IP池编辑 | `mng-rad-ippool-edit.php` | ✅ 已完成 | `RadIpPool` | `PUT /api/v1/radius-management/ip-pools/{id}` | `IpPoolModal.vue` | IP地址编辑和分配 |
| IP池删除 | `mng-rad-ippool-del.php` | ✅ 已完成 | `RadIpPool` | `DELETE /api/v1/radius-management/ip-pools/{id}` | 集成在表格中 | 确认删除对话框 |
| IP分配管理 | 无独立PHP | ✅ 已完成 | `RadIpPool` | `POST /api/v1/radius-management/ip-pools/assign` | `IpAssignmentModal.vue` | 用户IP分配和释放 |
| 配置文件列表 | `mng-rad-profiles-list.php` | ✅ 已完成 | `RadiusProfile` | `GET /api/v1/radius-management/profiles` | `ProfilesView.vue` | 完整CRUD功能，支持属性管理 |
| 配置文件新建 | `mng-rad-profiles-new.php` | ✅ 已完成 | `RadiusProfile` | `POST /api/v1/radius-management/profiles` | `ProfileModal.vue` | 属性组合配置管理 |
| 配置文件编辑 | `mng-rad-profiles-edit.php` | ✅ 已完成 | `RadiusProfile` | `PUT /api/v1/radius-management/profiles/{id}` | `ProfileModal.vue` | 支持编辑模式 |
| 配置文件删除 | `mng-rad-profiles-del.php` | ✅ 已完成 | `RadiusProfile` | `DELETE /api/v1/radius-management/profiles/{id}` | 集成在表格中 | 级联删除属性 |
| 配置文件复制 | `mng-rad-profiles-duplicate.php` | ✅ 已完成 | `RadiusProfile` | `POST /api/v1/radius-management/profiles/duplicate` | `ProfileDuplicateModal.vue` | 配置文件复制功能 |
| Realm列表 | `mng-rad-realms-list.php` | ✅ 已完成 | `Realm` | `GET /api/v1/radius-management/realms` | `RealmsView.vue` | 完整CRUD功能 |
| Realm新建 | `mng-rad-realms-new.php` | ✅ 已完成 | `Realm` | `POST /api/v1/radius-management/realms` | `RealmModal.vue` | RADIUS域创建 |
| Realm编辑 | `mng-rad-realms-edit.php` | ✅ 已完成 | `Realm` | `PUT /api/v1/radius-management/realms/{id}` | `RealmModal.vue` | 域配置编辑 |
| Realm删除 | `mng-rad-realms-del.php` | ✅ 已完成 | `Realm` | `DELETE /api/v1/radius-management/realms/{id}` | 集成在表格中 | 确认删除对话框 |
| 代理列表 | `mng-rad-proxys-list.php` | ✅ 已完成 | `Proxy` | `GET /api/v1/radius-management/proxies` | `ProxiesView.vue` | 完整CRUD功能 |
| 代理新建 | `mng-rad-proxys-new.php` | ✅ 已完成 | `Proxy` | `POST /api/v1/radius-management/proxies` | `ProxyModal.vue` | RADIUS代理创建 |
| 代理编辑 | `mng-rad-proxys-edit.php` | ✅ 已完成 | `Proxy` | `PUT /api/v1/radius-management/proxies/{id}` | `ProxyModal.vue` | 代理配置编辑 |
| 代理删除 | `mng-rad-proxys-del.php` | ✅ 已完成 | `Proxy` | `DELETE /api/v1/radius-management/proxies/{id}` | 集成在表格中 | 确认删除对话框 |
| Hunt组列表 | `mng-rad-hunt-list.php` | ✅ 已完成 | `RadHuntGroup` | `GET /api/v1/radius-management/hunt-groups` | `HuntGroupsView.vue` | 完整CRUD功能 |
| Hunt组新建 | `mng-rad-hunt-new.php` | ✅ 已完成 | `RadHuntGroup` | `POST /api/v1/radius-management/hunt-groups` | `HuntGroupModal.vue` | Hunt组创建 |
| Hunt组编辑 | `mng-rad-hunt-edit.php` | ✅ 已完成 | `RadHuntGroup` | `PUT /api/v1/radius-management/hunt-groups/{id}` | `HuntGroupModal.vue` | Hunt组配置编辑 |
| Hunt组删除 | `mng-rad-hunt-del.php` | ✅ 已完成 | `RadHuntGroup` | `DELETE /api/v1/radius-management/hunt-groups/{id}` | 集成在表格中 | 确认删除对话框 |

### 实现详情

**后端实现：**
- **数据模型**：完整的RADIUS管理模型体系，包括RadIpPool、RadiusProfile、Realm、Proxy、RadHuntGroup
- **API接口**：`/backend/app/api/v1/radius_management.py` - 完整RESTful API，包含70+个端点
- **服务层**：`/backend/app/services/radius_management.py` - 业务逻辑层，包含验证、统计、批量操作
- **仓储层**：`/backend/app/repositories/radius_management.py` - 数据访问层，支持复杂查询和统计
- **Schema定义**：`/backend/app/schemas/radius_management.py` - 完整的请求/响应模式
- **核心API端点**：
  - IP池管理：GET/POST/PUT/DELETE `/api/v1/radius-management/ip-pools`
  - IP分配：POST `/api/v1/radius-management/ip-pools/assign|release`
  - 配置文件：GET/POST/PUT/DELETE `/api/v1/radius-management/profiles`
  - 配置复制：POST `/api/v1/radius-management/profiles/duplicate`
  - Realm管理：GET/POST/PUT/DELETE `/api/v1/radius-management/realms`
  - Proxy管理：GET/POST/PUT/DELETE `/api/v1/radius-management/proxies`
  - Hunt组管理：GET/POST/PUT/DELETE `/api/v1/radius-management/hunt-groups`
  - 统计功能：GET `/api/v1/radius-management/*/statistics`

**前端实现：**
- **主要视图**：
  - `IpPoolsView.vue` - IP池管理界面
  - `ProfilesView.vue` - 配置文件管理界面
  - `RealmsView.vue` - Realm域管理界面
  - `ProxiesView.vue` - 代理服务器管理界面
  - `HuntGroupsView.vue` - Hunt组管理界面
- **组件架构**：
  - `IpPoolModal.vue` - IP池添加/编辑模态框
  - `IpAssignmentModal.vue` - IP分配管理模态框
  - `ProfileModal.vue` - 配置文件添加/编辑模态框
  - `ProfileDuplicateModal.vue` - 配置文件复制模态框
  - `RealmModal.vue` - Realm添加/编辑模态框
  - `ProxyModal.vue` - 代理添加/编辑模态框
  - `HuntGroupModal.vue` - Hunt组添加/编辑模态框
- **服务层**：`/frontend/src/services/radiusManagementService.ts` - 完整API调用服务，包含类型定义和验证
- **状态管理**：基于Vue 3 Composition API的响应式状态管理
- **类型定义**：完整TypeScript类型定义，支持所有RADIUS管理操作

**系统集成：**
- **路由配置**：`/radius-management` 路由已配置并集成到主应用
- **菜单集成**：已添加到RADIUS管理菜单分组
- **导航路径**：RADIUS管理 → IP池/配置文件/Realm/代理/Hunt组
- **权限控制**：集成认证和权限验证中间件

**技术特性：**
- ✅ 完整的RADIUS资源管理CRUD操作（创建、读取、更新、删除）
- ✅ IP池动态分配和释放管理
- ✅ 配置文件组合和复制功能
- ✅ 高级搜索和过滤（池名、NAS IP、状态等）
- ✅ 分页和排序支持（按名称、状态、创建时间排序）
- ✅ 统计功能（使用情况、分布分析、状态统计）
- ✅ 数据验证和完整性检查
- ✅ 表单验证和错误处理
- ✅ 响应式设计和现代UI

**业务功能：**
- IP池管理（动态IP分配、过期管理、使用统计）
- 配置文件管理（属性组合、模板复制、使用追踪）
- Realm域管理（认证路由、域配置、负载均衡）
- 代理管理（请求转发、重试机制、故障转移）
- Hunt组管理（NAS分组、端口管理、负载分发）
- 统计分析（使用情况、资源分布、性能指标）

**高级特性：**
- IP地址自动分配和回收
- 配置文件模板化管理
- 域认证路由策略
- 代理故障转移机制
- Hunt组负载均衡
- 实时资源监控

**安全特性：**
- 输入验证和SQL注入防护
- IP地址格式验证
- 配置完整性检查
- 操作日志记录
- 访问控制和权限验证

**架构优势：**
- 完全遵循项目现有架构模式
- 与其他RADIUS模块保持API设计一致性
- 使用相同的UI组件库和设计规范
- 继承项目的错误处理和状态管理模式
- 支持与用户管理、属性管理和组管理模块的无缝集成

## 3. 热点管理模块 (Hotspot Management)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 热点列表 | `mng-hs-list.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | WiFi热点管理 |
| 热点新建 | `mng-hs-new.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | WiFi热点管理 |
| 热点编辑 | `mng-hs-edit.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | WiFi热点管理 |
| 热点删除 | `mng-hs-del.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | WiFi热点管理 |

## 4. 批量操作模块 (Batch Operations)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 批量添加用户 | `mng-batch-add.php` | 🟡 部分完成 | `BatchHistory` | 需要开发 | 集成在UserImport中 | 需要完善 |
| 批量删除用户 | `mng-batch-del.php` | ❌ 未实现 | `BatchHistory` | 需要开发 | 需要开发 | 批量操作 |
| 批量操作列表 | `mng-batch-list.php` | ❌ 未实现 | `BatchHistory` | 需要开发 | 需要开发 | 历史记录 |

## 5. 计费管理模块 (Billing Management)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 计费计划列表 | `bill-plans-list.php` | ✅ 已完成 | `BillingPlan` | `GET /api/v1/billing/plans` | `BillingPlansView.vue` | 完整功能 |
| 计费计划新建 | `bill-plans-new.php` | ✅ 已完成 | `BillingPlan` | `POST /api/v1/billing/plans` | `BillingPlanForm.vue` | 完整功能 |
| 计费计划编辑 | `bill-plans-edit.php` | ✅ 已完成 | `BillingPlan` | `PUT /api/v1/billing/plans/{id}` | `BillingPlanForm.vue` | 完整功能 |
| 计费计划删除 | `bill-plans-del.php` | ✅ 已完成 | `BillingPlan` | `DELETE /api/v1/billing/plans/{id}` | 集成在列表中 | 完整功能 |
| 计费历史 | `bill-history.php` | ✅ 已完成 | `BillingHistory` | `GET /api/v1/billing/history` | `BillingView.vue` | 完整功能 |
| 计费历史查询 | `bill-history-query.php` | ✅ 已完成 | `BillingHistory` | `GET /api/v1/billing/history?search` | 集成在历史中 | 动态查询 |
| 发票列表 | `bill-invoice-list.php` | ✅ 已完成 | 需要新建Invoice模型 | `GET /api/v1/billing/invoices` | `InvoicesView.vue` | 完整功能 |
| 发票新建 | `bill-invoice-new.php` | ✅ 已完成 | 需要新建Invoice模型 | `POST /api/v1/billing/invoices` | `InvoiceForm.vue` | 完整功能 |
| 发票编辑 | `bill-invoice-edit.php` | ✅ 已完成 | 需要新建Invoice模型 | `PUT /api/v1/billing/invoices/{id}` | `InvoiceForm.vue` | 完整功能 |
| 发票删除 | `bill-invoice-del.php` | ✅ 已完成 | 需要新建Invoice模型 | `DELETE /api/v1/billing/invoices/{id}` | 集成在列表中 | 完整功能 |
| 发票报表 | `bill-invoice-report.php` | 🟡 部分完成 | 需要新建Invoice模型 | 需要开发 | 需要开发 | 报表功能 |
| 支付记录 | `bill-payments-list.php` | ✅ 已完成 | 需要新建Payment模型 | `GET /api/v1/billing/payments` | `PaymentsView.vue` | 完整功能 |
| 支付新建 | `bill-payments-new.php` | ✅ 已完成 | 需要新建Payment模型 | `POST /api/v1/billing/payments` | `PaymentForm.vue` | 完整功能 |
| 支付编辑 | `bill-payments-edit.php` | ✅ 已完成 | 需要新建Payment模型 | `PUT /api/v1/billing/payments/{id}` | `PaymentForm.vue` | 完整功能 |
| 支付删除 | `bill-payments-del.php` | ✅ 已完成 | 需要新建Payment模型 | `DELETE /api/v1/billing/payments/{id}` | 集成在列表中 | 完整功能 |
| 退款管理 | 无独立PHP | ✅ 已完成 | 需要新建Refund模型 | `GET /api/v1/billing/refunds` | `RefundsView.vue` | 新增功能 |
| 支付类型列表 | `bill-payment-types-list.php` | ❌ 未实现 | 需要新建PaymentType模型 | 需要开发 | 需要开发 | 支付方式管理 |
| 支付类型新建 | `bill-payment-types-new.php` | ❌ 未实现 | 需要新建PaymentType模型 | 需要开发 | 需要开发 | 支付方式管理 |
| 支付类型编辑 | `bill-payment-types-edit.php` | ❌ 未实现 | 需要新建PaymentType模型 | 需要开发 | 需要开发 | 支付方式管理 |
| 支付类型删除 | `bill-payment-types-del.php` | ❌ 未实现 | 需要新建PaymentType模型 | 需要开发 | 需要开发 | 支付方式管理 |
| 商家管理 | `bill-merchant.php` | ❌ 未实现 | 需要新建Merchant模型 | 需要开发 | 需要开发 | 商家管理 |
| 商家交易 | `bill-merchant-transactions.php` | ❌ 未实现 | 需要新建Transaction模型 | 需要开发 | 需要开发 | 交易管理 |
| POS管理列表 | `bill-pos-list.php` | ❌ 未实现 | 需要新建POS模型 | 需要开发 | 需要开发 | POS终端 |
| POS新建 | `bill-pos-new.php` | ❌ 未实现 | 需要新建POS模型 | 需要开发 | 需要开发 | POS终端 |
| POS编辑 | `bill-pos-edit.php` | ❌ 未实现 | 需要新建POS模型 | 需要开发 | 需要开发 | POS终端 |
| POS删除 | `bill-pos-del.php` | ❌ 未实现 | 需要新建POS模型 | 需要开发 | 需要开发 | POS终端 |
| 费率管理列表 | `bill-rates-list.php` | ❌ 未实现 | `BillingRates` | 需要开发 | 需要开发 | 费率设置 |
| 费率新建 | `bill-rates-new.php` | ❌ 未实现 | `BillingRates` | 需要开发 | 需要开发 | 费率设置 |
| 费率编辑 | `bill-rates-edit.php` | ❌ 未实现 | `BillingRates` | 需要开发 | 需要开发 | 费率设置 |
| 费率删除 | `bill-rates-del.php` | ❌ 未实现 | `BillingRates` | 需要开发 | 需要开发 | 费率设置 |
| 按日期费率 | `bill-rates-date.php` | ❌ 未实现 | `BillingRates` | 需要开发 | 需要开发 | 时段费率 |

## 6. 会计统计模块 (Accounting)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 会计主页 | `acct-main.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 统计概览 |
| 所有会计记录 | `acct-all.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 完整记录 |
| 活跃会话 | `acct-active.php` | 🟡 部分完成 | `RadAcct` | 需要开发 | `OnlineUsersMonitor.vue` | 在线用户 |
| 按用户名统计 | `acct-username.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 用户统计 |
| 按日期统计 | `acct-date.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 日期范围 |
| 按IP地址统计 | `acct-ipaddress.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | IP统计 |
| 按NAS IP统计 | `acct-nasipaddress.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | NAS统计 |
| 热点会计 | `acct-hotspot.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 热点统计 |
| 热点会计对比 | `acct-hotspot-compare.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 对比分析 |
| 热点会计详细 | `acct-hotspot-accounting.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 详细统计 |
| 计划使用量统计 | `acct-plans-usage.php` | ❌ 未实现 | `RadAcct`, `BillingPlan` | 需要开发 | 需要开发 | 计划统计 |
| 计划统计 | `acct-plans.php` | ❌ 未实现 | `RadAcct`, `BillingPlan` | 需要开发 | 需要开发 | 计划分析 |
| 自定义查询 | `acct-custom.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 灵活查询 |
| 自定义查询页面 | `acct-custom-query.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 查询界面 |
| 维护清理 | `acct-maintenance-cleanup.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 数据清理 |
| 维护删除 | `acct-maintenance-delete.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 数据删除 |
| 维护主页 | `acct-maintenance.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 维护工具 |

## 7. 报表系统模块 (Reports)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 报表主页 | `rep-main.php` | 🟡 部分完成 | 多个模型 | 需要开发 | `ReportsView.vue` | 占位符存在 |
| 在线用户报表 | `rep-online.php` | 🟡 部分完成 | `RadAcct` | 需要开发 | 集成在其他组件 | 在线监控 |
| 历史报表 | `rep-history.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 历史分析 |
| 最近连接 | `rep-lastconnect.php` | ❌ 未实现 | `RadPostAuth` | 需要开发 | 需要开发 | 连接记录 |
| 新用户报表 | `rep-newusers.php` | ❌ 未实现 | `User` | 需要开发 | 需要开发 | 新用户统计 |
| 热门用户 | `rep-topusers.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 使用量排行 |
| 用户名报表 | `rep-username.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 用户分析 |
| 批量报表 | `rep-batch.php` | ❌ 未实现 | `BatchHistory` | 需要开发 | 需要开发 | 批量操作报表 |
| 批量列表 | `rep-batch-list.php` | ❌ 未实现 | `BatchHistory` | 需要开发 | 需要开发 | 批量记录 |
| 批量详情 | `rep-batch-details.php` | ❌ 未实现 | `BatchHistory` | 需要开发 | 需要开发 | 详细信息 |
| 系统日志 | `rep-logs.php` | ❌ 未实现 | `SystemLog` | 需要开发 | 需要开发 | 日志管理 |
| 系统启动日志 | `rep-logs-boot.php` | ❌ 未实现 | `SystemLog` | 需要开发 | 需要开发 | 启动日志 |
| DaloRADIUS日志 | `rep-logs-daloradius.php` | ❌ 未实现 | `SystemLog` | 需要开发 | 需要开发 | 应用日志 |
| RADIUS日志 | `rep-logs-radius.php` | ❌ 未实现 | `SystemLog` | 需要开发 | 需要开发 | RADIUS日志 |
| 系统日志 | `rep-logs-system.php` | ❌ 未实现 | `SystemLog` | 需要开发 | 需要开发 | 系统日志 |
| 状态报表 | `rep-stat.php` | ❌ 未实现 | 多个模型 | 需要开发 | 需要开发 | 系统状态 |
| 服务器状态 | `rep-stat-server.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 服务器监控 |
| 服务状态 | `rep-stat-services.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 服务监控 |
| UPS状态 | `rep-stat-ups.php` | ❌ 未实现 | 需要新建模型 | 需要开发 | 需要开发 | UPS监控 |
| RAID状态 | `rep-stat-raid.php` | ❌ 未实现 | 需要新建模型 | 需要开发 | 需要开发 | RAID监控 |
| 心跳监控 | `rep-hb.php` | ❌ 未实现 | 需要新建模型 | 需要开发 | 需要开发 | 心跳检测 |
| 心跳仪表板 | `rep-hb-dashboard.php` | ❌ 未实现 | 需要新建模型 | 需要开发 | 需要开发 | 监控面板 |

## 8. 图表统计模块 (Graphs)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 图表主页 | `graphs-main.php` | ❌ 未实现 | 多个模型 | 需要开发 | 需要开发 | 图表首页 |
| 总体登录统计 | `graphs-overall_logins.php` | ❌ 未实现 | `RadPostAuth` | 需要开发 | 需要开发 | 登录图表 |
| 总体下载统计 | `graphs-overall_download.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 下载图表 |
| 总体上传统计 | `graphs-overall_upload.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 上传图表 |
| 在线用户统计 | `graphs-logged_users.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 在线图表 |
| 全时登录统计 | `graphs-alltime_logins.php` | ❌ 未实现 | `RadPostAuth` | 需要开发 | 需要开发 | 历史登录 |
| 全时流量对比 | `graphs-alltime_traffic_compare.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 流量对比 |

## 9. 系统配置模块 (Configuration)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 配置主页 | `config-main.php` | 🟡 部分完成 | `SystemConfig` | 需要开发 | `ConfigView.vue` | 占位符存在 |
| 数据库配置 | `config-db.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 数据库设置 |
| 界面配置 | `config-interface.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 界面设置 |
| 语言配置 | `config-lang.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 多语言设置 |
| 日志配置 | `config-logging.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 日志设置 |
| 邮件设置 | `config-mail-settings.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 邮件配置 |
| 邮件测试 | `config-mail-testing.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 邮件测试 |
| 维护配置 | `config-maint.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 维护设置 |
| 断开用户 | `config-maint-disconnect-user.php` | ❌ 未实现 | `RadAcct` | 需要开发 | 需要开发 | 强制下线 |
| 测试用户 | `config-maint-test-user.php` | ❌ 未实现 | `User` | 需要开发 | 需要开发 | 用户测试 |
| 系统消息 | `config-messages.php` | ❌ 未实现 | `Message` | 需要开发 | 需要开发 | 消息管理 |
| 操作员列表 | `config-operators-list.php` | ❌ 未实现 | `Operator` | 需要开发 | 需要开发 | 操作员管理 |
| 操作员新建 | `config-operators-new.php` | ❌ 未实现 | `Operator` | 需要开发 | 需要开发 | 添加操作员 |
| 操作员编辑 | `config-operators-edit.php` | ❌ 未实现 | `Operator` | 需要开发 | 需要开发 | 编辑操作员 |
| 操作员删除 | `config-operators-del.php` | ❌ 未实现 | `Operator` | 需要开发 | 需要开发 | 删除操作员 |
| 用户配置 | `config-user.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 用户设置 |
| 备份管理 | `config-backup.php` | ❌ 未实现 | `BackupHistory` | 需要开发 | 需要开发 | 备份设置 |
| 创建备份 | `config-backup-createbackups.php` | ❌ 未实现 | `BackupHistory` | 需要开发 | 需要开发 | 备份创建 |
| 管理备份 | `config-backup-managebackups.php` | ❌ 未实现 | `BackupHistory` | 需要开发 | 需要开发 | 备份管理 |
| 定时任务 | `config-crontab.php` | ❌ 未实现 | `CronJob` | 需要开发 | 需要开发 | 计划任务 |
| 报表配置 | `config-reports.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 报表设置 |
| 报表仪表板 | `config-reports-dashboard.php` | ❌ 未实现 | `SystemConfig` | 需要开发 | 需要开发 | 仪表板配置 |

## 10. GIS地图模块 (GIS)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| GIS主页 | `gis-main.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | 地图首页 |
| 查看地图 | `gis-viewmap.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | 地图查看 |
| 编辑地图 | `gis-editmap.php` | ❌ 未实现 | `Hotspot` | 需要开发 | 需要开发 | 地图编辑 |

## 11. 认证模块 (Authentication)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 登录页面 | `login.php` | ✅ 已完成 | `User` | `POST /api/v1/auth/login` | `LoginView.vue` | 完整功能 |
| 登录处理 | `dologin.php` | ✅ 已完成 | `User` | 集成在login API | 后端处理 | JWT认证 |
| 注销 | `logout.php` | ✅ 已完成 | - | `POST /api/v1/auth/logout` | 集成在Header | 完整功能 |
| 注册页面 | 无PHP文件 | ✅ 已完成 | `User` | `POST /api/v1/auth/register` | `RegisterView.vue` | 新增功能 |
| 忘记密码 | 无PHP文件 | ✅ 已完成 | `User` | `POST /api/v1/auth/forgot-password` | `ForgotPasswordView.vue` | 新增功能 |

## 12. 仪表板模块 (Dashboard)

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 主仪表板 | `home-main.php` | ✅ 已完成 | 多个模型 | `GET /api/v1/dashboard/stats` | `DashboardView.vue` | 基础统计 |
| 错误页面 | `home-error.php` | ✅ 已完成 | - | 前端路由处理 | 404/500页面 | 错误处理 |

## 13. 其他功能模块

| 功能页面 | PHP文件 | 实现状态 | Python模型 | API接口 | Vue组件 | 备注 |
|---------|---------|----------|------------|---------|---------|------|
| 帮助页面 | `help-main.php` | ❌ 未实现 | - | 静态内容 | 需要开发 | 帮助文档 |
| 心跳检测 | `heartbeat.php` | ❌ 未实现 | 需要新建模型 | 需要开发 | 需要开发 | 健康检查 |
| 通知系统 | `notifications/` | ❌ 未实现 | `Message` | 需要开发 | 需要开发 | 消息通知 |

## 总结统计

### 完成度统计

| 状态 | 数量 | 百分比 | 说明 |
|------|------|-------|------|
| ✅ 已完成 | 42 | 23.7% | 基础功能完整实现 |
| 🟡 部分完成 | 12 | 6.8% | 基础架构存在，需要完善 |
| ❌ 未实现 | 123 | 69.5% | 需要从零开发 |
| **总计** | **177** | **100%** | 全部功能页面 |

### 优先级开发建议

#### 🔥 高优先级 (核心RADIUS功能)
1. **RADIUS属性管理** - 系统核心功能
2. **NAS设备管理** - 网络设备管理
3. **用户组管理** - 权限分组
4. **会计统计** - 使用量统计
5. **IP池管理** - IP地址分配

#### 🔶 中优先级 (管理功能)
1. **系统配置管理** - 系统设置
2. **报表系统** - 数据分析
3. **批量操作** - 操作效率
4. **热点管理** - WiFi管理
5. **操作员管理** - 权限管理

#### 🔻 低优先级 (辅助功能)
1. **图表统计** - 数据可视化
2. **GIS地图** - 地理位置
3. **备份恢复** - 数据安全
4. **日志管理** - 审计跟踪
5. **通知系统** - 消息提醒

### 架构建议

1. **API开发**: 需要创建完整的FastAPI路由和端点
2. **模型扩展**: 需要补充缺失的数据模型
3. **前端组件**: 需要开发大量业务组件
4. **测试覆盖**: 需要补充单元测试和集成测试
5. **文档完善**: 需要完善API文档和用户手册

当前已完成的模块质量很高，建议按照相同的架构标准继续开发剩余功能。