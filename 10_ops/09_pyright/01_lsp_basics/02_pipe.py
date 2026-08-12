"""② 管道通信 —— 读子进程的输出、往子进程发消息

运行: python 02_pipe.py

默认情况下子进程的输出直接打印到终端，你的代码读不到。
加上 PIPE 就建了一根"管道"，你的代码可以通过这根管子读/写。

演示：
  ① PIPE 读子进程的输出
  ② PIPE 往子进程发数据
  ③ stdin + stdout 双向管道
"""

import subprocess


def demo01_read_pipe():
    """① stdout=PIPE —— 读子进程的输出"""
    print("① 读子进程的输出")

    # stdout=PIPE + text=True：输出自动转字符串，不用 .decode()
    p = subprocess.Popen(
        ["python", "-c", "print('hello from 子进程')"],
        stdout=subprocess.PIPE,
        text=True,                         # ← 自动 str，不用写 .decode()
    )

    output = p.stdout.read()
    p.wait()
    print(f"  读到: {output!r}")


def demo02_write_pipe():
    """② stdin=PIPE —— 往子进程发数据"""
    print("\n② 往子进程发数据")

    # 这个子进程会读一行输入，然后回一句
    p = subprocess.Popen(
        ["python", "-c", "name = input(); print(f'你好，{name}')"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,                         # ← 自动 str，不用写 .encode()/.decode()
    )

    p.stdin.write("Alice\n")              # 直接写字符串
    p.stdin.flush()
    reply = p.stdout.readline()            # 直接读字符串
    p.wait()

    print(f"  子进程回: {reply.strip()!r}")


def demo03_bidirectional():
    """③ stdin + stdout 双向管道 = 跟子进程对话"""
    print("\n③ 双向对话")

    # 子进程代码：一直等输入，收到 quit 才退出
    child_code = """
import sys
for line in sys.stdin:
    line = line.strip()
    if line == "quit":
        break
    print(f"echo: {line}")
    sys.stdout.flush()
"""
    p = subprocess.Popen(
        ["python", "-c", child_code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,                         # 自动 str 编解码，不用手写 .encode()/.decode()
    )

    # 跟子进程对话三个回合
    for msg in ["你好", "hello", "quit"]:
        p.stdin.write(msg + "\n")
        p.stdin.flush()
        if msg != "quit":
            print(f"  发 {msg!r} → 收 {p.stdout.readline().strip()!r}")

    p.wait()
    print("  对话结束")


if __name__ == "__main__":
    demo01_read_pipe()
    demo02_write_pipe()
    demo03_bidirectional()
