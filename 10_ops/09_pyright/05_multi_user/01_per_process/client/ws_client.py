"""
多用户测试客户端——模拟 N 个用户同时连接，验证三个阶段的隔离性

运行方式（在项目根目录）：
  python 10_ops/09_pyright/05_multi_user/client/ws_client.py

默认连接阶段1（端口4001），可通过 --port 切换：
  python ... --port 4001   → 阶段1
  python ... --port 4002   → 阶段2
  python ... --port 4003   → 阶段3

依赖：
  pip install websockets
"""

import argparse
import asyncio
import json

import websockets


# 每个用户写不同的代码，验证诊断/补全互不干扰
USER_CODES = [
    # 用户0：正确代码，无诊断
    'from interface import ntdata\nx: int = 42\n',
    # 用户1：类型错误，应有 1 条诊断
    'from interface import ntdata\nbad: int = "hello"\n',
    # 用户2：两个类型错误，应有 2 条诊断
    'from interface import ntdata\na: int = "x"\nb: str = 123\n',
]


async def simulate_user(user_id: int, port: int) -> None:
    """模拟一个用户：连接 → 初始化 → 打开文档 → 等诊断 → 请求补全"""
    ws_url = f"ws://127.0.0.1:{port}/lsp"
    code = USER_CODES[user_id % len(USER_CODES)]

    async with websockets.connect(ws_url) as ws:
        req_id = 0

        async def request(method: str, params: dict) -> dict | None:
            nonlocal req_id
            req_id += 1
            msg = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
            await ws.send(msg)
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                if data.get("id") == req_id:
                    return data.get("result")
                # 打印收到的诊断
                if data.get("method") == "textDocument/publishDiagnostics":
                    diags = data["params"]["diagnostics"]
                    for d in diags:
                        line = d["range"]["start"]["line"] + 1
                        print(f"  [用户{user_id}] 诊断: 第{line}行 {d['message']}")

        async def notify(method: str, params: dict) -> None:
            msg = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
            await ws.send(msg)

        # ① 初始化
        await request("initialize", {
            "processId": None,
            "capabilities": {"textDocument": {"completion": {"completionItem": {"snippetSupport": True}}}},
            "rootUri": None,
        })
        await notify("initialized", {})

        # ② 打开文档
        uri = "file:///workspace/main.py"
        await notify("textDocument/didOpen", {
            "textDocument": {"uri": uri, "languageId": "python", "version": 1, "text": code},
        })
        print(f"[用户{user_id}] 已打开文档，代码: {repr(code[:30])}...")

        # ③ 等待诊断推送
        await asyncio.sleep(2)

        # ④ 请求补全
        # 在第一行 "from interface import ntdata" 后面加一行 "ntdata." 测试补全
        # 先更新文档
        new_code = code + "ntdata.\n"
        await notify("textDocument/didChange", {
            "textDocument": {"uri": uri, "version": 2},
            "contentChanges": [{"text": new_code}],
        })
        await asyncio.sleep(0.5)

        # 补全位置：最后一行 "ntdata." 的点后面
        lines = new_code.strip().split("\n")
        line_idx = len(lines) - 1
        result = await request("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": line_idx, "character": 7},
        })
        if result and result.get("items"):
            items = result["items"][:3]
            labels = [item["label"] for item in items]
            print(f"[用户{user_id}] 补全结果: {labels}... 共 {len(result['items'])} 项")
        else:
            print(f"[用户{user_id}] 补全结果: 无")


async def main(port: int, num_users: int) -> None:
    print(f"模拟 {num_users} 个用户同时连接 ws://127.0.0.1:{port}/lsp")
    print("=" * 60)

    # 并发启动所有用户
    tasks = [simulate_user(i, port) for i in range(num_users)]
    await asyncio.gather(*tasks)

    print("=" * 60)
    print("测试完成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="多用户测试客户端")
    parser.add_argument("--port", type=int, default=4001, help="桥接服务端口")
    parser.add_argument("--users", type=int, default=3, help="模拟用户数")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.port, args.users))
    except ConnectionRefusedError:
        print(f"连接被拒绝，请先启动桥接服务（端口 {args.port}）")
