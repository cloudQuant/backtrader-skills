# Iteration 25：可携带的依赖来源证据——需求文档

## 背景与问题

Iteration 23 的 clean-wheel probe 将 `filelock.__file__` 的绝对临时路径写入
`distribution.runtime_dependencies.filelock.module_path`。Iteration 24 刷新后，发布 evidence
包含 `/private/var/.../backtrader-skills-wheel-acceptance-.../installed/filelock/__init__.py`，而
该临时目录在 acceptance 结束后已删除。

该字段虽然当时证明了来源，却使 packaged evidence 带有不可复现、无效且环境特定的路径。

## 目标

保留“模块确实在 clean install target 内”的证明，同时把发布证据中的模块路径规范化为相对
install root 的可携带 POSIX 路径。

## 功能需求

### FR-1：相对 module_path

`runtime_dependencies.filelock.module_path` 必须是 clean install root 内的相对路径，例如
`filelock/__init__.py`；不得是绝对路径，不得包含 `..`。

### FR-2：来源校验不弱化

probe 仍先以 resolved 绝对路径验证 `module_path.is_relative_to(install_root)`，仅在验证成功后
才序列化相对路径。验证失败仍终止 acceptance，不能靠字符串裁剪掩盖逃逸。

### FR-3：回归覆盖

clean probe 测试必须在临时 root 内复原相对路径并验证文件存在；published evidence 测试必须
拒绝绝对路径和父目录片段。

### FR-4：刷新发布证据

通过公开 acceptance forwarder 刷新 packaged JSON，并重建 manifest。

### FR-5：发布完整性

执行 pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel 7 x 2 和差异检查。

## 非目标

- 不改变 filelock 版本解析、依赖范围、wheel 安装方法或 7 x 2 matrix。
- 不记录临时目录、用户目录、绝对文件系统路径或网络位置。
- 不改变其他 historical evidence 字段。

## 成功标准

1. clean 结果和 published evidence 的 `module_path` 均为安全的相对 POSIX 路径。
2. target-origin proof 仍为 true，且测试能在临时 target 中定位该模块。
3. 绝对路径与 `..` 在回归测试中失败。
4. 刷新 evidence 与完整发布门禁通过。
