# backtrader-skills

**English** | [**中文**](#-中文文档)

`backtrader-skills` is an offline, independently installable author/review/test product for this
Backtrader fork. It turns a registered local dataset and a typed `StrategySpec v1` into either a
collected pytest strategy or a three-file Python bundle, reviews the candidate without importing it,
and runs approved candidates in separate runonce/runnext child processes.

It does not import or start sibling MCP or Agent products. The bundled catalog snapshot contains
metadata for 1,152 functional strategy tests and 1,035 three-file packages, with 1,032 mapped IDs,
so normal operation does not require either source corpus.

## Required Backtrader source

The only Backtrader source accepted for strategy execution and acceptance is
[`cloudQuant/backtrader`](https://github.com/cloudQuant/backtrader). A matching package name or
version number is not sufficient: the tool verifies the Git remote, or PEP 610 installation
metadata that leads back to that remote.

Run `doctor` before using the product. If the active Python environment has no `backtrader`,
doctor installs `git+https://github.com/cloudQuant/backtrader.git` with that same interpreter and
verifies it again. If a `backtrader` package already exists but cannot be proven to be the
cloudQuant fork, doctor returns a `BACKTRADER_SOURCE_WARNING`; it does not silently replace the
existing package. The `run` command uses the same preflight and writes that warning to stderr.

Every `--target` and source-checkout `--repository` is also required to be a cloudQuant Git
checkout. A valid-looking package from another fork is rejected with
`BACKTRADER_SOURCE_MISMATCH`.

## Install the runtime

From the `backtrader-skills` checkout, activate any supported Python 3.10–3.13 environment and
install the distribution. Conda is optional; for example, `conda activate base` may be used before
these commands:

```bash
python -m pip install .
backtrader-skills --target /path/to/backtrader doctor
```

Runtime state is always `<target>/.backtrader-skills/`. Dataset objects, manifests, draft bytes,
approval-token digests, run evidence, and install manifests remain there. The 256-bit token handle
is returned once to the caller and is never persisted in plaintext. `doctor` records the actual
interpreter and environment used by the installed command; no local machine path is part of the
distribution interface.

## Install the three canonical skills

The same distribution supports four project-level layouts:

| Host | Destination |
| --- | --- |
| Claude Code | `.claude/skills/backtrader-*` |
| Codex | `.agents/skills/backtrader-*` |
| OpenCode | `.opencode/skills/backtrader-*` |
| OpenClaw | `<workspace>/skills/backtrader-*` |

Preview, approve, and apply:

```bash
BT_TARGET=/path/to/backtrader

backtrader-skills --target "$BT_TARGET" \
  install preview --host codex
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  install apply --plan-id install_codex_... --token-id tok_...
```

Use `claude`, `opencode`, or `openclaw` for the other native locations. Installation is create-only.
For OpenClaw, set `BT_TARGET` to the actual agent workspace root because its native skill directory
is `<workspace>/skills`; the installer does not register an OpenClaw agent for you.
Uninstall is also preview/approval/apply; files whose hash changed after installation are preserved:

```bash
backtrader-skills --target "$BT_TARGET" \
  install uninstall-preview --host codex
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  install uninstall-apply --plan-id uninstall_codex_... --token-id tok_...
```

Each installed skill has one thin `scripts/backtrader_skills.py` forwarder. Deterministic behavior
lives only in `src/backtrader_skills/`.

## Verify discovery and make the first request

Applying an install plan proves that the canonical files reached the native directory; it does not
prove that an external model session discovered them. Reload the project or start a new host session
after installation. Use the following read-only first request, replacing `/path/to/backtrader` with
the Backtrader project root:

```text
Without writing any files, use the backtrader-strategy-author skill. Run:
backtrader-skills --target /path/to/backtrader doctor
Return the doctor pass/fail result, the no-sibling-product-imports check, and the catalog counts.
```

The expected smoke result has `passed=true`, a passing `no-sibling-product-imports` check, and the
verified catalog baseline `1,152/1,035/1,032`. A host that cannot name or load the skill has not
completed discovery, even if the files exist.

### Claude Code

Confirm `.claude/skills/backtrader-strategy-author/SKILL.md` exists, restart Claude Code in the
project, and send the first request above. Prefixing the request with “use the
`backtrader-strategy-author` skill” is the explicit trigger; keep the returned transcript or host
tool trace as discovery evidence.

### Codex

Confirm `.agents/skills/backtrader-strategy-author/SKILL.md` exists and start a new task in the
project. Invoke the skill explicitly with:

```text
$backtrader-strategy-author Perform the read-only doctor smoke described above.
```

Record the resolved skill name and command output. A filesystem-only check is not a Codex discovery
test.

### OpenCode

Confirm `.opencode/skills/backtrader-strategy-author/SKILL.md` exists, reload the project, and ask
OpenCode to “load and use the `backtrader-strategy-author` skill” before sending the first request.
Retain the skill/tool trace and the doctor JSON result as evidence.

### OpenClaw

Set `BT_TARGET` to an existing, explicitly registered OpenClaw agent workspace before installation,
then confirm `skills/backtrader-strategy-author/SKILL.md` exists below that workspace. Reload the
registered agent and ask it to “use the workspace skill `backtrader-strategy-author`” for the first
request. This installer does not create or register the agent itself.

OpenClaw was not installed in the environment used for the current acceptance snapshot. Its layout,
metadata, forwarders, conflict handling, and protected uninstall are statically tested; live
discovery must remain unchecked until an installed OpenClaw agent completes the smoke above.

## Register local data

P0 accepts only offline local files inside explicitly registered, read-only roots. Portable
manifests contain an opaque root ID and relative path, never the local absolute path.

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

`DataSpec` supports multiple named feeds, roles, timeframe/compression, timezone, explicit column
mapping, deterministic transforms, and `intersection|left|explicit_asof` declarations. Registration
normalizes header-based CSV/tabular inputs to UTF-8 canonical CSV, validates timestamps, finite
OHLC, ordering and duplicates, and stores content-addressed objects. Formats are
`generic_csv`, `backtrader_csv`, `yahoo_csv`, `mt5_csv`, `pandas`, and
`pandas_custom_lines`; Pandas profiles consume a safely materialized CSV, never pickle or a callable.
Any source-byte change invalidates the manifest and its approvals.

## Author and apply

Search the shipped catalog and create a scaffold:

```bash
backtrader-skills --target "$BT_TARGET" \
  catalog search --query "multi timeframe momentum" --archetype multi_timeframe
backtrader-skills --target "$BT_TARGET" \
  spec scaffold --archetype multi_timeframe --output-profile python_bundle \
  --dataset-id 'ds_<64hex>' --feed-count 2 > strategy-spec.json
```

Validate the JSON after removing any surrounding CLI presentation, then use the two-phase writer:

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

Bundles are created under `strategies/generated/`. Collected generated tests are created under
`tests/functional/strategies/generated/`. Existing files require an explicit expected hash.
Multi-file apply stages every byte first and uses a journal plus rollback, so a later-file failure
does not leave a partially applied bundle.

All seven archetypes-single-data indicator, multi-indicator, multi-asset allocation,
multi-timeframe, pairs/spread, order/risk, and precomputed/ML signal-use the same restricted
Expression/Action/StateRule IR for both output profiles. Direct `bt.Strategy` templates intentionally
do not call `super().__init__()` in this fork.

## Review, repair, and run

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

When a diagnostic requires a semantic change, revise the typed spec and bind it to the failed
ValidationReport:

```bash
backtrader-skills --target "$BT_TARGET" \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
```

The controller never imports candidate code. It proves the candidate is an unchanged artifact from
an approved render/apply, recomputes candidate, dataset, source-data, and environment hashes,
consumes a separate execution approval, and invokes the distribution's active Python interpreter
with `-I` for each mode.
Approval capabilities expire after 15 minutes by default and end in
`CONSUMED`, `REVOKED`, or `EXPIRED`. Reports are stored as JSON and Markdown.

The 11 metrics have frozen units: six integer bar/trade counts; account-currency `final_value`;
nullable dimensionless `sharpe_ratio`; nullable ratio `annual_return`; percent `max_drawdown`; and
percent `return_rate`. Integers and normalized events compare exactly. Floats use `rel_tol=1e-7`,
`abs_tol=1e-9`, with a documented amount override. Null equals only null; missing, NaN, and Infinity
fail.

## Security and current limits

- P0 runs only product-generated and explicitly approved candidates. Unknown code may receive a
  static review but cannot receive a run token.
- Generated candidates may import only top-level `backtrader`. AST gates reject controller and
  filesystem imports, dynamic execution/import, subprocess, known network clients, sockets, live
  stores, absolute paths, traversal, and positive line offsets.
- `python -I` child isolation is not a complete OS sandbox. P0 has no network namespace, container,
  seccomp, or resource cgroup.
- Data is offline and header-based. No download, database, API key, pickle, live feed, or arbitrary
  loader/callable is accepted.
- Alignment (`intersection`, `left`, or `explicit_asof`), resample, and replay intent is frozen in
  the DatasetManifest and validated before feed assembly. The P0 runner delegates bar-clock
  advancement to Backtrader and does not silently fill missing bars or change calendars.
- The automated P0 runner proves runonce/runnext parity. A separately checked-out, human-approved
  master/dev financial baseline remains an explicit release workflow, not an inferred expected
  return.
- Host-client UI discovery cannot be emulated without each client binary. Product tests verify all
  four native paths, canonical skill metadata, forwarders, conflicts, and protected uninstall.
- General concurrent CLI invocations against the same `--target` remain unsupported. State files
  outside approval tokens are not globally serialized; run one command at a time per target.
- A single approval token is protected across local processes: render apply and install or uninstall
  hold a per-token lock through their protected writes, while run atomically consumes its token before
  launching child processes. At most one operation can consume the same token. This does not serialize
  unrelated tokens, data-root registration, draft previews, or arbitrary target writes.

## Verify the distribution

Run these commands from the `backtrader-skills` checkout with the intended environment activated.
Repository maintainers use the Anaconda base environment required by the repository's `AGENTS.md`,
but that machine-specific executable path is not part of the public commands.

The source-checkout helpers automatically locate a Backtrader repository only when this product is
either nested below that repository or next to a sibling directory named `backtrader`. They validate
that the selected root contains `backtrader/version.py` and that its Git remote is
`cloudQuant/backtrader`. They return `SOURCE_CHECKOUT_NOT_FOUND` when neither layout exists and
`BACKTRADER_SOURCE_MISMATCH` when a candidate is another fork, rather than guessing or continuing
with an incompatible implementation.

After changing a distribution-included file, rebuild the tracked manifest once with
`python scripts/build_manifest.py`. For routine, read-only validation use
`python scripts/build_manifest.py --check`; both `--check` and `--help` leave
`manifest.json` unchanged.

```bash
# Automatic discovery for a nested or sibling Backtrader checkout
python scripts/doctor.py
python scripts/build_manifest.py --check
python scripts/build_catalog.py --check
python -m pytest tests -q
python scripts/run_acceptance.py \
  --matrix all --require-no-mcp --require-no-agent

# A Backtrader checkout in any other location
python scripts/doctor.py --target /path/to/backtrader
python scripts/run_acceptance.py --repository /path/to/backtrader \
  --matrix all --require-no-mcp --require-no-agent
```

`doctor`, the acceptance matrix, and the execution tests run strategies through the cloudQuant
Backtrader source package. The test suite also honors `BT_BACKTRADER_DIR` pointing at that
checkout's `backtrader` package directory, and skips source-backed tests when the package is absent.

Continuous integration enforces this on every push to `master`: a dedicated acceptance job checks
out the cloudQuant Backtrader fork, runs the full suite with the source package present (execution,
doctor, and acceptance tests included), enforces at least 80% coverage over
`src/backtrader_skills`, and then runs the complete 7×2 acceptance matrix. Pull requests keep the
lighter quality and supported-Python jobs. Emulating each host client binary and the
human-approved master/dev financial baseline remain local release steps.

The acceptance command builds a wheel, installs it into an isolated directory, exposes only the
Backtrader source package to a clean fixture repository, and runs the full 7×2 matrix from that
installed distribution with the source checkout absent from `sys.path`. The seven archetypes use
seven distinct DatasetManifests covering all six declared adapters; multi-data, resample, and
precomputed custom-line semantics are recorded per cell. Every cell records independent runonce
and runnext hashes plus comparison results. Multi-data, multi-timeframe, and precomputed/ML
representative cells must also pass a structured failure -> typed-IR repair -> revalidation ->
approved dual-mode backtest gate.

The wheel contains seven named JSON Schemas, `comparison-profile-v1.json`, the full metadata
snapshot, four host adapter manifests, and all three canonical skills. `manifest.json` records every
published file hash and compatibility range.

---

# 📖 中文文档

[**English**](#backtrader-skills) | **中文**

---

`backtrader-skills` 是面向本 Backtrader fork 的离线、可独立安装的编写 / 审查 / 测试产
品。它把已登记的本地数据集和 typed `StrategySpec v1` 转换为一个收集型 pytest 策略或
三文件 Python bundle，在不导入候选项的前提下审查它，并在独立的 runonce/runnext 子进
程中运行已批准的候选项。

它不导入或启动 sibling 的 MCP 或 Agent 产品。内置的 catalog 快照含 1,152 个功能策略
测试和 1,035 个三文件包的元数据，以及 1,032 个已映射 ID，因此正常使用不需要任一源语
料。

## 必需的 Backtrader 来源

策略执行和验收只接受
[`cloudQuant/backtrader`](https://github.com/cloudQuant/backtrader)。仅凭同名包或版本号不能
证明兼容性：工具会校验 Git remote，或校验可回溯至该 remote 的 PEP 610 安装元数据。

使用产品前先运行 `doctor`。若当前 Python 环境没有 `backtrader`，doctor 会使用同一解释器
安装 `git+https://github.com/cloudQuant/backtrader.git`，随后再次验证来源。若已存在
`backtrader` 但无法证明来自 cloudQuant fork，doctor 会返回
`BACKTRADER_SOURCE_WARNING`；它不会静默替换已有包。`run` 命令使用同一预检，并将该警告
写入 stderr。

每个 `--target` 和源码检出 `--repository` 也必须是 cloudQuant Git 检出。来自其他 fork 的
目录即使包含看似有效的包，也会以 `BACKTRADER_SOURCE_MISMATCH` 拒绝。

## 安装运行时

在 `backtrader-skills` 检出目录下，激活任意受支持的 Python 3.10–3.13 环境并安装本分
发。Conda 是可选的；例如，可在这些命令前先 `conda activate base`：

```bash
python -m pip install .
backtrader-skills --target /path/to/backtrader doctor
```

运行时状态始终位于 `<target>/.backtrader-skills/`。数据集对象、manifest、草稿字节、
审批 token 摘要、运行证据和安装 manifest 都留在那里。256 位 token 句柄只返回一次给调
用方，绝不以明文持久化。`doctor` 记录已安装命令实际使用的解释器和环境；任何本地机器
路径都不是分发接口的一部分。

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
OpenClaw，把 `BT_TARGET` 设为实际的 agent 工作区根目录，因为其原生 skill 目录是
`<workspace>/skills`；安装器不会替你注册 OpenClaw agent。卸载同样是
preview/approval/apply；安装后哈希变化过的文件会被保留：

```bash
backtrader-skills --target "$BT_TARGET" \
  install uninstall-preview --host codex
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  install uninstall-apply --plan-id uninstall_codex_... --token-id tok_...
```

每个已安装 skill 都有一个薄薄的 `scripts/backtrader_skills.py` 转发器。确定性逻辑只存
在于 `src/backtrader_skills/`。

## 验证发现并发起首个请求

应用安装计划只证明规范文件到达了原生目录，并不能证明外部 model 会话发现了它们。安装
后请重载项目或开启新的宿主会话。使用下面的只读首个请求，把 `/path/to/backtrader` 替
换为 Backtrader 项目根目录：

```text
Without writing any files, use the backtrader-strategy-author skill. Run:
backtrader-skills --target /path/to/backtrader doctor
Return the doctor pass/fail result, the no-sibling-product-imports check, and the catalog counts.
```

预期 smoke 结果为 `passed=true`、通过的 `no-sibling-product-imports` 检查，以及已验证的
catalog 基线 `1,152/1,035/1,032`。无法命名或加载该 skill 的宿主即便文件存在，也未完
成发现。

### Claude Code

确认 `.claude/skills/backtrader-strategy-author/SKILL.md` 存在，在项目中重启 Claude
Code，并发送上文首个请求。在请求前加“use the `backtrader-strategy-author` skill”是显
式触发；保留返回的 transcript 或宿主工具 trace 作为发现证据。

### Codex

确认 `.agents/skills/backtrader-strategy-author/SKILL.md` 存在，并在项目中开启新任
务。用如下方式显式调用 skill：

```text
$backtrader-strategy-author Perform the read-only doctor smoke described above.
```

记录解析出的 skill 名和命令输出。仅文件系统检查不算 Codex 发现测试。

### OpenCode

确认 `.opencode/skills/backtrader-strategy-author/SKILL.md` 存在，重载项目，并在发送
首个请求前要求 OpenCode “load and use the `backtrader-strategy-author` skill”。保留
skill/tool trace 和 doctor JSON 结果作为证据。

### OpenClaw

安装前把 `BT_TARGET` 设为一个已存在、已显式注册的 OpenClaw agent 工作区，然后确认该
工作区下存在 `skills/backtrader-strategy-author/SKILL.md`。重载已注册的 agent，并要
求它对首个请求“use the workspace skill `backtrader-strategy-author`”。本安装器不创建
或注册 agent 本身。

当前验收快照所用环境未安装 OpenClaw。其布局、元数据、转发器、冲突处理和受保护卸载经
过静态测试；在已安装的 OpenClaw agent 完成上述 smoke 之前，live 发现保持未检查状态。

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

bundle 创建在 `strategies/generated/` 下。收集型生成测试创建在
`tests/functional/strategies/generated/` 下。既有文件需要显式预期哈希。多文件 apply 会
先暂存每个字节，并使用日志加回滚，因此后续文件失败不会留下部分应用的 bundle。

全部七个 archetype--单数据指标、多指标、多资产配置、多 timeframe、配对 / 价差、订单
/ 风险、precomputed/ML 信号--对两种输出 profile 都使用同一套受限的
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

```bash
backtrader-skills --target "$BT_TARGET" \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
```

控制器绝不导入候选代码。它证明候选项是来自已批准 render/apply 的未变 artifact，重算
candidate、dataset、source-data 和环境哈希，消费一次单独的执行审批，并对每个 mode 用
分发的活动 Python 解释器加 `-I` 调用。审批能力默认 15 分钟后过期，并以
`CONSUMED`、`REVOKED` 或 `EXPIRED` 结束。报告以 JSON 和 Markdown 存储。

11 个指标有冻结的单位：六个整数 bar/trade 计数；账户币种 `final_value`；可空无量纲
`sharpe_ratio`；可空比率 `annual_return`；百分比 `max_drawdown`；百分比
`return_rate`。整数和归一化事件精确比较。浮点数用 `rel_tol=1e-7`、`abs_tol=1e-9`，并
有文档化的 amount override。null 仅等于 null；缺失、NaN 和 Infinity 失败。

## 安全与当前限制

- P0 只运行产品生成且已显式批准的候选项。未知代码可获静态审查，但不能拿到 run
  token。
- 生成的候选项只能 import 顶层 `backtrader`。AST 门禁拒绝控制器和文件系统 import、动
  态执行 / import、subprocess、已知网络客户端、socket、实盘 store、绝对路径、穿越和正
  行偏移。
- `python -I` 子进程隔离不是完整 OS 沙箱。P0 无网络 namespace、容器、seccomp 或资源
  cgroup。
- 数据为离线、基于表头。不接受下载、数据库、API key、pickle、实盘 feed 或任意
  loader/callable。
- 对齐（`intersection`、`left` 或 `explicit_asof`）、resample 和 replay 意图冻结在
  DatasetManifest 中，并在 feed 装配前校验。P0 runner 把 bar 时钟推进委托给
  Backtrader，不静默填充缺失 bar 或更改日历。
- 自动化 P0 runner 证明 runonce/runnext 一致性。单独检出、人工批准的 master/dev 财务
  基线仍是显式发布工作流，而非推断出的预期收益。
- 宿主客户端 UI 发现无法在缺少各客户端二进制的情况下模拟。产品测试验证全部四条原生路
  径、规范 skill 元数据、转发器、冲突和受保护卸载。
- 对同一 `--target` 的一般并发 CLI 调用仍不受支持。审批令牌以外的状态文件没有全局
  串行化；每个 target 一次只运行一条命令。
- 同一审批 token 在本地跨进程间受保护：render apply、install 和 uninstall 在受保护写入期间
  持有 per-token 锁；run 会在启动子进程前原子消费 token。同一 token 最多只能被一个操作消费。
  这不串行化无关 token、数据 root 登记、草稿 preview 或任意 target 写入。

## 验证分发

在 `backtrader-skills` 检出目录下激活目标环境后运行这些命令。仓库维护者使用仓库
`AGENTS.md` 要求的 Anaconda base 环境，但该机器特定的可执行路径不属于公开命令。

源码检出辅助脚本只会在两种布局下自动定位 Backtrader 仓库：本产品位于该仓库内，或本产品
与名为 `backtrader` 的仓库目录同级。它会校验目标根目录含有
`backtrader/version.py`，且 Git remote 为 `cloudQuant/backtrader`；两种布局都不满足时返回
结构化 `SOURCE_CHECKOUT_NOT_FOUND` 错误，候选目录属于其他 fork 时返回
`BACKTRADER_SOURCE_MISMATCH`，不会猜测其他目录或继续使用不兼容实现。

修改被分发的文件后，先用 `python scripts/build_manifest.py` 重建一次受跟踪的清单。
日常只读验证使用 `python scripts/build_manifest.py --check`；`--check` 和
`--help` 都不会修改 `manifest.json`。

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

`doctor`、验收矩阵和执行测试都要通过 cloudQuant Backtrader 源码包来运行策略。测试套件也
支持用 `BT_BACKTRADER_DIR` 指向该 checkout 的 `backtrader` 包目录，并在缺少该包时自动跳过
这些测试。

持续集成在每次 push 到 `master` 时强制执行上述验证：专用 acceptance 任务检出 cloudQuant
Backtrader fork，在源码包存在的情况下运行完整测试套件（包含执行、doctor 和 acceptance 测试），
要求 `src/backtrader_skills` 覆盖率至少 80%，随后运行完整 7×2 验收矩阵。Pull request 保留较轻
量的 quality 与受支持 Python 任务。模拟各宿主客户端二进制和人工批准的 master/dev 财务基线仍属
于本地发布步骤。

验收命令构建 wheel，安装到隔离目录，只把 Backtrader 源码包暴露给一个干净 fixture 仓
库，并从该已安装分发运行完整 7×2 矩阵，源码检出不在 `sys.path` 上。七个 archetype 使
用七个不同的 DatasetManifest，覆盖全部六个已声明 adapter；多数据、resample 和
precomputed 自定义 line 语义按单元记录。每个单元记录独立的 runonce 和 runnext 哈希加
比较结果。多数据、多 timeframe 和 precomputed/ML 代表单元还须通过结构化的
失败 -> typed-IR 修复 -> 重新校验 -> 已批准双模式回测门禁。

wheel 含七个具名 JSON Schema、`comparison-profile-v1.json`、完整元数据快照、四个宿主
adapter manifest 和全部三个规范 skill。`manifest.json` 记录每个已发布文件哈希和兼容
范围。
