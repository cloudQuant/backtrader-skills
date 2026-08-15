# 技能

`backtrader-skills` 附带三个规范 skill，每个流水线阶段一个。安装会把它们放入宿主的原生
skill 目录（见[首页](index.md)）；每个已安装 skill 都有一个薄薄的
`scripts/backtrader_skills.py` 转发器，确定性逻辑只存在于 `src/backtrader_skills/`。

| Skill | 角色 |
| --- | --- |
| `backtrader-strategy-author` | 使用 `StrategySpec v1` 和受限的 Expression/Action/StateRule IR，从已登记的离线数据集创建可审计的 Backtrader 策略。 |
| `backtrader-strategy-review` | 在不导入候选代码的前提下审查 `StrategySpec` 和生成的 Python artifact；返回结构化 `ValidationReport v1`。 |
| `backtrader-strategy-test` | 在固定的隔离子进程中运行已批准的候选项，并比较 runonce 与 runnext。 |

## 流水线

编写 → 审查 → 测试。

1. **编写** 运行 `doctor`，登记数据 root 与数据集，搜索内置 catalog，并产出规范
   `StrategySpec v1`。它在渲染前解析 feed 角色、方向、仓位、入场、出场与风险，然后在
   `render_write` 审批 token 下 preview、校验并应用渲染产物。
2. **审查** 静态校验已编写的草稿和已应用的 artifact——`review --file` 用于已应用候选
   项，`render validate --draft-id` 用于产品草稿——并按稳定代码、严重度、文件、行、规
   则、解释和修复方式报告诊断。它绝不导入或执行候选项。
3. **测试** 是最终门禁：`run prepare` 针对 DatasetManifest 重算已应用候选项的哈希和静
   态校验证据，单独批准的 `run execute` 在两个固定的 `python -I` 子进程中运行它，做
   runonce/runnext 比较。控制进程绝不导入候选代码。

## 修复循环

校验失败或 parity 运行失败时，通过编写 / 审查循环修复：修订 typed spec（或用
`repair --spec ... --validation-report ...` 把修订后的 spec 绑定到失败的
`ValidationReport`），创建新草稿，并在重试前取得新的写入和运行审批。修复只回到已存储
的 StrategySpec 并重新渲染；它绝不修补任意第三方源码。Catalog 示例是设计证据，不是预
期盈利，回测也绝不意味着预测收益。

## 附带的参考资料

每个 skill 都附带其参考契约、工作示例和故障手册，由测试与运行时事实漂移锁定。文件位
于每个 `SKILL.md` 旁边；CLI 是使用它们的唯一受支持方式。

**`backtrader-strategy-author`**

- `references/authoring-contract.md` —— 规范字段、IR 语法、运算符表和两阶段写入契约。
- `references/worked-example.md` —— 一个双 feed 的 `multi_timeframe` scaffold-to-apply 序列。
- `references/failure-playbook.md` —— token、校验、parity 和源错误恢复。

**`backtrader-strategy-review`**

- `references/review-rules.md` —— 诊断目录、严重度、修复方式和信任边界。
- `references/worked-example.md` —— 一个注入故障的候选项和预期的 `ValidationReport` 摘录。
- `references/failure-playbook.md` —— token、诊断、parity 和源错误恢复。

**`backtrader-strategy-test`**

- `references/metric-contract.md` —— 11 个指标单位和可空规则。
- `references/worked-example.md` —— prepare → approve → execute 和预期报告字段。
- `references/failure-playbook.md` —— token、parity 和源错误恢复。

## 编写不变量

author skill 把运行时状态保存在 `<target>/.backtrader-skills/` 下，只把 bundle 生成在
`strategies/generated/` 下，只把收集型测试生成在
`tests/functional/strategies/generated/` 下，并为本 fork 生成不带
`super().__init__()` 的直接 `bt.Strategy` 子类。它拒绝正行偏移、任意 import、动态执行、
网络访问、实盘 store、绝对数据路径和未知运算符。
