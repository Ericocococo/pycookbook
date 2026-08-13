"""
WebSocket 客户端 —— 连接 LSP 桥接服务，发 LSP 请求收响应

掌握：
  - 用 websockets 库连接 LSP 桥接服务
  - 发送 LSP initialize / completion / hover 请求
  - 接收 Pyright 的诊断推送和补全结果

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/client/ws_client.py

依赖：
  pip install websockets
"""

import asyncio
import json

import websockets


# ──────────────────────────────────────────
# 示例代码内容
# ──────────────────────────────────────────
SAMPLE_CODE = '''
from interface import ntdata, nttrader, nttype, ntconstant

account = nttype.StockAccount("backtest")

ntdata.
ntconstant.
account.
ntdata.get_market_data_ex

bad: int = "hello"
'''


class LSPClient:
    """LSP 客户端，封装 LSP 协议消息"""

    def __init__(self, ws):
        self.ws = ws
        self._id = 0

    async def request(self, method: str, params: dict) -> dict | None:
        """发送 LSP 请求并等待响应"""
        self._id += 1
        msg = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        await self.ws.send(msg)

        # 等待带相同 id 的响应
        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == self._id:
                return data.get("result")
            # 诊断推送没有 id，打印出来
            if "method" in data and data["method"] == "textDocument/publishDiagnostics":
                diags = data["params"]["diagnostics"]
                for d in diags:
                    line = d["range"]["start"]["line"] + 1
                    col = d["range"]["start"]["character"] + 1
                    level = {1: "ERROR", 2: "WARNING", 3: "INFO"}.get(d["severity"], "?")
                    print(f"  [{level}] 第 {line} 行 {col} 列: {d['message']}")

    async def notify(self, method: str, params: dict) -> None:
        """发送 LSP 通知（无返回值）"""
        msg = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
        await self.ws.send(msg)

    async def initialize(self) -> None:
        """初始化 LSP 连接"""
        result = await self.request("initialize", {
            "processId": None,
            "capabilities": {
                "textDocument": {
                    "completion": {"completionItem": {"snippetSupport": True}},
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                },
            },
            "rootUri": None,
        })
        print(f"初始化完成，服务器能力: {json.dumps(result.get('capabilities', {}), ensure_ascii=False)[:200]}...")

        await self.notify("initialized", {})

    async def open_document(self, uri: str, text: str, language: str = "python") -> None:
        """打开文档（触发 Pyright 分析）"""
        await self.notify("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language,
                "version": 1,
                "text": text,
            },
        })

    async def completion(self, uri: str, line: int, char: int) -> list[dict]:
        """请求代码补全"""
        result = await self.request("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": char},
        })
        return result.get("items", []) if result else []

    async def hover(self, uri: str, line: int, char: int) -> dict | None:
        """请求悬浮文档"""
        return await self.request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": char},
        })


async def main():
    # 连接 WebSocket（两个方案二选一）
    # ws_url = "ws://127.0.0.1:3001"        # 方案一：websockets
    ws_url = "ws://127.0.0.1:3002/lsp"  # 方案二：FastAPI

    async with websockets.connect(ws_url) as ws:
        client = LSPClient(ws)

        # ① 初始化
        await client.initialize()

        # ② 打开文档（使用虚拟路径，桥接层会重写为真实路径）
        uri = "file:///workspace/main.py"
        await client.open_document(uri, SAMPLE_CODE)
        print("\n等待诊断结果...")
        await asyncio.sleep(1)

        # ③ 请求补全（光标在 "ntdata." 的点后面，第 5 行）
        print("\n请求补全（ntdata. 的位置）...")
        items = await client.completion(uri, line=5, char=7)
        for item in items[:5]:
            label = item["label"]
            detail = item.get("detail", "")
            print(f"  · {label}{detail}")
        if items:
            print(f"  ... 共 {len(items)} 项")

        # ④ 请求悬浮文档（光标在 "ntdata.get_market_data_ex" 上，第 8 行）
        print("\n请求悬浮文档（get_market_data_ex）...")
        hover = await client.hover(uri, line=8, char=12)
        if hover and "contents" in hover:
            value = hover["contents"]
            if isinstance(value, dict):
                value = value.get("value", str(value))
            print(f"  {value}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConnectionRefusedError:
        print("连接被拒绝，请先启动 LSP 桥接服务：")
        print("  方案一：python 02_lsp_bridge_ws.py --serve")
        print("  方案二：python 03_lsp_bridge_fastapi.py --serve")
