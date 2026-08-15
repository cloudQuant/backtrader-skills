# 更新日志

本项目所有重要变更都记录在此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.2.0] - 2026-08-15

### 新增

- 源码检出校验：`scripts/doctor.py` 和 `scripts/run_acceptance.py` 转发器能可靠解析嵌套
  或同级的 `cloudQuant/backtrader` 检出，尊重显式 `--target`/`--repository` 覆盖，并返回
  结构化 `SOURCE_CHECKOUT_NOT_FOUND` / `BACKTRADER_SOURCE_MISMATCH` 代码，而不是猜测。
- 审批 token 并发：同一 token 在本地跨进程受保护；恰好一个 claim 或 consume 胜出，失败
  的 claim 让 token 保持 `ISSUED`，锁超时映射为 `APPROVAL_LOCK_TIMEOUT`（`filelock` 声明
  为依赖）。
- manifest 工具安全：`scripts/build_manifest.py --check` 和 `--help` 只读，绝不修改
  `manifest.json`；只读检查已接入 CI。
- 比较契约类型化：metrics 和 events 比较结果的完整键集与可重算的 `comparison_hash`，外
  加 `mypy src/backtrader_skills` CI 门禁。
- 受支持 Python CI 矩阵：3.11 上的 quality 任务和跨 Python 3.10–3.13 的 pytest 矩阵，
  每个任务带正确的 extras。
- 干净 wheel 依赖隔离：acceptance 用 `--ignore-installed --target` 安装构建出的 wheel，
  并在安装根目录内于 `python -I -S` 下探测 `filelock`，证明分发不借用宿主 site-packages。
- 已发布验收证据：完整 7×2 矩阵结果经公共转发器刷新并打包，历史基线清晰标注。
- 可移植依赖证据：已发布证据记录 `filelock` 来源和相对 `module_path`，不含绝对路径或
  `..` 组件。
- 干净 wheel 安装 smoke：隔离的 `python -I -S` 子进程从干净 wheel 完成 Codex
  preview → approve → apply 循环，安装全部三个规范 skill。
- 校验报告完整性：`apply` 在 claim token 之前以 `IntegrityError` 拒绝被篡改的校验报
  告，让 token 保持 `ISSUED` 且不写任何 target 文件。
- cloudQuant 来源加固：URL 归一化、Git-remote 和 PEP 610 校验、缺失包安装、对不可验证
  已装包的 `BACKTRADER_SOURCE_WARNING`，以及带净化诊断的 `BACKTRADER_INSTALL_FAILED`。
- skill 落地：三个规范 skill 附带完整参考契约、诊断目录、工作示例、故障手册和流水线交
  接，由测试与运行时事实漂移锁定。
- CI：master 专属的完整验收 workflow 检出 cloudQuant Backtrader fork，运行完整套件并对
  `src/backtrader_skills` 施加 80% 覆盖率门禁，然后运行完整 7×2 验收矩阵；pull request
  保留较轻量的 quality 与受支持 Python 任务。
- Evals：golden-prompt skill eval 套件（七个 archetype prompt 加对抗性与跨 skill
  prompt）与机械评分器（`scripts/record_eval.py`）和 runbook。
- 仓库卫生：新增 `CLAUDE.md`、`AGENTS.md`、`CHANGELOG.md` 和 `docs/roadmap.md`；README
  现在链接维护者文档并声明 SemVer 政策。
