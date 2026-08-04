"""⑦-2 WebSocket 基础（客户端）—— 连服务端，发消息收回声

运行（先起服务端，再跑本文件）：
  终端1  python 07_01_websocket_server.py --serve
  终端2  python 07_02_websocket_client.py --client

对应服务端 0701：客户端发什么，服务端加"回声:"前缀返回。

演示：
  ① connect()  —— 连上 WebSocket 服务端
  ② send/recv  —— 发一条、收一条（同步阻塞，一问一答）
  ③ with vs 手动 close —— 两种资源管理写法对比

┌──────────────────────────────────────────────────┐
│ with 写法（推荐）  │ 手动 close 写法            │
│ ─────────────────  │ ─────────────────           │
│ 自动关闭，异常安全 │ 需 try/finally 保证 close   │
│ 代码更短           │ 可灵活控制关闭时机          │
└──────────────────────────────────────────────────┘
"""

import argparse
from websockets.sync.client import connect


MESSAGES = ["你好", "hello", "123"]


# ──────────────────────────────────────────
# 写法 1: with（推荐）
# ──────────────────────────────────────────
def run_with(host: str, port: int):
    """connect() 返回的对象支持上下文管理器，离开 with 自动 close"""
    url = f"ws://{host}:{port}"
    print(f"[with] 客户端连接:  {url}")

    with connect(url) as ws:                 # 连上服务端；with 退出时自动 ws.close()
        for msg in MESSAGES:
            ws.send(msg)                     # 发一条
            reply = ws.recv()                # 阻塞等回复
            print(f"  发 {msg!r} → 收 {reply!r}")
    # ← 到这里连接已关闭，即使循环中抛异常也会关

    print("[with] 客户端结束\n")


# ──────────────────────────────────────────
# 写法 2: 手动 close
# ──────────────────────────────────────────
def run_manual(host: str, port: int):
    """不用 with，必须自己 try/finally 保证 close"""
    url = f"ws://{host}:{port}"
    print(f"[手动] 客户端连接:  {url}")

    ws = connect(url)                        # 连上服务端，返回连接对象
    try:
        for msg in MESSAGES:
            ws.send(msg)
            reply = ws.recv()
            print(f"  发 {msg!r} → 收 {reply!r}")
    finally:
        ws.close()                           # 必须在 finally 里关，否则异常时泄漏连接

    print("[手动] 客户端结束\n")


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", action="store_true", help="起客户端")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    # IDE 里直接跑就起客户端（需先起好 0701 服务端）
    args = parser.parse_args(['--client'])

    if args.client:
        try:
            run_with(args.host, args.port)
            run_manual(args.host, args.port)
        except ConnectionRefusedError:
            print("连接被拒绝，请先启动服务端: python 07_01_websocket_server.py --serve")
    else:
        print("WebSocket 回声客户端")
        print()
        print("先起服务端: python 07_01_websocket_server.py --serve")
        print("再跑客户端: python 07_02_websocket_client.py --client")
