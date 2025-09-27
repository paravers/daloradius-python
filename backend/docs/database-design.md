# DaloRADIUS Python Backend - 数据关系设计文档

## 1. 概述

本文档详细描述了 DaloRADIUS Python 后端的数据库设计和模型关系。系统采用 SQLAlchemy ORM 架构，支持 PostgreSQL 数据库，涵盖用户管理、RADIUS 协议、计费系统、网络访问服务器（NAS）管理、系统配置等核心业务领域。

## 2. 架构概述

### 2.1 模块结构

```
backend/app/models/
├── base.py              # 基础模型类和 Mixin
├── user.py             # 用户管理模型
├── radius.py           # RADIUS 协议相关模型
├── radius_groups.py    # RADIUS 组管理模型
├── accounting.py       # 计费和会话记录模型
├── billing.py          # 业务计费模型
├── nas.py              # NAS 设备管理模型
├── access_control.py   # 访问控制和字典模型
└── system.py           # 系统配置和日志模型
```

### 2.2 设计原则

1. **分层架构**: 清晰的领域分离，每个模块负责特定的业务逻辑
2. **标准化**: 统一的基础模型类和时间戳管理
3. **可扩展性**: 支持未来功能扩展和第三方集成
4. **性能优化**: 合理的索引设计和查询优化
5. **数据完整性**: 外键约束和枚举类型确保数据一致性

## 3. 核心实体关系图

### 3.1 整体系统架构

```mermaid
erDiagram
    %% 用户管理核心
    User ||--o{ RadCheck : "has authentication attributes"
    User ||--o{ RadReply : "has authorization attributes" 
    User ||--o{ RadAcct : "has session records"
    User ||--o{ BillingHistory : "has billing records"
    User ||--o{ UserInfo : "has profile"
    
    %% RADIUS 组织管理
    RadGroupCheck ||--o{ UserGroup : "group check rules"
    RadGroupReply ||--o{ UserGroup : "group reply rules"
    User ||--o{ UserGroup : "member of groups"
    
    %% NAS 设备管理
    Nas ||--o{ RadAcct : "receives accounting from"
    Nas ||--o{ RadIpPool : "manages IP pools"
    Nas ||--o{ Realm : "belongs to realm"
    
    %% 计费系统
    BillingPlan ||--o{ BillingHistory : "plan assignments"
    BillingPlan ||--o{ User : "current plan"
    
    %% 系统管理
    Operator ||--o{ OperatorAcl : "has permissions"
    OperatorAclFile ||--o{ OperatorAcl : "defines access files"
    
    %% 审计和日志
    SystemLog ||--|| User : "activity by user"
    RadPostAuth ||--|| User : "authentication attempts"
    
    %% 字典和配置
    Dictionary }|--|| RadCheck : "attribute definitions"
    Dictionary }|--|| RadReply : "attribute definitions"
    SystemConfig }|--o{ CronJob : "system settings"
```

### 3.2 用户管理域

```mermaid
erDiagram
    User {
        int id PK
        string username UK "唯一用户名"
        string email UK "邮箱地址"
        string password_hash "密码哈希"
        enum auth_type "认证类型"
        boolean is_active "是否激活"
        enum status "账户状态"
        string first_name "名"
        string last_name "姓"
        string department "部门"
        string company "公司"
        datetime created_at
        datetime updated_at
    }
    
    UserInfo {
        int id PK
        int user_id FK
        string username "用户名(冗余)"
        string firstname "名"
        string lastname "姓"  
        string email "邮箱"
        string department "部门"
        string company "公司"
        string workphone "工作电话"
        string homephone "家庭电话"
        string mobilephone "手机"
        text address "地址"
        string city "城市"
        string state "省份"
        string country "国家"
        string zip "邮编"
        text notes "备注"
        date changeuserinfo "信息更新日期"
        string portalloginpassword "门户登录密码"
        enum enableportallogin "启用门户登录"
        datetime creationdate
        string creationby
        datetime updatedate 
        string updateby
    }
    
    UserGroup {
        int id PK
        string username FK
        string groupname FK
        int priority "优先级"
    }
    
    BatchHistory {
        int id PK
        string batch_name "批次名称"
        string batch_description "批次描述"
        string batch_status "批次状态"
        datetime batch_creationdate
        string batch_creationby
        int hotspot_id FK
    }
    
    User ||--|| UserInfo : "has profile"
    User ||--o{ UserGroup : "member of groups"
    User ||--o{ BatchHistory : "created in batch"
```

### 3.3 RADIUS 协议域

```mermaid
erDiagram
    RadCheck {
        int id PK
        string username FK
        string attribute "属性名"
        enum op "操作符"
        string value "属性值"
    }
    
    RadReply {
        int id PK  
        string username FK
        string attribute "属性名"
        enum op "操作符"
        string value "属性值"
    }
    
    RadGroupCheck {
        int id PK
        string groupname FK
        string attribute "属性名" 
        string op "操作符"
        string value "属性值"
    }
    
    RadGroupReply {
        int id PK
        string groupname FK
        string attribute "属性名"
        string op "操作符" 
        string value "属性值"
    }
    
    RadPostAuth {
        int id PK
        string username FK
        string pass "密码"
        string reply "RADIUS响应"
        datetime authdate "认证时间"
        string class "类别"
    }
    
    RadIpPool {
        int id PK
        string pool_name "IP池名称"
        inet framedipaddress "分配的IP"
        inet nasipaddress "NAS IP地址"
        string calledstationid "被叫站ID"
        string callingstationid "主叫站ID"
        datetime expiry_time "过期时间"
        string username "用户名"
        string pool_key "池键"
    }
    
    User ||--o{ RadCheck : "authentication rules"
    User ||--o{ RadReply : "authorization rules"
    User ||--o{ RadPostAuth : "auth attempts"
    RadGroupCheck }|--|| UserGroup : "group auth rules"
    RadGroupReply }|--|| UserGroup : "group authz rules"
    Nas ||--o{ RadIpPool : "manages pools"
```

### 3.4 会话计费域

```mermaid
erDiagram
    RadAcct {
        int radacctid PK
        string username FK "用户名"
        string realm "域"
        string acctsessionid "会话ID"
        string acctuniqueid UK "唯一会话ID"
        string groupname "组名"
        inet nasipaddress "NAS IP地址"
        string nasportid "NAS端口ID"
        string nasporttype "NAS端口类型"
        string nasidentifier "NAS标识"
        string calledstationid "被叫站ID"
        string callingstationid "主叫站ID"
        inet framedipaddress "分配IP地址"
        string framedipv6address "IPv6地址"
        string framedipv6prefix "IPv6前缀"
        string framedinterfaceid "接口ID"
        string delegatedipv6prefix "委派IPv6前缀"
        string framedprotocol "帧协议"
        string servicetype "服务类型"
        string class_attribute "类属性"
        datetime acctstarttime "会话开始时间"
        datetime acctstoptime "会话结束时间"
        int acctsessiontime "会话时长(秒)"
        int acctinterval "计费间隔"
        string acctauthentic "认证方法"
        bigint acctinputoctets "输入字节数"
        bigint acctoutputoctets "输出字节数"
        bigint acctinputgigawords "输入千兆字"
        bigint acctoutputgigawords "输出千兆字"
        bigint acctinputpackets "输入包数"
        bigint acctoutputpackets "输出包数"
        string acctterminatecause "终止原因"
        string connectinfo_start "连接开始信息"
        string connectinfo_stop "连接结束信息"
    }
    
    AccountingSummary {
        int id PK
        string username FK
        date summary_date "汇总日期"
        bigint total_session_time "总会话时长"
        bigint total_input_octets "总输入字节"
        bigint total_output_octets "总输出字节"
        int session_count "会话数量"
        datetime created_at
        datetime updated_at
    }
    
    User ||--o{ RadAcct : "generates sessions"
    Nas ||--o{ RadAcct : "receives from NAS"
    RadAcct ||--o{ AccountingSummary : "summarized into"
```

### 3.5 业务计费域

```mermaid
erDiagram
    BillingPlan {
        int id PK
        string planName "计划名称"
        string planId "计划ID" 
        string planType "计划类型"
        string planTimeBank "时间银行"
        string planTimeType "时间类型"
        string planTimeRefillCost "时间充值费用"
        string planBandwidthUp "上行带宽"
        string planBandwidthDown "下行带宽"
        string planTrafficTotal "总流量"
        string planTrafficUp "上行流量"
        string planTrafficDown "下行流量"
        string planTrafficRefillCost "流量充值费用"
        string planRecurring "循环计费"
        string planRecurringPeriod "循环周期"
        string planRecurringBillingSchedule "计费调度"
        string planCost "计划费用"
        string planSetupCost "设置费用"
        string planTax "税费"
        string planCurrency "货币"
        string planGroup "计划组"
        string planActive "是否激活"
        datetime creationdate
        string creationby
        datetime updatedate
        string updateby
    }
    
    BillingHistory {
        int id PK
        string username FK "用户名"
        int planId FK "计划ID"
        string billAmount "账单金额"
        string billAction "账单操作"
        string billPerformer "操作员"
        string billReason "账单原因"
        string paymentmethod "付款方式"
        string cash "现金"
        string creditcardname "信用卡姓名"
        string creditcardnumber "信用卡号"
        string creditcardverification "信用卡验证码"
        string creditcardtype "信用卡类型"
        string creditcardexp "信用卡到期"
        string coupon "优惠券"
        string discount "折扣"
        string notes "备注"
        datetime creationdate
        string creationby
        datetime updatedate
        string updateby
    }
    
    BillingRates {
        int id PK
        string rateName "费率名称"
        string rateType "费率类型"
        decimal rateCost "费率成本"
        datetime creationdate
        string creationby
        datetime updatedate
        string updateby
    }
    
    User ||--o{ BillingHistory : "has billing records"
    BillingPlan ||--o{ BillingHistory : "applied to users"
    BillingPlan ||--o{ User : "current plan"
```

### 3.6 NAS 设备管理域

```mermaid
erDiagram
    Nas {
        int id PK
        string nasname UK "NAS名称/IP"
        string shortname "短名称"
        string type "设备类型"
        int ports "端口数"
        string secret "RADIUS密钥"
        string server "虚拟服务器"
        string community "SNMP团体字符串"
        text description "描述"
        boolean is_active "是否激活"
        datetime last_seen "最后可见时间"
        int total_requests "总请求数"
        int successful_requests "成功请求数"
        int failed_requests "失败请求数"
        datetime created_at
        datetime updated_at
    }
    
    Realm {
        int id PK
        string realmname UK "域名"
        string type "域类型"
        string authhost "认证主机"
        int authport "认证端口"
        string accthost "计费主机"
        int acctport "计费端口"
        string secret "共享密钥"
        boolean ldflag "负载标志"
        boolean nostrip "不剥离标志"
        text description "描述"
        boolean is_active "是否激活"
        datetime created_at
        datetime updated_at
    }
    
    Proxy {
        int id PK
        string proxyname UK "代理名称"
        string retry_delay "重试延迟"
        string retry_count "重试次数"
        string dead_time "死亡时间"
        string default_fallback "默认回退"
        text description "描述"
        boolean is_active "是否激活"
        datetime created_at
        datetime updated_at
    }
    
    Hotspot {
        int id PK
        string name UK "热点名称"
        string mac_address UK "MAC地址"
        string geocode "地理编码"
        string owner "所有者"
        string email_owner "所有者邮箱"
        string manager "管理员"
        string email_manager "管理员邮箱"
        text address "地址"
        string company "公司"
        text description "描述"
        string phone1 "电话1"
        string phone2 "电话2"
        datetime created_at
        datetime updated_at
    }
    
    Nas ||--o{ RadAcct : "receives accounting"
    Nas ||--o{ RadIpPool : "manages IP pools"
    Realm ||--o{ Nas : "contains NAS devices"
    User ||--o{ Hotspot : "accesses via hotspots"
```

### 3.7 访问控制域

```mermaid
erDiagram
    Operator {
        int id PK
        string username UK "操作员用户名"
        string password "密码哈希"
        string firstname "名"
        string lastname "姓"
        string title "职位"
        string department "部门"
        string company "公司"
        string phone1 "电话1"
        string phone2 "电话2"
        string email "邮箱"
        string messenger "即时通讯"
        text notes "备注"
        datetime lastlogin "最后登录"
        datetime creationdate
        string creationby
        datetime updatedate
        string updateby
    }
    
    OperatorAcl {
        int id PK
        int operator_id FK "操作员ID"
        string file "文件路径"
        int access "访问权限"
    }
    
    OperatorAclFile {
        int id PK
        string file UK "文件路径"
        string category "文件分类"
        text description "文件描述"
        boolean is_active "是否激活"
    }
    
    Dictionary {
        int id PK
        string Type "属性类型"
        string Attribute "属性名"
        string Value "属性值"
        string Format "格式"
        string Vendor "厂商"
        string RecommendedOP "推荐操作符"
        string RecommendedTable "推荐表"
        string RecommendedHelper "推荐助手"
        string RecommendedTooltip "推荐提示"
    }
    
    Message {
        int id PK
        enum type "消息类型"
        text content "消息内容"
        datetime created_on "创建时间"
        string created_by "创建者"
        datetime modified_on "修改时间"
        string modified_by "修改者"
    }
    
    Operator ||--o{ OperatorAcl : "has permissions"
    OperatorAclFile ||--o{ OperatorAcl : "defines files"
    Dictionary }|--|| RadCheck : "defines attributes"
    Dictionary }|--|| RadReply : "defines attributes"
```

### 3.8 系统管理域

```mermaid
erDiagram
    SystemConfig {
        int id PK
        string config_key UK "配置键"
        text config_value "配置值"
        string config_type "配置类型"
        string category "配置分类"
        text description "描述"
        boolean is_encrypted "是否加密"
        boolean is_system "是否系统配置"
        boolean requires_restart "是否需要重启"
        datetime created_at
        datetime updated_at
        string updated_by "更新者"
    }
    
    SystemLog {
        int id PK
        string log_level "日志级别"
        string logger_name "日志记录器名称"
        text message "日志消息"
        string username "用户名"
        string ip_address "IP地址"
        text user_agent "用户代理"
        string request_path "请求路径"
        string request_method "请求方法"
        json extra_data "额外数据"
        text exception_traceback "异常追踪"
        datetime created_at "创建时间"
    }
    
    BackupHistory {
        int id PK
        string backup_name "备份名称"
        string backup_type "备份类型"
        int backup_size "备份大小"
        string backup_path "备份路径"
        string status "备份状态"
        text error_message "错误消息"
        text tables_included "包含的表"
        boolean compression_used "是否使用压缩"
        boolean encryption_used "是否使用加密"
        datetime started_at "开始时间"
        datetime completed_at "完成时间"
        string created_by "创建者"
    }
    
    CronJob {
        int id PK
        string name UK "任务名称"
        string command "执行命令"
        string schedule "调度表达式"
        text description "任务描述"
        boolean is_active "是否激活"
        datetime last_run "最后运行时间"
        datetime next_run "下次运行时间"
        text last_output "最后输出"
        string status "任务状态"
        datetime created_at
        datetime updated_at
        string created_by "创建者"
    }
    
    SystemConfig }|--o{ CronJob : "configures jobs"
    SystemLog ||--|| User : "logs user activity"
    BackupHistory }|--|| SystemConfig : "configured by"
```

## 4. 数据流图

### 4.1 用户认证流程

```mermaid
flowchart TD
    A[用户认证请求] --> B[查询RadCheck]
    B --> C{认证成功?}
    C -->|是| D[查询RadReply]
    C -->|否| E[记录RadPostAuth失败]
    D --> F[返回授权属性]
    F --> G[创建RadAcct会话]
    G --> H[记录RadPostAuth成功]
    E --> I[返回拒绝响应]
```

### 4.2 计费数据处理流程

```mermaid
flowchart TD
    A[NAS发送Accounting-Request] --> B[解析会话数据]
    B --> C{会话类型}
    C -->|Start| D[创建新RadAcct记录]
    C -->|Update| E[更新现有RadAcct记录]
    C -->|Stop| F[完成RadAcct记录]
    D --> G[更新用户统计]
    E --> G
    F --> G
    G --> H[触发计费规则]
    H --> I[更新BillingHistory]
```

### 4.3 系统配置管理流程

```mermaid
flowchart TD
    A[管理员配置变更] --> B[验证操作员权限]
    B --> C{权限检查}
    C -->|通过| D[更新SystemConfig]
    C -->|失败| E[记录访问拒绝日志]
    D --> F[记录配置变更日志]
    F --> G{需要重启?}
    G -->|是| H[标记重启标志]
    G -->|否| I[应用配置]
    H --> I
    I --> J[记录SystemLog]
```

## 5. 性能优化设计

### 5.1 索引策略

1. **主键索引**: 所有表都有自增主键
2. **唯一索引**: 用户名、邮箱等唯一字段
3. **外键索引**: 提高关联查询性能
4. **复合索引**: 常用查询组合字段
5. **时间索引**: 按时间范围查询的字段

### 5.2 分区策略

```sql
-- RadAcct 表按时间分区
CREATE TABLE radacct_y2024m01 PARTITION OF radacct
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- SystemLog 表按日志级别分区  
CREATE TABLE systemlog_error PARTITION OF systemlogs
    FOR VALUES IN ('ERROR', 'CRITICAL');
```

### 5.3 查询优化

1. **预加载关联**: 使用 SQLAlchemy 的 `joinedload`
2. **批量操作**: 避免 N+1 查询问题
3. **缓存策略**: Redis 缓存热点数据
4. **连接池**: 数据库连接池管理
5. **读写分离**: 主从数据库架构支持

## 6. 数据完整性约束

### 6.1 外键约束

```sql
-- 用户相关约束
ALTER TABLE radcheck ADD CONSTRAINT fk_radcheck_username 
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE;

ALTER TABLE radreply ADD CONSTRAINT fk_radreply_username
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE;

-- 计费约束
ALTER TABLE billing_history ADD CONSTRAINT fk_billing_user
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE RESTRICT;
```

### 6.2 业务规则约束

1. **用户名唯一性**: 跨表用户名一致性检查
2. **会话完整性**: RadAcct 记录的开始/结束时间逻辑性
3. **计费一致性**: 使用量与计费记录匹配
4. **权限层次**: 操作员权限继承关系

### 6.3 数据校验

```python
# 用户模型校验示例
class User(BaseModel):
    @validates('email')
    def validate_email(self, key, email):
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError("Invalid email format")
        return email
    
    @validates('username') 
    def validate_username(self, key, username):
        if not re.match(r'^[a-zA-Z0-9_-]{3,64}$', username):
            raise ValueError("Username must be 3-64 chars, alphanumeric")
        return username
```

## 7. 安全设计

### 7.1 敏感数据保护

1. **密码加密**: bcrypt 哈希存储
2. **RADIUS 密钥**: AES 加密存储
3. **审计日志**: 所有敏感操作记录
4. **数据脱敏**: 日志中的敏感信息脱敏

### 7.2 访问控制

```mermaid
graph TD
    A[用户请求] --> B[身份验证]
    B --> C[权限检查]
    C --> D[ACL 验证]
    D --> E[资源访问]
    E --> F[操作审计]
```

### 7.3 数据备份与恢复

1. **定期备份**: 自动化数据库备份
2. **增量备份**: 减少备份时间和存储
3. **加密备份**: 备份文件加密存储
4. **恢复测试**: 定期恢复测试验证

## 8. 监控与维护

### 8.1 性能监控

```python
# 数据库性能监控指标
class DatabaseMetrics:
    - connection_pool_usage: float
    - query_execution_time: dict
    - slow_query_count: int  
    - active_session_count: int
    - lock_wait_time: float
```

### 8.2 数据质量监控

1. **数据一致性检查**: 定期检查外键完整性
2. **业务规则验证**: 自动化业务逻辑检查
3. **异常数据告警**: 异常模式检测和告警
4. **数据清理**: 过期数据自动清理

## 9. 扩展性设计

### 9.1 水平扩展

1. **分库分表**: 按用户或时间维度分片
2. **读写分离**: 主从复制架构
3. **缓存层**: Redis 集群缓存
4. **消息队列**: 异步处理计费数据

### 9.2 功能扩展

1. **插件架构**: 支持第三方插件集成
2. **API 版本控制**: REST API 版本化管理
3. **事件驱动**: 基于事件的松耦合架构
4. **微服务准备**: 模块化设计便于微服务拆分

## 10. 总结

DaloRADIUS Python 后端的数据库设计遵循了现代化的架构原则，通过合理的表结构设计、索引优化、约束定义和安全机制，确保了系统的高性能、高可用性和数据安全性。设计充分考虑了 RADIUS 协议的复杂性和网络计费系统的业务需求，为构建可扩展的网络认证计费平台提供了坚实的数据基础。

### 关键特性

- ✅ **完整的 RADIUS 协议支持**: 包括认证、授权、计费的完整流程
- ✅ **灵活的计费系统**: 支持多种计费模式和业务规则  
- ✅ **强大的用户管理**: 用户生命周期管理和批量操作
- ✅ **细粒度权限控制**: 基于文件和操作的访问控制
- ✅ **全面的审计跟踪**: 完整的操作日志和审计记录
- ✅ **高性能设计**: 合理的索引和查询优化
- ✅ **可扩展架构**: 支持水平扩展和功能扩展

该设计为 DaloRADIUS 系统的 Python 重构提供了现代化、可维护的数据层基础，能够支撑大规模网络环境下的认证计费需求。