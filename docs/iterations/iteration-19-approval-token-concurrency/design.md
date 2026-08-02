# Iteration 19：审批令牌并发安全——设计文档

## 1. 设计概览

在 TokenStore 内部以 token digest 派生的独立 lock 文件为互斥键。令牌 JSON 仍是唯一状态
记录；lock 文件不保存 token 明文、绑定或审批内容。FileLock 的操作系统级锁在进程退出时释
放，因此不依赖手工删除陈旧标记。

锁粒度选择 token 而非 target：一个令牌的状态机必须线性化，而无关令牌不应因本轮改动被迫
串行。这个粒度不改变 RuntimePaths 中其他状态文件的现有并发边界。

## 2. 状态机与锁边界

~~~text
ISSUED --approve--> ISSUED(approved_at set)
ISSUED --claim success / consume--> CONSUMED
ISSUED --revoke / binding drift--> REVOKED
ISSUED --expiry check--> EXPIRED
~~~

所有会读取后写入上述状态的路径都在同一个 per-token FileLock 内。内部私有函数只可在已获
锁时调用：

~~~python
def consume(token_id, kind, bindings):
    with self._locked(token_id):
        record = self._verify_unlocked(token_id, kind, bindings)
        return self._consume_unlocked(token_id, record)

@contextmanager
def claim(token_id, kind, bindings):
    with self._locked(token_id):
        record = self._verify_unlocked(token_id, kind, bindings)
        yield self._public(token_id, record)
        self._consume_unlocked(token_id, record)
~~~

异常穿过 yield 时不会执行 consume，因此操作失败不会伪造“写入已成功”的令牌终态。

## 3. 调用方集成

| 调用方 | 现状风险 | 改造 |
| --- | --- | --- |
| DraftManager.apply | verify 后才写入并 consume | 全部预检、暂存、提交和回滚置于 claim |
| SkillInstaller.apply_install | verify 后复制 skill 文件 | 文件复制置于 claim |
| SkillInstaller.apply_uninstall | verify 后删除文件 | 哈希核验与删除置于 claim |
| ControlledRunner.execute | verify 与 consume 两次调用 | 仅调用原子 consume，再启动隔离子进程 |

run 保持“开始执行即消费”语义：子进程失败不重新开放执行能力。三个文件写入操作保持“副
作用成功才消费”语义：写入失败时 token 可由调用方安全重试或撤销。

## 4. 错误与可观察性

FileLock.Timeout 映射为 ApprovalLockTimeout，CLI 返回：

~~~json
{
  "status": "error",
  "code": "APPROVAL_LOCK_TIMEOUT",
  "message": "approval token is busy; retry the operation"
}
~~~

锁路径仅由令牌摘要命名，运行时目录不记录 token 明文。现有 digest-only 持久化要求不变。

## 5. 测试策略

1. 使用两个独立进程和可控 BarrierTokenStore 制造旧实现中的 verify 到 consume 竞争。
2. 验证新 claim 对同一 token 只允许一个正常退出，另一个进程得到已消费错误。
3. 验证 claim 抛出异常后 token 仍可被批准状态读取和后续成功 claim 消费。
4. 现有 drafts / installer / runner 测试作为调用方回归。
5. wheel 测试读取 METADATA，断言 Requires-Dist 包含 filelock。

## 6. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 进程崩溃留下锁文件 | 使用 FileLock 的 OS 级锁而非存在即锁的 SoftFileLock |
| 同 token 长时间占用 | 固定有限 timeout，返回可机读错误 |
| 运行时依赖未打包声明 | pyproject 依赖与 wheel METADATA 测试同时约束 |
| 锁内异常错误消费 token | consume 放在 claim 的正常退出分支 |
| 误称全局并发安全 | README 明确保留 target 级并发限制 |
