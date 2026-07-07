"""对象表示 —— print 完整用法

Python 3.12。
运行: python 02_print.py

print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)

大多数人只用 print(x)，但四个参数各有用处。

演示：
  ① sep：多个参数之间的分隔符
  ② end：结尾字符（默认换行）
  ③ file：输出到文件或 stderr
  ④ flush：立即刷新缓冲区
  ⑤ 实际场景：进度条 / 打印到文件 / 打印到 stderr
"""
import sys


def demo01_sep():
    """① sep：控制多个参数之间的分隔符，默认空格

    print 可以接受多个参数，sep 指定它们之间的分隔符。
    """
    print("① sep 参数")

    # 默认 sep=' '
    print("  默认:", "a", "b", "c")            # a b c

    # 自定义分隔符
    print("  逗号:", "a", "b", "c", sep=",")   # a,b,c
    print("  竖线:", "a", "b", "c", sep="|")   # a|b|c
    print("  无分隔:", "a", "b", "c", sep="")  # abc
    print("  换行:", "a", "b", "c", sep="\n")  # 每个占一行

    # 打印日期：等价于 f"{y}-{m}-{d}"
    y, m, d = 2026, 7, 6
    print("  日期:", y, m, d, sep="-")         # 2026-7-6

    # 打印路径
    parts = ["home", "user", "documents"]
    print("  路径:", *parts, sep="/")           # home/user/documents


def demo02_end():
    """② end：结尾字符，默认 '\\n'（换行）

    设置 end='' 可以在同一行追加内容，
    常用于进度显示或拼接输出。
    """
    print("\n② end 参数")

    # 默认 end='\n'，每次 print 自动换行
    print("  第一行")
    print("  第二行")

    # end='' 不换行，下一个 print 接着写
    print("  不换行: ", end="")
    print("接着这里", end="")
    print("再接着")

    # end 可以是任意字符串
    items = ["苹果", "香蕉", "橙子"]
    for item in items:
        print(f"  {item}", end=" | ")
    print()    # 最后补一个换行


def demo03_file():
    """③ file：输出目标，默认 sys.stdout

    可以把 print 的输出重定向到：
      - sys.stderr：打印错误信息
      - 文件对象：写入文件
      - StringIO：写入内存字符串
    """
    print("\n③ file 参数")

    # 打印到 stderr（错误/日志信息）
    print("  这是错误信息", file=sys.stderr)
    print("  这是正常输出")   # 两行顺序可能不同，stderr 和 stdout 独立缓冲

    # 打印到文件
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                     delete=False, encoding="utf-8") as f:
        print("第一行", file=f)
        print("第二行", file=f)
        print(42, 3.14, file=f)
        tmp = f.name

    with open(tmp, encoding="utf-8") as f:
        print("  文件内容:")
        for line in f:
            print("   ", repr(line), end="")
    os.unlink(tmp)

    # 打印到 StringIO（捕获 print 输出为字符串）
    from io import StringIO
    buf = StringIO()
    print("hello", "world", sep="-", file=buf)
    print(42, file=buf)
    result = buf.getvalue()
    print(f"\n  StringIO 捕获: {result!r}")


def demo04_flush():
    """④ flush：立即刷新输出缓冲区

    Python 的输出默认有缓冲，不是写一个字符就立刻显示一个字符。
    flush=True 强制立即将缓冲区内容发送到终端/文件。

    需要 flush 的场景：
      - 进度条（实时看到更新）
      - 子进程输出（父进程实时读取）
      - 程序可能崩溃时保证日志不丢失
    """
    print("\n④ flush 参数")

    import time

    # 不 flush：可能在缓冲区积累，不实时显示
    # flush=True：每次立即显示
    print("  进度: ", end="", flush=True)
    for i in range(5):
        print(f"{i+1}/5 ", end="", flush=True)   # 实时显示
        time.sleep(0.1)
    print()    # 换行


def demo05_practical():
    """⑤ 实际场景综合示例"""
    print("\n⑤ 实际场景")

    import time

    # 场景一：进度条
    total = 10
    print("  进度条: ", end="", flush=True)
    for i in range(total + 1):
        bar = "█" * i + "░" * (total - i)
        percent = i * 10
        print(f"\r  进度条: [{bar}] {percent:3d}%", end="", flush=True)
        time.sleep(0.05)
    print()    # 完成后换行

    # 场景二：表格输出
    print("\n  表格输出:")
    headers = ["姓名", "年龄", "城市"]
    rows = [("Alice", 30, "北京"), ("Bob", 25, "上海"), ("Charlie", 35, "广州")]

    print("  ", *headers, sep="\t")
    print("  " + "-" * 30)
    for row in rows:
        print("  ", *row, sep="\t")

    # 场景三：调试时区分正常输出和错误输出
    def process(data):
        if not data:
            print("  警告: 数据为空", file=sys.stderr)
            return
        print(f"  处理数据: {data}")

    process([1, 2, 3])
    process([])


if __name__ == "__main__":
    demo01_sep()
    demo02_end()
    demo03_file()
    demo04_flush()
    demo05_practical()
