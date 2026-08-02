# Iteration 22：受支持 Python CI 矩阵——设计文档

## 工作流结构

~~~text
quality (Python 3.11, .[dev])
  ├─ Ruff
  ├─ Black
  ├─ Mypy
  ├─ catalog check
  └─ manifest check

test-supported-python (Python 3.10 / 3.11 / 3.12 / 3.13, .[test])
  └─ pytest tests -q
~~~

`quality` 保留一个固定解释器，避免同一静态分析在所有版本重复。`test-supported-python`
使用 `strategy.matrix.python-version`，`fail-fast: false` 让一个版本失败时其余版本仍产生诊断。

## 本地配置契约测试

`tests/test_ci_python_matrix.py` 使用标准库文本检查 workflow 的两个 job 区段：

- test job 含有精确的四版本数组、动态 `${{ matrix.python-version }}` 和 `.[test]` 安装；
- quality job 固定 3.11、安装 `.[dev]`，并包含 `python -m mypy src/backtrader_skills`；
- pytest 仅位于矩阵 job，避免测试责任混淆。

该测试验证项目内可审计的配置承诺；GitHub Actions YAML 解析和各解释器真实运行由远端 runner
在 PR/push 触发时承担。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| README/metadata 支持版本与 CI 脱节 | 测试断言精确 3.10–3.13 矩阵 |
| 四倍运行 lint 造成慢且重复 | 质量 job 单独固定 3.11 |
| 某版本失败时丢失其他版本证据 | `fail-fast: false` |
| 把 source-coupled runner 当作 hosted CI 覆盖 | 文档明确其跳过与本地 7 x 2 门禁边界 |
