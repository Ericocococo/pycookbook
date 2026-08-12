"""① 启动一个子进程 —— subprocess.Popen

运行: python 01_popen_start.py

Popen = Process Open = 打开一个子进程。
Python 里可以像在命令行里敲命令一样，启动任何程序。

演示：
  ① 启动一个程序（等价于命令行输入程序名）
  ② 等它跑完
  ③ 拿到退出码
"""

import subprocess


def demo01_start():
    """① 启动 Windows 自带的 ping 命令"""
    print("① 启动 ping 命令")

    # 这行代码等价于在命令行输入: ping 127.0.0.1 -n 2
    p = subprocess.Popen(["ping", "127.0.0.1", "-n", "2"])

    print(f"  进程已启动，PID: {p.pid}")
    print(f"  还在跑吗？{p.poll() is None}")     # poll() 返回 None = 还在跑


def demo02_wait():
    """② wait() —— 等子进程跑完"""
    print("\n② 等待进程结束")

    p = subprocess.Popen(["ping", "127.0.0.1", "-n", "2"])
    print("  等待中...")

    returncode = p.wait()                         # 阻塞等待，直到进程退出
    print(f"  进程结束，退出码: {returncode}")     # 0 = 成功，非 0 = 出错


def demo03_poll():
    """③ poll() —— 看一眼进程状态，不阻塞"""
    print("\n③ poll() 非阻塞检查")

    p = subprocess.Popen(["ping", "127.0.0.1", "-n", "3"])
    print(f"  启动后立即 poll(): {p.poll()}")      # None → 还在跑

    p.wait()
    print(f"  跑完后 poll(): {p.poll()}")           # 0 → 已结束，退出码 0


def demo04_list():
    """④ 命令写成列表，第一个是要运行的程序，后面是参数"""
    print("\n④ 命令的写法")

    # 写法一：列表（推荐，不会引发 shell 注入）
    subprocess.Popen(["ping", "127.0.0.1", "-n", "1"]).wait()

    # 这就是你之前看到的：
    # subprocess.Popen(["pyright-langserver", "--stdio"])
    #     ↑ 程序名               ↑ 参数


if __name__ == "__main__":
    demo01_start()
    demo02_wait()
    demo03_poll()
    demo04_list()
