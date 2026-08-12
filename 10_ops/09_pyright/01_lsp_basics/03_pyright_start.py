"""③ 启动 Pyright —— 跟命令行一样，只是用代码启动

运行: python 03_pyright_start.py

之前你在命令行手动输入 pyright-langserver --stdio 启动，
现在用 subprocess.Popen 让 Python 替你启。

注意：03 之后跟 Pyright 通信用二进制管道，
因为 LSP 的 Content-Length 按字节算，不能用 text=True。

演示：
  ① 启动 Pyright，看它的启动消息
  ② 读 Pyright 的 LSP 消息
"""

import json
import shutil
import subprocess


def demo01_start():
    """① 启动 pyright-langserver，像命令行一样"""
    print("① 启动 Pyright")

    exe = shutil.which("pyright-langserver")
    print(f"  Pyright 位置: {exe}")

    p = subprocess.Popen(
        [exe, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    print(f"  进程 PID: {p.pid}")
    print(f"  还在跑: {p.poll() is None}")

    p.kill()
    p.wait()
    print("  已关闭")


def demo02_read_message():
    """② 读 Pyright 发出的第一条消息"""
    print("\n② 读 Pyright 的启动消息")

    exe = shutil.which("pyright-langserver")
    p = subprocess.Popen(
        [exe, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    line = p.stdout.readline()
    print(f"  收到第一行: {line!r}")               # b'Content-Length: 119\r\n'

    p.kill()
    p.wait()


def demo03_full_message():
    """③ 完整读完一条 Pyright 消息"""
    print("\n③ 完整读一条消息")

    exe = shutil.which("pyright-langserver")
    p = subprocess.Popen(
        [exe, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    # 步骤 1：读头部，拿到 Content-Length
    content_length = 0
    while True:
        line = p.stdout.readline()
        if line.startswith("Content-Length:"):
            content_length = int(line.split(":")[1])
        if not line.strip():                      # 空行 = 头部结束
            break

    # 步骤 2：读 Content-Length 个字节，解码为 JSON
    body = p.stdout.read(content_length)
    data = json.loads(body)
    print(data)
    print(f"  消息长度: {content_length} 字节")
    print(f"  方法: {data['method']}")            # window/logMessage
    print(f"  内容: {data['params']['message']}")   # 启动日志

    p.kill()
    p.wait()


if __name__ == "__main__":
    demo01_start()
    demo02_read_message()
    demo03_full_message()
