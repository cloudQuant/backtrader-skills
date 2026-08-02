# Iteration 22：受支持 Python CI 矩阵——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | CI 配置契约测试 | 精确 3.10–3.13 matrix、动态 Python、正确 extras/job 分工 |
| AT-02 | quality job | 固定 3.11，Ruff、Black、Mypy、catalog、manifest 各运行一次 |
| AT-03 | test job | 四个 Python 单元各安装 `.[test]` 并运行 pytest |
| AT-04 | 本地完整回归 | pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 通过 |
| AT-05 | hosted 执行边界 | 文档记录四版本真实执行由后续 PR/push 的 GitHub Actions 产生，不伪造远端结果 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_ci_python_matrix.py -v -p no:cacheprovider
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

AT-01 至 AT-04 全部满足、AT-05 的边界明确记录且 `git diff --check` 无输出，即通过本地实现
验收；远端四版本实际执行结果需由后续 PR/push 的 GitHub Actions 记录。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | `tests/test_ci_python_matrix.py` 通过，断言 quality/test job 区分、精确四版本矩阵、动态 setup-python 与各自 extras；workflow 也已完成 YAML 解析检查 |
| AT-02 | `quality` 固定 `python-version: "3.11"`，安装 `.[dev]`，依次运行 Ruff、Black、Mypy、catalog 与 manifest；其中 pytest 不在该 job |
| AT-03 | `test-supported-python` 配置 `fail-fast: false` 和 `["3.10", "3.11", "3.12", "3.13"]`，使用 `${{ matrix.python-version }}`，安装 `.[test]` 后唯一运行一次 pytest 命令 |
| AT-04 | pytest 40 passed；mypy 27 个 source files 无问题；Ruff 通过；Black 检查 49 files；manifest `1750b81efa5c606f21f11c53e8d08bc7ec24785af47e2d06360ec68772617268`（66 files）已验证；catalog entries_verified=1155；doctor passed=true、14 checks；clean-wheel 7 x 2 matrix passed=true、14 cells、built-wheel-clean-install、installed_origin_verified=true |
| AT-05 | 本轮未推送分支或创建 PR，因此未伪造 GitHub-hosted 四版本结果；workflow 将在用户后续 push/PR 时实际执行 3.10–3.13。依赖 Backtrader source 的 runner 验收已由本地 7 x 2 gate 覆盖 |
| 差异完整性 | `git diff --check` 退出码 0，无输出 |

Iteration 22 本地实现验收状态：通过；GitHub-hosted 四版本执行状态：待后续 PR/push 触发。
