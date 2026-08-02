# Iteration 28：cloudQuant Backtrader 来源约束——设计文档

## 1. 设计决策

新增一个纯 Python 的 provenance 模块，集中处理 URL 归一化、Git remote 检查、PEP 610
元数据检查和缺失包安装。它不导入 `backtrader`，避免在检测阶段加载不可信代码。

`cloudQuant/backtrader` 的来源证据优先级为：

1. distribution 的 `direct_url.json` 中的 VCS URL；
2. PEP 610 本地 `file://` URL 所指 checkout 的 Git remote；
3. 已解析模块文件向上追溯得到的本地 Git remote；
4. 策略 target / repository 根目录或其 `backtrader` 包真实路径的 Git remote。

只要一个可验证证据指向唯一仓库即通过；有模块但没有任何可验证证据则是 warning，不把猜测
当作合规。

## 2. 模块边界

| 文件 | 责任 |
| --- | --- |
| `src/backtrader_skills/backtrader_provenance.py` | 来源 URL 归一化、环境探测、缺失安装、target 验证 |
| `src/backtrader_skills/source_checkout.py` | 调用 provenance 验证已解析的源码仓库 |
| `src/backtrader_skills/doctor.py` | 将宿主环境检查纳入 JSON doctor checks |
| `src/backtrader_skills/runner.py` | 在生成 run manifest 前拒绝非 cloudQuant target |
| `src/backtrader_skills/acceptance.py` | 在 acceptance 开始前拒绝非 cloudQuant repository |
| `src/backtrader_skills/errors.py` | 稳定的来源不匹配 / 安装失败错误类型 |
| `tests/test_backtrader_provenance.py` | URL、Git checkout、安装分支和 warning 行为 |
| `tests/test_source_checkout.py` | 源码转发器仅接受 cloudQuant target |

## 3. 环境算法

~~~text
probe importlib.util.find_spec("backtrader")
if module absent:
    run [sys.executable, "-m", "pip", "install", "--upgrade", git-url]
    if non-zero: return BACKTRADER_INSTALL_FAILED
    probe again
if any trusted provenance evidence exists:
    return verified
return BACKTRADER_SOURCE_WARNING
~~~

安装命令通过调用方解释器执行，不能使用硬编码的系统 `pip`。pip 输出仅保留限制长度的失败摘要，
避免将环境细节或凭据写入 doctor JSON。

## 4. Target 算法

一个 target 首先必须有 `backtrader/version.py`。然后尝试从 repository 根目录和已解析的
`backtrader` 包目录向上查找 Git worktree，并执行 Git 配置读取。任意 remote URL 归一化后必须
等于 `github.com/cloudquant/backtrader`；否则抛出 `BACKTRADER_SOURCE_MISMATCH`。执行器和
acceptance 均使用同一函数，因此不会出现 doctor 通过而实际运行切换到其他 fork 的情况。

## 5. 输出协议

新增 doctor 项的示意：

~~~json
{
  "check": "runtime-backtrader-provenance",
  "passed": false,
  "code": "BACKTRADER_SOURCE_WARNING",
  "severity": "warning",
  "module_origin": "/.../site-packages/backtrader/__init__.py",
  "message": "installed backtrader cannot be verified as cloudQuant/backtrader"
}
~~~

对目标源码错误，源码转发器维持现有结构化 JSON 错误形状，但 code 为
`BACKTRADER_SOURCE_MISMATCH`。这使脚本调用者可区分路径不存在与路径来源不合规。

## 6. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 普通 PyPI 包没有 VCS 元数据 | 不猜测；明确 warning |
| editable 安装使用 `file://` | 解析本地 checkout remote |
| clean-wheel 使用 `-I -S` | 不在 clean acceptance 子进程执行宿主 pip 预检；只验证显式源码 target |
| 非 Git 打包源码无法证明来源 | 作为来源不匹配拒绝执行，要求用户改用 cloudQuant checkout |
| pip 网络失败 | 返回稳定安装失败状态，不伪造成功，也不覆盖已有非匹配包 |

## 7. 兼容性

支持 Python 3.10–3.13。模块只使用标准库；不新增 PyPI 运行时依赖。唯一会联网的路径是
doctor 发现模块缺失时的显式安装分支。
