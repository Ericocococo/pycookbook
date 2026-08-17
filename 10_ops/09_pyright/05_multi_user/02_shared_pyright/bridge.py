"""
阶段2：共享一个 Pyright

所有用户共享一个 Pyright 进程，通过 session ID 区分用户。
桥接层负责三件事：URI 命名空间隔离、请求 ID 去重、出站路由。

用户隔离方式：用文件名区分，不建子目录
  用户A → file:///真实路径/_s_a1b2c3d4.py
  用户B → file:///真实路径/_s_c5d6e7f8.py

优点：内存高效（只需 ~150MB，不随用户数增长）
缺点：Pyright stdin/stdout 串行，用户多了会排队

运行方式（在项目根目录）：
  python 10_ops/09_pyright/05_multi_user/02_shared_pyright/bridge.py --serve

端口：ws://127.0.0.1:4002/lsp

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
from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

_DIR = Path(__file__).resolve().parent
_dir_posix = _DIR.as_posix()
if len(_dir_posix) >= 2 and _dir_posix[1] == ':':
    # Windows: 盘符统一小写，与 Pyright 输出一致（D:/ → d:/）
    _dir_posix = _dir_posix[0].lower() + _dir_posix[1:]
    _WORKSPACE_URI = f"file:///{_dir_posix}"
else:
    # Linux/macOS: 路径已是 /home/... 格式
    _WORKSPACE_URI = f"file://{_dir_posix}"

# 前端统一用这个虚拟 URI，bridge 替换为每个 session 的真实 URI
_VIRTUAL_PREFIX = "file:///workspace/"

app = FastAPI(title="阶段2：共享一个 Pyright")


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
# URI 映射——前缀替换，前端传什么文件名都行
# ──────────────────────────────────────────
# 前端: file:///workspace/xxx.py → 后端: file:///真实路径/_s_{session}/xxx.py
# 磁盘上不建任何文件或目录，Pyright 在内存中分析

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
# 全局状态
# ──────────────────────────────────────────
_pyright: subprocess.Popen | None = None
_sessions: dict[str, WebSocket] = {}       # session_id → ws 连接
_id_map: dict[int, tuple[str, int]] = {}   # 全局id → (session_id, 原始id)
_global_id: int = 0
_initialized: bool = False
_init_result: dict | None = None
_reader_task: asyncio.Task | None = None
_init_lock = asyncio.Lock()


# ──────────────────────────────────────────
# Pyright 生命周期
# ──────────────────────────────────────────
def _ensure_pyright() -> None:
    """确保 Pyright 进程已启动。进程崩溃时重置初始化状态。"""
    global _pyright, _initialized
    if _pyright is None or _pyright.poll() is not None:
        _pyright = subprocess.Popen(
            [_LANGSERVER, "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        _initialized = False
        print("[阶段2] Pyright 进程已启动")


async def _initialize_pyright() -> dict:
    """发送 LSP initialize（只做一次），用 Lock 防并发竞态。"""
    global _initialized, _init_result

    async with _init_lock:
        if _initialized:
            return _init_result

        _ensure_pyright()
        loop = asyncio.get_event_loop()

        init_msg = json.dumps({
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
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
        _write_lsp_message(_pyright.stdin, init_msg.encode())

        body = await loop.run_in_executor(None, _read_lsp_message, _pyright.stdout)
        _init_result = json.loads(body)

        notif = json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}})
        _write_lsp_message(_pyright.stdin, notif.encode())

        _initialized = True
        print("[阶段2] Pyright 初始化完成")
        return _init_result


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
# 后台 reader——从 Pyright stdout 路由到正确的用户
# ──────────────────────────────────────────
async def _pyright_reader() -> None:
    loop = asyncio.get_event_loop()

    while True:
        try:
            body = await loop.run_in_executor(None, _read_lsp_message, _pyright.stdout)
        except Exception as e:
            print(f"  [reader] 读取异常: {e}")
            break
        if body is None:
            print("  [reader] Pyright stdout 关闭")
            break
        try:
            data = json.loads(body)
        except Exception as e:
            print(f"  [reader] JSON 解析失败: {e}")
            continue

        # ① Pyright 服务端请求（有 id + method，不在映射表）——必须回响应
        if "id" in data and "method" in data and data["id"] not in _id_map:
            resp = {"jsonrpc": "2.0", "id": data["id"], "result": None}
            if data["method"] == "workspace/configuration":
                n = len(data.get("params", {}).get("items", []))
                resp["result"] = [{}] * max(n, 1)
            print(f"  [reader] → 回复服务端请求: {data['method']}")
            try:
                _write_lsp_message(_pyright.stdin, json.dumps(resp).encode())
            except (BrokenPipeError, OSError):
                pass
            continue

        # ② 响应消息（有 id）——按 ID 映射表路由
        if "id" in data and data["id"] in _id_map:
            session_id, original_id = _id_map.pop(data["id"])
            data["id"] = original_id
            _reorder_completions(data)
            ws = _sessions.get(session_id)
            if ws:
                text = json.dumps(data, ensure_ascii=False)
                text = _rewrite_to_virtual(text, session_id)
                try:
                    await ws.send_text(text)
                except Exception:
                    pass
            continue

        # ③ 通知消息——从 URI 提取 session_id 路由
        if "method" in data:
            params = data.get("params")
            if not isinstance(params, dict):
                continue
            uri = params.get("uri", "")
            if not uri:
                uri = params.get("textDocument", {}).get("uri", "")
            sid = _extract_session(uri)
            if sid and sid in _sessions:
                text = json.dumps(data, ensure_ascii=False)
                text = _rewrite_to_virtual(text, sid)
                try:
                    await _sessions[sid].send_text(text)
                except Exception:
                    pass


# ──────────────────────────────────────────
# WebSocket 端点
# ──────────────────────────────────────────
@app.websocket("/lsp")
async def lsp_endpoint(ws: WebSocket):
    global _global_id, _reader_task

    await ws.accept()
    session_id = uuid.uuid4().hex[:8]
    _sessions[session_id] = ws
    print(f"[阶段2] 新连接 session={session_id}，当前 {len(_sessions)} 个用户")

    init_result = await _initialize_pyright()

    if _reader_task is None or _reader_task.done():
        _reader_task = asyncio.create_task(_pyright_reader())

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            method = msg.get("method", "")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": init_result.get("result", {"capabilities": {}}),
                }
                await ws.send_text(json.dumps(resp, ensure_ascii=False))
                continue

            if method == "initialized":
                continue

            # URI 重写：虚拟前缀 → 真实前缀
            text = json.dumps(msg, ensure_ascii=False)
            text = _rewrite_to_real(text, session_id)
            msg = json.loads(text)

            # 请求 ID 重写
            if "id" in msg:
                _global_id += 1
                _id_map[_global_id] = (session_id, msg["id"])
                msg["id"] = _global_id

            _write_lsp_message(
                _pyright.stdin,
                json.dumps(msg, ensure_ascii=False).encode(),
            )

    except WebSocketDisconnect:
        pass
    finally:
        _sessions.pop(session_id, None)
        print(f"[阶段2] session={session_id} 断开，剩余 {len(_sessions)} 个用户")


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="阶段2：共享一个 Pyright")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4002)
    parser.add_argument("--workers", type=int, default=1, help="uvicorn worker 进程数（生产部署用）")
    args = parser.parse_args(["--serve"])

    if args.serve:
        print(f"阶段2 桥接服务: ws://{args.host}:{args.port}/lsp")
        print(f"所有连接共享一个 Pyright 进程（uvicorn workers={args.workers}）")
        if args.workers > 1:
            uvicorn.run("bridge:app", host=args.host, port=args.port, workers=args.workers)
        else:
            uvicorn.run(app, host=args.host, port=args.port)
