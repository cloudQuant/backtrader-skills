# Iteration 25：可携带的依赖来源证据——设计文档

## 处理顺序

~~~text
resolved filelock.__file__
       |
       v
is_relative_to(install_root)? -- no --> IntegrityError
       |
      yes
       |
       v
relative_to(install_root).as_posix()
       |
       v
JSON module_path + origin_verified=true
~~~

绝对路径只在子进程内部用于安全比较，不进入输出 JSON。`relative_to` 只在布尔来源检查通过后
执行，避免异常成为正常分支。

## 测试边界

- clean helper 测试把 JSON 的相对路径连接到 live `install_root`，断言文件存在、解析后仍在 root
  内，且路径不绝对、不含 `..`。
- packaged evidence 测试执行同样的路径形状约束，但不要求历史临时目录存在。
- 刷新证据后 manifest hash 覆盖其更新内容。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 先相对化导致逃逸被隐藏 | 先 resolved 路径验证，再调用 relative_to |
| 证据仍泄露机器路径 | 只序列化 POSIX 相对路径 |
| 相对路径不能定位模块 | 聚焦测试在实际 install root 中检查文件 |
