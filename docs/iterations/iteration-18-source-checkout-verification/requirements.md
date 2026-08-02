# Iteration 18：源码检出验证转发器可靠性——需求文档

## 1. 背景与问题

产品以独立仓库方式检出时，Backtrader 仓库通常与本仓库同级。当前
scripts/doctor.py 和 scripts/run_acceptance.py 将本仓库父目录直接作为
Backtrader 仓库根目录。在同级布局中，该父目录并不包含
backtrader/version.py，因此 README 所列的无参数验证命令会失败；只有手工传入真实
Backtrader 根目录才会成功。

这不是 Backtrader 运行时故障：2026-08-02 的基线中，显式根目录执行完整 7 archetypes
x 2 profiles 的 clean-wheel 验收通过。问题是源码检出辅助脚本的目标解析与文档承诺不一致。

## 2. 目标

让源码检出辅助脚本以一致、可预测且可测试的规则定位 Backtrader 仓库根目录，使本地
README 自检命令在支持的布局中无需额外参数即可运行。

## 3. 功能需求

### FR-1：统一根目录解析

新增一个可单元测试的解析器。输入为本产品根目录和可选的显式路径，输出必须是一个包含
backtrader/version.py 的 Backtrader 仓库根目录。

无显式路径时，按以下顺序查找：

1. 本产品父目录本身（支持产品嵌套在 Backtrader 仓库内）。
2. 本产品父目录下的 backtrader 子目录（支持两个仓库同级）。

显式路径优先，并且必须经过同样的结构校验。没有候选项有效时，返回稳定、可机读的
SOURCE_CHECKOUT_NOT_FOUND 错误，不得默默使用一个已知无效的目录。

### FR-2：doctor 源码转发器

scripts/doctor.py 必须支持 --target PATH。未指定时使用 FR-1 的自动解析；指定时使用
显式路径。成功时仍委托规范 CLI 的 doctor 命令并输出原有 JSON 结构。

### FR-3：acceptance 源码转发器

scripts/run_acceptance.py 必须支持 --repository PATH。未指定时使用 FR-1 的自动解析；
指定时使用显式路径。除该路径选项外，必须原样保留 --matrix、--require-no-mcp、
--require-no-agent 和 --output 等规范验收参数。

### FR-4：文档契约

README 中英文两部分必须说明：

- 无参数脚本仅在相邻或嵌套 Backtrader 源码布局中自动发现根目录；
- 其他布局使用 --target 或 --repository 显式指定 Backtrader 仓库根目录；
- 验证命令与实际脚本参数一致。

### FR-5：分发清单同步

本轮新增或修改了被分发的源码和脚本。实现完成后必须运行
scripts/build_manifest.py，令 manifest.json 的文件哈希清单与工作树一致；该生成步骤是
全量测试与 clean-wheel 验收的前置条件。

## 4. 非目标

- 不改变正式安装后的 backtrader-skills --target CLI 接口。
- 不改变验收矩阵、策略 IR、数据契约或 Backtrader 本体。
- 不以猜测、递归扫描磁盘或网络下载替代确定性的两级查找。

## 5. 成功标准

1. 同级和嵌套两种布局都能由单元测试解析到正确根目录。
2. 显式有效路径覆盖自动发现；无效显式路径产生稳定错误。
3. 源码 doctor 转发器带显式路径返回 passed=true。
4. 当前同级实际布局下，README 的无参数 doctor 与 full acceptance 命令都通过。
5. 重新生成分发清单后，原有测试、Ruff、Black、catalog 和 clean-wheel 验收保持通过。
