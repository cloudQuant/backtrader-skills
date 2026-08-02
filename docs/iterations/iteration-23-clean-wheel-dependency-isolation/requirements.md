# Iteration 23：clean-wheel 运行时依赖隔离——需求文档

## 背景与问题

Iteration 19 为审批锁加入 `filelock`，wheel metadata 已声明 `Requires-Dist: filelock`。但
`run_clean_wheel_acceptance` 用 `pip install --no-deps --target ...` 安装 wheel，随后子进程
只使用 `-I`；`-I` 不会移除解释器的全局 site-packages。当前 base 环境恰好有 `filelock 3.16.1`，
因此 acceptance 可以从全局环境满足 import，而非证明 wheel 依赖被安装到 clean target。

这使 built-wheel-clean-install 对运行时依赖的证明不完整：metadata 存在不等于实际安装与
加载路径正确。

## 目标

让 clean-wheel acceptance 使用正常 pip 依赖解析，并证明 `filelock` 从临时安装目录而非源
checkout 或解释器全局 site-packages 加载。

## 功能需求

### FR-1：解析 runtime dependencies

clean-wheel 安装移除 `--no-deps`，使用 `--ignore-installed --target <install_root>` 安装构建的
wheel。即使宿主已有同名依赖，pip 也必须将解析结果写入 clean target。

### FR-2：依赖来源证明

在执行 acceptance 前，以 `-I -S` 子进程只将 `install_root` 作为第三方路径导入
`backtrader_skills.state` 和 `filelock`。导入失败或 `filelock.__file__` 不位于 target 内都必须
中止 acceptance。

### FR-3：结果可审计

clean-wheel 结果的 `distribution` 增加 filelock 的版本、模块路径和 `origin_verified=true`；
不改变既有 matrix/cell 结构。

### FR-4：回归测试

新增聚焦测试：构建 wheel、调用共享 clean 安装/验证路径，并在 `-I -S` 下证明 state 使用
target 内的 filelock，而不是 base 环境副本。

### FR-5：发布完整性

重建并验证 manifest，运行 pytest、mypy、Ruff、Black、catalog、doctor 与 7 x 2 clean-wheel。

## 非目标

- 不 vendor `filelock`，不改变它的版本范围。
- 不承诺安装过程永不使用 pip resolver；正常用户安装本就负责依赖解析。
- 不验证可选开发/测试依赖。
- 不改变 Backtrader 源码隔离、矩阵或 sibling 产品排除规则。

## 成功标准

1. 安装无 `--no-deps` 且有 `--ignore-installed`。
2. `-I -S` 探针证明 state/filelock 可用，且 filelock 在 target 内。
3. clean acceptance 输出有 runtime dependency 来源证据。
4. 聚焦与完整发布门禁通过。
