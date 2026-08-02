# Iteration 22：受支持 Python CI 矩阵——需求文档

## 背景与问题

`pyproject.toml` 声明 `requires-python >=3.10`，并列出 Python 3.10、3.11、3.12、3.13
classifiers；README 的中英文安装说明也承诺支持 3.10–3.13。但当前 GitHub Actions 固定使用
Python 3.11，因此其余三个公开支持版本没有持续验证。

## 目标

让公开的 Python 支持承诺成为可执行 CI 契约，同时避免把静态分析和目录/清单检查重复运行四次。

## 功能需求

### FR-1：运行时测试矩阵

CI 新增或改造一个测试 job，矩阵必须精确包含 `3.10`、`3.11`、`3.12`、`3.13`，并将
`actions/setup-python` 的 `python-version` 绑定到 `matrix.python-version`。每个单元安装
`.[test]` 后运行 `python -m pytest tests -q`。

### FR-2：质量门禁单次运行

Ruff、Black、Mypy、catalog 和 manifest 检查保留在一个固定 Python 3.11 的 quality job，安装
`.[dev]`。不得因矩阵引入重复且无额外覆盖价值的四倍静态门禁。

### FR-3：配置回归保护

新增本地 pytest，读取 workflow 并断言精确四版本矩阵、动态 setup-python 引用、`.[test]`
安装路径和质量 job 的 mypy 命令，防止未来悄然缩小承诺覆盖范围。

### FR-4：现实执行边界

GitHub-hosted matrix 验证不需要本地预装四个解释器。当前本地验收验证 workflow 契约和可用
解释器上的完整测试；PR 或 push 后由 GitHub Actions 执行实际四版本测试。源 Backtrader
checkout 仍不在 hosted CI 中，依赖它的测试按既有规则跳过，完整 7 x 2 runner acceptance
仍是本地发布门禁。

### FR-5：发布完整性

完成 pytest、mypy、Ruff、Black、manifest/catalog、doctor、clean-wheel acceptance 和
`git diff --check`，并记录可复现证据。

## 非目标

- 不降低 `requires-python`，不改变运行时依赖或发布包内容。
- 不在 CI 下载或发布用户的 Backtrader fork。
- 不引入 tox、nox、Docker 或新的测试编排依赖。
- 不声称在未触发远端 workflow 前已获得 GitHub-hosted 的四版本执行结果。

## 成功标准

1. CI 测试 job 精确覆盖 Python 3.10–3.13，且动态选择解释器。
2. quality job 仅一次执行现有质量门禁并包含 Mypy。
3. 配置契约有本地回归测试；本地完整测试与现有发布门禁通过。
4. 验收文档清楚区分本地验证与待 GitHub Actions 触发的 hosted 执行。
