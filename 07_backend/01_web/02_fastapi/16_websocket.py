"""
16_websocket.py —— WebSocket：实时双向通信
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 16_websocket.py         # 自测（用 websockets 库当客户端）
  python 16_websocket.py --serve  # 起服务

要点:
  ① @app.websocket("/ws") —— 定义 WebSocket 端点
  ② await ws.accept() —— 接受连接
  ③ await ws.receive_text() / ws.send_text() —— 收发消息
  ④ WebSocketDisconnect —— 客户端断开时的异常处理

  和 03_step_by_step 里学的 websockets 库不同，这里用 FastAPI 内置的 WebSocket 支持，
  可以和 HTTP 路由共存在同一个 app 里。
================================================================================
"""

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

PORT = 8036
app = FastAPI()


@app.get("/")
async def root():
    return {"msg": "WebSocket 端点在 ws://127.0.0.1:8036/ws"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """① WebSocket 端点：回声 + 在线人数。"""
    # ② 接受连接
    await ws.accept()
    print(f"[WS] 客户端接入")
    try:
        while True:
            # ③ 收消息
            text = await ws.receive_text()
            print(f"[WS] 收到: {text}")
            # 回声
            await ws.send_text(f"回声: {text}")
    except WebSocketDisconnect:
        # ④ 客户端断开
        print(f"[WS] 客户端断开")


CURL_CASES = [
    {"desc": "HTTP 根路由（WebSocket 不能用 curl 测）", "path": "/"},
]

if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest

        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
