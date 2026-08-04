"""⑧ 串起来 —— 浏览器 ←WebSocket→ Python ←管道→ Pyright

运行（开两个终端）：
  终端1  python 08_01_bridge.py --serve
  终端2  python 08_02_bridge_client.py --client

把前面 7 步学到的全部拼在一起：
  ①③ subprocess.Popen 启动 Pyright
  ④⑤ 读写 LSP 消息、初始化
  ⑥ 请求补全、接收诊断
  ⑦ 用 WebSocket 接收前端请求
  ★ 注入自定义补全函数

前端连接: ws://127.0.0.1:3001
"""

import argparse
import json
import shutil
import subprocess
import threading
from websockets.sync.server import serve

_LANGSERVER = shutil.which("pyright-langserver")

# ──────────────────────────────────────────
# 自定义补全项
# ──────────────────────────────────────────
CUSTOM_COMPLETIONS = [
    {"label": "query_stock", "kind": 3, "detail": "(code: str) -> DataFrame",
     "sortText": "00.0000.query_stock"},
    {"label": "calc_ma",     "kind": 3, "detail": "(df: DataFrame, n: int) -> Series",
     "sortText": "00.0000.calc_ma"},
]

data = {
    'jsonrpc': '2.0',
    'id': 99,
    'result': {
        'items': [{'label': '__doc__', 'kind': 6, 'sortText': '13.9999.__doc__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__doc__'}},
                  {'label': '__module__', 'kind': 6,
                   'sortText': '13.9999.__module__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__module__'}},
                  {'label': '__qualname__', 'kind': 6,
                   'sortText': '13.9999.__qualname__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__qualname__'}},
                  {'label': '__new__', 'kind': 2, 'sortText': '13.9999.__new__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__new__'}},
                  {'label': 'as_integer_ratio', 'kind': 2,
                   'sortText': '09.9999.as_integer_ratio',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'as_integer_ratio'}},
                  {'label': 'real', 'kind': 10, 'sortText': '09.9999.real',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True, 'symbolLabel': 'real'}},
                  {'label': 'imag', 'kind': 10, 'sortText': '09.9999.imag',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True, 'symbolLabel': 'imag'}},
                  {'label': 'numerator', 'kind': 10,
                   'sortText': '09.9999.numerator',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'numerator'}},
                  {'label': 'denominator', 'kind': 10,
                   'sortText': '09.9999.denominator',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'denominator'}},
                  {'label': 'conjugate', 'kind': 2,
                   'sortText': '09.9999.conjugate',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'conjugate'}},
                  {'label': 'bit_length', 'kind': 2,
                   'sortText': '09.9999.bit_length',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'bit_length'}},
                  {'label': 'bit_count', 'kind': 2,
                   'sortText': '09.9999.bit_count',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'bit_count'}},
                  {'label': 'to_bytes', 'kind': 2,
                   'sortText': '09.9999.to_bytes',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'to_bytes'}},
                  {'label': 'from_bytes', 'kind': 2,
                   'sortText': '09.9999.from_bytes',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'from_bytes'}},
                  {'label': 'is_integer', 'kind': 2,
                   'sortText': '09.9999.is_integer',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': 'is_integer'}},
                  {'label': '__add__', 'kind': 2, 'sortText': '13.9999.__add__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__add__'}},
                  {'label': '__sub__', 'kind': 2, 'sortText': '13.9999.__sub__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__sub__'}},
                  {'label': '__mul__', 'kind': 2, 'sortText': '13.9999.__mul__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__mul__'}},
                  {'label': '__floordiv__', 'kind': 2,
                   'sortText': '13.9999.__floordiv__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__floordiv__'}},
                  {'label': '__truediv__', 'kind': 2,
                   'sortText': '13.9999.__truediv__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__truediv__'}},
                  {'label': '__mod__', 'kind': 2, 'sortText': '13.9999.__mod__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__mod__'}},
                  {'label': '__divmod__', 'kind': 2,
                   'sortText': '13.9999.__divmod__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__divmod__'}},
                  {'label': '__radd__', 'kind': 2,
                   'sortText': '13.9999.__radd__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__radd__'}},
                  {'label': '__rsub__', 'kind': 2,
                   'sortText': '13.9999.__rsub__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rsub__'}},
                  {'label': '__rmul__', 'kind': 2,
                   'sortText': '13.9999.__rmul__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rmul__'}},
                  {'label': '__rfloordiv__', 'kind': 2,
                   'sortText': '13.9999.__rfloordiv__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rfloordiv__'}},
                  {'label': '__rtruediv__', 'kind': 2,
                   'sortText': '13.9999.__rtruediv__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rtruediv__'}},
                  {'label': '__rmod__', 'kind': 2,
                   'sortText': '13.9999.__rmod__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rmod__'}},
                  {'label': '__rdivmod__', 'kind': 2,
                   'sortText': '13.9999.__rdivmod__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rdivmod__'}},
                  {'label': '__pow__', 'kind': 2, 'sortText': '13.9999.__pow__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__pow__'}},
                  {'label': '__rpow__', 'kind': 2,
                   'sortText': '13.9999.__rpow__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rpow__'}},
                  {'label': '__and__', 'kind': 2, 'sortText': '13.9999.__and__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__and__'}},
                  {'label': '__or__', 'kind': 2, 'sortText': '13.9999.__or__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__or__'}},
                  {'label': '__xor__', 'kind': 2, 'sortText': '13.9999.__xor__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__xor__'}},
                  {'label': '__lshift__', 'kind': 2,
                   'sortText': '13.9999.__lshift__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__lshift__'}},
                  {'label': '__rshift__', 'kind': 2,
                   'sortText': '13.9999.__rshift__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rshift__'}},
                  {'label': '__rand__', 'kind': 2,
                   'sortText': '13.9999.__rand__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rand__'}},
                  {'label': '__ror__', 'kind': 2, 'sortText': '13.9999.__ror__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__ror__'}},
                  {'label': '__rxor__', 'kind': 2,
                   'sortText': '13.9999.__rxor__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rxor__'}},
                  {'label': '__rlshift__', 'kind': 2,
                   'sortText': '13.9999.__rlshift__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rlshift__'}},
                  {'label': '__rrshift__', 'kind': 2,
                   'sortText': '13.9999.__rrshift__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__rrshift__'}},
                  {'label': '__neg__', 'kind': 2, 'sortText': '13.9999.__neg__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__neg__'}},
                  {'label': '__pos__', 'kind': 2, 'sortText': '13.9999.__pos__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__pos__'}},
                  {'label': '__invert__', 'kind': 2,
                   'sortText': '13.9999.__invert__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__invert__'}},
                  {'label': '__trunc__', 'kind': 2,
                   'sortText': '13.9999.__trunc__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__trunc__'}},
                  {'label': '__ceil__', 'kind': 2,
                   'sortText': '13.9999.__ceil__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__ceil__'}},
                  {'label': '__floor__', 'kind': 2,
                   'sortText': '13.9999.__floor__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__floor__'}},
                  {'label': '__round__', 'kind': 2,
                   'sortText': '13.9999.__round__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__round__'}},
                  {'label': '__getnewargs__', 'kind': 2,
                   'sortText': '13.9999.__getnewargs__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__getnewargs__'}},
                  {'label': '__eq__', 'kind': 2, 'sortText': '13.9999.__eq__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__eq__'}},
                  {'label': '__ne__', 'kind': 2, 'sortText': '13.9999.__ne__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__ne__'}},
                  {'label': '__lt__', 'kind': 2, 'sortText': '13.9999.__lt__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__lt__'}},
                  {'label': '__le__', 'kind': 2, 'sortText': '13.9999.__le__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__le__'}},
                  {'label': '__gt__', 'kind': 2, 'sortText': '13.9999.__gt__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__gt__'}},
                  {'label': '__ge__', 'kind': 2, 'sortText': '13.9999.__ge__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__ge__'}},
                  {'label': '__float__', 'kind': 2,
                   'sortText': '13.9999.__float__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__float__'}},
                  {'label': '__int__', 'kind': 2, 'sortText': '13.9999.__int__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__int__'}},
                  {'label': '__abs__', 'kind': 2, 'sortText': '13.9999.__abs__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__abs__'}},
                  {'label': '__hash__', 'kind': 2,
                   'sortText': '13.9999.__hash__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__hash__'}},
                  {'label': '__bool__', 'kind': 2,
                   'sortText': '13.9999.__bool__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__bool__'}},
                  {'label': '__index__', 'kind': 2,
                   'sortText': '13.9999.__index__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__index__'}},
                  {'label': '__format__', 'kind': 2,
                   'sortText': '13.9999.__format__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__format__'}},
                  {'label': '__dict__', 'kind': 6,
                   'sortText': '13.9999.__dict__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__dict__'}},
                  {'label': '__annotations__', 'kind': 6,
                   'sortText': '13.9999.__annotations__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__annotations__'}},
                  {'label': '__class__', 'kind': 10,
                   'sortText': '13.9999.__class__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__class__'}},
                  {'label': '__init__', 'kind': 2,
                   'sortText': '13.9999.__init__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__init__'}},
                  {'label': '__setattr__', 'kind': 2,
                   'sortText': '13.9999.__setattr__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__setattr__'}},
                  {'label': '__delattr__', 'kind': 2,
                   'sortText': '13.9999.__delattr__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__delattr__'}},
                  {'label': '__str__', 'kind': 2, 'sortText': '13.9999.__str__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__str__'}},
                  {'label': '__repr__', 'kind': 2,
                   'sortText': '13.9999.__repr__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__repr__'}},
                  {'label': '__getattribute__', 'kind': 2,
                   'sortText': '13.9999.__getattribute__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__getattribute__'}},
                  {'label': '__sizeof__', 'kind': 2,
                   'sortText': '13.9999.__sizeof__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__sizeof__'}},
                  {'label': '__reduce__', 'kind': 2,
                   'sortText': '13.9999.__reduce__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__reduce__'}},
                  {'label': '__reduce_ex__', 'kind': 2,
                   'sortText': '13.9999.__reduce_ex__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__reduce_ex__'}},
                  {'label': '__getstate__', 'kind': 2,
                   'sortText': '13.9999.__getstate__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__getstate__'}},
                  {'label': '__dir__', 'kind': 2, 'sortText': '13.9999.__dir__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__dir__'}},
                  {'label': '__init_subclass__', 'kind': 2,
                   'sortText': '13.9999.__init_subclass__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__init_subclass__'}},
                  {'label': '__subclasshook__', 'kind': 2,
                   'sortText': '13.9999.__subclasshook__',
                   'data': {'uri': 'file:///demo.py',
                            'position': {'line': 2, 'character': 2},
                            'funcParensDisabled': True,
                            'symbolLabel': '__subclasshook__'}}],
        'isIncomplete': True}}


# ──────────────────────────────────────────
# LSP 消息工具
# ──────────────────────────────────────────
def _read_lsp_message(stdout) -> bytes | None:
    content_length = 0
    while True:
        line = stdout.readline()
        if not line:
            return None
        if line.startswith(b"Content-Length:"):
            content_length = int(line.split(b":")[1])
        if not line.strip():
            break
    return stdout.read(content_length) if content_length > 0 else None


def _write_lsp_message(stdin, raw: bytes) -> None:
    stdin.write(f"Content-Length: {len(raw)}\r\n\r\n".encode() + raw)
    stdin.flush()


# ──────────────────────────────────────────
# 每个 WebSocket 连接的处理
# ──────────────────────────────────────────
def handle(ws):
    """启动 Pyright，双向转发 WebSocket ↔ Pyright"""
    addr = ws.request.headers.get("Host", "?")
    print(f"[连接] 客户端接入: {addr}")

    pyright = subprocess.Popen(
        [_LANGSERVER, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    print(f"[Pyright] 进程已启动, pid={pyright.pid}")

    def ws_to_pyright():
        try:
            for message in ws:
                print('message', message)
                data = json.loads(message.split("\r\n\r\n", 1)[-1])
                method = data.get("method", "")
                msg_id = data.get("id", "-")
                print(f"  [客户端→Pyright] id={msg_id}  {method}")
                pyright.stdin.write(message.encode())
                pyright.stdin.flush()
        except Exception:
            pass
        print("[连接] 客户端断开")

    def pyright_to_ws():
        while True:
            body = _read_lsp_message(pyright.stdout)
            if body is None:
                break
            data = json.loads(body)
            print('data', data)

            method = data.get("method", "")
            msg_id = data.get("id", "-")

            injected = False
            if "result" in data and isinstance(data.get("result"), dict):
                items = data["result"].get("items")
                if items is not None:
                    items.extend(CUSTOM_COMPLETIONS)
                    injected = True

            if injected:
                print(f"  [Pyright→客户端] id={msg_id}  补全响应（已注入 {len(CUSTOM_COMPLETIONS)} 项自定义补全）")
            elif method:
                print(f"  [Pyright→客户端] {method}")
            else:
                print(f"  [Pyright→客户端] id={msg_id}  响应")

            ws.send(json.dumps(data, ensure_ascii=False))

    t1 = threading.Thread(target=ws_to_pyright, daemon=True)
    t2 = threading.Thread(target=pyright_to_ws, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    pyright.kill()
    pyright.wait()
    print(f"[Pyright] 进程已退出, pid={pyright.pid}")


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    # args = parser.parse_args()
    args = parser.parse_args([
        '--serve',
    ])

    if args.serve:
        print(f"LSP 桥接:  ws://{args.host}:{args.port}")
        with serve(handle, args.host, args.port) as server:
            server.serve_forever()
    else:
        print("LSP 桥接服务")
        print()
        print("启动: python 08_01_bridge.py --serve")
        print("客户端: python 08_02_bridge_client.py --client")
