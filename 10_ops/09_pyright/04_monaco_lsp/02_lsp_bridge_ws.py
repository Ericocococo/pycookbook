"""
Pyright LSP WebSocket 桥接服务 —— websockets 方案

优势：极简，只一个依赖，无路由/ASGI 转发层

职责：
  - WebSocket 接收前端 Monaco Editor 的 LSP 请求
  - 注入 rootUri，让 Pyright 能找到 interface 包提供补全
  - 转发给 pyright-langserver 子进程
  - 将 Pyright 响应回传给前端

前端同事连接：
  ws://127.0.0.1:3001

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/02_lsp_bridge_ws.py --serve

依赖：
  pip install websockets
  npm install -g pyright
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

import websockets

_DIR = Path(__file__).resolve().parent


# ──────────────────────────────────────────
# 工作区路径——让 Pyright 能找到 interface 包
# ──────────────────────────────────────────
# 前端用虚拟 URI（file:///workspace/main.py），桥接层替换成磁盘真实路径再转发给 Pyright，
# Pyright 响应回来再替换回虚拟路径。这样 Pyright 看到文件与 interface/ 同级，能正确解析 import。
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
# WebSocket 处理
# ──────────────────────────────────────────
async def lsp_handler(ws) -> None:
    """每个 WebSocket 连接启动一个 pyright 进程，双向桥接"""
    pyright = subprocess.Popen(
        [_LANGSERVER, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    loop = asyncio.get_event_loop()

    async def ws_to_pyright():
        """前端 → Pyright（注入 rootUri，重写虚拟路径为真实路径）"""
        async for message in ws:
            text = message if isinstance(message, str) else message.decode()
            # 虚拟路径 → 磁盘真实路径
            text = _rewrite_to_real(text)
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
            await ws.send(text)

    try:
        await asyncio.gather(ws_to_pyright(), pyright_to_ws())
    finally:
        pyright.kill()


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pyright LSP WebSocket 桥接服务")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    # args = parser.parse_args()
    args = parser.parse_args([
        "--serve",
    ])

    if args.serve:
        async def _start():
            await websockets.serve(lsp_handler, args.host, args.port)
            print(f"WebSocket 服务:  ws://{args.host}:{args.port}")
            await asyncio.Future()  # 永久挂起

        asyncio.run(_start())
    else:
        print("Pyright LSP WebSocket 桥接服务（websockets 方案）")
        print()
        print("启动：python 02_lsp_bridge_ws.py --serve")
        print("前端连接：ws://127.0.0.1:3001")
