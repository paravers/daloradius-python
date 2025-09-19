# daloRADIUS Web 页面分析计划

## 设计原则指导

本分析计划严格遵循 design.prompt.md 的核心原则：

### 核心设计原则
1. **SRP (单一职责原则)**: 每个页面分析专注于一个明确的功能点
2. **OCP (开闭原则)**: 设计应易于扩展的 RESTful API 架构
3. **KISS (保持简单原则)**: 分析必须尽可能简单直接
4. **YAGNI (你不会需要它)**: 只针对当前明确的需求进行设计分析
5. **DIP (依赖倒置原则)**: 专注于抽象接口设计而非具体实现

## 分析框架与方法论

### 分析维度
每个页面分析包含以下三个维度：

1. **数据层面分析**
   - 输入数据结构和验证规则
   - 输出数据格式和内容
   - 数据库操作和关联关系
   - 数据流向和转换逻辑

2. **UI结构分析**
   - 页面布局组件结构
   - 数据呈现的具体UI组件
   - 交互模式和用户体验流程
   - 表单、表格、图表等组件的使用

3. **现代化设计建议**
   - Python RESTful API 接口设计
   - 前后端分离的 Vue 组件架构
   - 数据模型和业务逻辑抽象
   - 性能和安全考量

### 分析标准化模板

每个页面分析文档将采用以下标准结构：

```markdown
# {页面名称} 分析报告

## 模块概述
- 职责：页面核心功能描述
- 业务价值：在整体系统中的作用

## 数据层面分析

### 输入数据结构
- HTTP 方法和参数
- 表单字段和验证规则
- 文件上传和特殊输入

### 数据处理逻辑
- 数据库查询和更新操作
- 业务规则和计算逻辑
- 数据转换和格式化

### 输出数据结构
- 页面展示数据
- JSON/XML 响应格式
- 错误和状态信息

## UI结构分析

### 页面布局架构
- 主要布局区域划分
- 导航和操作区域
- 内容展示区域

### 核心UI组件
- 表单组件及其字段
- 数据表格及其列结构
- 图表和可视化组件
- 交互控件（按钮、链接、模态框）

### 用户交互流程
- 用户操作路径
- 状态变化和反馈
- 错误处理和提示

## Python RESTful API 设计

### 接口规范
- REST 资源路径设计
- HTTP 方法映射
- 请求和响应格式

### 数据模型
- Pydantic 模型定义
- 数据验证和序列化
- 关联关系处理

### 业务逻辑层
- Service 层抽象
- 业务规则实现
- 错误处理机制

## Vue 前端组件设计

### 组件架构
- 页面级组件设计
- 可复用子组件
- 组件通信机制

### 状态管理
- 页面状态设计
- 数据流管理
- 异步操作处理

### 用户体验增强
- 响应式设计考虑
- 性能优化建议
- 无障碍访问支持

## 技术债务和改进建议

### 当前实现的局限性
### 重构优先级评估
### 性能和安全考量
```

## 任务分解计划

根据模块复杂度和业务优先级，将 189 个页面分为以下执行批次：

### 第一批：系统基础页面 (9个文件) - 立即执行
**优先级：最高** - 为后续分析建立基础模式

1. `index.php` - 系统入口页面
2. `login.php` - 用户登录页面
3. `logout.php` - 用户登出页面
4. `dologin.php` - 登录处理页面
5. `home-main.php` - 系统主页
6. `home-error.php` - 错误处理页面
7. `help-main.php` - 帮助页面
8. `heartbeat.php` - 心跳检测页面
9. `page-footer.php` - 页面底部组件

### 第二批：用户管理核心页面 (8个文件) - 第1周
**优先级：高** - 系统核心功能

10. `mng-main.php` - 用户管理主页
11. `mng-new.php` - 新建用户页面
12. `mng-edit.php` - 编辑用户页面
13. `mng-del.php` - 删除用户页面
14. `mng-list-all.php` - 用户列表页面
15. `mng-search.php` - 用户搜索页面
16. `mng-new-quick.php` - 快速新建用户页面
17. `mng-users.php` - 用户管理入口页面

### 第三批：计费管理核心页面 (12个文件) - 第2周
**优先级：高** - 业务关键功能

18. `bill-main.php` - 计费管理主页
19. `bill-invoice.php` - 发票管理主页
20. `bill-invoice-new.php` - 新建发票页面
21. `bill-invoice-edit.php` - 编辑发票页面
22. `bill-invoice-del.php` - 删除发票页面
23. `bill-invoice-list.php` - 发票列表页面
24. `bill-payments.php` - 支付管理主页
25. `bill-payments-new.php` - 新建支付记录页面
26. `bill-payments-edit.php` - 编辑支付记录页面
27. `bill-payments-del.php` - 删除支付记录页面
28. `bill-payments-list.php` - 支付记录列表页面
29. `bill-plans.php` - 计费计划主页

### 第四批：会计模块页面 (17个文件) - 第3周
**优先级：中高** - 数据分析基础

30. `acct-main.php` - 会计主页
31. `acct-active.php` - 活跃用户会计
32. `acct-all.php` - 所有用户会计
33. `acct-username.php` - 按用户名会计
34. `acct-ipaddress.php` - 按IP地址会计
35. `acct-nasipaddress.php` - 按NAS IP会计
36. `acct-date.php` - 按日期会计
37. `acct-hotspot.php` - 热点会计主页
38. `acct-hotspot-accounting.php` - 热点会计记录
39. `acct-hotspot-compare.php` - 热点会计比较
40. `acct-plans.php` - 计费计划会计主页
41. `acct-plans-usage.php` - 计费计划使用情况
42. `acct-maintenance.php` - 维护主页
43. `acct-maintenance-cleanup.php` - 维护清理
44. `acct-maintenance-delete.php` - 维护删除
45. `acct-custom.php` - 自定义会计主页
46. `acct-custom-query.php` - 自定义查询

### 第五批：配置管理页面 (23个文件) - 第4周
**优先级：中** - 系统管理功能

47. `config-main.php` - 系统配置主页
48. `config-db.php` - 数据库配置
49. `config-interface.php` - 界面配置
50. `config-lang.php` - 语言配置
51. `config-logging.php` - 日志配置
52. `config-messages.php` - 消息配置
53. `config-mail-settings.php` - 邮件设置
54. `config-mail-testing.php` - 邮件测试
55. `config-backup.php` - 备份管理主页
56. `config-backup-createbackups.php` - 创建备份
57. `config-backup-managebackups.php` - 管理备份
58. `config-operators.php` - 操作员管理主页
59. `config-operators-new.php` - 新建操作员
60. `config-operators-edit.php` - 编辑操作员
61. `config-operators-del.php` - 删除操作员
62. `config-operators-list.php` - 操作员列表
63. `config-maint.php` - 维护主页
64. `config-maint-disconnect-user.php` - 断开用户连接
65. `config-maint-test-user.php` - 测试用户
66. `config-crontab.php` - 定时任务配置
67. `config-reports.php` - 报告配置主页
68. `config-reports-dashboard.php` - 报告仪表板配置
69. `config-user.php` - 用户配置

### 第六批：报表模块页面 (22个文件) - 第5周
**优先级：中** - 数据展示功能

70. `rep-main.php` - 报表主页
71. `rep-online.php` - 在线用户报表
72. `rep-lastconnect.php` - 最后连接报表
73. `rep-newusers.php` - 新用户报表
74. `rep-topusers.php` - 热门用户报表
75. `rep-username.php` - 按用户名报表
76. `rep-history.php` - 历史报表
77. `rep-batch.php` - 批量操作报表主页
78. `rep-batch-list.php` - 批量操作列表
79. `rep-batch-details.php` - 批量操作详情
80. `rep-stat.php` - 系统状态主页
81. `rep-stat-server.php` - 服务器状态
82. `rep-stat-services.php` - 服务状态
83. `rep-stat-raid.php` - RAID状态
84. `rep-stat-ups.php` - UPS状态
85. `rep-logs.php` - 日志报表主页
86. `rep-logs-radius.php` - RADIUS日志
87. `rep-logs-daloradius.php` - daloRADIUS日志
88. `rep-logs-system.php` - 系统日志
89. `rep-logs-boot.php` - 启动日志
90. `rep-hb.php` - 心跳主页
91. `rep-hb-dashboard.php` - 心跳仪表板

### 第七批：计费管理剩余页面 (24个文件) - 第6周
**优先级：中** - 完善计费功能

92. `bill-invoice-report.php` - 发票报告
93. `bill-payment-types-new.php` - 新建支付类型
94. `bill-payment-types-edit.php` - 编辑支付类型
95. `bill-payment-types-del.php` - 删除支付类型
96. `bill-payment-types-list.php` - 支付类型列表
97. `bill-plans-new.php` - 新建计费计划
98. `bill-plans-edit.php` - 编辑计费计划
99. `bill-plans-del.php` - 删除计费计划
100. `bill-plans-list.php` - 计费计划列表
101. `bill-rates.php` - 费率管理主页
102. `bill-rates-new.php` - 新建费率
103. `bill-rates-edit.php` - 编辑费率
104. `bill-rates-del.php` - 删除费率
105. `bill-rates-list.php` - 费率列表
106. `bill-rates-date.php` - 按日期查看费率
107. `bill-pos.php` - POS管理主页
108. `bill-pos-new.php` - 新建POS
109. `bill-pos-edit.php` - 编辑POS
110. `bill-pos-del.php` - 删除POS
111. `bill-pos-list.php` - POS列表
112. `bill-merchant.php` - 商户管理主页
113. `bill-merchant-transactions.php` - 商户交易记录
114. `bill-history.php` - 计费历史主页
115. `bill-history-query.php` - 计费历史查询

### 第八批：用户管理批量操作 (4个文件) - 第7周
**优先级：中** - 批量处理功能

116. `mng-batch.php` - 批量操作主页
117. `mng-batch-add.php` - 批量添加用户
118. `mng-batch-del.php` - 批量删除用户
119. `mng-batch-list.php` - 批量操作列表

### 第九批：热点管理页面 (5个文件) - 第7周
**优先级：中** - WiFi管理功能

120. `mng-hs.php` - 热点管理主页
121. `mng-hs-new.php` - 新建热点
122. `mng-hs-edit.php` - 编辑热点
123. `mng-hs-del.php` - 删除热点
124. `mng-hs-list.php` - 热点列表

### 第十批：RADIUS属性管理 (7个文件) - 第8周
**优先级：中** - RADIUS配置功能

125. `mng-rad-attributes.php` - RADIUS属性主页
126. `mng-rad-attributes-new.php` - 新建属性
127. `mng-rad-attributes-edit.php` - 编辑属性
128. `mng-rad-attributes-del.php` - 删除属性
129. `mng-rad-attributes-list.php` - 属性列表
130. `mng-rad-attributes-search.php` - 属性搜索
131. `mng-rad-attributes-import.php` - 属性导入

### 第十一批：用户组管理 (6个文件) - 第8周
**优先级：中** - 权限管理功能

132. `mng-rad-groups.php` - 用户组主页
133. `mng-rad-usergroup.php` - 用户组关系主页
134. `mng-rad-usergroup-new.php` - 新建用户组关系
135. `mng-rad-usergroup-edit.php` - 编辑用户组关系
136. `mng-rad-usergroup-del.php` - 删除用户组关系
137. `mng-rad-usergroup-list.php` - 用户组关系列表
138. `mng-rad-usergroup-list-user.php` - 按用户列出组关系

### 第十二批：组检查和回复属性 (10个文件) - 第9周
**优先级：中低** - RADIUS高级配置

139. `mng-rad-groupcheck-new.php` - 新建组检查属性
140. `mng-rad-groupcheck-edit.php` - 编辑组检查属性
141. `mng-rad-groupcheck-del.php` - 删除组检查属性
142. `mng-rad-groupcheck-list.php` - 组检查属性列表
143. `mng-rad-groupcheck-search.php` - 组检查属性搜索
144. `mng-rad-groupreply-new.php` - 新建组回复属性
145. `mng-rad-groupreply-edit.php` - 编辑组回复属性
146. `mng-rad-groupreply-del.php` - 删除组回复属性
147. `mng-rad-groupreply-list.php` - 组回复属性列表
148. `mng-rad-groupreply-search.php` - 组回复属性搜索

### 第十三批：配置文件管理 (6个文件) - 第9周
**优先级：中低** - RADIUS配置文件

149. `mng-rad-profiles.php` - 配置文件主页
150. `mng-rad-profiles-new.php` - 新建配置文件
151. `mng-rad-profiles-edit.php` - 编辑配置文件
152. `mng-rad-profiles-del.php` - 删除配置文件
153. `mng-rad-profiles-list.php` - 配置文件列表
154. `mng-rad-profiles-duplicate.php` - 复制配置文件

### 第十四批：网络设备管理 - NAS (5个文件) - 第10周
**优先级：中低** - 网络基础设施

155. `mng-rad-nas.php` - NAS主页
156. `mng-rad-nas-new.php` - 新建NAS
157. `mng-rad-nas-edit.php` - 编辑NAS
158. `mng-rad-nas-del.php` - 删除NAS
159. `mng-rad-nas-list.php` - NAS列表

### 第十五批：网络设备管理 - 代理和IP池 (9个文件) - 第10周
**优先级：中低** - 网络基础设施

160. `mng-rad-proxys-new.php` - 新建代理
161. `mng-rad-proxys-edit.php` - 编辑代理
162. `mng-rad-proxys-del.php` - 删除代理
163. `mng-rad-proxys-list.php` - 代理列表
164. `mng-rad-ippool.php` - IP池主页
165. `mng-rad-ippool-new.php` - 新建IP池
166. `mng-rad-ippool-edit.php` - 编辑IP池
167. `mng-rad-ippool-del.php` - 删除IP池
168. `mng-rad-ippool-list.php` - IP池列表

### 第十六批：网络设备管理 - Hunt组和域 (10个文件) - 第11周
**优先级：中低** - 网络基础设施

169. `mng-rad-hunt.php` - Hunt组主页
170. `mng-rad-hunt-new.php` - 新建Hunt组
171. `mng-rad-hunt-edit.php` - 编辑Hunt组
172. `mng-rad-hunt-del.php` - 删除Hunt组
173. `mng-rad-hunt-list.php` - Hunt组列表
174. `mng-rad-realms.php` - 域主页
175. `mng-rad-realms-new.php` - 新建域
176. `mng-rad-realms-edit.php` - 编辑域
177. `mng-rad-realms-del.php` - 删除域
178. `mng-rad-realms-list.php` - 域列表

### 第十七批：用户导入和图表模块 (8个文件) - 第11周
**优先级：低** - 辅助功能

179. `mng-import-users.php` - 用户导入
180. `graphs-main.php` - 图表主页
181. `graphs-overall_logins.php` - 总体登录图表
182. `graphs-overall_download.php` - 总体下载图表
183. `graphs-overall_upload.php` - 总体上传图表
184. `graphs-alltime_logins.php` - 历史登录图表
185. `graphs-alltime_traffic_compare.php` - 历史流量比较图表
186. `graphs-logged_users.php` - 已登录用户图表

### 第十八批：GIS模块 (3个文件) - 第12周
**优先级：最低** - 地理信息增值功能

187. `gis-main.php` - GIS主页
188. `gis-viewmap.php` - 查看地图
189. `gis-editmap.php` - 编辑地图

## 执行策略和质量保证

### 并行执行策略
- **快速通道**：系统基础页面可以并行分析
- **核心通道**：用户管理和计费管理按依赖关系顺序执行
- **支撑通道**：配置和报表模块可以并行进行

### 质量检查点
1. **每批次结束**：进行跨页面模式一致性检查
2. **每周结束**：进行 API 设计一致性审查
3. **每两周**：进行组件复用性评估

### 风险控制
- **复杂度控制**：如单个页面分析超过预期复杂度，拆分为多个子任务
- **依赖管理**：确保核心模块分析完成后再进行相关模块
- **质量保证**：每个分析文档都需要经过设计原则符合性检查

## 输出规范

### 文件命名规范
- 格式：`analysis_{module}_{page_name}.md`
- 示例：`analysis_mng_new_user.md`

### 文档结构一致性
- 严格遵循标准化模板
- 保持技术术语的一致性
- 确保设计原则的正确应用

### 交付物检查清单
- [ ] 数据层面分析完整性
- [ ] UI结构分析准确性
- [ ] RESTful API设计合理性
- [ ] Vue组件设计可行性
- [ ] 设计原则符合性
- [ ] 文档格式规范性

这个分析计划确保了系统性、渐进性和质量可控性，为 daloRADIUS 的现代化重构提供了清晰的路线图。