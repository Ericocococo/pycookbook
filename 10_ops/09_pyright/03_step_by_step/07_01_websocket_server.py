"""⑦-1 WebSocket 基础（服务端）—— 最简单的回声服务器

运行（开两个终端）：
  终端1  python 07_01_websocket_server.py --serve    # 起服务端（本文件），阻塞等连接
  终端2  python 07_02_websocket_client.py --client    # 起客户端（隔壁文件），发消息看回声

前面都是直接发消息给 Pyright（本机管道），但编辑器要通过网络连你的代码。
WebSocket 就是浏览器和你的服务之间那根"网线"。本例先脱离 Pyright，
只练最基础的 WebSocket 服务端：客户端发什么，就原样加"回声:"前缀返回。

演示：
  ① serve()           —— 起 WebSocket 服务端
  ② for message in ws —— 阻塞收消息，来一条处理一条
  ③ with vs 手动 close —— 两种资源管理写法对比

┌──────────────────────────────────────────────────┐
│ with 写法（推荐）  │ 手动写法                    │
│ ─────────────────  │ ─────────────────           │
│ 自动 shutdown      │ 需 try/finally 保证关闭     │
│ 代码更短           │ 可灵活控制生命周期          │
└──────────────────────────────────────────────────┘
"""

import argparse
from websockets.sync.server import serve


# ──────────────────────────────────────────
# 服务端处理函数
# ──────────────────────────────────────────
def handler(ws):
    """
    每来一个连接，serve() 就调一次 handler。
    for message in ws 是阻塞循环：有消息才执行一次，客户端断开循环自动结束。
    """
    for message in ws:                       # 阻塞等客户端发消息（websockets.sync 收到的是 str）
        print(f"  服务端收到: {message}")
        ws.send(f"回声: {message}")           # 原样加前缀回给客户端


# ──────────────────────────────────────────
# 写法 1: with（推荐）
# ──────────────────────────────────────────
def run_with(host: str, port: int):
    """with 退出时自动 server.shutdown()"""
    print(f"[with] 回声服务端:  ws://{host}:{port}（Ctrl+C 停止）")
    with serve(handler, host, port) as server:
        server.serve_forever()               # 阻塞，一直服务
    # ← 到这里 server 已 shutdown


# ──────────────────────────────────────────
# 写法 2: 手动 shutdown
# ──────────────────────────────────────────
def run_manual(host: str, port: int):
    """不用 with，必须自己 try/finally 保证 shutdown"""
    print(f"[手动] 回声服务端:  ws://{host}:{port}（Ctrl+C 停止）")
    server = serve(handler, host, port)
    try:
        server.serve_forever()
    finally:
        server.shutdown()                    # 必须在 finally 里关，否则异常时端口不释放


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="起服务端")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    # IDE 里直接跑就起服务端
    args = parser.parse_args(['--serve'])

    if args.serve:
        run_with(args.host, args.port)
    else:
        print("WebSocket 回声服务端")
        print()
        print("启动: python 07_01_websocket_server.py --serve")
        print("再开一个终端跑客户端: python 07_02_websocket_client.py --client")
