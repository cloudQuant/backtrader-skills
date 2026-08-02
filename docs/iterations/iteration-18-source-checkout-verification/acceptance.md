# Iteration 18：源码检出验证转发器可靠性——验收文档

## 1. 验收范围

本轮只验收源码检出辅助脚本的 Backtrader 根目录解析、参数透传与 README 操作契约。

## 2. 验收用例

| 编号 | 场景 | 操作 | 预期 |
| --- | --- | --- | --- |
| AT-01 | 嵌套布局 | 在临时 Backtrader 根目录下放置产品根目录 | 自动返回产品父目录 |
| AT-02 | 同级布局 | 在临时父目录下创建 backtrader 子仓库和产品目录 | 自动返回 sibling backtrader |
| AT-03 | 显式覆盖 | 传入有效 --target 或 --repository | 返回显式仓库，不受自动候选影响 |
| AT-04 | 无效路径 | 传入缺少 backtrader/version.py 的目录 | JSON code 为 SOURCE_CHECKOUT_NOT_FOUND，退出码为 2 |
| AT-05 | doctor 转发器 | python scripts/doctor.py --target REAL_BACKTRADER | 返回 JSON 且 passed=true |
| AT-06 | README 默认 doctor | 当前同级布局运行 python scripts/doctor.py | passed=true |
| AT-07 | README 默认 acceptance | 当前同级布局运行 python scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent | passed=true，14 个 cells |
| AT-08 | 分发与回归 | 重建 manifest 后运行 pytest、Ruff、Black、catalog 与 wheel 验收 | 全部退出码为 0 |

## 3. 验收命令

所有 Python 调用使用本仓库 AGENTS.md 指定的 Anaconda base 环境：

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -q -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
~~~

## 4. 通过判定

AT-01 至 AT-08 均满足，且 git diff --check 无输出，才允许把 Iteration 18 标记为验收通过。
任一脚本产生非结构化 traceback、错误根目录或 README 命令失败均视为未通过。

## 5. 分发清单前置步骤

每次修改包含在分发内的源码、脚本、资源或 skill 文件后，先运行：

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py
~~~

随后再执行第 3 节的全量测试和 clean-wheel 验收。manifest.json 必须由该脚本生成，不能手工
修改哈希。

## 6. 本次执行证据

执行日期：2026-08-02；执行分支：codex/continuous-optimization。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01、AT-02 | tests/test_source_checkout.py 覆盖嵌套与同级布局，5 passed |
| AT-03、AT-04 | 同一测试覆盖显式有效路径与无效路径；无效路径返回 SOURCE_CHECKOUT_NOT_FOUND 和退出码 2 |
| AT-05 | scripts/doctor.py --target 临时有效仓库返回 passed=true |
| AT-06 | 当前同级布局直接运行 scripts/doctor.py：14 项 checks 均通过，target-backtrader-source=true |
| AT-07 | 当前同级布局直接运行 scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent：passed=true，14 cells，data_profile_gate=true，repair_gate=true，built-wheel-clean-install |
| AT-08 | scripts/build_manifest.py 生成 manifest 7cf07e026165a5130375fb5367034a2884cb8237f3df79ab9d18cc2b17515bfb（66 files）；pytest 收集并通过 31 项，Ruff 通过，Black 检查 45 files，catalog check 退出码 0 |
| 差异完整性 | git diff --check 退出码 0，无输出 |

Iteration 18 验收状态：通过。
