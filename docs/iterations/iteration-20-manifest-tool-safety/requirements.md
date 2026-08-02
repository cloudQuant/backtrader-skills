# Iteration 20：分发清单工具安全性——需求文档

## 1. 背景与问题

scripts/build_manifest.py 是分发清单的唯一生成器，但它当前忽略命令行参数。运行
scripts/build_manifest.py --help 仍会重建并写入 manifest.json，而不是输出帮助；这使一个
通常被认为只读的命令意外修改工作树。

Iteration 19 的验收中已实际观察到该行为：向该脚本传入 --help 输出的是 rebuilt manifest
而非 usage。该问题不会损坏内容，但会误导维护者、制造无意 diff，并且 CI 没有通过该公开
脚本验证清单。

## 2. 目标

保持无参数重建行为兼容，同时使 --help 绝对只读，并提供不改写 manifest 的 --check 模式。
CI 和 README 应使用同一公开命令，避免“库函数可用而脚本行为不同”的漂移。

## 3. 功能需求

### FR-1：参数化入口

scripts/build_manifest.py 使用 argparse：

- 无参数：重建 manifest.json，保持现有输出语义。
- --help：输出 usage 并以 0 退出，不读写 manifest。
- --check：调用 verify_distribution_manifest，成功时输出 manifest hash 与文件数，不写文件。

### FR-2：失败语义

--check 检测到清单缺失、哈希失配或文件差异时，以非零退出码和简洁错误信息退出，不输出
Python traceback。重建失败同样返回非零退出码。

### FR-3：可回归验证

自动化测试必须证明 --help 与 --check 前后 manifest.json 的字节完全一致，并证明默认无参数
调用仍能重建。测试不得手工编辑或暂时破坏仓库真实 manifest。

### FR-4：操作与 CI 契约

README 中英文说明重建和只读验证的区别。GitHub Actions 的 distribution manifest gate 使用
scripts/build_manifest.py --check，而不是内联 Python 片段。

### FR-5：发布完整性

修改脚本、README 或分发源码后使用默认重建器更新 manifest.json，并验证完整测试、wheel
和 clean-wheel acceptance。

## 4. 非目标

- 不变更 manifest 文件格式、哈希算法、包含根目录或默认重建行为。
- 不引入新依赖、远程存储、签名服务或自动提交。
- 不把 --check 扩展为自动修复模式。

## 5. 成功标准

1. --help 返回 usage 且 manifest 字节不变。
2. --check 成功返回 0 且 manifest 字节不变。
3. 默认命令重建清单；现有 verify_distribution_manifest 与 wheel 测试保持通过。
4. CI、README 与测试都指向一致的公开命令。
5. pytest、Ruff、Black、catalog、doctor 和 7 x 2 clean-wheel acceptance 均通过。
