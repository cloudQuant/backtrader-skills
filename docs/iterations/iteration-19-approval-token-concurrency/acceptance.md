# Iteration 19：审批令牌并发安全——验收文档

## 1. 验收范围

本轮验收同一审批 token 的跨进程互斥、受保护副作用的 claim 语义、依赖元数据和既有策略
生成 / 安装 / 执行回归；不验收全局 target 并发。

## 2. 验收用例

| 编号 | 场景 | 预期 |
| --- | --- | --- |
| AT-01 | 两进程同时 consume 同一已批准 token | 恰好一个 CONSUMED；另一个返回审批状态错误 |
| AT-02 | 两进程同时 claim 同一 token | 恰好一个成功完成副作用并消费；另一个不执行副作用 |
| AT-03 | claim 内抛出异常 | token 保持 ISSUED 和 approved_at，可由后续成功 claim 消费 |
| AT-04 | 锁超时 | 稳定 code 为 APPROVAL_LOCK_TIMEOUT，退出码为 2 |
| AT-05 | Draft / install / uninstall / run 回归 | 既有测试全通过，语义无回退 |
| AT-06 | wheel metadata | Requires-Dist 声明 filelock |
| AT-07 | 发布清单 | build_manifest 后 verify_distribution_manifest=true |
| AT-08 | 完整产品验收 | pytest、Ruff、Black、catalog、默认 doctor、7 x 2 clean-wheel acceptance 全通过 |

## 3. 验收命令

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_token_concurrency.py -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

## 4. 通过判定

AT-01 至 AT-08 全部满足且无差异检查错误，才能把 Iteration 19 标记为验收通过。

## 5. 本次执行证据

执行日期：2026-08-02；执行分支：codex/continuous-optimization。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | tests/test_token_concurrency.py 的两进程 consume 竞争用例通过；恰好一个操作消费 token |
| AT-02 | 两进程 claim 竞争用例通过；只留下一个副作用文件，恰好一个 token 消费成功 |
| AT-03 | claim 内异常后 token 保持 ISSUED；后续正常 claim 成功消费，测试通过 |
| AT-04 | 受控 FileLock.Timeout 映射为 APPROVAL_LOCK_TIMEOUT，测试通过 |
| AT-05 | tests/test_drafts_installer.py 和 tests/test_runner.py 共 8 项通过；全量 pytest 35 passed |
| AT-06 | wheel 内容测试通过，METADATA 包含 Requires-Dist: filelock |
| AT-07 | scripts/build_manifest.py 生成 manifest e4f642ba38a74cdd6261339274f116447e7b0946390b78f4dadcb28124900584（66 files）；全量分发清单验证随 pytest 通过 |
| AT-08 | Ruff 通过；Black 检查 46 files；catalog check 退出码 0；默认 doctor 14 项 checks 全通过；clean-wheel 7 x 2 matrix passed=true、14 cells、data_profile_gate=true、repair_gate=true |
| 差异完整性 | git diff --check 退出码 0，无输出 |

Iteration 19 验收状态：通过。
