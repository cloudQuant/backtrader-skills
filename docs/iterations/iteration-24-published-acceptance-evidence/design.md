# Iteration 24：发布验收证据同步——设计文档

## 证据刷新流

~~~text
scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
                           --output evidence/acceptance-7x2.json
                                  |
                                  v
current clean wheel / 7 x 2 matrix / dependency-origin evidence
                                  |
                                  v
published JSON structural regression test
                                  |
                                  v
scripts/build_manifest.py -> wheel packages matching evidence
~~~

## 实现边界

- 测试只断言稳定的结构与布尔/字符串约束，不固定随机 run IDs、wheel SHA 或临时 module path。
- 测试读取 `evidence/acceptance-7x2.json`，而不是重新运行 7 x 2 matrix；重跑由显式发布验收
  命令承担，避免每个 CI unit test 都触发昂贵集成流程。
- 实施报告保留历史 Iteration 17 的上下文，但把它与当前 evidence 的精确结果来源分开表述。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 新代码输出存在但 shipped evidence 仍旧 | JSON 契约测试要求 runtime dependency 证据 |
| 随机 run IDs 造成无意义测试失败 | 仅检查结构、状态和稳定语义 |
| evidence 更改未进入 wheel | manifest 重建和 wheel-content test 已覆盖 evidence 文件 |
