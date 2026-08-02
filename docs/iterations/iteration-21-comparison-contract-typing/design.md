# Iteration 21：比较结果类型契约——设计文档

## 数据流

~~~text
comparison profile + left/right inputs
             |
             v
typed differences + diagnostics
             |
             v
MetricComparison / EventComparison（comparison_hash 先置空）
             |
             v
复制并移除 comparison_hash 后 canonical_hash
             |
             v
写回 comparison_hash 并返回
~~~

结果对象首次赋值时就满足全部 `TypedDict` 必填字段。哈希输入从该对象浅复制后移除
`comparison_hash`，与原先“先构造无哈希 dict、再附加哈希”的有效载荷相同。

## 实现边界

- `compare.py` 导入 `MetricDifference`，显式标注差异列表和两类结果对象。
- 不新增运行时类型验证或序列化层；`TypedDict` 仅约束开发期静态检查。
- `tests/test_comparison_type_contract.py` 使用现有 profile/fixtures，复算返回对象哈希并断言
  两类对象的精确键集合。
- CI 在 Ruff 与 Black 后、pytest 前运行 `python -m mypy src/backtrader_skills`。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 误把 `comparison_hash` 纳入哈希 | 测试删除该字段后复算 canonical hash |
| 修复改变 JSON 字段 | 测试断言精确键集合和既有 fixture 判定 |
| 用 cast 隐藏字段缺失 | 显式 TypedDict 构造与 mypy gate |
| CI 与本地命令漂移 | workflow、测试和验收均使用同一 mypy 命令 |
