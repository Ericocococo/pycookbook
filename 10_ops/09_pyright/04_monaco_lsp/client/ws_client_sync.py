"""
WebSocket 客户端（同步版）—— 用 websocket-client 连 LSP 桥接服务

对比异步版 (ws_client.py):
  - 不需要 asyncio / async / await
  - 顺序发送 → 等待回包 → 继续，逻辑直白
  - 缺点：一个连接阻塞时其他操作全卡住

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/client/ws_client_sync.py

依赖：
  pip install websocket-client
"""

import json
import time
import websocket


# ──────────────────────────────────────────
# 示例代码
# ──────────────────────────────────────────
SAMPLE_CODE = '''
def add(a: int, b: int) -> int:
    return a + b

x = add(3, 4)
print(x.)

y: str = 42
'''


class LSPClientSync:
    """同步 LSP 客户端"""

    def __init__(self, ws: websocket.WebSocket):
        self.ws = ws
        self._id = 0

    def request(self, method: str, params: dict) -> dict | None:
        """发送请求，阻塞等待响应"""
        self._id += 1
        msg = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        self.ws.send(msg)

        while True:
            raw = self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == self._id:
                return data.get("result")
            # 诊断推送不是请求响应，打印出来
            if data.get("method") == "textDocument/publishDiagnostics":
                for d in data["params"]["diagnostics"]:
                    line = d["range"]["start"]["line"] + 1
                    col = d["range"]["start"]["character"] + 1
                    level = {1: "ERROR", 2: "WARNING", 3: "INFO"}.get(d["severity"], "?")
                    print(f"  [{level}] 第 {line} 行 {col} 列: {d['message']}")

    def notify(self, method: str, params: dict) -> None:
        """发送通知，不等待响应"""
        msg = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
        self.ws.send(msg)

    def initialize(self) -> None:
        """初始化"""
        result = self.request("initialize", {
            "processId": None,
            "capabilities": {
                "textDocument": {"completion": {}, "hover": {}},
            },
            "rootUri": None,
        })
        print(f"初始化完成")
        self.notify("initialized", {})

    def open_document(self, uri: str, text: str) -> None:
        """打开文档"""
        self.notify("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": "python", "version": 1, "text": text},
        })

    def completion(self, uri: str, line: int, char: int) -> list[dict]:
        """请求补全（阻塞）"""
        result = self.request("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": char},
        })
        return result.get("items", []) if result else []

    def hover(self, uri: str, line: int, char: int) -> dict | None:
        """请求悬浮文档（阻塞）"""
        return self.request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": char},
        })


def main():
    # 连接 WebSocket
    ws = websocket.create_connection("ws://127.0.0.1:3001", timeout=10)
    client = LSPClientSync(ws)

    client.initialize()

    uri = "file:///demo.py"
    client.open_document(uri, SAMPLE_CODE)
    print("\n等待诊断...")
    time.sleep(1)

    print("\n请求补全...")
    items = client.completion(uri, line=5, char=8)
    for item in items[:5]:
        print(f"  · {item['label']} {item.get('detail', '')}")

    print("\n请求悬浮文档...")
    hover = client.hover(uri, line=1, char=4)
    if hover:
        contents = hover.get("contents", {})
        text = contents.get("value", str(contents)) if isinstance(contents, dict) else str(contents)
        print(f"  {text}")

    ws.close()


if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print("连接被拒绝，请先启动 LSP 桥接服务")
