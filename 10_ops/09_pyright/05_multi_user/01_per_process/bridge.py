"""
阶段1：一连接一进程

每个 WebSocket 连接启动独立的 Pyright 进程，天然隔离，无需路由。

优点：简单，用户之间完全隔离
缺点：内存开销大（每进程 ~150MB），50 用户就要 ~7.5GB

架构：
  用户A ─→ ws_a ─→ Pyright_A
  用户B ─→ ws_b ─→ Pyright_B
  用户C ─→ ws_c ─→ Pyright_C

运行方式（在项目根目录）：
  python 10_ops/09_pyright/05_multi_user/01_per_process/bridge.py --serve

端口：ws://127.0.0.1:3001/lsp

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

# _DIR 指向本阶段目录（interface 包所在目录）
_DIR = Path(__file__).resolve().parent

app = FastAPI(title="阶段1：一连接一进程")

# ──────────────────────────────────────────
# 工作区路径——让 Pyright 能找到 interface 包
# ──────────────────────────────────────────
_dir_posix = _DIR.as_posix()
if len(_dir_posix) >= 2 and _dir_posix[1] == ':':
    _dir_posix = _dir_posix[0].lower() + _dir_posix[1:]
    _WORKSPACE_URI = f"file:///{_dir_posix}"
else:
    _WORKSPACE_URI = f"file://{_dir_posix}"
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
# 补全排序——typing 符号和 dunder 排到末尾
# ──────────────────────────────────────────
_DEMOTE_NAMES = frozenset({
    'annotations', 'Any', 'Callable', 'ClassVar', 'Dict', 'Final',
    'Generic', 'List', 'Literal', 'Optional', 'Protocol', 'Set',
    'Tuple', 'Type', 'TypeVar', 'Union', 'TYPE_CHECKING', 'TypedDict',
    'runtime_checkable', 'overload', 'cast', 'no_type_check',
})


def _reorder_completions(data: dict) -> None:
    """把 typing 导入和 dunder 属性排到补全列表末尾"""
    if "result" not in data or not isinstance(data.get("result"), dict):
        return
    items = data["result"].get("items")
    if not items:
        return
    for item in items:
        label = item.get("label", "")
        if label in _DEMOTE_NAMES or label.startswith("_"):
            item["sortText"] = "zz" + item.get("sortText", label)


# ──────────────────────────────────────────
# WebSocket 端点
# ──────────────────────────────────────────
@app.websocket("/lsp")
async def lsp_endpoint(ws: WebSocket):
    """每个连接启动一个 Pyright 进程，一对一绑定"""
    await ws.accept()
    print(f"[阶段1] 新连接，启动独立 Pyright 进程")

    pyright = subprocess.Popen(
        [_LANGSERVER, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    loop = asyncio.get_event_loop()

    async def ws_to_pyright():
        """前端 → Pyright（注入 rootUri，重写路径）"""
        try:
            while True:
                raw = await ws.receive_text()
                text = _rewrite_to_real(raw)
                # 拦截 initialize，注入 rootUri
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
        """Pyright → 前端（回写虚拟路径，补全排序）"""
        while True:
            body = await loop.run_in_executor(
                None, _read_lsp_message, pyright.stdout
            )
            if body is None:
                break
            text = _rewrite_to_virtual(body.decode())
            data = json.loads(text)
            _reorder_completions(data)
            await ws.send_text(json.dumps(data, ensure_ascii=False))

    try:
        await asyncio.gather(ws_to_pyright(), pyright_to_ws())
    finally:
        pyright.kill()
        print(f"[阶段1] 连接断开，Pyright 进程已回收")


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="阶段1：一连接一进程")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    parser.add_argument("--workers", type=int, default=1, help="uvicorn worker 进程数（生产部署用）")
    args = parser.parse_args(["--serve"])

    if args.serve:
        print(f"阶段1 桥接服务: ws://{args.host}:{args.port}/lsp")
        print(f"每个连接独立启动一个 Pyright 进程（uvicorn workers={args.workers}）")
        if args.workers > 1:
            # 多 worker 模式需要用模块字符串，不能传 app 对象
            uvicorn.run("bridge:app", host=args.host, port=args.port, workers=args.workers)
        else:
            uvicorn.run(app, host=args.host, port=args.port)
