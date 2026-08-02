# Iteration 23：clean-wheel 运行时依赖隔离——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | clean wheel install | 有 `--ignore-installed --target`，无 `--no-deps` |
| AT-02 | `-I -S` dependency probe | state/filelock 导入成功，filelock path 位于 install target |
| AT-03 | clean acceptance 结果 | distribution 含 filelock version/path/origin_verified=true |
| AT-04 | 聚焦回归 | wheel 构建、解析安装和隔离探针通过，不借用全局 site-packages |
| AT-05 | 发布回归 | pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 均通过 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_clean_wheel_dependencies.py -v -p no:cacheprovider
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

AT-01 至 AT-05 全部满足且 `git diff --check` 无输出，Iteration 23 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | `_install_clean_wheel` 使用 `pip install --disable-pip-version-check --ignore-installed --target <install_root> <wheel>`；原 `--no-deps` 已移除 |
| AT-02 | `_probe_clean_runtime_dependencies` 用 `python -I -S` 只插入 install root，并同时导入 `backtrader_skills.state` 与 `filelock`；路径逃出 target、无 JSON 或导入失败均会中止 |
| AT-03 | 7 x 2 clean acceptance 返回 `distribution.runtime_dependencies.filelock`；本次 `filelock_version=3.32.2`、`filelock_origin_verified=True`，与 base 环境的 3.16.1 区分，证明没有借用全局副本 |
| AT-04 | `tests/test_clean_wheel_dependencies.py` 通过：构建 wheel 后使用共享 resolver/probe helper，断言 target 内 module path、版本和 origin_verified |
| AT-05 | pytest 41 passed；mypy 27 个 source files 无问题；Ruff 通过；Black 检查 50 files；manifest `440ff5e36d6cb67821b7f8de9b76fa4885f7a63376b0bfaaaae45c744111dcd3`（66 files）已验证；catalog entries_verified=1155；doctor passed=true、14 checks；clean-wheel 7 x 2 matrix passed=true、14 cells、built-wheel-clean-install、filelock_origin_verified=true |
| 差异完整性 | `git diff --check` 退出码 0，无输出 |

Iteration 23 验收状态：通过。
