# Iteration 21：比较结果类型契约——需求文档

## 背景与问题

`src/backtrader_skills/types.py` 已把 `MetricComparison` 与 `EventComparison` 声明为稳定的
JSON `TypedDict` 契约，但两个比较函数先构造普通 `dict[str, Any]` 再返回。2026-08-02 的
质量审计运行 `mypy src/backtrader_skills`，在两个返回语句各发现一个 `return-value` 错误。
此外 mypy 已在开发依赖中配置，却不是 GitHub Actions 门禁。

## 目标

使比较 API 的实现、声明类型和自动化门禁一致：源包 mypy 必须通过，CI 必须执行同一检查，
运行时 JSON 字段、比较判定和比较哈希必须保持兼容。

## 功能需求

### FR-1：显式结果类型

`compare_metrics` 构造 `MetricComparison`，`compare_events` 构造 `EventComparison`，指标差异
使用 `MetricDifference`。不得用宽泛 `cast(...)` 掩盖返回类型错误。

### FR-2：哈希兼容性

两个函数仍然对不含 `comparison_hash` 的有效载荷计算哈希，再将其写入结果；相同输入的字段、
通过/失败判定和哈希语义不得变化。

### FR-3：回归验证

新增测试覆盖 metrics 与 events 的完整公开字段和哈希复算，防止静态修复遗漏字段或改变哈希。

### FR-4：持续质量门禁

GitHub Actions 在已有开发依赖安装后运行 `python -m mypy src/backtrader_skills`，本地验收使用
完全相同的路径和命令。

### FR-5：发布完整性

源文件变更后重建并验证 `manifest.json`，并完成测试、静态检查、格式检查、catalog、doctor 和
clean-wheel acceptance。

## 非目标

- 不改变 comparison profile、浮点容差、诊断代码或结果 JSON schema。
- 不把 mypy 扩展到第三方 Backtrader 源码、tests 或生成策略。
- 不在本迭代解决 Python 版本矩阵覆盖；类型修复验收通过后再单独处理。

## 成功标准

1. `mypy src/backtrader_skills` 退出码为 0。
2. 两类比较结果的完整字段和哈希均有回归测试。
3. CI 有显式 Mypy gate。
4. pytest、Ruff、Black、manifest/catalog、doctor 和 7 x 2 clean-wheel acceptance 全部通过。
