## Copilot / AI Agent 指引（为本仓库定制，简明版）

说明：这是为本项目精简过的 agent 指南，旨在让 AI agent 快速、安全且可验证地在仓库中修改代码。要求 agent 要诚实，科学，理性，别猜测。如果你对一个事情（对象，对象的方法，名称等等）如果不确定或者没有信息，你就需要先去找到相应的源文件做确认。

1. 开场（必须）

- 一句中文：要做什么与为何。1-2 行高层计划（如何实现、如何验证）。
- 使用仓库内的 `.github/agent-response-template.md` 来格式化会话产出。
- 如果有不明确的问题或者需求，请不要猜测，先和我确认。

2. 必须可见的 Checklist（每项在会话中回答）

- 输入/输出契约（接口、命令、成功判定、错误模式）。
- 三个关键边界情况（空/None、性能/大数据、权限/文件系统/并发/超时）。
- 最小变更集（列出文件）与回滚命令（如 `git revert <sha>`）。
- 质量门：运行 lint/mypy（如配置存在）与至少 1 个 happy-path + 1 个边界测试。
- 外部/系统敏感操作须声明（例如修改 iptables、wg、netns、/etc/\*）；

3. 本仓库的关键约定（参考示例文件）

- 代码风格：Python 3.8+，PEP8，优先类型注解。
- 测试：所生成的 python 代码需要经过`mypy`及`flake8 --ignore E501,W293`静态代码检查。
- 快速本地 smoke-test：可运行 `python sdn/controller/service/{module}/run_tests.py`（仓库中已有此脚本用于本地验证）。
- 软件工程中的过程文档放在每个模块的`.aise`目录下面，`.aise`有 requirement,design,research,plan,report,implement(log),review 目录。agent 交互过程中生成的文档或临时代码，需要按照其目录结构摆放。

4. 与系统/网络交互的具体规则

- 修改系统状态（iptables/ipset/wg/netns/sysctl）前必须：保存当前状态、使用完整路径、捕获错误码、并在 PR 中提供恢复命令。

5. 项目特有模式（不可忽略）

- 配置优先环境变量，避免硬编码敏感数据（查 `config/` 目录）。

6. 交付产物（每次会话结尾必须提供）

- 变更清单（修改/新增文件）。
- 执行的命令与关键输出摘要（stdout/stderr 200 字内）。
- 测试结果（PASS/FAIL）。

7. 例子（短）

- 任务：为 `api/service.py` 的 create 接口添加 IPv4 校验。质量门：新增测试通过且 `flake8 --ignore=W293,E501` 无错误。验证：`python -m pytest tests/test_service_validation.py -q`。

9. 真实环境的信息

- 如果要使用开发的真实环境进行调试，这里是相关的一些配置文件`sdn/config/test_env_config.py`
