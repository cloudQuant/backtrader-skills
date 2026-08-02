# Iteration 28：cloudQuant Backtrader 来源约束——需求文档

## 1. 背景

`backtrader-skills` 的策略执行依赖 Backtrader 源码，但仅以包名、版本号或
`backtrader/version.py` 的存在判断目标，会把 PyPI 原版、其他 fork 甚至手工复制的目录
误认为兼容实现。项目的唯一允许来源是
`https://github.com/cloudQuant/backtrader.git`。

同时，开发者环境可能尚未安装 `backtrader`，也可能已经安装了来源不明的同名包。缺失时应
安装指定仓库；已存在但无法证明来自指定仓库时，必须明确告警，不得静默声称环境合规。

## 2. 目标

1. 将可执行的 Backtrader 源码目标限制为 cloudQuant fork。
2. 在 doctor 中检查当前 Python 环境的 `backtrader` 来源；缺失时安装指定 Git 仓库。
3. 对已存在但非 cloudQuant 或来源不可证实的包输出稳定、机器可读的警告。
4. 保持离线 clean-wheel 验收的隔离模型，不因宿主环境自动安装而泄漏 site-packages。

## 3. 功能需求

### FR-1：唯一来源标识

唯一受信任的仓库为 `https://github.com/cloudQuant/backtrader.git`。实现必须接受其等价的
HTTPS/SSH URL 形式；不得只以 `backtrader` 的 distribution 名称、导入路径或
`__version__` 判定来源。

### FR-2：目标源码强制约束

`--target`、源码转发器解析的 `--target` / `--repository` 以及受控运行器使用的 Backtrader
源码目录，都必须同时满足：存在 `backtrader/version.py`，且 Git remote 能证明其来自 FR-1
仓库。非匹配源码不得作为策略执行或 acceptance 的输入。

### FR-3：当前环境预检与安装

`doctor` 必须检查执行它的 Python 解释器可解析的 `backtrader` 模块。

- 模块缺失时，通过同一解释器执行 `python -m pip install`，安装
  `git+https://github.com/cloudQuant/backtrader.git`，再重新检测来源。
- 已安装且可经 PEP 610 `direct_url.json` 或本地 Git remote 证明来源时，报告验证通过。
- 已安装但不属于或无法证明属于 cloudQuant fork 时，不覆盖用户环境；输出
  `BACKTRADER_SOURCE_WARNING`，并将 doctor 的相应检查标为未通过。
- 安装失败时，报告 `BACKTRADER_INSTALL_FAILED`，包含已脱敏的诊断摘要。

### FR-4：输出与兼容性

doctor 成功和警告均保持 JSON 输出。新增的来源检查应包含状态、模块路径、已发现的来源证据和
稳定 code；不输出 pip 的完整环境路径、凭据或无界日志。现有的策略、数据和 IR JSON 契约不变。

### FR-5：文档与分发

README 的中英文说明必须写明唯一来源、自动安装行为、非匹配包只告警不自动替换的政策，以及
如何通过 doctor 验证。所有受分发文件变动后必须用 `scripts/build_manifest.py` 重建清单。

## 4. 非目标

- 不固定到某一 commit、tag 或 PyPI version；本轮限制的是 fork 来源。
- 不在每个纯离线命令（catalog、spec、approval 等）启动时联网安装依赖。
- 不因已安装了非匹配包而强制卸载或覆盖它。
- 不把 GitHub/Gitee 镜像、名称相同的包或任意包含 `version.py` 的目录视为等价来源。

## 5. 成功标准

1. 有效 cloudQuant remote、SSH URL、PEP 610 VCS URL 和本地 Git checkout 均被识别。
2. 缺失环境触发一次指定仓库安装并在重新检测后通过；安装失败有稳定错误。
3. 非匹配环境和非匹配 target 都被拒绝或明确警告，绝不静默通过。
4. 真实 cloudQuant sibling checkout 下 doctor、完整 acceptance、clean-wheel 验收与质量门禁通过。
