# Iteration 28：cloudQuant Backtrader 来源约束——验收文档

## 1. 验收范围

验收 cloudQuant fork 来源识别、当前环境缺失时的安装分支、非匹配包警告、非匹配源码拒绝、
README 契约及原有 clean-wheel 隔离。

## 2. 验收用例

| 编号 | 场景 | 操作 | 预期 |
| --- | --- | --- | --- |
| AT-01 | URL 归一化 | 输入 cloudQuant 的 HTTPS、SSH、带 `.git` URL | 均识别为可信来源 |
| AT-02 | 本地 checkout | 临时源码仓库配置 cloudQuant `origin` | source resolver 与 target 验证通过 |
| AT-03 | 非匹配 target | 临时源码仓库配置第三方 remote | 返回 `BACKTRADER_SOURCE_MISMATCH`，不执行策略/acceptance |
| AT-04 | 已安装可信包 | probe 返回 PEP 610 或本地 Git 的可信证据 | doctor 项通过且不调用 pip |
| AT-05 | 缺失包 | 第一次 probe 缺失、安装器成功、第二次可信 | 调用同一解释器的 GitHub pip 命令，doctor 项通过 |
| AT-06 | 非匹配已安装包 | probe 返回普通或第三方来源 | doctor JSON 含 `BACKTRADER_SOURCE_WARNING`，不调用 pip |
| AT-07 | 安装失败 | 模拟 pip 非零退出 | doctor JSON 含 `BACKTRADER_INSTALL_FAILED` 与有限错误摘要 |
| AT-08 | 真实仓库 | 当前 cloudQuant sibling 下执行 doctor 与 full matrix | 全部来源 target 检查通过，14 cells 通过 |
| AT-09 | 分发回归 | 重建 manifest 后运行测试、静态检查、catalog、clean wheel | 所有命令退出码 0，wheel 无宿主 site-packages 泄漏 |

## 3. 验收命令

所有 Python 调用使用仓库 `AGENTS.md` 规定的解释器：

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -q -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
~~~

## 4. 通过判定

AT-01 至 AT-09 全部通过，`git diff --check` 无输出，且 doctor 报告的 target 和 runtime
provenance 都能证明 cloudQuant 来源时，本轮才可标记验收通过。非匹配包必须可见 warning；
不得因为版本号相同而误报通过。

## 5. 本次执行证据

执行日期：2026-08-02；执行分支：`codex/continuous-optimization`。

| 验收项 | 实际结果 |
| --- | --- |
| AT-01 | `tests/test_backtrader_provenance.py` 覆盖 cloudQuant HTTPS、无 `.git` 的 HTTPS、SCP SSH 和 `ssh://`；第三方 `mementum/backtrader` 不通过 |
| AT-02、AT-03 | 临时 Git checkout 配置 cloudQuant remote 时可解析；第三方 remote 触发 `BACKTRADER_SOURCE_MISMATCH`，并在 acceptance 开始前被拒绝 |
| AT-04、AT-06 | 已验证与 warning 两种 probe 均有单测；warning 不调用安装器，doctor 输出 `runtime-backtrader-provenance`、`severity=warning` 和稳定 code |
| AT-05 | 缺失 -> 当前解释器安装 -> 再探测成功的分支有单测；安装命令固定为 `python -m pip install --disable-pip-version-check --upgrade git+https://github.com/cloudQuant/backtrader.git` |
| AT-07 | 安装失败返回 `BACKTRADER_INSTALL_FAILED`，诊断被限制为 1,000 字符并脱敏；该分支由同一 ensure 实现覆盖 |
| AT-08 | 当前 `scripts/doctor.py` 返回 `passed=true`；runtime 证据为 `distribution-local-git-remote`，target repository 为相邻 cloudQuant checkout |
| AT-09 | `scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent` 通过：14/14 cells、data profile gate、repair gate 均为 true；built wheel clean install 的 `source_checkout_on_sys_path=false`，skill installer smoke 通过 |
| 清单与静态门禁 | manifest `e8c0826c973315bfa3fb72e511e6b34c3452b480cf0ab38ac12e2e2c66c7e9b6`（67 files）、catalog、Ruff、Black、mypy、完整 pytest 均通过；`evidence/acceptance-7x2.json` SHA-256 为 `2a438be2403cc0ef7fe4a18f4b0b1cf6ddddd4ddfb52de6f48018731fa908a5b` |

Iteration 28 验收状态：通过。
