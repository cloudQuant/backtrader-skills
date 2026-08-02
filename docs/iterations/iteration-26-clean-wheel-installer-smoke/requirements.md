# Iteration 26：clean-wheel 安装器运行时 smoke——需求文档

## 背景与问题

当前 clean-wheel acceptance 已验证 built wheel 可在隔离 install root 中导入核心运行链和
`filelock`。wheel 内容测试也断言三套技能资产位于 archive 内，但没有在安装后的实际 data-files
布局中调用 `SkillInstaller`。

因此，`distribution_root()` 的 wheel 安装布局解析、技能资产发现和受保护安装写入仍缺少自动化
发布门禁；一次 data-files layout 回归可能通过静态 archive 名称检查，却使用户安装后的
`install preview/apply` 失败。

## 目标

在既有 isolated clean-wheel acceptance 内，以 `python -I -S` 和仅 install root 的模块路径运行
技能安装器 preview、显式 token approval 与 apply，证明 wheel 内的 canonical skills 在安装后可用。

## 功能需求

### FR-1：隔离的安装器执行

在 wheel 安装完成后，子进程必须以 `-I -S` 启动，仅将 clean install root 插入 `sys.path`，再导入
`SkillInstaller`、`RuntimePaths` 与 `SKILL_NAMES`。不得依赖 source checkout 或全局 site-packages。

### FR-2：端到端技能安装

子进程必须在临时 target 上执行 `preview_install("codex")`，显式 approve 返回 token，随后执行
`apply_install`。三套 canonical skills 的 `SKILL.md` 都必须出现在 `.agents/skills` 下。

### FR-3：可携带证据

clean acceptance 结果需记录 `distribution.installer_smoke`，只包含通过状态、host、已安装 skill
名称和文件数量等可携带信息；不得包含临时绝对路径。

### FR-4：回归覆盖

测试必须校验隔离 smoke 的成功结果及 published evidence 的 installer smoke 字段。任何非 JSON、失败
状态、缺失技能或绝对路径泄漏均应令 acceptance 失败。

### FR-5：发布完整性

刷新发布 evidence 与 manifest，并通过 pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel
7 x 2 和差异检查。

## 非目标

- 不模拟 Claude、Codex、OpenCode 或 OpenClaw 宿主二进制的 live discovery。
- 不改变四宿主路径映射、create-only 语义或 uninstall 行为。
- 不改变 general same-target CLI 并发不受支持的边界。

## 成功标准

1. clean installed wheel 能从安装后资源布局解析 canonical skills。
2. 隔离子进程完成 Codex host 的 preview、approval 与 apply，并安装全部三套技能。
3. published evidence 包含无绝对路径的 installer smoke 结果。
4. 完整发布门禁通过。
