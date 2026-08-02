# Iteration 26：clean-wheel 安装器运行时 smoke——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | isolated installer helper | `-I -S` 环境中 preview、approve、apply 成功，三套技能完整安装 |
| AT-02 | evidence contract | `installer_smoke` 包含通过状态、Codex host、三套技能、正文件数，且无绝对路径 |
| AT-03 | full clean acceptance | 7 x 2 结果保留既有依赖来源证据，并增加 portable installer smoke |
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

AT-01 至 AT-04 全部满足且 `git diff --check` 无输出，Iteration 26 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | 通过。真实 wheel 经 `pip --target` 安装后，`python -I -S` 子进程完成 Codex `preview -> approve -> apply`；安装 `backtrader-strategy-author`、`backtrader-strategy-review`、`backtrader-strategy-test` 三套技能，共 15 个文件。 |
| AT-02 | 通过。`distribution.installer_smoke` 仅记录 `passed=true`、`host=codex`、三套已安装技能和 `installed_file_count=15`；不包含临时路径。 |
| AT-03 | 通过。公开 `scripts/run_acceptance.py` forwarder 刷新 7 archetypes x 2 profiles（14 cells）并保留 `filelock` 的 portable `module_path=filelock/__init__.py`、`origin_verified=true` 与 installer smoke。 |
| AT-04 | 通过。`pytest` 为 43 passed；mypy 检查 27 个源文件无问题；Ruff 通过；Black 确认 51 个文件无需变更；`compileall` 通过；manifest 为 `a61762bad1de387b64217bf555a9eeadb323937bb8bdc2a4766aeb2df8cbb847`（66 files）；catalog snapshot 为 1,155 entries；doctor 的 14 项检查全部通过；当前 manifest 下独立 clean-wheel 7 x 2 通过；`git diff --check` 无输出。 |

Iteration 26 验收状态：**通过**。
