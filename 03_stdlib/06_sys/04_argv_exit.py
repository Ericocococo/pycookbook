"""sys —— 命令行参数与退出

标准库。Python 3.12。运行: python 04_argv_exit.py
也可传参演示: python 04_argv_exit.py hello world --flag
"""
import sys


def demo01_argv():
    """① sys.argv：结构（argv[0]=脚本路径，后续为参数）；模拟解析"""
    print("① sys.argv —— 命令行参数列表")
    print("  sys.argv:", sys.argv)
    print("  argv[0]（脚本路径）:", sys.argv[0])
    print("  后续参数 argv[1:]:", sys.argv[1:])
    print()

    # 简单手工解析（无需 argparse 时的轻量方案）
    args = sys.argv[1:]
    flags = [a for a in args if a.startswith("--")]
    positional = [a for a in args if not a.startswith("-")]
    options = [a for a in args if a.startswith("-") and not a.startswith("--")]
    print("  位置参数:", positional)
    print("  长选项（--xxx）:", flags)
    print("  短选项（-x）:", options)
    print()
    print("  提示: 复杂参数解析请用 argparse 或 click / typer")
    print("    sys.argv 适合极简脚本（1-2 个参数、无需帮助文档）")


def demo02_exit():
    """② sys.exit()：触发 SystemExit 异常的三种形式"""
    print("② sys.exit —— 触发 SystemExit（不在这里真正退出）")
    print("  sys.exit(0)        -> SystemExit(0)      正常退出，code=0 表示成功")
    print("  sys.exit(1)        -> SystemExit(1)      异常退出，code≠0 表示失败")
    print("  sys.exit('msg')    -> SystemExit('msg')  打印 msg 到 stderr，以 code=1 退出")
    print()
    print("  底层: sys.exit() 只是 raise SystemExit(code)")
    print("  因此可以被 try/except SystemExit 捕获（见 demo03）")
    print("  如果不被捕获，解释器处理 SystemExit 时会正常退出（不打印 traceback）")


def demo03_catch_exit():
    """③ 用 try/except SystemExit 捕获退出（常用于测试 / 演示）"""
    print("③ 捕获 SystemExit —— 测试或演示时避免真正退出")

    test_cases = [0, 1, 2, "操作失败：找不到配置文件", None]
    for code in test_cases:
        try:
            sys.exit(code)
        except SystemExit as e:
            print(f"  sys.exit({code!r:30s}) -> SystemExit.code = {e.code!r}")

    print()
    print("  规律:")
    print("    sys.exit(0)    -> code=0  （通常认为成功）")
    print("    sys.exit(int)  -> code=该整数")
    print("    sys.exit(str)  -> code=该字符串（shell 中实际 exit code=1）")
    print("    sys.exit()     -> code=None（等同于 exit code=0）")
    print()
    print("  测试框架常见用法:")
    print("    with pytest.raises(SystemExit) as exc_info:")
    print("        some_func_that_calls_sys_exit()")
    print("    assert exc_info.value.code == 0")


def demo04_flags():
    """④ sys.flags：查看解释器启动标志"""
    print("④ sys.flags —— 解释器启动标志（只读，反映 python 命令行选项）")
    f = sys.flags
    print("  sys.flags:", f)
    print()
    print("  常用字段（当前值）:")
    print("    debug        (-d):", f.debug)          # python -d：启用内部调试输出
    print("    inspect      (-i):", f.inspect)        # python -i：脚本结束后进入交互
    print("    interactive  (-c 或 stdin):", f.interactive)
    print("    optimize     (-O/-OO):", f.optimize)   # -O=1 去 assert，-OO=2 也去 docstring
    print("    no_site      (-S):", f.no_site)        # python -S：不自动 import site
    print("    verbose      (-v):", f.verbose)        # 导入模块时打印来源
    print("    bytes_warning(-b):", f.bytes_warning)  # bytes/str 比较时发警告
    print("    ignore_environment (-E):", f.ignore_environment)  # 忽略 PYTHON* 环境变量
    print("    isolated     (-I):", f.isolated)       # 隔离模式：-E -s 组合，常用于工具链
    print("    utf8_mode    (-X utf8):", f.utf8_mode) # 强制 UTF-8 模式（Python 3.7+）


if __name__ == "__main__":
    demo01_argv()
    print()
    demo02_exit()
    print()
    demo03_catch_exit()
    print()
    demo04_flags()
