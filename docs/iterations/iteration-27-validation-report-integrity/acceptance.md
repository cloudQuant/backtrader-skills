# Iteration 27：ValidationReport 完整性闭环——验收文档

## 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | 篡改 validation report | canonical hash 不匹配时 apply 在 claim 前以 `IntegrityError` 拒绝 |
| AT-02 | token 和 target 保护 | AT-01 后 token 仍 `ISSUED`，没有生成目标文件 |
| AT-03 | 正常 apply | 既有 validate -> approve -> apply 与 multi-file rollback 保持通过 |
| AT-04 | 发布回归 | pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 通过 |

## 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_drafts_installer.py -v -p no:cacheprovider
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

AT-01 至 AT-04 全部满足且 `git diff --check` 无输出，Iteration 27 才可标记为通过。

## 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | 通过。真实 draft 完成 validate 后，将持久化 `validation-report.json` 的 `status` 篡改为 `failed` 而不重算 `validation_hash`；apply 在 `TokenStore.claim()` 前以 `IntegrityError: validation report hash is invalid` 拒绝。 |
| AT-02 | 通过。上述拒绝后原 approval token 状态仍为 `ISSUED`，draft 的所有目标输出路径都不存在。 |
| AT-03 | 通过。`tests/test_drafts_installer.py` 的 8 项测试均通过，覆盖正常 validate -> approve -> apply 与 multi-file rollback。 |
| AT-04 | 通过。全量 `pytest` 为 44 passed；mypy 检查 27 个源文件无问题；Ruff 通过；Black 确认 51 个文件无需变更；`compileall` 通过；manifest 为 `7f11cfd71cb6e42a9879aba0b3407b15e5879f42b392178709cb6e3642f8448b`（66 files）；catalog snapshot 为 1,155 entries；doctor 的 14 项检查全部通过；当前 manifest 下独立 clean-wheel 7 x 2 通过；`git diff --check` 无输出。 |

Iteration 27 验收状态：**通过**。
