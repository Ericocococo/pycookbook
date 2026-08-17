"""
阶段3：Pyright 进程池 + 调度

固定 N 个 Pyright Worker 进程，新连接按最少连接数分配到 Worker。
每个 Worker 内部的路由逻辑与阶段2 相同（session ID + 文件名隔离 + ID 映射）。

用户隔离方式：用文件名区分，不建子目录
  用户A → file:///真实路径/_s_a1b2c3d4.py  (Worker-0)
  用户B → file:///真实路径/_s_c5d6e7f8.py  (Worker-1)

优点：兼顾内存和并发（N×150MB，N 可配置）
缺点：实现复杂，需要 Worker 生命周期管理

运行方式（在项目根目录）：
  python 10_ops/09_pyright/05_multi_user/03_process_pool/bridge.py --serve

端口：ws://127.0.0.1:4003/lsp

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
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

_DIR = Path(__file__).resolve().parent
_dir_posix = _DIR.as_posix()
if len(_dir_posix) >= 2 and _dir_posix[1] == ':':
    _dir_posix = _dir_posix[0].lower() + _dir_posix[1:]
    _WORKSPACE_URI = f"file:///{_dir_posix}"
else:
    _WORKSPACE_URI = f"file://{_dir_posix}"
_VIRTUAL_PREFIX = "file:///workspace/"

POOL_SIZE = 3


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
    header = f"Content-Length: {len(raw)}\r\n\r\n".encode()
    stdin.write(header + raw)
    stdin.flush()


# ──────────────────────────────────────────
# URI 映射
# ──────────────────────────────────────────
def _real_prefix(session_id: str) -> str:
    return f"{_WORKSPACE_URI}/_s_{session_id}_"


def _extract_session(uri: str) -> str | None:
    uri = unquote(uri)
    marker = f"{_WORKSPACE_URI}/_s_"
    if not uri.startswith(marker):
        return None
    rest = uri[len(marker):]
    if len(rest) < 8:
        return None
    return rest[:8]


def _rewrite_to_real(text: str, session_id: str) -> str:
    return text.replace(_VIRTUAL_PREFIX, _real_prefix(session_id))


def _rewrite_to_virtual(text: str, session_id: str) -> str:
    real = _real_prefix(session_id)
    text = text.replace(real, _VIRTUAL_PREFIX)
    text = text.replace(real.replace(":", "%3A"), _VIRTUAL_PREFIX)
    return text


# ──────────────────────────────────────────
# 补全排序
# ──────────────────────────────────────────
_DEMOTE_NAMES = frozenset({
    'annotations', 'Any', 'Callable', 'ClassVar', 'Dict', 'Final',
    'Generic', 'List', 'Literal', 'Optional', 'Protocol', 'Set',
    'Tuple', 'Type', 'TypeVar', 'Union', 'TYPE_CHECKING', 'TypedDict',
    'runtime_checkable', 'overload', 'cast', 'no_type_check',
})


def _reorder_completions(data: dict) -> None:
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
# Worker：一个 Pyright 进程 + 路由状态
# ──────────────────────────────────────────
class PyrightWorker:

    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.process: subprocess.Popen | None = None
        self.sessions: dict[str, WebSocket] = {}
        self.id_map: dict[int, tuple[str, int]] = {}
        self.global_id: int = worker_id * 1_000_000
        self.initialized: bool = False
        self.init_result: dict | None = None
        self.reader_task: asyncio.Task | None = None

    @property
    def load(self) -> int:
        return len(self.sessions)

    def start(self) -> None:
        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(
                [_LANGSERVER, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            self.initialized = False
            print(f"  Worker-{self.worker_id} Pyright 已启动")

    async def initialize(self) -> dict:
        if self.initialized:
            return self.init_result
        self.start()
        loop = asyncio.get_event_loop()

        init_msg = json.dumps({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {
                "processId": None,
                "capabilities": {
                    "textDocument": {
                        "completion": {"completionItem": {"snippetSupport": True}},
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "publishDiagnostics": {"relatedInformation": True},
                    },
                },
                "rootUri": _WORKSPACE_URI,
            },
        })
        _write_lsp_message(self.process.stdin, init_msg.encode())
        body = await loop.run_in_executor(None, _read_lsp_message, self.process.stdout)
        self.init_result = json.loads(body)

        notif = json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}})
        _write_lsp_message(self.process.stdin, notif.encode())
        self.initialized = True
        return self.init_result

    def ensure_reader(self) -> None:
        if self.reader_task is None or self.reader_task.done():
            self.reader_task = asyncio.create_task(self._reader_loop())

    async def _reader_loop(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            try:
                body = await loop.run_in_executor(
                    None, _read_lsp_message, self.process.stdout
                )
            except Exception:
                break
            if body is None:
                break
            try:
                data = json.loads(body)
            except Exception:
                continue

            # ① 服务端请求——回响应
            if "id" in data and "method" in data and data["id"] not in self.id_map:
                resp = {"jsonrpc": "2.0", "id": data["id"], "result": None}
                if data["method"] == "workspace/configuration":
                    n = len(data.get("params", {}).get("items", []))
                    resp["result"] = [{}] * max(n, 1)
                try:
                    _write_lsp_message(self.process.stdin, json.dumps(resp).encode())
                except (BrokenPipeError, OSError):
                    pass
                continue

            # ② 响应——按 ID 映射路由
            if "id" in data and data["id"] in self.id_map:
                session_id, original_id = self.id_map.pop(data["id"])
                data["id"] = original_id
                _reorder_completions(data)
                ws = self.sessions.get(session_id)
                if ws:
                    text = json.dumps(data, ensure_ascii=False)
                    text = _rewrite_to_virtual(text, session_id)
                    try:
                        await ws.send_text(text)
                    except Exception:
                        pass
                continue

            # ③ 通知——从 URI 提取 session 路由
            if "method" in data:
                params = data.get("params")
                if not isinstance(params, dict):
                    continue
                uri = params.get("uri", "")
                if not uri:
                    uri = params.get("textDocument", {}).get("uri", "")
                sid = _extract_session(uri)
                if sid and sid in self.sessions:
                    text = json.dumps(data, ensure_ascii=False)
                    text = _rewrite_to_virtual(text, sid)
                    try:
                        await self.sessions[sid].send_text(text)
                    except Exception:
                        pass

    def send_to_pyright(self, session_id: str, msg: dict) -> None:
        text = json.dumps(msg, ensure_ascii=False)
        text = _rewrite_to_real(text, session_id)
        msg = json.loads(text)

        if "id" in msg:
            self.global_id += 1
            self.id_map[self.global_id] = (session_id, msg["id"])
            msg["id"] = self.global_id

        _write_lsp_message(
            self.process.stdin,
            json.dumps(msg, ensure_ascii=False).encode(),
        )

    def close_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)


# ──────────────────────────────────────────
# 进程池
# ──────────────────────────────────────────
_workers: list[PyrightWorker] = []
_session_to_worker: dict[str, PyrightWorker] = {}


def _pick_worker() -> PyrightWorker:
    return min(_workers, key=lambda w: w.load)


@asynccontextmanager
async def lifespan(app):
    print(f"[阶段3] 启动 {POOL_SIZE} 个 Pyright Worker")
    for i in range(POOL_SIZE):
        worker = PyrightWorker(i)
        await worker.initialize()
        worker.ensure_reader()
        _workers.append(worker)
    print(f"[阶段3] 所有 Worker 就绪")
    yield


app = FastAPI(title="阶段3：Pyright 进程池", lifespan=lifespan)


@app.get("/status")
async def status():
    return {
        "pool_size": POOL_SIZE,
        "workers": [{"id": w.worker_id, "sessions": w.load} for w in _workers],
    }


# ──────────────────────────────────────────
# WebSocket 端点
# ──────────────────────────────────────────
@app.websocket("/lsp")
async def lsp_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = uuid.uuid4().hex[:8]

    worker = _pick_worker()
    worker.sessions[session_id] = ws
    _session_to_worker[session_id] = worker
    worker.ensure_reader()
    print(f"[阶段3] session={session_id} → Worker-{worker.worker_id}（负载 {worker.load}）")

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            method = msg.get("method", "")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": worker.init_result.get("result", {"capabilities": {}}),
                }
                await ws.send_text(json.dumps(resp, ensure_ascii=False))
                continue

            if method == "initialized":
                continue

            worker.send_to_pyright(session_id, msg)

    except WebSocketDisconnect:
        pass
    finally:
        worker.close_session(session_id)
        _session_to_worker.pop(session_id, None)
        print(f"[阶段3] session={session_id} 断开，Worker-{worker.worker_id} 剩余 {worker.load}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="阶段3：Pyright 进程池")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4003)
    parser.add_argument("--pool-size", type=int, default=3, help="Pyright Worker 数量")
    parser.add_argument("--workers", type=int, default=4, help="uvicorn worker 进程数（生产部署用）")
    args = parser.parse_args(["--serve"])

    POOL_SIZE = args.pool_size
    if args.serve:
        print(f"阶段3 桥接服务: ws://{args.host}:{args.port}/lsp")
        print(f"Pyright 进程池: {POOL_SIZE}，uvicorn workers: {args.workers}")
        if args.workers > 1:
            uvicorn.run("bridge:app", host=args.host, port=args.port, workers=args.workers)
        else:
            uvicorn.run(app, host=args.host, port=args.port)
