# Agent Response Template（供 GitHub Copilot / AI Agent 使用）

说明：每次 agent 会话开始时使用此模版，保证输出格式统一、可验证并遵守仓库的约定（参见 `.github/copilot_instructions.md`）。请保持简洁：首段 1 句宣告 + 1-2 行高层计划；其余按检查表逐项填写。

## 1. 一句话任务接收与高层计划
- Preamble（1句）：我将做什么（为何／预期结果）。
- 高层计划（1-2 行）：如何实现、如何验证。

## 2. 会话 Checklist（每项必须可见并逐项标注状态）
1) 输入/输出契约（必填）
   - 输入（函数/脚本/命令）：
   - 输出/成功判定：
   - 错误模式与异常处理：

2) 三个最重要的边界情况（必填）
   - 空/None/缺失输入：说明如何处理与返回值。
   - 大量数据/性能：说明性能考量、流控或分页策略。
   - 权限/文件系统/并发/超时：说明所需权限、文件锁或超时与重试策略。

3) 最小变更集（必填）
   - 修改的文件/新增文件（列出路径）：
   - 回滚策略（如何恢复到修改前状态，例如 git revert/备份命令）：

4) 快速质量门（必填）
   - 要运行的 lint/类型检查：例如 `flake8`/`mypy` 等（若仓库已有配置则使用其配置）。
   - 单元测试命令（至少 1 个 happy path + 1 边界）：例如 `pytest tests/ -q` 或特定测试用例。
   - 本次执行结果摘要（PASS/FAIL + 关键输出片段 200 字内）。

5) 外部/系统敏感操作声明（必填）
   - 是否会联网或操作内核/系统工具（iptables/ipset/wg/netns/文件等）：是/否。
   - 若是，说明影响、回滚与是否已获许可。

## 3. Actions taken（执行记录，列出命令与关键输出摘要）
- 运行的命令（列出）：
  - 例如：`python -m pytest tests/test_foo.py::test_bar -q`（在这里粘贴关键 stdout/stderr 200 字内摘要）
- 关键输出摘要（200 字内）：

## 4. Files changed（简短列举并说明目的）
- `path/to/file.py` — 目的（例如：修复 x，添加输入校验）。
- `...`

## 5. How to verify（可复制的验证步骤）
- 本地验证命令（复制粘贴即可运行）：

```bash
# 例：运行特定测试
python -m pytest tests/test_simple.py::test_example -q

# 例：lint
flake8 .
```

## 6. Next steps / 未完成项（1-3 条）
- 优先级 1：xxx
- 优先级 2：xxx

## 7. 额外约定（小而重要的规则）
- 提问原则：只有在缺少关键信息时才提问。问题要提供 1-2 个可选答案以便快速决策。 
- Commit message 模版：`<scope>: <短描述>`（如 `fix: validate ip pool parsing`）。
- PR 内容需包含：目的、变更点清单、风险/兼容性说明、回滚方式、测试说明。

## 8. 示例（完整示范填写）
Preamble: 我将为 `api/vnode.py` 的 create 接口增加 IPv4 输入校验，失败返回 400。

Checklist:
1) 输入/输出契约：
   - 输入：JSON body 包含 `ip` 字段。 
   - 输出：成功返回 201；输入错误返回 400。 
   - 错误模式：缺失 ip → 400；格式错误 → 400；其它异常 → 500。
2) 边界情况：
   - 空输入：检查并返回 400；
   - 大量数据：一次请求单个对象，不支持批量；若改为批量需分页；
   - 权限/文件系统：无需文件系统权限；无特权命令。
3) 最小变更集：修改 `api/vnode.py`、新增 `tests/test_vnode_validation.py`。
   - 回滚：`git revert <commit>`。
4) 质量门：运行 `flake8`、`pytest tests/test_vnode_validation.py::test_ip_invalid`。
5) 外部操作声明：无。

Actions taken:
- 修改 `api/vnode.py`，新增测试，运行 pytest → all pass。

How to verify:
- `python -m pytest tests/test_vnode_validation.py -q`

Next steps:
- 合并 PR 并在 CI 上运行完整测试套件。



