# daloRADIUS app/operators 模块功能表

## **计费会计模块（Accounting）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 活跃用户计费查询 | acct-active.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：username, attribute, value, acctstarttime, framedipaddress |
| 全部用户计费记录 | acct-all.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：username, nasipaddress, starttime, stoptime, sessiontime |
| 自定义计费查询 | acct-custom-query.php | `?query={custom_sql}` | `{query: string}` | 自定义查询结果表格 |
| 自定义计费报告 | acct-custom.php | 无 | 无POST表单 | 报告页面框架 |
| 按日期计费查询 | acct-date.php | `?startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：username, acctstarttime, acctstoptime, acctsessiontime |
| 热点计费记录 | acct-hotspot-accounting.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 热点用户计费表格 |
| 热点计费对比 | acct-hotspot-compare.php | `?startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 热点使用对比图表 |
| 热点计费主页 | acct-hotspot.php | 无 | 无POST表单 | 热点计费导航页面 |
| IP地址计费查询 | acct-ipaddress.php | `?framedipaddress={ip_address}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：username, framedipaddress, acctstarttime, acctstoptime |
| 计费主页 | acct-main.php | 无 | 无POST表单 | 计费功能导航页面 |
| 计费维护清理 | acct-maintenance-cleanup.php | 无 | `{cleanup_type: string, older_than: number}` | 操作结果状态 |
| 计费数据删除 | acct-maintenance-delete.php | 无 | `{delete_type: string, date_criteria: string}` | 删除操作结果 |
| 计费维护 | acct-maintenance.php | 无 | 无POST表单 | 维护操作导航页面 |
| NAS IP计费查询 | acct-nasipaddress.php | `?nasipaddress={ip_address}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：username, nasipaddress, acctstarttime, acctstoptime |
| 套餐使用查询 | acct-plans-usage.php | `?planname={plan_name}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 套餐使用统计表格 |
| 套餐计费 | acct-plans.php | 无 | 无POST表单 | 套餐计费导航页面 |
| 用户名计费查询 | acct-username.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 表格显示：acctstarttime, acctstoptime, acctsessiontime, acctinputoctets, acctoutputoctets |

## **账单管理模块（Billing）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 账单历史查询 | bill-history-query.php | `?username={username}&period={period}` | `{username: string, start_date: date, end_date: date}` | 账单历史记录表格 |
| 账单历史 | bill-history.php | 无 | 无POST表单 | 账单历史导航页面 |
| 发票删除 | bill-invoice-del.php | `?invoice_id={id}` | `{invoice_id: int, confirmed: boolean}` | 删除操作结果 |
| 发票编辑 | bill-invoice-edit.php | `?invoice_id={id}` | `{user_id: int, invoice_type_id: int, invoice_status_id: int, invoice_date: date, invoice_notes: string}` | 更新操作结果 |
| 发票列表 | bill-invoice-list.php | `?username={username}&status={status}` | 无POST表单 | 发票列表表格 |
| 新建发票 | bill-invoice-new.php | 无 | `{user_id: int, invoice_type_id: int, invoice_status_id: int, invoice_date: date, invoice_notes: string}` | 创建操作结果 |
| 发票报告 | bill-invoice-report.php | `?invoice_id={id}` | 无POST表单 | PDF发票报告 |
| 发票管理 | bill-invoice.php | 无 | 无POST表单 | 发票管理导航页面 |
| 账单主页 | bill-main.php | 无 | 无POST表单 | 账单功能导航页面 |
| 商户交易 | bill-merchant-transactions.php | `?merchant_id={id}&date_range={range}` | 无POST表单 | 商户交易记录表格 |
| 商户管理 | bill-merchant.php | 无 | `{merchant_name: string, merchant_type: string, contact_info: object}` | 商户操作结果 |
| 支付类型删除 | bill-payment-types-del.php | `?payment_type_id={id}` | `{payment_type_id: int, confirmed: boolean}` | 删除操作结果 |
| 支付类型编辑 | bill-payment-types-edit.php | `?payment_type_id={id}` | `{payment_type_name: string, payment_description: string}` | 更新操作结果 |
| 支付类型列表 | bill-payment-types-list.php | 无 | 无POST表单 | 支付类型列表表格 |
| 新建支付类型 | bill-payment-types-new.php | 无 | `{payment_type_name: string, payment_description: string}` | 创建操作结果 |
| 支付删除 | bill-payments-del.php | `?payment_id={id}` | `{payment_id: int, confirmed: boolean}` | 删除操作结果 |
| 支付编辑 | bill-payments-edit.php | `?payment_id={id}` | `{user_id: int, amount: decimal, payment_date: date, payment_type_id: int, notes: string}` | 更新操作结果 |
| 支付列表 | bill-payments-list.php | `?username={username}&payment_type={type}` | 无POST表单 | 支付记录列表表格 |
| 新建支付 | bill-payments-new.php | 无 | `{user_id: int, amount: decimal, payment_date: date, payment_type_id: int, notes: string}` | 创建操作结果 |
| 支付管理 | bill-payments.php | 无 | 无POST表单 | 支付管理导航页面 |
| 套餐删除 | bill-plans-del.php | `?plan_id={id}` | `{plan_id: int, confirmed: boolean}` | 删除操作结果 |
| 套餐编辑 | bill-plans-edit.php | `?plan_id={id}` | `{plan_name: string, plan_type: string, price: decimal, description: string}` | 更新操作结果 |
| 套餐列表 | bill-plans-list.php | 无 | 无POST表单 | 套餐列表表格 |
| 新建套餐 | bill-plans-new.php | 无 | `{plan_name: string, plan_type: string, price: decimal, description: string}` | 创建操作结果 |
| 套餐管理 | bill-plans.php | 无 | 无POST表单 | 套餐管理导航页面 |
| POS删除 | bill-pos-del.php | `?pos_id={id}` | `{pos_id: int, confirmed: boolean}` | 删除操作结果 |
| POS编辑 | bill-pos-edit.php | `?pos_id={id}` | `{pos_name: string, pos_location: string, merchant_id: int}` | 更新操作结果 |
| POS列表 | bill-pos-list.php | 无 | 无POST表单 | POS设备列表表格 |
| 新建POS | bill-pos-new.php | 无 | `{pos_name: string, pos_location: string, merchant_id: int}` | 创建操作结果 |
| POS管理 | bill-pos.php | 无 | 无POST表单 | POS管理导航页面 |
| 费率按日期 | bill-rates-date.php | `?start_date={yyyy-mm-dd}&end_date={yyyy-mm-dd}` | 无POST表单 | 日期范围费率表格 |
| 费率删除 | bill-rates-del.php | `?rate_id={id}` | `{rate_id: int, confirmed: boolean}` | 删除操作结果 |
| 费率编辑 | bill-rates-edit.php | `?rate_id={id}` | `{rate_name: string, rate_type: string, rate_cost: decimal, rate_setup: decimal}` | 更新操作结果 |
| 费率列表 | bill-rates-list.php | 无 | 无POST表单 | 费率列表表格 |
| 新建费率 | bill-rates-new.php | 无 | `{rate_name: string, rate_type: string, rate_cost: decimal, rate_setup: decimal}` | 创建操作结果 |
| 费率管理 | bill-rates.php | 无 | 无POST表单 | 费率管理导航页面 |

## **配置管理模块（Configuration）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 备份创建 | config-backup-createbackups.php | 无 | `{backup_type: string, include_data: boolean, compression: string}` | 备份操作结果 |
| 备份管理 | config-backup-managebackups.php | 无 | `{backup_file: string, action: string}` | 备份文件管理结果 |
| 备份主页 | config-backup.php | 无 | 无POST表单 | 备份功能导航页面 |
| 定时任务配置 | config-crontab.php | 无 | `{cron_expression: string, command: string, description: string}` | 定时任务配置结果 |
| 数据库配置 | config-db.php | 无 | `{db_host: string, db_port: int, db_name: string, db_user: string, db_pass: string}` | 数据库配置结果 |
| 界面配置 | config-interface.php | 无 | `{theme: string, language: string, items_per_page: int, timezone: string}` | 界面配置结果 |
| 语言配置 | config-lang.php | 无 | `{default_language: string, available_languages: array}` | 语言配置结果 |
| 日志配置 | config-logging.php | 无 | `{log_level: string, log_file: string, max_log_size: int, rotation: boolean}` | 日志配置结果 |
| 邮件设置 | config-mail-settings.php | 无 | `{smtp_host: string, smtp_port: int, smtp_user: string, smtp_pass: string, smtp_encryption: string}` | 邮件配置结果 |
| 邮件测试 | config-mail-testing.php | 无 | `{test_email: string, subject: string, message: string}` | 邮件测试结果 |
| 配置主页 | config-main.php | 无 | 无POST表单 | 配置功能导航页面 |
| 维护断开用户 | config-maint-disconnect-user.php | 无 | `{username: string, nas_ip: string, reason: string}` | 断开操作结果 |
| 维护测试用户 | config-maint-test-user.php | 无 | `{username: string, password: string, nas_ip: string}` | 测试操作结果 |
| 维护配置 | config-maint.php | 无 | 无POST表单 | 维护功能导航页面 |
| 消息配置 | config-messages.php | 无 | `{message_type: string, message_content: string, enabled: boolean}` | 消息配置结果 |
| 操作员删除 | config-operators-del.php | `?operator_id={id}` | `{operator_id: int, confirmed: boolean}` | 删除操作结果 |
| 操作员编辑 | config-operators-edit.php | `?operator_id={id}` | `{username: string, firstname: string, lastname: string, email1: string, phone1: string, department: string, company: string}` | 更新操作结果 |
| 操作员列表 | config-operators-list.php | 无 | 无POST表单 | 操作员列表表格 |
| 新建操作员 | config-operators-new.php | 无 | `{username: string, password: string, firstname: string, lastname: string, title: string, department: string, company: string, phone1: string, phone2: string, email1: string, email2: string, messenger1: string, messenger2: string, notes: string}` | 创建操作结果 |
| 操作员管理 | config-operators.php | 无 | 无POST表单 | 操作员管理导航页面 |
| 报告仪表板配置 | config-reports-dashboard.php | 无 | `{dashboard_layout: object, widgets: array, refresh_interval: int}` | 仪表板配置结果 |
| 报告配置 | config-reports.php | 无 | `{report_settings: object, email_reports: boolean, report_schedule: string}` | 报告配置结果 |
| 用户配置 | config-user.php | 无 | `{user_settings: object, default_group: string, password_policy: object}` | 用户配置结果 |

## **用户管理模块（Management）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 批量添加用户 | mng-batch-add.php | 无 | `{user_list: array, default_group: string, default_password: string}` | 批量添加结果 |
| 批量删除用户 | mng-batch-del.php | 无 | `{user_list: array, confirmed: boolean}` | 批量删除结果 |
| 批量用户列表 | mng-batch-list.php | 无 | 无POST表单 | 批量操作用户列表 |
| 批量管理 | mng-batch.php | 无 | 无POST表单 | 批量操作导航页面 |
| 删除用户 | mng-del.php | `?username={username}` | `{username: string, confirmed: boolean}` | 删除操作结果 |
| 编辑用户 | mng-edit.php | `?username={username}` | `{username: string, password: string, authType: string, firstname: string, lastname: string, email: string, department: string, company: string, workphone: string, homephone: string, mobilephone: string, address: string, city: string, state: string, country: string, zip: string, notes: string, groups: array, dictAttributes: object}` | 更新操作结果 |
| 热点删除 | mng-hs-del.php | `?hotspot_id={id}` | `{hotspot_id: int, confirmed: boolean}` | 删除操作结果 |
| 热点编辑 | mng-hs-edit.php | `?hotspot_id={id}` | `{name: string, mac_address: string, location: string, description: string}` | 更新操作结果 |
| 热点列表 | mng-hs-list.php | 无 | 无POST表单 | 热点列表表格 |
| 新建热点 | mng-hs-new.php | 无 | `{name: string, mac_address: string, location: string, description: string}` | 创建操作结果 |
| 热点管理 | mng-hs.php | 无 | 无POST表单 | 热点管理导航页面 |
| 导入用户 | mng-import-users.php | 无 | `{import_file: file, delimiter: string, enclosure: string, escape: string}` | 导入操作结果 |
| 用户列表（全部） | mng-list-all.php | `?username={username}&group={group}` | 无POST表单 | 用户列表表格 |
| 管理主页 | mng-main.php | 无 | 无POST表单 | 用户管理导航页面 |
| 快速新建用户 | mng-new-quick.php | 无 | `{username: string, password: string}` | 快速创建结果 |
| 新建用户 | mng-new.php | 无 | `{username: string, password: string, authType: string, passwordType: string, macaddress: string, pincode: string, groups: array, firstname: string, lastname: string, email: string, department: string, company: string, workphone: string, homephone: string, mobilephone: string, address: string, city: string, state: string, country: string, zip: string, notes: string, portalLoginPassword: string, changeUserInfo: boolean, enableUserPortalLogin: boolean, dictAttributes: object}` | 创建操作结果 |
| RADIUS属性删除 | mng-rad-attributes-del.php | `?attribute_id={id}` | `{attribute_id: int, confirmed: boolean}` | 删除操作结果 |
| RADIUS属性编辑 | mng-rad-attributes-edit.php | `?attribute_id={id}` | `{username: string, attribute: string, op: string, value: string}` | 更新操作结果 |
| RADIUS属性导入 | mng-rad-attributes-import.php | 无 | `{import_file: file, delimiter: string}` | 导入操作结果 |
| RADIUS属性列表 | mng-rad-attributes-list.php | `?username={username}` | 无POST表单 | 属性列表表格 |
| 新建RADIUS属性 | mng-rad-attributes-new.php | 无 | `{username: string, attribute: string, op: string, value: string}` | 创建操作结果 |
| RADIUS属性搜索 | mng-rad-attributes-search.php | `?attribute={attribute}&value={value}` | `{attribute: string, value: string, op: string}` | 搜索结果表格 |
| RADIUS属性管理 | mng-rad-attributes.php | 无 | 无POST表单 | 属性管理导航页面 |
| 用户搜索 | mng-search.php | `?username={username}&firstname={firstname}&lastname={lastname}` | `{username: string, firstname: string, lastname: string, email: string, department: string}` | 搜索结果表格 |
| 用户管理 | mng-users.php | 无 | 无POST表单 | 用户管理导航页面 |

## **报告分析模块（Reports）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 批量详情报告 | rep-batch-details.php | `?batch_id={id}` | 无POST表单 | 批量操作详情表格 |
| 批量操作列表 | rep-batch-list.php | 无 | 无POST表单 | 批量操作历史列表 |
| 批量报告 | rep-batch.php | 无 | 无POST表单 | 批量操作报告导航页面 |
| 心跳仪表板 | rep-hb-dashboard.php | 无 | 无POST表单 | 系统监控仪表板 |
| 心跳报告 | rep-hb.php | 无 | 无POST表单 | 系统状态报告 |
| 历史报告 | rep-history.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 用户历史记录表格 |
| 最后连接报告 | rep-lastconnect.php | `?username={username}` | 无POST表单 | 最后连接信息表格 |
| 启动日志 | rep-logs-boot.php | 无 | 无POST表单 | 系统启动日志 |
| daloRADIUS日志 | rep-logs-daloradius.php | 无 | 无POST表单 | 应用日志 |
| RADIUS日志 | rep-logs-radius.php | 无 | 无POST表单 | RADIUS服务日志 |
| 系统日志 | rep-logs-system.php | 无 | 无POST表单 | 系统日志 |
| 日志报告 | rep-logs.php | 无 | 无POST表单 | 日志报告导航页面 |
| 报告主页 | rep-main.php | 无 | 无POST表单 | 报告功能导航页面 |
| 新用户报告 | rep-newusers.php | `?startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 新用户统计表格 |
| 在线用户报告 | rep-online.php | 无 | 无POST表单 | 当前在线用户表格 |
| RAID状态 | rep-stat-raid.php | 无 | 无POST表单 | RAID状态信息 |
| 服务器统计 | rep-stat-server.php | 无 | 无POST表单 | 服务器性能统计 |
| 服务状态 | rep-stat-services.php | 无 | 无POST表单 | 系统服务状态 |
| UPS状态 | rep-stat-ups.php | 无 | 无POST表单 | UPS状态信息 |
| 系统统计 | rep-stat.php | 无 | 无POST表单 | 系统统计导航页面 |
| 热门用户报告 | rep-topusers.php | `?orderBy={field}&orderType={asc|desc}&limit={number}` | 无POST表单 | 热门用户统计表格 |
| 用户名报告 | rep-username.php | `?username={username}` | 无POST表单 | 特定用户详情报告 |

## **图表展示模块（Graphs）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 全时间登录图表 | graphs-alltime_logins.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 登录统计图表 |
| 全时间流量对比 | graphs-alltime_traffic_compare.php | `?startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 流量对比图表 |
| 已登录用户图表 | graphs-logged_users.php | 无 | 无POST表单 | 当前登录用户图表 |
| 图表主页 | graphs-main.php | 无 | 无POST表单 | 图表功能导航页面 |
| 总下载量图表 | graphs-overall_download.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 下载流量图表 |
| 总登录次数图表 | graphs-overall_logins.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 登录次数图表 |
| 总上传量图表 | graphs-overall_upload.php | `?username={username}&startdate={yyyy-mm-dd}&enddate={yyyy-mm-dd}` | 无POST表单 | 上传流量图表 |

## **地理信息模块（GIS）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 编辑地图 | gis-editmap.php | `?map_id={id}` | `{map_name: string, coordinates: object, markers: array}` | 地图更新结果 |
| GIS主页 | gis-main.php | 无 | 无POST表单 | GIS功能导航页面 |
| 查看地图 | gis-viewmap.php | `?map_id={id}` | 无POST表单 | 地图显示页面 |

## **认证授权模块（Authentication）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 执行登录 | dologin.php | 无 | `{operator_user: string, operator_pass: string, location: string}` | 登录结果重定向 |
| 登录页面 | login.php | 无 | 无POST表单 | 登录表单页面 |
| 登出 | logout.php | 无 | 无POST表单 | 登出结果重定向 |
| 入口页面 | index.php | 无 | 无POST表单 | 系统入口页面 |

## **系统监控模块（System）**

| 文件功能 | 文件名路径 | URL Schema | 表单数据结构 | 返回数据结构 |
|----------|------------|------------|--------------|--------------|
| 心跳监控 | heartbeat.php | 无 | 无POST表单 | JSON格式系统状态 |
| 帮助页面 | help-main.php | 无 | 无POST表单 | 帮助文档页面 |
| 错误页面 | home-error.php | 无 | 无POST表单 | 错误信息显示 |
| 系统主页 | home-main.php | 无 | 无POST表单 | 系统主页面 |
| 页面底部 | page-footer.php | 无 | 无POST表单 | 页面底部HTML片段 |