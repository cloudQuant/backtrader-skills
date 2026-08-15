# backtrader-skills

`backtrader-skills` 是面向本 Backtrader fork 的离线、可独立安装的编写 / 审查 / 测试产
品：它把已登记的本地数据集和 typed `StrategySpec v1` 转换为一个收集型 pytest 策略或
三文件 Python bundle，在不导入候选项的前提下审查它，并在独立的 runonce/runnext 子进
程中运行已批准的候选项。

它不导入或启动 sibling 的 MCP 或 Agent 产品。内置的 catalog 快照含 1,152 个功能策略
测试和 1,035 个三文件包的元数据，以及 1,032 个已映射 ID，因此正常使用不需要任一源语
料。项目遵循语义化版本（SemVer）；当前发布版本为 0.2.0。

## 站点页面

- [技能](skills.md) —— 三个规范 skill 及其流水线。
- [评估](evals.md) —— golden/对抗性 prompt 套件与评分器。
- [更新日志](changelog.md) —— 发布历史（Keep a Changelog）。
- [路线图](roadmap.md) —— P1 backlog 与来源化限制。

## 必需的 Backtrader 来源

策略执行和验收只接受
[`cloudQuant/backtrader`](https://github.com/cloudQuant/backtrader)。仅凭同名包或版本号
不能证明兼容性：工具会校验 Git remote，或校验可回溯至该 remote 的 PEP 610 安装元数据。

使用产品前先运行 `doctor`。若当前 Python 环境没有 `backtrader`，doctor 会使用同一解释
器安装 `git+https://github.com/cloudQuant/backtrader.git`，随后再次验证来源。若已存在
`backtrader` 但无法证明来自 cloudQuant fork，doctor 会返回
`BACKTRADER_SOURCE_WARNING`；它不会静默替换已有包。`run` 命令使用同一预检，并将该警
告写入 stderr。每个 `--target` 和源码检出 `--repository` 也必须是 cloudQuant Git 检出。
来自其他 fork 的目录即使包含看似有效的包，也会以 `BACKTRADER_SOURCE_MISMATCH` 拒绝。

## 快速上手

在 `backtrader-skills` 检出目录下，激活任意受支持的 Python 3.10–3.13 环境并安装本分
发：

```bash
python -m pip install .
backtrader-skills --target /path/to/backtrader doctor
```

运行时状态始终位于 `<target>/.backtrader-skills/`——数据集对象、manifest、草稿字节、
审批 token 摘要、运行证据和安装 manifest 都留在那里。256 位 token 句柄只返回一次给调
用方，绝不以明文持久化。`doctor` 记录已安装命令实际使用的解释器和环境。

## 安装三个规范 skill

同一分发支持四种项目级布局：

| 宿主 | 目标位置 |
| --- | --- |
| Claude Code | `.claude/skills/backtrader-*` |
| Codex | `.agents/skills/backtrader-*` |
| OpenCode | `.opencode/skills/backtrader-*` |
| OpenClaw | `<workspace>/skills/backtrader-*` |

preview、approve、apply：

```bash
BT_TARGET=/path/to/backtrader

backtrader-skills --target "$BT_TARGET" \
  install preview --host codex
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  install apply --plan-id install_codex_... --token-id tok_...
```

其他原生位置用 `claude`、`opencode` 或 `openclaw`。安装是 create-only 的。对
OpenClaw，`BT_TARGET` 必须是实际的 agent 工作区根目录（安装器不会替你注册 OpenClaw
agent）。卸载遵循同样的 preview → approve → apply 模式；安装后哈希变化过的文件会被保
留。

## 验证发现并发起首个请求

应用安装计划只证明规范文件到达了原生目录，并不能证明外部 model 会话发现了它们。安装
后请重载项目或开启新的宿主会话，然后发送下面的只读首个请求（把 `/path/to/backtrader`
替换为 Backtrader 项目根目录）：

```text
Without writing any files, use the backtrader-strategy-author skill. Run:
backtrader-skills --target /path/to/backtrader doctor
Return the doctor pass/fail result, the no-sibling-product-imports check, and the catalog counts.
```

预期 smoke 结果为 `passed=true`、通过的 `no-sibling-product-imports` 检查，以及已验证
的 catalog 基线 `1,152/1,035/1,032`。无法命名或加载该 skill 的宿主即便文件存在，也未
完成发现。

- Claude Code：确认 `.claude/skills/backtrader-strategy-author/SKILL.md` 存在，重启会
  话，并在请求前加“use the `backtrader-strategy-author` skill”。
- Codex：确认 `.agents/skills/backtrader-strategy-author/SKILL.md` 存在，开启新任务，
  并用以下方式调用 skill：

  ```text
  $backtrader-strategy-author Perform the read-only doctor smoke described above.
  ```

- OpenCode：确认 `.opencode/skills/backtrader-strategy-author/SKILL.md` 存在，重载项
  目，并先要求它“load and use the `backtrader-strategy-author` skill”。
- OpenClaw：确认已注册工作区下存在 `skills/backtrader-strategy-author/SKILL.md`，并要
  求 agent“use the workspace skill `backtrader-strategy-author`”。其布局与受保护卸载经
  过静态测试；在已安装的 OpenClaw agent 完成上述 smoke 之前，live 发现保持未检查状
  态。

## 登记本地数据

P0 只接受显式注册的只读 root 内的离线本地文件。可移植 manifest 含不透明 root ID 和相
对路径，绝不含本地绝对路径。

```bash
backtrader-skills --target "$BT_TARGET" \
  data root-add --directory /path/to/fixtures --root-id prices
backtrader-skills --target "$BT_TARGET" \
  data inspect --feed-spec feed.json
backtrader-skills --target "$BT_TARGET" \
  data register --spec data-spec.json
backtrader-skills --target "$BT_TARGET" \
  data preview --dataset-id 'ds_<64hex>' --rows 5
```

`DataSpec` 支持多个具名 feed、角色、timeframe/compression、时区、显式列映射、确定性
transform，以及 `intersection|left|explicit_asof` 声明。注册把基于表头的 CSV / 表格输
入归一化为 UTF-8 规范 CSV，校验时间戳、有限 OHLC、顺序和重复，并存储内容寻址对象。格
式为 `generic_csv`、`backtrader_csv`、`yahoo_csv`、`mt5_csv`、`pandas` 和
`pandas_custom_lines`；Pandas profile 消费安全物化的 CSV，绝不接受 pickle 或
callable。任何源字节变化都会使 manifest 及其审批失效。

## 编写与应用

搜索内置 catalog 并创建脚手架：

```bash
backtrader-skills --target "$BT_TARGET" \
  catalog search --query "multi timeframe momentum" --archetype multi_timeframe
backtrader-skills --target "$BT_TARGET" \
  spec scaffold --archetype multi_timeframe --output-profile python_bundle \
  --dataset-id 'ds_<64hex>' --feed-count 2 > strategy-spec.json
```

去掉任何外围 CLI 展示后校验 JSON，然后用两阶段 writer：

```bash
backtrader-skills --target "$BT_TARGET" \
  spec validate --spec strategy-spec.json
backtrader-skills --target "$BT_TARGET" \
  render preview --spec strategy-spec.json
backtrader-skills --target "$BT_TARGET" \
  render validate --draft-id draft_...
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  render apply --draft-id draft_... --token-id tok_...
```

bundle 创建在 `strategies/generated/` 下，收集型生成测试创建在
`tests/functional/strategies/generated/` 下；既有文件需要显式预期哈希。多文件 apply 会
先暂存每个字节，并使用日志加回滚，因此后续文件失败不会留下部分应用的 bundle。全部七
个 archetype——单数据指标、多指标、多资产配置、多 timeframe、配对 / 价差、订单 / 风
险、precomputed/ML 信号——对两种输出 profile 都使用同一套受限的
Expression/Action/StateRule IR。本 fork 中直接的 `bt.Strategy` 模板刻意不调用
`super().__init__()`。

## 审查、修复与运行

```bash
backtrader-skills --target "$BT_TARGET" \
  review --file "$BT_TARGET/strategies/generated/.../strategy.py"
backtrader-skills --target "$BT_TARGET" \
  repair --draft-id draft_...
backtrader-skills --target "$BT_TARGET" \
  run prepare --candidate "$BT_TARGET/strategies/generated/.../strategy.py" \
  --dataset-id 'ds_<64hex>'
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  run execute --run-id run_... --token-id tok_...
```

当诊断需要语义修改时，修订 typed spec 并把它绑定到失败的 ValidationReport：
`repair --spec revised-strategy-spec.json --validation-report failed-validation.json`。

控制器绝不导入候选代码。它证明候选项是来自已批准 render/apply 的未变 artifact，重算
candidate、dataset、source-data 和环境哈希，消费一次单独的执行审批，并对每个 mode 用
分发的活动 Python 解释器加 `-I` 调用。审批能力默认 15 分钟后过期，并以
`CONSUMED`、`REVOKED` 或 `EXPIRED` 结束。

## 安全与当前限制

- P0 只运行产品生成且已显式批准的候选项。未知代码可获静态审查，但不能拿到 run token。
- 生成的候选项只能 import 顶层 `backtrader`。AST 门禁拒绝控制器和文件系统 import、动
  态执行 / import、subprocess、已知网络客户端、socket、实盘 store、绝对路径、穿越和正
  行偏移。
- `python -I` 子进程隔离不是完整 OS 沙箱（无网络 namespace、容器、seccomp 或资源
  cgroup），且数据为离线、基于表头：不接受下载、数据库、API key、pickle、实盘 feed 或
  任意 loader/callable。
- 对齐（`intersection`、`left` 或 `explicit_asof`）、resample 和 replay 意图冻结在
  DatasetManifest 中，并在 feed 装配前校验；P0 runner 把 bar 时钟推进委托给
  Backtrader，不静默填充缺失 bar 或更改日历。
- 自动化 P0 runner 证明 runonce/runnext 一致性。单独检出、人工批准的 master/dev 财务
  基线仍是显式发布工作流，而非推断出的预期收益。
- 宿主客户端 UI 发现无法在缺少各客户端二进制的情况下模拟。产品测试验证全部四条原生路
  径、skill 元数据、转发器、冲突和受保护卸载。对同一 `--target` 的一般并发 CLI 调用仍
  不受支持：每个 target 一次只运行一条命令。
- 同一审批 token 在本地跨进程间受保护：render apply、install 和 uninstall 在受保护写入
  期间持有 per-token 锁；run 会在启动子进程前原子消费 token。同一 token 最多只能被一个
  操作消费。

## 验证分发

在 `backtrader-skills` 检出目录下激活目标环境后运行这些命令。源码检出辅助脚本只会在本
产品嵌套于该仓库内、或与名为 `backtrader` 的目录同级时定位 Backtrader 仓库；两种布局
都不存在时返回 `SOURCE_CHECKOUT_NOT_FOUND`，属于其他 fork 时返回
`BACKTRADER_SOURCE_MISMATCH`，绝不猜测。

```bash
# 产品嵌套在 Backtrader 仓库中，或两个仓库同级时自动发现
python scripts/doctor.py
python scripts/build_manifest.py --check
python scripts/build_catalog.py --check
python -m pytest tests -q
python scripts/run_acceptance.py \
  --matrix all --require-no-mcp --require-no-agent

# Backtrader 位于其他位置时显式指定其仓库根目录
python scripts/doctor.py --target /path/to/backtrader
python scripts/run_acceptance.py --repository /path/to/backtrader \
  --matrix all --require-no-mcp --require-no-agent
```

修改被分发的文件后，用 `python scripts/build_manifest.py` 重建受跟踪的 manifest；
`--check` 和 `--help` 是只读校验，不会修改 `manifest.json`。

持续集成在每次 push 到 `master` 时强制执行：专用 acceptance 任务检出 cloudQuant
Backtrader fork，运行完整套件并对 `src/backtrader_skills` 施加 80% 覆盖率门禁（不含两
个 `python -I` 子进程模块），随后运行完整 7×2 验收矩阵；pull request 保留较轻量的
quality 与受支持 Python 任务。

验收命令构建 wheel，安装到隔离目录，只把 Backtrader 源码包暴露给一个干净 fixture 仓
库，并从该已安装分发运行完整 7×2 矩阵（源码检出不在 `sys.path` 上），包括结构化的失
败 -> typed-IR 修复 -> 重新校验 -> 已批准双模式门禁。
