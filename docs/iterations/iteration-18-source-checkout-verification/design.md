# Iteration 18：源码检出验证转发器可靠性——设计文档

## 1. 设计决策

在 src/backtrader_skills/source_checkout.py 中提供唯一的
resolve_backtrader_repository 函数。它不依赖当前工作目录，不扫描任意祖先目录，也不
读取网络或用户主目录；因此同一产品路径与显式输入始终得到相同结果。

解析成功的最小结构条件是：

~~~text
<repository>/backtrader/version.py
~~~

该条件与 doctor 的 target-backtrader-source 检查保持一致。验收和子进程还会使用该
目录下实际的包内容，因此结构正确且不存在包时会在既有验收中失败，不把“存在空文件”误
报为完整功能成功。

## 2. 模块边界

| 文件 | 责任 |
| --- | --- |
| src/backtrader_skills/source_checkout.py | 根目录结构判断、候选顺序和稳定错误 |
| src/backtrader_skills/errors.py | 新增 SOURCE_CHECKOUT_NOT_FOUND 稳定错误类型 |
| scripts/doctor.py | 解析 --target，并把结果交给规范 CLI doctor |
| scripts/run_acceptance.py | 解析 --repository，并把其余参数交给规范 acceptance CLI |
| tests/test_source_checkout.py | 纯解析、脚本显式覆盖和错误 JSON 契约 |
| README.md | 英文与中文操作说明 |

## 3. 解析算法

~~~python
def resolve_backtrader_repository(product_root, explicit=None):
    candidates = [explicit] if explicit is not None else [
        product_root.parent,
        product_root.parent / "backtrader",
    ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "backtrader" / "version.py").is_file():
            return resolved
    raise SourceCheckoutNotFound(...)
~~~

显式输入不会在无效时回退到自动发现，避免调用方拼写错误被悄悄掩盖。

## 4. 转发器协议

两个脚本各自仅消费自己的路径参数，并使用 parse_known_args 保留规范 CLI 的其余参数。
解析异常以与规范 CLI 相同形状的 JSON 错误输出：

~~~json
{
  "status": "error",
  "code": "SOURCE_CHECKOUT_NOT_FOUND",
  "message": "..."
}
~~~

进程退出码为 2。成功路径继续调用已有 main 函数，因此不复制 doctor 或 acceptance 的
业务逻辑。

## 5. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 脚本参数被吞掉 | 测试 --matrix 等剩余参数仍会透传；仅剥离本脚本的路径参数 |
| 错误路径被静默接受 | 显式路径验证失败立即返回稳定错误 |
| CI 没有同级 Backtrader | 布局解析为纯临时目录单测；真实完整验收只在拥有 Backtrader 源码时执行 |
| 文档再次漂移 | 验收清单逐条执行 README 的命令 |

## 6. 兼容性

Python 3.10–3.13；不新增运行时第三方依赖；不改变已安装 CLI 的命令格式和 JSON 成功
载荷。

## 7. 分发清单

manifest.json 是本产品对源码、脚本、资源和技能文件的哈希承诺。source_checkout.py 和两个
转发器的改变都会影响该承诺，因此使用既有 scripts/build_manifest.py 在代码定稿后重建。
验收必须先验证该清单，再运行 wheel 安装隔离验收；不得手工编辑文件哈希。
