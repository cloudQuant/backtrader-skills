# Iteration 23：clean-wheel 运行时依赖隔离——设计文档

## 控制流

~~~text
build wheel
   |
   v
pip install --ignore-installed --target install_root <wheel>
   |
   v
python -I -S: sys.path=[install_root, stdlib] -> import state + filelock
   |
   +-- import/source invalid -> IntegrityError
   |
   v
python -I: execute 7 x 2 acceptance from install_root
   |
   v
distribution.runtime_dependencies.filelock evidence
~~~

## 实现边界

- `acceptance.py` 提取 wheel 安装与依赖来源检查 helper，主流程和测试共用，避免复制子进程命令。
- 安装使用当前解释器的 pip、`--disable-pip-version-check`、`--ignore-installed`、`--target`，不传
  `--no-deps`。
- 探针使用 `-I -S`，仅手动插入 install root，因此无法借用 Conda 全局 filelock。
- 验证信息仅 additive 地写入 `distribution.runtime_dependencies`。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 宿主同名包掩盖缺依赖 | `--ignore-installed`、`-I -S` 与路径断言 |
| resolver 失败难定位 | 裁剪 pip stderr 写入 `ExecutionError.details` |
| 探针未覆盖 package 真实 import | 同时导入 `backtrader_skills.state` 和 `filelock` |
| 格式扰动既有消费者 | 仅添加 distribution 子字段 |
