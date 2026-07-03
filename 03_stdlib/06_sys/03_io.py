"""sys —— 标准流与编码

标准库。Python 3.12。运行: python 03_io.py
"""
import sys
import io


def demo01_streams():
    """① sys.stdin / sys.stdout / sys.stderr：类型、fileno、encoding、line_buffering"""
    print("① 标准流属性一览")
    # stdin 在非交互模式下也存在，但演示时避免实际读取
    for name, stream in [("stdout", sys.stdout), ("stderr", sys.stderr)]:
        print(f"  sys.{name}:")
        print("    type:", type(stream))
        print("    fileno():", stream.fileno())            # 0=stdin, 1=stdout, 2=stderr
        print("    encoding:", stream.encoding)
        print("    line_buffering:", stream.line_buffering) # True 时每行末尾自动 flush
        print("    errors:", stream.errors)                  # 编码错误处理策略

    print("  sys.stdin 类型:", type(sys.stdin))
    print("  sys.stdin fileno():", sys.stdin.fileno())       # 文件描述符 0


def demo02_original_streams():
    """② sys.__stdout__ / sys.__stdin__：原始流引用（重定向后恢复用）"""
    print("② 原始流引用")
    print("  sys.__stdout__ is sys.stdout:", sys.__stdout__ is sys.stdout)
    print("  sys.__stdin__  is sys.stdin:", sys.__stdin__ is sys.stdin)
    print("  sys.__stderr__ is sys.stderr:", sys.__stderr__ is sys.stderr)
    print()
    print("  用途: 重定向 sys.stdout 后，sys.__stdout__ 始终指向真实终端")
    print("    恢复写法: sys.stdout = sys.__stdout__")
    print("    优于直接赋值的地方: 无需事先保存，随时可取原始流")


def demo03_encoding():
    """③ sys.getdefaultencoding() / sys.getfilesystemencoding() / sys.getwindowsversion()"""
    print("③ 编码查询")
    print("  sys.getdefaultencoding():", sys.getdefaultencoding())        # 通常 'utf-8'
    print("  sys.getfilesystemencoding():", sys.getfilesystemencoding())  # 文件名编码
    print()
    print("  区别:")
    print("    getdefaultencoding() — str.encode() 默认编码，Python 3 固定 utf-8")
    print("    getfilesystemencoding() — 文件路径与操作系统交互时用的编码")
    print("      Windows: 'utf-8'（Python 3.6+ 默认）/ 旧版可能 'mbcs'")
    print("      Linux/macOS: 通常 'utf-8'")
    print()
    if hasattr(sys, "getwindowsversion"):
        wv = sys.getwindowsversion()
        print("  sys.getwindowsversion():", wv)
        print("    major:", wv.major, "  minor:", wv.minor, "  build:", wv.build)
        print("    service_pack:", wv.service_pack)
    else:
        print("  sys.getwindowsversion(): 仅 Windows 可用（当前非 Windows）")


def demo04_redirect_stdout():
    """④ 重定向 stdout 到 StringIO，捕获函数输出，再恢复"""
    print("④ 重定向 stdout 捕获输出")

    def greet(name: str) -> None:
        """内含 print 的普通函数——演示如何捕获其输出"""
        print(f"Hello, {name}!")
        print(f"欢迎来到 Python 世界，{name}。")

    buf = io.StringIO()
    _orig_stdout = sys.stdout
    sys.stdout = buf             # 重定向到内存缓冲区
    try:
        greet("Alice")
        greet("Bob")
    finally:
        sys.stdout = _orig_stdout  # finally 保证一定恢复，即使 greet 抛异常

    captured = buf.getvalue()
    print("  捕获到的内容（共", len(captured.splitlines()), "行）:")
    for line in captured.splitlines():
        print("   |", line)
    print("  类型:", type(captured))

    print()
    print("  更 Pythonic 的写法（contextlib.redirect_stdout）:")
    import contextlib
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        print("contextlib 捕获的内容")
    print("  contextlib 捕获结果:", buf2.getvalue().strip())


def demo05_write_vs_print():
    """⑤ sys.stdout.write vs print：差异"""
    print("⑤ write vs print 的差异")

    # write：返回写入字符数，不自动加换行，不支持 sep/end/file 参数
    n = sys.stdout.write("  write 输出（无换行）—— ")
    sys.stdout.write("同一行继续\n")      # 手动加换行
    print("  write 返回值（写入字符数）:", n)

    print()
    # print 是对 write 的高层封装
    print("  print(sep='|', end='!') ->", end=" ")
    print("A", "B", "C", sep="|", end="!\n")

    print()
    # print 到 stderr（常用于错误提示，不被 stdout 重定向影响）
    print("  写 stderr（下一行输出到 stderr）:")
    print("  [stderr] 这是一条错误提示", file=sys.stderr)

    print()
    print("  总结:")
    print("    write(s)  — 原始写入，无额外处理，返回字符数")
    print("    print(*)  — 自动 sep 连接、end 结尾、支持 file 参数，更易用")


if __name__ == "__main__":
    demo01_streams()
    print()
    demo02_original_streams()
    print()
    demo03_encoding()
    print()
    demo04_redirect_stdout()
    print()
    demo05_write_vs_print()
