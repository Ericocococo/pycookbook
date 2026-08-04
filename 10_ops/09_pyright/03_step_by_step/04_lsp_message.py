"""④ 看懂 LSP 消息格式 —— Content-Length 头 + JSON 体

运行: python 04_lsp_message.py

Pyright 通过 stdin/stdout 通信，消息格式固定：
  1. 先发一行 Content-Length: <字节数>\r\n
  2. 空一行 \r\n
  3. 发 JSON 体（正好 Content-Length 个字节）

关于分隔符 \r\n\r\n：
  - \r = 回车 (CR)，\n = 换行 (LF)，\r\n = CRLF
  - LSP 协议规定用 \r\n\r\n（和 HTTP 一样），跟操作系统无关
  - 哪怕在 Linux/Mac 上跑，也照样用 \r\n，不是 Windows 专属
  - 本文件用 \n\n 也能跑通只因 Pyright 解析宽容，规范写法是 \r\n\r\n

演示：
  ① 手动构造一条 LSP 消息
  ② 完整收发一轮（发请求 → 读响应）
"""

import json
import shutil
import subprocess

# ── 发送的 initialize 请求（你问 Pyright："你能干啥"）──
SEND = {
    "jsonrpc": "2.0",                              # JSON-RPC 协议版本，固定 2.0
    "id": 1,                                       # 请求编号，响应会带回同样的 id 让你对上号
    "method": "initialize",                        # 方法名：LSP 规定连上后第一个必须发 initialize
    "params": {                                    # 该方法的参数
        "processId": None,                         # 客户端进程 PID，None=不告诉它（它就不监控父进程存活）
        "capabilities": {},                        # 客户端支持的能力，空={}=我啥都不特别声明，用默认
        "rootUri": None                            # 项目根目录 URI，None=不指定（单文件场景够用）
    }
}

# ── 收到的响应（Pyright 回你一份"能力清单" capabilities）──
# 对照编辑器 5 大功能：
#   completionProvider  → 自动补全（触发字符 . [ " '）
#   hoverProvider       → 悬浮文档
#   definitionProvider  → 跳转定义
#   renameProvider      → 重命名
#   textDocumentSync: 2 → 增量同步文档（才能持续检查、画波浪线）
RECEIVE = {
    'jsonrpc': '2.0',                              # JSON-RPC 协议版本，固定 2.0
    'id': 1,                                       # 对应请求的 id，表示"这是 id=1 请求的回复"
    'result': {                                    # 响应结果（请求成功时有 result，失败时有 error）
        'capabilities': {                          # 能力清单：Pyright 支持哪些功能
            # textDocumentSync=2 → 增量同步：文档改动时只发变化的部分（1=全量，0=不同步）
            # 这是"红色波浪线"的基础——文档持续同步，Pyright 才能实时检查
            'textDocumentSync': 2,

            # 跳转到定义：Ctrl+点击函数名，跳到它定义的地方
            # workDoneProgress=True → 支持进度提示（大项目分析时显示进度条）
            'definitionProvider': {
                'workDoneProgress': True
            },
            # 跳转到声明（declaration 和 definition 在 C/C++ 里区分，Python 里通常一样）
            'declarationProvider': {
                'workDoneProgress': True
            },
            # 跳转到类型定义：跳到变量"类型"的定义处（如变量是 User 类型，跳到 class User）
            'typeDefinitionProvider': {
                'workDoneProgress': True
            },
            # 查找所有引用：这个函数/变量在哪些地方被用到
            'referencesProvider': {
                'workDoneProgress': True
            },
            # 文档大纲：列出当前文件里所有函数/类/变量（IDE 左侧的结构树）
            'documentSymbolProvider': {
                'workDoneProgress': True
            },
            # 工作区符号搜索：跨整个项目搜函数/类名（Ctrl+T 全局搜索）
            'workspaceSymbolProvider': {
                'workDoneProgress': True
            },
            # 悬浮文档：鼠标停在函数名上，显示类型签名和 docstring
            'hoverProvider': {
                'workDoneProgress': True
            },
            # 高亮同名符号：光标停在变量上，文件里所有同名处一起高亮
            'documentHighlightProvider': {
                'workDoneProgress': True
            },
            # 重命名：改一个变量名，所有引用处一起改
            'renameProvider': {
                'prepareProvider': True,           # 重命名前先校验光标位置能不能改
                'workDoneProgress': True
            },
            # 自动补全：核心功能
            'completionProvider': {
                # 输入这些字符时自动弹出补全（. 后面补方法，[ 后面补 key 等）
                'triggerCharacters': ['.', '[', '"', "'"],
                'resolveProvider': True,           # 支持"补全项详情懒加载"（选中才查文档，省性能）
                'workDoneProgress': True,
                'completionItem': {
                    'labelDetailsSupport': True    # 补全项支持显示额外详情（如参数签名）
                }
            },
            # 函数签名提示：输入 ( 后显示参数列表，提示第几个参数
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',', ')'],  # 这些字符触发签名提示
                'workDoneProgress': True
            },
            # 快速修复：波浪线处按灯泡图标，提供修复建议
            'codeActionProvider': {
                # 支持的修复类型：quickfix=快速修复，organizeImports=整理导入
                'codeActionKinds': ['quickfix', 'source.organizeImports'],
                'workDoneProgress': True
            },
            # 执行命令：客户端可让服务器执行预定义命令（commands 为空表示没有）
            'executeCommandProvider': {
                'commands': [],
                'workDoneProgress': True
            },
            # 调用层级：查看某函数被谁调用、又调用了谁（调用树）
            'callHierarchyProvider': True,
            # 工作区（多文件夹项目）相关能力
            'workspace': {
                'workspaceFolders': {
                    'supported': True,             # 支持多根文件夹的工作区
                    'changeNotifications': True    # 文件夹增删时会收到通知
                }
            }
        }
    }
}


def demo01_format():
    """① LSP 消息的格式"""
    print("① LSP 消息格式")

    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"processId": None, "capabilities": {}, "rootUri": None},
    })
    raw = body
    header = f"Content-Length: {len(raw)}\r\n\r\n"

    print(f"  完整消息:")
    print(f"  {(header + raw)!r}")
    print()
    print(f"  结构:")
    print(f"    Content-Length: {len(raw)}              ← 必须等于 JSON 字节数")
    print(f"    <空行>")
    print(f"    {body}                           ← JSON 体")


def demo02_roundtrip():
    """② 发一条消息，读一条响应"""
    print("\n② 发 initialize，收响应")

    exe = shutil.which("pyright-langserver")
    p = subprocess.Popen(
        [exe, "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # 不加 text=True —— 跟 Pyright 通信一律用 bytes（Windows text 模式会把
        # \r\n 写成畸形的 \r\r\n，导致 Pyright 认不出消息边界卡死）
    )

    # 步骤 1：构造并发送 initialize 请求（bytes）
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"processId": None, "capabilities": {}, "rootUri": None},
    }).encode()
    p.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    p.stdin.flush()
    print("  已发送 initialize 请求")

    # 步骤 2：跳过 Pyright 的启动日志，等 initialize 响应
    while True:
        content_length = 0
        while True:
            line = p.stdout.readline()
            if line.startswith(b"Content-Length:"):
                content_length = int(line.split(b":")[1])
            if not line.strip():
                break

        body = p.stdout.read(content_length)
        data = json.loads(body)
        # 启动日志 → 跳过
        if data.get("method") == "window/logMessage":
            print(f"  Pyright 日志: {data['params']['message'][:50]}...")
            continue

        # initialize 响应
        if "id" in data and data["id"] == 1:
            caps = data["result"]["capabilities"]
            print(f"  响应 id={data['id']}，能力: {json.dumps(caps, ensure_ascii=False)[:100]}...")
            break

    p.kill()
    p.wait()


if __name__ == "__main__":
    demo01_format()
    demo02_roundtrip()
