# Iteration 21：比较结果类型契约——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | `mypy src/backtrader_skills` | exit 0，无类型错误 |
| AT-02 | metrics 比较结果 | 键集合完整，删除 comparison_hash 后复算哈希一致 |
| AT-03 | events 比较结果 | 键集合完整，删除 comparison_hash 后复算哈希一致 |
| AT-04 | CI 配置 | 有 `python -m mypy src/backtrader_skills` gate |
| AT-05 | 发布回归 | pytest、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 均通过 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_comparison_type_contract.py -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m mypy src/backtrader_skills
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

## 通过判定

AT-01 至 AT-05 全部满足且 `git diff --check` 无输出，Iteration 21 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | `mypy src/backtrader_skills`：27 个 source files，`Success: no issues found` |
| AT-02 | `tests/test_comparison_type_contract.py` 的 metrics 用例通过，断言完整键集合、fixture 判定与去除 comparison_hash 后的 canonical hash 一致 |
| AT-03 | 同一测试的 events 用例通过，断言完整键集合、规范化字段和 hash 一致 |
| AT-04 | `.github/workflows/ci.yml` 已加入名为 `Mypy` 的 `python -m mypy src/backtrader_skills` step |
| AT-05 | pytest 39 passed；Ruff 通过；Black 检查 48 files；manifest `1750b81efa5c606f21f11c53e8d08bc7ec24785af47e2d06360ec68772617268`（66 files）已验证；catalog check 退出码 0；默认 doctor 14 项 checks 全通过；clean-wheel 7 x 2 matrix passed=true、14 cells、data_profile_gate=true、repair_gate=true、installed_origin_verified=true |
| 差异完整性 | `git diff --check` 退出码 0，无输出 |

Iteration 21 验收状态：通过。
