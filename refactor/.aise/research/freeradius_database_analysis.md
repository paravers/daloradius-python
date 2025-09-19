# daloradius-python FreeRADIUS 数据表结构研究文档

## 执行概述
本文档深入分析了 daloradius 项目中使用的 FreeRADIUS 标准数据表结构和 daloRADIUS 扩展表结构，识别每个表的业务用途、关键字段和数据关系，为 Python 重构提供准确的数据模型理解基础。

## 数据库架构分析

### 1. FreeRADIUS 核心表结构

#### 1.1 radacct - 会计记录表
**业务用途**：存储用户会话的计费和统计信息
**核心字段**：
- `radacctid`：主键，自增ID
- `username`：用户名，关联用户身份
- `acctsessionid`：会话ID，标识唯一连接
- `acctstarttime`/`acctstoptime`：会话开始/结束时间
- `acctsessiontime`：会话持续时间（秒）
- `acctinputoctets`/`acctoutputoctets`：上传/下载流量（字节）
- `nasipaddress`：NAS设备IP地址
- `framedipaddress`：分配给用户的IP地址
- `acctterminatecause`：会话终止原因

**业务意义**：
- 计费计算的核心数据源
- 用户使用统计和报表基础
- 流量控制和配额管理
- 会话监控和审计

#### 1.2 radcheck - 用户认证检查表
**业务用途**：定义用户级别的认证和授权属性
**核心字段**：
- `username`：用户名
- `attribute`：属性名（如Password、Auth-Type等）
- `op`：操作符（==、:=、!=等）
- `value`：属性值

**业务意义**：
- 用户密码验证
- 用户级别的访问控制
- 特定用户的授权属性定义

#### 1.3 radreply - 用户回复属性表
**业务用途**：定义认证成功后返回给用户的属性
**核心字段**：
- `username`：用户名
- `attribute`：回复属性名
- `op`：操作符
- `value`：属性值

**业务意义**：
- 用户带宽限制
- 会话时间限制
- IP地址分配策略
- 其他用户特定配置

#### 1.4 radgroupcheck - 组认证检查表
**业务用途**：定义用户组级别的认证属性
**核心字段**：
- `groupname`：组名
- `attribute`：属性名
- `op`：操作符
- `value`：属性值

**业务意义**：
- 组级别的访问控制
- 批量用户属性管理
- 分层权限控制

#### 1.5 radgroupreply - 组回复属性表
**业务用途**：定义组级别的回复属性
**核心字段**：
- `groupname`：组名
- `attribute`：回复属性名
- `op`：操作符
- `value`：属性值

**业务意义**：
- 组级别的服务配置
- 统一的组策略管理

#### 1.6 radusergroup - 用户组关联表
**业务用途**：建立用户与组的多对多关系
**核心字段**：
- `username`：用户名
- `groupname`：组名
- `priority`：优先级（数字越小优先级越高）

**业务意义**：
- 用户组成员关系管理
- 权限继承和优先级控制
- 灵活的用户分类管理

#### 1.7 radpostauth - 认证后记录表
**业务用途**：记录用户认证尝试的详细信息
**核心字段**：
- `username`：用户名
- `pass`：密码（通常为加密或掩码）
- `reply`：认证结果
- `authdate`：认证时间

**业务意义**：
- 安全审计和日志记录
- 认证失败分析
- 用户行为监控

#### 1.8 nas - 网络接入服务器表
**业务用途**：定义和管理NAS设备配置
**核心字段**：
- `nasname`：NAS设备名称或IP
- `shortname`：简短名称
- `secret`：共享密钥
- `type`：设备类型
- `ports`：端口数

**业务意义**：
- NAS设备认证和授权
- 设备配置管理
- 网络拓扑维护

#### 1.9 radippool - IP地址池表
**业务用途**：管理动态IP地址分配
**核心字段**：
- `pool_name`：IP池名称
- `framedipaddress`：IP地址
- `username`：分配的用户名
- `expiry_time`：过期时间

**业务意义**：
- 动态IP地址管理
- IP地址回收和重用
- 用户IP分配追踪

### 2. daloRADIUS 扩展表结构

#### 2.1 billing_plans - 计费套餐表
**业务用途**：定义各种计费套餐和服务包
**核心字段**：
- `planName`：套餐名称
- `planType`：套餐类型
- `planTimeBank`：时间配额
- `planCost`：套餐费用
- `planBandwidthUp`/`planBandwidthDown`：上传/下载带宽
- `planRecurring`：是否循环计费
- `planActive`：套餐激活状态

**业务意义**：
- 产品套餐定义和管理
- 价格策略配置
- 服务质量控制

#### 2.2 billing_history - 计费历史表
**业务用途**：记录用户的计费和支付历史
**核心字段**：
- `username`：用户名
- `billAmount`：账单金额
- `billAction`：计费动作
- `paymentmethod`：支付方式
- `creationdate`：创建时间

**业务意义**：
- 财务记录和审计
- 用户消费历史追踪
- 收入分析和报表

#### 2.3 userinfo - 用户信息表
**业务用途**：存储用户详细个人信息
**核心字段**：
- `username`：用户名（关联主键）
- `firstname`/`lastname`：姓名
- `email`：邮箱
- `department`：部门
- `company`：公司
- `workphone`：工作电话
- `homephone`：家庭电话
- `mobilephone`：手机号码

**业务意义**：
- 用户档案管理
- 联系信息维护
- 客户关系管理

#### 2.4 userbillinfo - 用户计费信息表
**业务用途**：用户计费状态和套餐关联
**核心字段**：
- `username`：用户名
- `planName`：关联的套餐名称
- `billstatus`：计费状态
- `creationdate`：创建时间
- `creationby`：创建者

**业务意义**：
- 用户套餐绑定关系
- 计费状态跟踪
- 用户生命周期管理

#### 2.5 operators - 操作员表
**业务用途**：系统操作员账户管理
**核心字段**：
- `username`：操作员用户名
- `password`：密码（加密）
- `firstname`/`lastname`：操作员姓名
- `department`：所属部门
- `company`：所属公司

**业务意义**：
- 后台管理员权限控制
- 操作审计和责任追踪
- 分级管理体系

#### 2.6 hotspots - 热点管理表
**业务用途**：管理Wi-Fi热点和接入点信息
**核心字段**：
- `name`：热点名称
- `mac`：MAC地址
- `geocode`：地理编码
- `owner`：所有者
- `company`：所属公司

**业务意义**：
- 热点位置管理
- 设备资产跟踪
- 地理统计分析

## 数据关系分析

### 核心业务流程的数据流向

#### 用户认证流程
```
nas → radcheck/radgroupcheck → radusergroup → radreply/radgroupreply → radpostauth
```

#### 计费流程
```
radacct → billing_plans → userbillinfo → billing_history
```

#### 用户管理流程
```
userinfo → radcheck → radusergroup → userbillinfo
```

### 关键关联关系

1. **用户认证关系**：
   - `radcheck.username` ← 一对多 → `radusergroup.username`
   - `radusergroup.groupname` ← 多对一 → `radgroupcheck.groupname`

2. **计费关系**：
   - `radacct.username` ← 一对多 → `userbillinfo.username`
   - `userbillinfo.planName` ← 多对一 → `billing_plans.planName`

3. **用户信息关系**：
   - `userinfo.username` ← 一对一 → `radcheck.username`
   - `userinfo.username` ← 一对一 → `userbillinfo.username`

4. **热点关系**：
   - `hotspots.mac` ← 一对多 → `radacct.calledstationid`

## 业务规则总结

### 认证授权规则
- 用户可属于多个组，通过优先级决定生效顺序
- 组属性和用户属性可同时生效，用户属性优先级更高
- 认证成功后返回组合的回复属性

### 计费规则
- 每个用户对应一个计费套餐
- 套餐定义时间、流量、带宽等限制
- 会计记录用于实际使用量统计

### 数据一致性要求
- 用户删除需级联删除相关记录
- 组删除需检查关联用户
- 计费套餐修改需考虑已绑定用户

---

本研究文档为Python版本数据模型设计提供准确的业务理解和表结构参考。