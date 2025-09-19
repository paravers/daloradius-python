# daloradius-python 当前架构分析报告（UML）

## UML 组件图

```uml
@startuml
package "daloradius-python" {
  [Web Frontend]
  [Operators Module]
  [Users Module]
  [Common Library]
  [Database]
  [Contrib Scripts]
}

[Web Frontend] --> [Operators Module]
[Web Frontend] --> [Users Module]
[Operators Module] --> [Common Library]
[Users Module] --> [Common Library]
[Common Library] --> [Database]
[Operators Module] --> [Database]
[Users Module] --> [Database]
[Operators Module] --> [Contrib Scripts]
[Common Library] --> [Contrib Scripts]
@enduml
```

## 架构说明
- Web 前端通过 Operators 和 Users 两大模块提供运营与用户自服务功能。
- Operators/Users 模块均依赖 Common Library 实现配置、数据库、通知等通用逻辑。
- Common Library 负责与数据库交互，提供底层服务。
- Operators/Users 可直接访问数据库以实现部分业务逻辑。
- Contrib Scripts 提供第三方集成与自动化支持，部分由 Operators/Common Library 调用。

---

本架构分析为后续评审与 Python 架构设计提供高质量索引。
