"""16_websocket.py 的 WebSocket 客户端。先启动: python 16_websocket.py --serve
安装: pip install websockets
"""

from websockets.sync.client import connect


def main():
    url = "ws://127.0.0.1:8036/ws"
    print(f"连接 {url}")

    with connect(url) as ws:
        for msg in ["你好", "hello", "FastAPI WebSocket"]:
            ws.send(msg)
            reply = ws.recv()
            print(f"  发 {msg!r} → 收 {reply!r}")

    print("客户端结束")


if __name__ == "__main__":
    main()
