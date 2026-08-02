# Iteration 24：发布验收证据同步——需求文档

## 背景与问题

`evidence/acceptance-7x2.json` 被打包进 wheel，`IMPLEMENTATION_REPORT.md` 也把它列为 7 x 2
验收依据。当前实时 `scripts/run_acceptance.py` 输出已包含
`distribution.runtime_dependencies.filelock`，但已发布的 evidence 文件仍是旧结构，缺少这项
依赖来源证明。这会造成源码当前行为、当前验收输出和随 distribution 交付的证据不一致。

## 目标

用当前 clean-wheel 7 x 2 结果刷新发布证据，并加入结构性回归测试，使关键验收证据字段不能
在未来静默落后于已实现的 clean-install 保障。

## 功能需求

### FR-1：刷新分发证据

通过公开的 `scripts/run_acceptance.py`，以默认 source-checkout 解析、完整 matrix、sibling
排除要求和 `--output evidence/acceptance-7x2.json` 生成新的 evidence 文件。

### FR-2：证据结构契约

新增 pytest 验证 packaged evidence 的 `acceptance-result-v1`、14 cells、passed 状态、
`built-wheel-clean-install`、安装来源与 filelock version/module_path/origin_verified=true。

### FR-3：报告语义明确

`IMPLEMENTATION_REPORT.md` 明确区分 Iteration 17 的历史测试数量与会随发布刷新、由 JSON
记录精确结果的 packaged acceptance evidence，避免旧的 25-test 描述被当作当前回归数量。

### FR-4：发布完整性

evidence 和报告变更后重建 manifest，并运行 pytest、mypy、Ruff、Black、catalog、doctor、
clean-wheel acceptance 和差异检查。

## 非目标

- 不改变 acceptance matrix、数据 fixture、Backtrader 代码或结果 schema 的其他字段。
- 不把 nondeterministic run ID、临时目录或 wheel SHA 固定为测试常量。
- 不在本轮建立远端 CI 结果存储或自动推送。

## 成功标准

1. shipped evidence 包含当前 runtime dependency 来源证明。
2. 测试能检测 evidence 丢失关键 clean-install 字段。
3. 报告不再把历史 25 passed 误写为当前产品测试数量。
4. 全部发布门禁通过且 manifest 记录新 evidence 哈希。
