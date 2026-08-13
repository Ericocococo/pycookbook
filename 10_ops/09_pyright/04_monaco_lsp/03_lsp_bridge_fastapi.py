"""
Pyright LSP WebSocket 桥接服务 —— FastAPI 方案

优势：可混合 HTTP + WebSocket 共用一个端口，有路由、中间件、自动文档

与 websockets 方案的区别：
  - FastAPI 底层用的还是 websockets 库，多了 ASGI 转发层（性能差异可忽略）
  - 多了路由能力（/lsp、/health 等可以写在不同函数）
  - 自带 /docs 交互式 API 文档
  - 启动方式不同：uvicorn.run(app) 而非 websockets.serve()

职责：
  - WebSocket 接收前端 Monaco Editor 的 LSP 请求
  - 注入 rootUri，让 Pyright 能找到 interface 包提供补全
  - 转发给 pyright-langserver 子进程
  - 将 Pyright 响应回传给前端

前端同事连接：
  ws://127.0.0.1:3002/lsp

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/03_lsp_bridge_fastapi.py --serve

依赖：
  pip install fastapi uvicorn
  npm install -g pyright
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Pyright LSP Bridge")


# ──────────────────────────────────────────
# 工作区路径——让 Pyright 能找到 interface 包
# ──────────────────────────────────────────
_WORKSPACE_URI = f"file:///{_DIR.as_posix()}"
_VIRTUAL_PREFIX = "file:///workspace/"
_REAL_PREFIX = _WORKSPACE_URI + "/"


def _rewrite_to_real(text: str) -> str:
    """前端虚拟路径 → 磁盘真实路径"""
    return text.replace(_VIRTUAL_PREFIX, _REAL_PREFIX)


def _rewrite_to_virtual(text: str) -> str:
    """磁盘真实路径 → 前端虚拟路径"""
    return text.replace(_REAL_PREFIX, _VIRTUAL_PREFIX)


# ──────────────────────────────────────────
# 定位 pyright-langserver
# ──────────────────────────────────────────
def _find_langserver() -> str:
    """定位 pyright-langserver 可执行文件"""
    path = shutil.which("pyright-langserver")
    if path:
        return path
    print("错误：找不到 pyright-langserver，请先安装：npm install -g pyright")
    sys.exit(1)


_LANGSERVER = _find_langserver()


# ──────────────────────────────────────────
# LSP 消息读写
# ──────────────────────────────────────────
def _read_lsp_message(stdout) -> bytes | None:
    """从 pyright stdout 读取一条 LSP 消息"""
    content_length = 0
    while True:
        line = stdout.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break
        if line.startswith(b"Content-Length:"):
            content_length = int(line.split(b":")[1].strip())
    if content_length == 0:
        return None
    return stdout.read(content_length)


def _write_lsp_message(stdin, raw: bytes) -> None:
    """向 pyright stdin 写入一条 LSP 消息"""
    header = f"Content-Length: {len(raw)}\r\n\r\n".encode()
    stdin.write(header + raw)
    stdin.flush()


# ──────────────────────────────────────────
# HTTP 端点（FastAPI 独有能力）
# ──────────────────────────────────────────
@app.get("/health")
async def health():
    """健康检查端点（websockets 方案没有）"""
    return {"status": "ok", "langserver": _LANGSERVER}


# ──────────────────────────────────────────
# WebSocket 端点
# ──────────────────────────────────────────
@app.websocket("/lsp")
async def lsp_endpoint(ws: WebSocket):
    """每个 WebSocket 连接启动一个 pyright 进程，双向桥接"""
    await ws.accept()

    pyright = subprocess.Popen(
        [_LANGSERVER, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    loop = asyncio.get_event_loop()

    async def ws_to_pyright():
        """前端 → Pyright（注入 rootUri，重写虚拟路径为真实路径）"""
        try:
            while True:
                raw = await ws.receive_text()
                # 虚拟路径 → 磁盘真实路径
                text = _rewrite_to_real(raw)
                # 拦截 initialize，注入 rootUri 让 Pyright 能找到 interface 包
                try:
                    msg = json.loads(text)
                    if msg.get("method") == "initialize":
                        msg.setdefault("params", {})
                        msg["params"]["rootUri"] = _WORKSPACE_URI
                        text = json.dumps(msg, ensure_ascii=False)
                except (json.JSONDecodeError, KeyError):
                    pass
                _write_lsp_message(pyright.stdin, text.encode())
        except WebSocketDisconnect:
            pass

    async def pyright_to_ws():
        """Pyright → 前端（回写虚拟路径）"""
        while True:
            body = await loop.run_in_executor(
                None, _read_lsp_message, pyright.stdout
            )
            if body is None:
                break
            # 磁盘真实路径 → 虚拟路径
            text = _rewrite_to_virtual(body.decode())
            await ws.send_text(text)

    try:
        await asyncio.gather(ws_to_pyright(), pyright_to_ws())
    finally:
        pyright.kill()


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pyright LSP WebSocket 桥接服务（FastAPI）")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3002)
    # args = parser.parse_args()
    args = parser.parse_args([
        '--serve',
    ])

    if args.serve:
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        print("Pyright LSP WebSocket 桥接服务（FastAPI 方案）")
        print()
        print("启动：python 03_lsp_bridge_fastapi.py --serve")
        print("前端连接：ws://127.0.0.1:3002/lsp")
        print("健康检查：http://127.0.0.1:3002/health")
        print("API 文档：http://127.0.0.1:3002/docs")
