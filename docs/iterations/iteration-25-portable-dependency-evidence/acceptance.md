# Iteration 25：可携带的依赖来源证据——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | clean dependency probe | module_path 相对、安全且在 live install root 中存在 |
| AT-02 | published evidence | module_path 非绝对、无 `..`，origin_verified=true |
| AT-03 | evidence refresh | full 7 x 2 输出保存可携带 module path |
| AT-04 | 发布回归 | pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 通过 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_clean_wheel_dependencies.py tests/test_published_acceptance_evidence.py -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent --output evidence/acceptance-7x2.json
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

AT-01 至 AT-04 全部满足且 `git diff --check` 无输出，Iteration 25 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | 通过。live clean target 中的 `module_path` 为 `filelock/__init__.py`；测试将其解析回 install root 后确认文件存在且未逃逸。 |
| AT-02 | 通过。发布 evidence 中 `origin_verified=true`、`filelock` 版本为 `3.32.2`，路径为相对 POSIX 路径 `filelock/__init__.py`，无绝对路径或 `..`。 |
| AT-03 | 通过。公开 `scripts/run_acceptance.py` forwarder 刷新 7 archetypes x 2 profiles（14 cells），结果 `passed=true`。 |
| AT-04 | 通过。`pytest` 为 42 passed；mypy 检查 27 个源文件无问题；Ruff 通过；Black 确认 51 个文件无需变更；`compileall` 通过；manifest 为 `cdcb29d3012a924e6f45e325f082fc389cbd0b3f45ed81c2eae519b49adc0a5d`（66 files）；catalog snapshot 为 1,155 entries；doctor 的 14 项检查全部通过；独立 clean-wheel 7 x 2 通过；`git diff --check` 无输出。 |

Iteration 25 验收状态：**通过**。
