# Iteration 27：ValidationReport 完整性闭环——需求文档

## 背景与问题

`validation-report-v1.schema.json` 已声明 `validation_hash` 是排除自身字段后的 canonical SHA-256。
`DraftManager.validate()` 也按此规则生成报告并把该 hash 绑定到 write approval token。

但 `DraftManager.apply()` 读取持久化 `validation-report.json` 后只检查
`report["summary"]["passed"]`，没有重新计算 `validation_hash`，也没有验证报告的
`draft_id`、`artifact_hash`、`spec_hash`、`dataset_id` 与当前 draft manifest 的关联。
因此，报告字段可在保留旧 `validation_hash` 的情况下被篡改，仍与原 token 绑定相符，破坏了
“validated report -> approved write”的完整性链。

## 目标

在任何 token claim 和 target mutation 之前，验证持久化 ValidationReport 的 canonical hash、身份绑定
和通过状态；发现篡改或关系漂移时 fail closed。

## 功能需求

### FR-1：验证 hash contract

`apply()` 必须移除 `validation_hash` 后重新计算 canonical hash，并与记录字段完全一致；缺失、类型错误
或不匹配均抛出 `IntegrityError`。

### FR-2：验证 report-to-draft 绑定

报告必须具有 `schema_version=validation-report-v1`，且 `draft_id`、`artifact_hash`、`spec_hash`、
`dataset_id` 分别等于当前已完整性验证的 draft manifest。

### FR-3：一致的通过状态

只有 `status="passed"` 且 `summary.passed is True` 的已验证报告可请求 write approval；不一致或失败
状态必须拒绝。

### FR-4：先拒绝、后 claim

所有上述校验必须发生在 `TokenStore.claim()` 之前。拒绝时不得写 target、不得消费或改变 approval token。

### FR-5：回归覆盖与发布完整性

自动测试要篡改已保存报告（但保留旧 hash 字段），证明 apply 拒绝且 token 仍为 `ISSUED`；随后完成
pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 和差异检查。

## 非目标

- 不将本地 runtime state 变成远程对抗性安全边界。
- 不改变 token 的 TTL、锁粒度、批准流程或策略生成逻辑。
- 不修改用户提供的 `repair --spec --validation-report` 输入契约。

## 成功标准

1. persisted report 的 hash 或 manifest identity 任一漂移都会在 token claim 前失败。
2. 正常 validate -> approve -> apply 流程保持可用。
3. 篡改回归测试证明 token 未消费、target 未写入。
4. 完整发布门禁通过。
