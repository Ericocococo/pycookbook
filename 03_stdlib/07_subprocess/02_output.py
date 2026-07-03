"""subprocess —— 输出控制：PIPE / DEVNULL / stderr / 实时读取

标准库。Python 3.12。
运行: python 02_output.py

核心问题：子进程输出去哪？
  - 默认：继承父进程终端，直接打到屏幕（父进程拿不到）
  - PIPE：通过内存管道，父进程捕获成字符串
  - DEVNULL：丢弃（静音，类似重定向到 /dev/null）

演示：
  ① PIPE vs DEVNULL vs 默认（不捕获）
  ② stderr 三种策略：分别捕获 / 合并 / 静默
  ③ encoding / errors：精确控制字节解码
  ④ 实时逐行读取：Popen + stdout 迭代
"""
import subprocess


def demo01_pipe_vs_devnull():
    """① 三种输出目的地对比"""
    print("① 三种输出模式")

    # 默认：子进程输出直接打到终端，父进程拿不到
    print("  [不捕获] 子进程输出直接出现在终端 ↓")
    subprocess.run(["python", "-c", "print('我在终端')"])

    print()

    # PIPE：父进程通过管道读取，终端看不到
    r = subprocess.run(
        ["python", "-c", "print('我在管道')"],
        stdout=subprocess.PIPE,
        text=True,
    )
    print("  [PIPE] 父进程捕获到:", repr(r.stdout.strip()))

    # DEVNULL：输出被丢弃，终端和父进程都看不到
    r = subprocess.run(
        ["python", "-c", "print('我被丢弃了')"],
        stdout=subprocess.DEVNULL,
    )
    print("  [DEVNULL] returncode:", r.returncode, "（输出已静默丢弃）")


def demo02_stderr():
    """② stderr 的三种处理策略

    子进程有两条输出流：
      stdout  正常输出（print 默认走这里）
      stderr  错误/诊断输出（print(file=sys.stderr)、traceback 走这里）

    三种策略：
      capture_output=True      分别捕获 stdout 和 stderr（最常用）
      stderr=STDOUT            合并到 stdout（适合需要完整日志的场景）
      stderr=DEVNULL           静默错误
    """
    print("\n② stderr 处理策略")

    # 策略一：分别捕获（stdout 和 stderr 互不干扰）
    r = subprocess.run(
        ["python", "-c",
         "import sys; print('out内容'); print('err内容', file=sys.stderr)"],
        capture_output=True,   # stdout=PIPE + stderr=PIPE 的缩写
        text=True,
    )
    print("  [分别捕获] stdout:", repr(r.stdout.strip()))
    print("  [分别捕获] stderr:", repr(r.stderr.strip()))

    # 策略二：合并到 stdout（stderr 内容按顺序混入 stdout）
    r = subprocess.run(
        ["python", "-c",
         "import sys; print('out'); print('err', file=sys.stderr)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # stderr 流合并进 stdout
        text=True,
    )
    print("  [合并] 混合流:", repr(r.stdout.strip()))

    # 策略三：静默 stderr，只捕获 stdout
    r = subprocess.run(
        ["python", "-c",
         "import sys; sys.stderr.write('error'); print('ok')"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # 丢弃 stderr
        text=True,
    )
    print("  [DEVNULL stderr] 只拿 stdout:", repr(r.stdout.strip()))


def demo03_encoding():
    """③ encoding / errors：精确控制字节解码

    术语：
      text=True       让 stdout/stderr 自动解码，等价于 encoding=locale 默认编码
      encoding        手动指定解码编码，如 "utf-8" "gbk" "cp936"
      errors          解码失败时的处理策略：
                        "strict"（默认）→ 抛 UnicodeDecodeError
                        "replace"       → 用 '?' 替换无法解码的字节
                        "ignore"        → 丢弃无法解码的字节

    Windows 中文系统默认编码是 cp936（GBK），遇到 UTF-8 输出需显式指定。
    """
    print("\n③ encoding / errors")

    # 显式指定 encoding（等价于 text=True，但更明确）
    r = subprocess.run(
        ["python", "-c", "print('你好，世界')"],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    print("  encoding=utf-8:", repr(r.stdout.strip()))

    # errors="replace"：遇到无法解码的字节，用 '?' 替换（不崩溃）
    r = subprocess.run(
        ["python", "-c",
         # 故意写入无效 UTF-8 字节（\xff\xfe）
         r"import sys; sys.stdout.buffer.write(b'hello\xff\xfe')"],
        stdout=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",   # 坏字节替换为 '?' 而非抛异常
    )
    print("  errors=replace:", repr(r.stdout))   # 'hello��' 或 'hello??'


def demo04_realtime():
    """④ 实时逐行读取（Popen + stdout 迭代）

    run() 必须等子进程全部结束才返回，无法实时看到输出。
    需要实时读取时，用 Popen + 逐行迭代 stdout。

    关键：
      python -u  子进程以无缓冲模式运行（否则输出会在缓冲区积攒，不实时）
      flush=True 每行 print 后立即刷新（也可以用 -u 统一解决）
    """
    print("\n④ 实时逐行读取")

    # 模拟一个持续输出的子进程（每 0.2 秒输出一行）
    script = (
        "import time, sys\n"
        "for i in range(4):\n"
        "    print(f'行 {i}', flush=True)\n"
        "    time.sleep(0.2)\n"
    )

    with subprocess.Popen(
        ["python", "-u", "-c", script],   # -u：无缓冲，保证实时
        stdout=subprocess.PIPE,
        text=True,
    ) as proc:
        # 逐行读，不等子进程结束
        for line in proc.stdout:
            print("  实时收到:", line, end="")
    print("  子进程结束，returncode:", proc.returncode)


if __name__ == "__main__":
    demo01_pipe_vs_devnull()
    demo02_stderr()
    demo03_encoding()
    demo04_realtime()
