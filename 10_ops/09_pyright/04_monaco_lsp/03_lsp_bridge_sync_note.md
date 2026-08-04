# FastAPI WebSocket 为什么不支持纯同步

FastAPI 的 HTTP 端点可以写 `def`（自动丢线程池），但 **WebSocket 端点必须 `async def`**。
原因是 WebSocket 是长连接，不能"丢线程池跑完就返回"。

## 如果非要用 FastAPI 且减少 async

思路：把阻塞的核心逻辑用 `asyncio.to_thread()` 包一层，让 async handler 尽量薄。

```python
import asyncio
from fastapi import FastAPI, WebSocket

app = FastAPI()

def _read_lsp_message(stdout) -> bytes | None:
    """纯同步函数，读 LSP 消息"""
    ...

@app.websocket("/lsp")
async def lsp_endpoint(ws: WebSocket):
    await ws.accept()
    pyright = subprocess.Popen(...)

    loop = asyncio.get_event_loop()

    async def ws_to_pyright():
        """前端 → Pyright：async 收 ws，同步写管道"""
        while True:
            raw = await ws.receive_text()
            pyright.stdin.write(raw.encode())      # 同步写，很快
            pyright.stdin.flush()

    async def pyright_to_ws():
        """Pyright → 前端：同步读管道丢线程，async 写 ws"""
        while True:
            body = await loop.run_in_executor(     # 把同步读扔线程池
                None, _read_lsp_message, pyright.stdout
            )
            if body is None: break
            data = json.loads(body)
            await ws.send_text(json.dumps(data))    # async 写 ws

    await asyncio.gather(ws_to_pyright(), pyright_to_ws())
```

## 如果完全不想碰 async

直接用 `02_lsp_bridge_sync.py`（websockets 同步 API + threading），零 async 代码。

## 其他同步方案

| 方案 | 说明 |
|---|---|
| `02_lsp_bridge_sync.py` | websockets 库原生同步 API，推荐 |
| Flask + Flask-SocketIO | 纯同步 Web 框架 + WS 插件，配置较繁琐 |
| Django Channels | Django 的 WS 方案，学习曲线最陡 |
