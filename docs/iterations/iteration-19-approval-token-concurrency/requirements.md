# Iteration 19：审批令牌并发安全——需求文档

## 1. 背景与问题

审批令牌承诺一次性、哈希绑定和可过期，但当前 TokenStore 的 consume 由 verify 后再写入
CONSUMED 状态组成。两个进程若同时读取同一已批准令牌，可能都看到 ISSUED 并成功返回。

更重要的是，render apply 与 install / uninstall apply 在 verify 和 consume 之间执行文件写
入。即使只修复 TokenStore.consume，本次副作用窗口仍可能让同一令牌驱动两次写操作。

这与 P0 的一次性审批安全边界冲突。当前 README 也明确承认同一 target 的跨进程 CLI 调用
不受支持；本轮不解除该全局限制，而是确保同一审批令牌不能授权两次成功的受保护操作。

## 2. 研究结论

候选方案评估：

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| 直接使用 fcntl | 不采用 | 仅覆盖 POSIX，需要另写 Windows 行为 |
| 自建 lock-file | 不采用 | 崩溃后的陈旧锁、重入和超时语义容易出错 |
| filelock FileLock | 采用 | 跨平台、支持超时、独立 lock 文件和可重入语义；适合单机同一文件系统的令牌状态 |

依据：filelock 官方文档说明 FileLock 使用独立 lock 路径、提供 timeout 和 Timeout 异常；
项目官方 PyPI 页面标注其为 MIT 许可的跨平台文件锁。链接：

- https://py-filelock.readthedocs.io/en/stable/how-to.html
- https://pypi.org/project/filelock/

## 3. 目标

令同一 token 的状态读取、批准、撤销、校验和消费在多个本地进程间线性化；令 render、
install 和 uninstall 的写副作用在一个独占 claim 内执行，只有成功退出 claim 才消费令牌。

## 4. 功能需求

### FR-1：声明可审计的运行时依赖

pyproject.toml 的 runtime dependencies 声明 filelock 的兼容版本范围。wheel metadata 必须
包含该依赖；不通过本地裸 import 偶然可用来掩盖声明缺失。

### FR-2：每令牌文件锁

TokenStore 对每个已存在的令牌使用其摘要派生的独立 lock 文件。锁等待必须有有限超时，超时
返回稳定的 APPROVAL_LOCK_TIMEOUT 错误。不同 token 不应互相串行化。

### FR-3：原子消费

consume 在同一个锁作用域内完成令牌读取、过期处理、kind 与 binding 验证、状态变为
CONSUMED 和持久化。并发调用同一 token 时只能有一个成功；其他调用必须观察到终态或超时。

### FR-4：副作用 claim

提供 TokenStore.claim 上下文。它在同一令牌锁内校验 token，运行调用方的受保护副作用，并
只在上下文正常退出时写入 CONSUMED。异常退出保留令牌的 ISSUED 状态，便于调用方处理真实
失败或显式撤销。

DraftManager.apply、SkillInstaller.apply_install、SkillInstaller.apply_uninstall 必须把全部
写入与回滚逻辑放进 claim；ControlledRunner.execute 必须使用原子 consume 后才启动子进程。

### FR-5：文档边界

README 的中英文安全限制必须说明：全局 target 并发仍不受支持，但相同审批 token 的受保护
操作已在跨进程层面互斥；这不是通用数据根、草稿预览或任意 CLI 并发锁。

### FR-6：发布完整性

每次修改分发内源码、脚本、README 或依赖元数据后运行 scripts/build_manifest.py。分发清单、
wheel metadata、完整回归和 clean-wheel acceptance 都是本轮验收的一部分。

## 5. 非目标

- 不引入多主机分布式锁、数据库锁或网络协调器。
- 不承诺对不同 token 的写操作排序或使任意 target 状态自动事务化。
- 不变更 token TTL、令牌明文不落盘、绑定哈希或现有审批 CLI 的成功 JSON 结构。
- 不为不受审批保护的数据 root、catalog 或只读命令创造虚假的全局并发安全承诺。

## 6. 成功标准

1. 多进程同时 claim 或 consume 相同 token 时恰好一个成功。
2. claim 中的异常不消费 token；成功 claim 消费且不可再次使用。
3. render、install、uninstall 和 run 的现有回归行为保持通过。
4. wheel 元数据声明 filelock，manifest 与实际分发文件一致。
5. pytest、Ruff、Black、catalog、默认 doctor 和 7 x 2 clean-wheel acceptance 均通过。
