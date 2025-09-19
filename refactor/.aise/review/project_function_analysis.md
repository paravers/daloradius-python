# daloradius-python 项目功能分析报告

## 项目结构概览

- `app/`：核心业务代码，分为 common（通用库）、operators（运营管理）、users（用户自服务）等模块。
- `contrib/`：第三方集成与脚本，如 chilli、db、docker、heartbeat、scripts。
- `doc/`：项目文档，包括账单、安装说明等。
- `log/`：日志文件。
- `python/`：预留 Python 代码目录，当前为空。
- `refactor/`：重构相关资料。
- `setup/`：安装脚本。

## 主要功能模块

### 1. 通用库（common）
- 配置读写、数据库连接、邮件、通知、PDF 生成、表单校验等基础功能。
- 静态资源（css/js/images）、模板（如 user-welcome.html）。

### 2. 运营管理（operators）
- 计费、账单、报表、用户管理、配置、维护、GIS 地图、统计图表等。
- 运营相关静态资源。

### 3. 用户自服务（users）
- 用户登录、信息管理、密码修改、通知、偏好设置等。
- 用户相关静态资源。

### 4. 第三方集成与脚本（contrib）
- chilli：Portal 相关集成。
- db：数据库初始化脚本。
- docker：运营商与用户配置。
- heartbeat：监控脚本。
- scripts：维护与自动化脚本。

### 5. 安装与文档
- 安装脚本（setup/install.sh）、多平台安装说明（doc/install/）。
- 账单说明（doc/billing.md）。

## 业务流程简述
- 用户通过 Web 前端访问 operators 或 users 模块，进行认证、账单查询、信息管理等操作。
- 后端通过 common 库处理数据库、配置、通知等通用逻辑。
- 运营人员可通过 operators 进行计费、报表、维护等管理操作。
- 系统通过 contrib 目录下脚本实现第三方集成与自动化。

---

本报告为后续 UML 架构分析和 Python 架构设计提供高质量索引上下文。
