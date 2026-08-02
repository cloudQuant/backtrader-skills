# Iteration 24：发布验收证据同步——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | evidence refresh | 公开 forwarder 成功写出 14-cell full matrix JSON |
| AT-02 | evidence 契约测试 | 验证 runtime filelock version/path/origin 和 clean-install 状态 |
| AT-03 | 实施报告 | 历史 25-test 记录与当前 published evidence 语义清晰分开 |
| AT-04 | 发布回归 | pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 通过 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent --output evidence/acceptance-7x2.json
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_published_acceptance_evidence.py -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m mypy src/backtrader_skills
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

## 通过判定

AT-01 至 AT-04 全部满足且 `git diff --check` 无输出，Iteration 24 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | 通过公开 `scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent --output evidence/acceptance-7x2.json` 刷新证据；输出 passed=true、14 cells、filelock 3.32.2、origin_verified=true |
| AT-02 | `tests/test_published_acceptance_evidence.py` 通过，验证 schema、passed、14 cells、clean-install 标识及 filelock 的 version/module_path/origin 字段 |
| AT-03 | `IMPLEMENTATION_REPORT.md` 已将 25 passed 标为 Iteration 17 historical baseline，并明确当前精确发布结果以刷新后的 packaged JSON 为准 |
| AT-04 | pytest 42 passed；mypy 27 个 source files 无问题；Ruff 通过；Black 检查 51 files；manifest `960cbef0d1f9aeeedc127958fa0b640243bbd3b764213c4ba2d7dd8102511516`（66 files）已验证；catalog entries_verified=1155；doctor passed=true、14 checks；clean-wheel 7 x 2 matrix passed=true、14 cells、built-wheel-clean-install、filelock_origin_verified=true |
| 差异完整性 | `git diff --check` 退出码 0，无输出 |

Iteration 24 验收状态：通过。
