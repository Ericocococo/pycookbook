"""
LSP JSON-RPC 消息格式参考

掌握：
  - LSP 协议的请求/响应/通知三种消息格式
  - 常用 LSP 方法的参数结构
  - 可以直接复制这些字典作为请求模板

规范：https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
"""

# ──────────────────────────────────────────
# 消息格式说明
# ──────────────────────────────────────────
"""
三种消息类型：

1. 请求（Request）    → 有 id，期待响应
   {"jsonrpc":"2.0", "id":1, "method":"...", "params":{...}}

2. 响应（Response）   → 带与请求相同的 id
   {"jsonrpc":"2.0", "id":1, "result":{...}}

3. 通知（Notification） → 无 id，无响应
   {"jsonrpc":"2.0", "method":"...", "params":{...}}
"""

URI = "file:///workspace/demo.py"


# ──────────────────────────────────────────
# 请求类
# ──────────────────────────────────────────

# 初始化（连接后第一条消息）
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "processId": None,
        "capabilities": {
            "textDocument": {
                "completion": {"completionItem": {"snippetSupport": True}},
                "hover": {"contentFormat": ["markdown", "plaintext"]},
            },
        },
        "rootUri": None,
    },
}

# 代码补全
COMPLETION = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "textDocument/completion",
    "params": {
        "textDocument": {"uri": URI},
        "position": {"line": 5, "character": 8},  # 光标位置（0-based）
    },
}

# 悬浮文档（鼠标悬停）
HOVER = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "textDocument/hover",
    "params": {
        "textDocument": {"uri": URI},
        "position": {"line": 1, "character": 4},
    },
}

# 跳转到定义
DEFINITION = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "textDocument/definition",
    "params": {
        "textDocument": {"uri": URI},
        "position": {"line": 3, "character": 2},
    },
}

# 查找所有引用
REFERENCES = {
    "jsonrpc": "2.0",
    "id": 5,
    "method": "textDocument/references",
    "params": {
        "textDocument": {"uri": URI},
        "position": {"line": 3, "character": 2},
        "context": {"includeDeclaration": True},
    },
}

# 文档符号（大纲）
DOCUMENT_SYMBOLS = {
    "jsonrpc": "2.0",
    "id": 6,
    "method": "textDocument/documentSymbol",
    "params": {
        "textDocument": {"uri": URI},
    },
}

# 代码折叠
FOLDING_RANGE = {
    "jsonrpc": "2.0",
    "id": 7,
    "method": "textDocument/foldingRange",
    "params": {
        "textDocument": {"uri": URI},
    },
}

# 重命名
RENAME = {
    "jsonrpc": "2.0",
    "id": 8,
    "method": "textDocument/rename",
    "params": {
        "textDocument": {"uri": URI},
        "position": {"line": 3, "character": 2},
        "newName": "new_function_name",
    },
}


# ──────────────────────────────────────────
# 通知类
# ──────────────────────────────────────────

# 初始化完成（收到 initialize 响应后发送）
INITIALIZED = {
    "jsonrpc": "2.0",
    "method": "initialized",
    "params": {},
}

# 打开文档
DID_OPEN = {
    "jsonrpc": "2.0",
    "method": "textDocument/didOpen",
    "params": {
        "textDocument": {
            "uri": URI,
            "languageId": "python",
            "version": 1,
            "text": 'print("hello")',
        },
    },
}

# 文档内容变更
DID_CHANGE = {
    "jsonrpc": "2.0",
    "method": "textDocument/didChange",
    "params": {
        "textDocument": {"uri": URI, "version": 2},
        "contentChanges": [{"text": 'print("world")'}],
    },
}

# 关闭文档
DID_CLOSE = {
    "jsonrpc": "2.0",
    "method": "textDocument/didClose",
    "params": {
        "textDocument": {"uri": URI},
    },
}

# 关闭服务
SHUTDOWN = {
    "jsonrpc": "2.0",
    "id": 99,
    "method": "shutdown",
    "params": {},
}

EXIT = {
    "jsonrpc": "2.0",
    "method": "exit",
    "params": {},
}


# ──────────────────────────────────────────
# 枚举值参考
# ──────────────────────────────────────────

# 补全类型（kind）
COMPLETION_KIND = {
    1: "Text",
    2: "Method",
    3: "Function",
    4: "Constructor",
    5: "Field",
    6: "Variable",
    7: "Class",
    8: "Interface",
    9: "Module",
    10: "Property",
    11: "Unit",
    12: "Value",
    13: "Enum",
    14: "Keyword",
    15: "Snippet",
    17: "Color",
    18: "File",
    19: "Reference",
    21: "Operator",
}

# 诊断严重级别（severity）
SEVERITY = {
    1: "Error",
    2: "Warning",
    3: "Information",
    4: "Hint",
}


# ──────────────────────────────────────────
# main（仅展示消息格式）
# ──────────────────────────────────────────
if __name__ == "__main__":
    import json
    print("LSP JSON-RPC 消息格式参考\n")

    for name in ["INITIALIZE", "COMPLETION", "HOVER", "DID_OPEN", "DID_CHANGE"]:
        msg = globals()[name]
        print(f"── {name} ──")
        print(json.dumps(msg, indent=2, ensure_ascii=False))
        print()
