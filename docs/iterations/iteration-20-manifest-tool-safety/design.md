# Iteration 20：分发清单工具安全性——设计文档

## 1. 接口

~~~text
python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/build_manifest.py --help
~~~

默认路径调用 build_distribution_manifest；--check 路径调用 verify_distribution_manifest。两个
函数继续位于 backtrader_skills.distribution，脚本只负责参数、输出和退出码，不复制清单
计算逻辑。

## 2. 控制流

~~~python
def main(argv=None):
    args = parser.parse_args(argv)
    try:
        if args.check:
            result = verify_distribution_manifest(PRODUCT_ROOT)
            print(f"verified manifest: {result['manifest_hash']} ({result['file_count']} files)")
        else:
            result = build_distribution_manifest(PRODUCT_ROOT)
            print(f"rebuilt manifest: {result['manifest_hash']} ({len(result['files'])} files)")
    except IntegrityError as error:
        print(f"manifest check failed: {error}", file=sys.stderr)
        return 2
    return 0
~~~

argparse 在处理 --help 时先行退出，因此不会进入生成器或校验函数。

## 3. 测试边界

子进程测试在真实产品根目录调用 --help 与 --check，并比较调用前后的 manifest.json bytes。
默认重建只在该测试的最后执行，随后用 verify_distribution_manifest 复核，确保测试自身没有
留下陈旧清单。

CI 改用脚本 --check 直接覆盖该公共入口。wheel 内容和清单完整性仍由既有测试覆盖。

## 4. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| --help 触发生成 | argparse 在任何生成调用前解析参数 |
| check 异常显示 traceback | 捕获 IntegrityError 与 OSError，统一简洁 stderr 和退出码 2 |
| 默认行为意外变化 | 子进程回归测试默认调用后再验证 |
| README / CI 漂移 | 同一测试文件和 workflow 显式引用脚本命令 |
