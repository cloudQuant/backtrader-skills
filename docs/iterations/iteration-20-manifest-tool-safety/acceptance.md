# Iteration 20：分发清单工具安全性——验收文档

## 1. 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | build_manifest --help | exit 0、输出 usage、manifest bytes 不变 |
| AT-02 | build_manifest --check | exit 0、输出 verified manifest、manifest bytes 不变 |
| AT-03 | 默认 build_manifest | exit 0、输出 rebuilt manifest，随后 library verify=true |
| AT-04 | CI | workflow 使用 python scripts/build_manifest.py --check |
| AT-05 | 文档 | README 英文与中文说明 build 与 check 两条路径 |
| AT-06 | 发布回归 | pytest、Ruff、Black、catalog、doctor、clean-wheel 7 x 2 均通过 |

## 2. 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_manifest_tool.py -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

## 3. 通过判定

AT-01 至 AT-06 全部满足且 git diff --check 无输出，Iteration 20 才可标记为通过。

## 4. 本次执行证据

执行日期：2026-08-02；执行分支：codex/continuous-optimization。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | tests/test_manifest_tool.py 验证 --help 输出 usage 且 manifest bytes 不变，2 项聚焦测试通过 |
| AT-02 | 同一测试验证 --check 输出 verified manifest 且 manifest bytes 不变；最终命令输出 d1aa36e866b2cc7fc905f85093151c8bbe69464405ef6e7ad955d270d2018fca（66 files） |
| AT-03 | 默认 build_manifest 输出 rebuilt manifest，随后 verify_distribution_manifest=true |
| AT-04 | .github/workflows/ci.yml 的 Distribution manifest check 已改为 python scripts/build_manifest.py --check |
| AT-05 | README 英文与中文均区分默认重建与只读 --check，并说明 --help 不改写清单 |
| AT-06 | pytest 37 passed；Ruff 通过；Black 检查 47 files；catalog check 退出码 0；默认 doctor 14 项 checks 全通过；clean-wheel 7 x 2 matrix passed=true、14 cells、data_profile_gate=true、repair_gate=true |
| 差异完整性 | git diff --check 退出码 0，无输出 |

Iteration 20 验收状态：通过。
