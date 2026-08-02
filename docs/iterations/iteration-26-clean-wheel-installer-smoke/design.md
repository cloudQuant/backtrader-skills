# Iteration 26：clean-wheel 安装器运行时 smoke——设计文档

## 处理顺序

~~~text
built wheel
    |
    v
pip --target clean install root
    |
    v
python -I -S + install_root only
    |
    v
SkillInstaller.preview_install("codex")
    |
    v
explicit TokenStore.approve(token)
    |
    v
SkillInstaller.apply_install(...)
    |
    v
verify every canonical SKILL.md under target/.agents/skills
    |
    v
portable installer_smoke evidence
~~~

## 子进程协议

父进程传入 `install_root` 与临时 target。子进程只输出单行 JSON：

- `passed`: bool；
- `host`: 固定为 `codex`；
- `installed_skills`: 已验证的 skill 名称列表；
- `installed_file_count`: apply manifest 中的文件数量。

父进程验证 JSON 结构、成功状态、host、完整 skill 集合和正的文件数量。输出不含 target、wheel、
install root 或其他绝对文件路径。

## 测试边界

- helper 测试以真实 wheel 和真实 `pip --target` 运行 smoke，验证 `-I -S` 环境中的成功协议。
- published evidence 测试只校验稳定、可携带的 smoke 字段。
- 现有 7 x 2 acceptance 继续验证策略执行；该 smoke 只证明 packaged installer 的资源解析和写入链。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 子进程意外加载 source checkout | 使用 `-I -S`，仅手动插入 install root |
| data-files 路径变更后静态测试仍通过 | 实际调用 `distribution_root()` 与安装器 apply |
| evidence 泄露临时路径 | JSON 协议只返回枚举、计数和 bool |
| 缺失单个 skill 未被发现 | 与 `SKILL_NAMES` 集合精确比较 |
