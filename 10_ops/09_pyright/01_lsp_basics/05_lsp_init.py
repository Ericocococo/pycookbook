"""⑤ LSP 初始化流程 —— 三步走：initialize → initialized → didOpen

运行: python 05_lsp_init.py

LSP 协议规定：连上后必须先握手（initialize），再告知打开了什么文件（didOpen），
Pyright 才会开始检查代码。

⚠ 为什么用二进制管道（不加 text=True）：
  Windows 上 text=True 会把写入的 \n 自动转成 \r\n，
  于是你写的 \r\n\r\n 会变成畸形的 \r\r\n\r\r\n（可自己验证：
  open(path, 'w').write('\r\n') 落盘后读出来是 b'\r\r\n'）。
  头部一畸形，Pyright 认不出消息边界就卡死。
  加上 Content-Length 本来就按字节算，所以跟 Pyright 通信一律用 bytes。

演示：
  ① initialize（请求，带 id，期待响应）
  ② initialized（通知，无 id，不期待响应）
  ③ didOpen（通知，Pyright 开始检查，推送诊断）
"""

import json
import shutil
import subprocess


def _read_message(p) -> dict | None:
    """读一条 LSP 消息：先读 Content-Length 头，再读对应字节数的 JSON 体"""
    content_length = 0
    while True:
        line = p.stdout.readline()  # bytes，如 b'Content-Length: 119\r\n'
        if not line:
            return None
        if line.startswith(b"Content-Length:"):
            content_length = int(line.split(b":")[1])
        if not line.strip():  # 空行 = 头部结束
            break
    return json.loads(p.stdout.read(content_length))


def _send(p, data: dict) -> None:
    """发一条 LSP 消息：JSON 转 bytes，前面加 Content-Length 头"""
    body = json.dumps(data).encode()  # dict → JSON 字符串 → bytes
    cb = f"Content-Length: {len(body)}\r\n\r\n".encode() + body
    print(cb)
    p.stdin.write(cb)
    p.stdin.flush()


def demo():
    """完整三步流程"""
    exe = shutil.which("pyright-langserver")
    p = subprocess.Popen(
        [exe, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # 不加 text=True —— 保持二进制，见文件顶部说明
    )

    # ── ① initialize（请求，带 id，期待响应）──
    print("① initialize（请求）")
    _send(p, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": None,
            "capabilities": {},
            "rootUri": None
        }
    })

    while True:
        msg = _read_message(p)
        if msg and msg.get("id") == 1:  # 等 id=1 的响应（跳过启动日志）
            print(f"  收到响应，id={msg['id']}")
            break

    # ── ② initialized（通知，无 id，不期待响应）──
    print("② initialized（通知）")
    _send(p, {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    })
    print("  已发送（无响应）")

    # ── ③ didOpen（通知 Pyright 打开文件，触发检查）──
    #
    # LSP 文档操作分两类：
    #
    #   did* 通知（无 id，不等回复，只是"告诉 Pyright 发生了什么"）：
    #     textDocument/didOpen    打开文件（本例）
    #     textDocument/didChange  内容改了（每改一次 version+1，Pyright 重新检查）
    #     textDocument/didSave    保存文件
    #     textDocument/didClose   关闭文件
    #
    #   查询请求（有 id，要等响应，都带 position 光标位置）：
    #     textDocument/completion  补全
    #     textDocument/hover       悬浮文档
    #     textDocument/definition  跳转定义
    #
    # params.textDocument 各字段：
    #   uri        文件唯一标识，多文件时区分谁是谁（假路径也行，但要唯一）
    #   languageId 语言类型，决定用哪套规则检查（必须是 "python"）
    #   version    文档版本号，每次改动 +1，Pyright 靠它判断新旧
    #   text       文件的完整内容（真正要检查的代码）
    print("③ didOpen（通知）")
    _send(p, {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": "file:///demo.py",
                "languageId": "python",
                "version": 1,
                "text": 'x: int = "hello"',  # ← 故意写错，看 Pyright 能不能发现
            }},
    })

    """
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Starting service instance "<default>"'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'No include entries specified; assuming \\<default workspace root>'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/node_modules'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/__pycache__'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Auto-excluding **/.*'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'Assuming Python version 3.12.13.final.0'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 1, 'message': 'File or directory "\\<default workspace root>" does not exist.'}}
    {'jsonrpc': '2.0', 'method': 'window/logMessage', 'params': {'type': 3, 'message': 'No source files found.'}}
    {'jsonrpc': '2.0', 'method': 'textDocument/publishDiagnostics', 'params': {'uri': 'file:///demo.py', 'version': 1, 'diagnostics': [{'range': {'start': {'line': 0, 'character': 9}, 'end': {'line': 0, 'character': 16}}, 'message': 'Type "Literal[\'hello\']" is not assignable to declared type "int"\n\xa0\xa0"Literal[\'hello\']" is not assignable to "int"', 'severity': 1, 'code': 'reportAssignmentType', 'source': 'Pyright', 'codeDescription': {'href': 'https://github.com/microsoft/pyright/blob/main/docs/configuration.md#reportAssignmentType'}}]}}
    """
    # ── Pyright 分析完主动推送的诊断结果，编辑器画红色波浪线就靠它 ──
    # 注意：line / character 都从 0 开始，转人类习惯要 +1
    a = {
        'method': 'textDocument/publishDiagnostics',  # 诊断推送（服务器主动发，不是回复某个请求）
        'params': {
            'uri': 'file:///demo.py',                 # 哪个文件的诊断（多文件时区分）
            'diagnostics': [{                          # 诊断列表，一个错误一项（这里只有 1 个）
                # range = 波浪线画在哪：第0行第9列 到 第0行第16列，正好框住 "hello"
                'range': {'start': {'line': 0, 'character': 9},
                          'end': {'line': 0, 'character': 16}},
                # message = 鼠标悬停在波浪线上显示的错误文字
                'message': 'Type "Literal[\'hello\']" is not assignable to declared type "int"',
                'severity': 1,                         # 严重级别：1=Error红 2=Warning黄 3=Info蓝 4=Hint灰
                'code': 'reportAssignmentType',        # 规则名，点它能跳到规则文档
                'source': 'Pyright',                   # 谁报的错（可能有多个检查器同时工作）
            }]
        }}
    # ↑ 编辑器拿到后：按 range 画线、按 severity 选颜色、悬停显示 message
    # 等诊断推送（Pyright 主动发的 publishDiagnostics）
    while True:
        msg = _read_message(p)
        print(msg)
        if msg and msg.get("method") == "textDocument/publishDiagnostics":
            diags = msg["params"]["diagnostics"]
            for d in diags:
                line = d["range"]["start"]["line"] + 1
                col = d["range"]["start"]["character"] + 1
                print(f"\n  诊断: 第 {line} 行 {col} 列 — {d['message']}")
            break

    p.kill()
    p.wait()


if __name__ == "__main__":
    demo()
