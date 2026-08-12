"""⑧ 桥接客户端 —— 通过 WebSocket 连 bridge，测试完整链路

运行（先起 bridge，再跑本文件）：
  终端1  python 08_01_bridge.py --serve
  终端2  python 08_02_bridge_client.py --client

验证完整链路：客户端 ←WebSocket→ bridge ←管道→ Pyright
  ① initialize + initialized   握手
  ② didOpen                    打开文件，触发 Pyright 分析
  ③ 等 publishDiagnostics      接收诊断推送
  ④ textDocument/completion    请求补全，验证 bridge 注入的自定义项

为什么 recv 要在独立线程：
  Pyright 会主动推消息（诊断、日志），不跟你的请求一一对应。
  如果在主线程同步 recv，发完 didOpen 后你不知道下一条是日志还是诊断，
  只能一直阻塞等。recv 线程把所有消息扔进 queue，主线程按条件取。

数据流（注意两端格式不同）：
  发送：客户端 → WebSocket → bridge → Pyright stdin
        必须带 Content-Length 头（bridge 原样转发 bytes 给管道）
  接收：Pyright stdout → bridge → WebSocket → 客户端
        纯 JSON 字符串（bridge 已剥离 Content-Length 头）
"""

import argparse
import json
import queue
import threading

from websockets.sync.client import connect


# ──────────────────────────────────────────
# LSP 消息工具
# ──────────────────────────────────────────
def _make_lsp(data: dict) -> str:
    """把 dict 打包成 LSP 线格式字符串（Content-Length 头 + JSON 体）。
    bridge 的 ws_to_pyright 会 message.encode() 后写入管道，
    所以这里返回的 str encode 后必须是合法的 LSP 二进制帧。
    """
    body = json.dumps(data)
    return f"Content-Length: {len(body.encode())}\r\n\r\n{body}"


def _wait_for(q: queue.Queue, predicate, timeout: float = 10.0) -> dict | None:
    """从 queue 里取消息，直到 predicate(msg) 为真，返回该消息。
    不匹配的消息打印后丢弃（日志类），超时返回 None。
    """
    while True:
        try:
            msg = q.get(timeout=timeout)
        except queue.Empty:
            print("  超时，未收到期望的响应")
            return None
        if predicate(msg):
            return msg
        # 不匹配的消息打印出来
        method = msg.get("method", "")
        msg_id = msg.get("id", "-")
        if method:
            print(f"  [跳过] {method}  {msg.get('params', '')}")
        else:
            print(f"  [跳过] id={msg_id}  {msg}")


# ──────────────────────────────────────────
# 客户端主流程
# ──────────────────────────────────────────
def run_client(host: str, port: int):
    url = f"ws://{host}:{port}"
    print(f"连接 bridge:  {url}\n")

    with connect(url) as ws:
        # ── recv 线程：一直收，全部扔进 queue ──
        q: queue.Queue[dict] = queue.Queue()

        def recv_loop():
            try:
                for raw in ws:
                    data = json.loads(raw)
                    print('----', data)
                    q.put(data)
            except Exception:
                pass  # 连接关闭时退出

        t = threading.Thread(target=recv_loop, daemon=True)
        t.start()

        # ── ① initialize ──
        print("① initialize")
        ws.send(_make_lsp({
            "jsonrpc": "2.0", "id": 1,
            "method": "initialize",
            "params": {"processId": None, "capabilities": {}, "rootUri": None},
        }))
        resp = _wait_for(q, lambda m: m.get("id") == 1)
        if resp:
            print(f"  握手成功\n")

        # ── ② initialized ──
        print("② initialized（通知）")
        ws.send(_make_lsp({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {},
        }))
        print("  已发送\n")

        # ── ③ didOpen —— 故意给错误代码，触发诊断 ──
        code = "import os\nx: int = 'hello'\nx."
        print(f"③ didOpen（代码: {code!r}）")
        ws.send(_make_lsp({
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": "file:///demo.py",
                    "languageId": "python",
                    "version": 1,
                    "text": code,
                },
            },
        }))

        # 等诊断推送
        diag_msg = _wait_for(
            q, lambda m: m.get("method") == "textDocument/publishDiagnostics")

        # ── Pyright 推送的诊断结果示例（实际运行时收到的 diag_msg 就长这样）──
        aa = {
            'jsonrpc': '2.0',                                    # JSON-RPC 协议版本，固定 2.0
            'method': 'textDocument/publishDiagnostics',         # 方法名：诊断推送（服务端主动发，无 id）
            'params': {
                'uri': 'file:///demo.py',                        # 哪个文件的诊断（和 didOpen 的 uri 对应）
                'version': 1,                                    # 文档版本号（和 didOpen 的 version 对应）
                'diagnostics': [                                 # 诊断列表，一个错误一项
                    {
                        'range': {                               # 波浪线画在哪
                            'start': {'line': 2, 'character': 1},  # 第3行第2列（x. 的 . 处）
                            'end': {'line': 2, 'character': 2},    # 到第3行第3列
                        },
                        'message': 'Expected attribute name after "."',  # 错误描述：点号后面缺属性名
                        'severity': 1,                           # 1=Error红 2=Warning黄 3=Info蓝 4=Hint灰
                        'source': 'Pyright',                     # 谁报的错
                    },
                    {
                        'range': {                               # 第二个错误的位置
                            'start': {'line': 1, 'character': 9},   # 第2行第10列（"hello" 的 " 处）
                            'end': {'line': 1, 'character': 16},    # 到第2行第17列（框住 "hello"）
                        },
                        'message': 'Type "Literal[\'hello\']" is not assignable to declared type "int"'  # 类型不匹配
                                   '\n\xa0\xa0"Literal[\'hello\']" is not assignable to "int"',          # 详细说明（\xa0 是不换行空格，缩进用）
                        'severity': 1,                           # Error
                        'code': 'reportAssignmentType',          # 规则名，可在配置里开关
                        'source': 'Pyright',
                        'codeDescription': {                     # 规则文档链接，编辑器里可点击跳转
                            'href': 'https://github.com/microsoft/pyright/blob/main/docs/configuration.md#reportAssignmentType',
                        },
                    },
                ],
            },
        }
        if diag_msg:
            diags = diag_msg["params"]["diagnostics"]
            print(f"  收到 {len(diags)} 条诊断:")
            for d in diags:
                line = d["range"]["start"]["line"] + 1
                col = d["range"]["start"]["character"] + 1
                print(f"    第{line}行{col}列 — {d['message']}")
        print()

        # ── ④ 请求补全（光标在 x. 后面） ──
        print("④ textDocument/completion（光标在 x. 后）")
        ws.send(_make_lsp({
            "jsonrpc": "2.0", "id": 99,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {"uri": "file:///demo.py"},
                "position": {"line": 2, "character": 2},
            },
        }))

        comp_msg = _wait_for(q, lambda m: m.get("id") == 99)
        if comp_msg:
            items = comp_msg["result"]["items"]
            print(f"  收到 {len(items)} 个补全项")

            # 按 sortText 前缀分：00 = 自定义注入，09/11/13 = Pyright 原生
            custom = [i for i in items if i.get("sortText", "").startswith("00.")]
            native = [i for i in items if not i.get("sortText", "").startswith("00.")]

            # Pyright 原生补全（按 sortText 排序，取前 5 个公开成员）
            native.sort(key=lambda i: i.get("sortText", ""))
            print("\n  Pyright 原生（前 5 项）:")
            for item in native[:5]:
                print(f"    · {item['label']:<20} kind={item.get('kind', '?')}  sortText={item.get('sortText', '')}")

            # bridge 注入的自定义补全
            if custom:
                print(f"\n  bridge 注入的自定义补全（{len(custom)} 项）:")
                for item in custom:
                    print(f"    ★ {item['label']:<20} {item.get('detail', '')}")
            else:
                print("\n  ⚠ 未找到自定义补全项，bridge 注入可能失败")

    print("\n客户端结束")


# ──────────────────────────────────────────
# 启动
# ──────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", action="store_true", help="起客户端")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3001)
    args = parser.parse_args(['--client'])

    if args.client:
        try:
            run_client(args.host, args.port)
        except ConnectionRefusedError:
            print("连接被拒绝，请先启动 bridge: python 08_01_bridge.py --serve")
    else:
        print("bridge 客户端")
        print()
        print("先起 bridge: python 08_01_bridge.py --serve")
        print("再跑客户端: python 08_02_bridge_client.py --client")
