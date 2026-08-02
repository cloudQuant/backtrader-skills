# Iteration 27：ValidationReport 完整性闭环——设计文档

## 处理顺序

~~~text
load draft manifest (already hash-verified)
        |
        v
load validation-report.json
        |
        v
schema + canonical validation_hash valid? -- no --> IntegrityError
        |
       yes
        |
        v
report identity equals manifest? -- no --> IntegrityError
        |
       yes
        |
        v
status == passed and summary.passed is True? -- no --> ContractError
        |
       yes
        |
        v
derive token bindings -> TokenStore.claim -> staged apply
~~~

## 实现边界

在 `DraftManager` 中提取私有 validated-report loader，供 `apply()` 在构造 bindings 前调用。该 loader：

1. 将 JSON 读取和结构检查转换为稳定的产品异常；
2. 以 `canonical_hash(report without validation_hash)` 验证 `validation_hash`；
3. 与已验证 manifest 的四个身份字段精确比对；
4. 单独保留“校验有效但报告失败”的 `ContractError` 语义。

`TokenStore.claim()` 与 `_apply_claimed()` 不变，从而保持 token 和事务职责分离。

## 测试边界

- 真实 draft 完成 validate 后，篡改持久化 `status`（不更新 `validation_hash`）。
- approve 原 token，再调用 apply：预期 `IntegrityError`，token 仍 `ISSUED`，目标文件不存在。
- 既有成功 apply 与 rollback 测试覆盖正常路径不回归。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 报告被错误地当作普通输入 | 在 apply 边界强制 x-hash-contract 与 manifest binding |
| 失败报告被错误归类为损坏 | hash/identity 有效但未通过时保留 ContractError |
| 校验后仍消费 token | 所有验证均在 claim context 之前完成 |
| 破坏正常审批流程 | 复用既有 report 格式与 token bindings，不改变成功路径 |
