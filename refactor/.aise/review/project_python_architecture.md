# daloradius-python Python 版本项目架构设计（UML）

## UML 组件图

```uml
@startuml
package "daloradius-python (Python)" {
  [Web Frontend]
  [Operator Service]
  [User Service]
  [Common Service]
  [API Gateway]
  [Database]
  [Integration Service]
}

[Web Frontend] --> [API Gateway]
[API Gateway] --> [Operator Service]
[API Gateway] --> [User Service]
[Operator Service] --> [Common Service]
[User Service] --> [Common Service]
[Common Service] --> [Database]
[Operator Service] --> [Database]
[User Service] --> [Database]
[Operator Service] --> [Integration Service]
[Common Service] --> [Integration Service]
@enduml
```

## 架构说明
- 前端通过 API Gateway 与后端服务交互，实现前后端分离。
- Operator Service 与 User Service 分别处理运营与用户自服务业务，均依赖 Common Service 实现通用逻辑。
- Common Service 统一处理配置、数据库、通知等底层服务。
- Integration Service 负责第三方集成与自动化。
- 所有服务通过标准化 API 进行通信，便于扩展和微服务化。
- 支持自动化测试与 CI/CD，提升开发与运维效率。

---

本架构设计为 Python 版本重构提供高质量索引和参考。
