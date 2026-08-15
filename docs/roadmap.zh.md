# 路线图

`backtrader-skills` 的 P1 backlog。状态与当前限制陈述来源自 README「安全与当前限制」一
节、`IMPLEMENTATION_REPORT.md`「Honest P0 limits」以及 CI workflow 定义——这里没有任何
推测。

| 条目 | 状态 | 当前限制（来源化） | 大致计划 |
| --- | --- | --- | --- |
| 执行的容器 / 网络 namespace 沙箱 | 未开始 | README：「`python -I` 子进程隔离不是完整 OS 沙箱。P0 无网络 namespace、容器、seccomp 或资源 cgroup。」IMPLEMENTATION_REPORT：「子进程隔离加 AST/path/import 门禁不是完整 OS 沙箱。没有容器、网络 namespace、seccomp 或 cgroup。」 | 在容器或网络 namespace 中包装 runonce/runnext 子进程执行，带 seccomp 和资源限制；保留现有 `python -I` 路径作为回退；在运行证据中记录沙箱元数据；以验收测试门禁。 |
| HTML 报告渲染 | 未开始 | IMPLEMENTATION_REPORT：「JSON 和 Markdown 报告已实现。HTML 渲染和容器执行仍是 P1。」 | 在 `reports.py` 中与 JSON/Markdown writer 并列增加 HTML 渲染器；为校验和运行报告输出自包含 HTML；JSON 仍为规范机器格式。 |
| Per-target CLI 串行化（一般同 target 并发） | 未开始 | README：「对同一 `--target` 的一般并发 CLI 调用仍不受支持。审批令牌以外的状态文件没有全局串行化；每个 target 一次只运行一条命令。」 | 把 iteration 19 的 per-token `filelock` 模式推广为覆盖所有状态写入的 per-target 锁；保持审批 token 语义不变；增加证明跨命令串行化的并发测试。 |
| OpenClaw live 发现验证 | 部分验证（静态测试通过；live 发现未检查） | README：「当前验收快照所用环境未安装 OpenClaw。其布局、元数据、转发器、冲突处理和受保护卸载经过静态测试；在已安装的 OpenClaw agent 完成上述 smoke 之前，live 发现保持未检查状态。」IMPLEMENTATION_REPORT：「测试验证四种原生宿主布局和 skill 元数据；实际的客户端 UI 发现需要相应宿主二进制，未被模拟。」 | 安装 OpenClaw，注册工作区，运行只读首个请求 smoke，并把 transcript 作为发现证据保留在 `evidence/` 下。 |
| Windows CI | 未开始 | 两个 workflow 都只在 `ubuntu-latest` 上运行（`.github/workflows/ci.yml`、`.github/workflows/acceptance.yml`）；没有 Windows runner 任务。 | 在 CI 矩阵中增加 Windows 任务（先 quality 任务，再测试矩阵）；审计 Windows 下的路径处理、`python -I` 子进程行为和 `filelock` 语义。 |
| 基于 embedding 的 catalog 搜索 | 未开始 | IMPLEMENTATION_REPORT：「catalog 快照是带确定性词法搜索的完整元数据。它不打包全部语料源码，也不提供 embedding 搜索。」 | 为内置 catalog 元数据增加 embedding 索引和相似度搜索 catalog 命令；确定性词法搜索仍为默认，CLI 保持离线。 |
