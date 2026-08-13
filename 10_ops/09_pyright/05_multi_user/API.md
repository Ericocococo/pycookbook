# LSP Bridge WebSocket 接口文档

> 供前端对接使用。后端提供 WebSocket 服务，前端通过 JSON-RPC 2.0 协议与之通信，
> 获得 Python 代码的**补全、诊断、悬浮文档、参数提示**能力。

## 连接信息

| 项目 | 值 |
|------|-----|
| 协议 | WebSocket |
| 地址 | `ws://{host}:{port}/lsp` |
| 消息格式 | JSON（JSON-RPC 2.0） |
| 编码 | UTF-8 |

前端不需要任何认证、session、token——连上就能用，后端自动管理会话。

## 消息类型

所有消息遵循 [JSON-RPC 2.0](https://www.jsonrpc.org/specification) 格式：

```
请求（前端→后端，有 id，等响应）：  {jsonrpc: "2.0", id: 数字, method: "xxx", params: {...}}
通知（前端→后端，无 id，不等响应）：{jsonrpc: "2.0", method: "xxx", params: {...}}
响应（后端→前端，有 id）：          {jsonrpc: "2.0", id: 数字, result: {...}}
推送（后端→前端，无 id）：          {jsonrpc: "2.0", method: "xxx", params: {...}}
```

## 连接生命周期

```
前端                              后端
 │                                 │
 │── WebSocket 连接 ──────────────→│
 │                                 │
 │── ① initialize 请求 ──────────→│
 │←── initialize 响应 ────────────│
 │                                 │
 │── ② initialized 通知 ─────────→│
 │                                 │
 │── ③ didOpen 通知 ─────────────→│  ← 从这里开始，后端分析代码
 │←── publishDiagnostics 推送 ────│  ← 后端主动推诊断（红线）
 │                                 │
 │── ④ 用户编辑 → didChange ─────→│
 │←── publishDiagnostics 推送 ────│  ← 每次编辑后推新诊断
 │                                 │
 │── ⑤ completion 请求 ──────────→│
 │←── completion 响应 ────────────│
 │                                 │
 │── ⑥ hover 请求 ───────────────→│
 │←── hover 响应 ─────────────────│
 │                                 │
 │── ⑦ signatureHelp 请求 ───────→│
 │←── signatureHelp 响应 ─────────│
 │                                 │
 │── WebSocket 断开 ─────────────→│  ← 后端自动清理
```

## 文件 URI 约定

前端使用 `file:///workspace/{文件名}` 格式：

```
"file:///workspace/strategy_001.py"
"file:///workspace/my_algo.py"
"file:///workspace/test.py"
```

- 文件名由前端自定义，任意合法的 `.py` 名称
- 同一个连接内所有请求（didOpen/didChange/completion/hover）使用**同一个 URI**
- 不同连接（不同用户/标签页）可以用相同文件名，后端自动隔离

---

## ① initialize（必须，连接后第一个请求）

建立 LSP 会话。

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "processId": null,
    "capabilities": {
      "textDocument": {
        "completion": {
          "completionItem": {"snippetSupport": true}
        },
        "hover": {
          "contentFormat": ["markdown", "plaintext"]
        },
        "publishDiagnostics": {
          "relatedInformation": true
        }
      }
    },
    "rootUri": null
  }
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "capabilities": {
      "completionProvider": {"triggerCharacters": ["."]},
      "hoverProvider": true,
      "signatureHelpProvider": {"triggerCharacters": ["(", ","]},
      "textDocumentSync": 2
    }
  }
}
```

> capabilities 内容由 Pyright 决定，前端不需要解析，直接进入下一步。

## ② initialized（必须，initialize 响应后立即发）

通知后端初始化完成。

```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

> 无响应。

## ③ textDocument/didOpen（必须，打开文档）

告诉后端"用户打开了一个文件"，触发代码分析。

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {
    "textDocument": {
      "uri": "file:///workspace/main.py",
      "languageId": "python",
      "version": 1,
      "text": "from interface import ntdata\n\nntdata.\n"
    }
  }
}
```

> 无响应。发送后后端开始分析代码，几秒内会推送 `publishDiagnostics`。

## ④ textDocument/didChange（用户每次编辑后发）

通知后端代码内容变更。

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didChange",
  "params": {
    "textDocument": {
      "uri": "file:///workspace/main.py",
      "version": 2
    },
    "contentChanges": [
      {"text": "完整的新代码内容"}
    ]
  }
}
```

> `version` 每次编辑 +1。`contentChanges` 发全量文本（不是增量 diff）。

## ⑤ textDocument/completion（代码补全）

用户输入 `.` 或手动触发时，请求补全列表。

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "textDocument/completion",
  "params": {
    "textDocument": {"uri": "file:///workspace/main.py"},
    "position": {"line": 2, "character": 7}
  }
}
```

> `line` 和 `character` 都从 **0** 开始。

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "items": [
      {
        "label": "get_market_data_ex",
        "kind": 3,
        "detail": "(field_list: List[str] = [], ...) -> Dict[str, DataFrame]",
        "documentation": {
          "kind": "markdown",
          "value": "获取历史行情数据。回测/实盘共用。..."
        },
        "sortText": "10.0000.get_market_data_ex",
        "insertText": "get_market_data_ex"
      }
    ]
  }
}
```

**items 字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `label` | string | 显示文本 |
| `kind` | number | 图标类型：3=函数, 5=字段, 6=变量, 7=类, 9=模块 |
| `detail` | string | 右侧灰色说明（函数签名等） |
| `documentation` | object/string | 选中后展示的文档（markdown） |
| `sortText` | string | 排序键（按字典序排列，前端照此排序） |
| `insertText` | string | 选中后插入的文本 |

## ⑥ textDocument/hover（悬浮文档）

鼠标悬停在标识符上时，请求类型信息和文档。

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "textDocument/hover",
  "params": {
    "textDocument": {"uri": "file:///workspace/main.py"},
    "position": {"line": 2, "character": 10}
  }
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "contents": {
      "kind": "markdown",
      "value": "```python\n(function) def get_market_data_ex(...) -> Dict[str, DataFrame]\n```\n---\n获取历史行情数据。"
    },
    "range": {
      "start": {"line": 2, "character": 7},
      "end": {"line": 2, "character": 27}
    }
  }
}
```

> `result` 为 `null` 表示该位置无悬浮信息。

## ⑦ textDocument/signatureHelp（参数提示）

输入 `(` 或 `,` 时，请求函数参数提示。

**请求：**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "textDocument/signatureHelp",
  "params": {
    "textDocument": {"uri": "file:///workspace/main.py"},
    "position": {"line": 3, "character": 25}
  }
}
```

**响应：**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "signatures": [
      {
        "label": "get_market_data_ex(field_list: List[str] = [], stock_list: List[str] = [], period: str = '1d', ...)",
        "parameters": [
          {"label": "field_list"},
          {"label": "stock_list"},
          {"label": "period"}
        ],
        "documentation": "获取历史行情数据。"
      }
    ],
    "activeSignature": 0,
    "activeParameter": 0
  }
}
```

> `activeParameter` 表示当前光标在第几个参数上（从 0 开始），前端据此高亮对应参数。

## 后端推送：textDocument/publishDiagnostics（诊断/红线）

后端**主动推送**，前端只需监听，不需要请求。

```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/publishDiagnostics",
  "params": {
    "uri": "file:///workspace/main.py",
    "diagnostics": [
      {
        "range": {
          "start": {"line": 5, "character": 0},
          "end": {"line": 5, "character": 22}
        },
        "severity": 1,
        "message": "Expression of type \"str\" is incompatible with declared type \"int\"",
        "source": "Pyright"
      }
    ]
  }
}
```

**severity 含义：**

| 值 | 含义 | 建议样式 |
|----|------|---------|
| 1 | Error | 红色波浪线 |
| 2 | Warning | 黄色波浪线 |
| 3 | Information | 蓝色波浪线 |
| 4 | Hint | 灰色省略号 |

> `diagnostics` 为空数组 `[]` 表示该文件无错误（清除之前的红线）。

## 前端实现要点

### 最小实现（4 步）

```javascript
// 1. 连接
const ws = new WebSocket('ws://host:port/lsp');

// 2. 连上后初始化
ws.onopen = () => {
    sendRequest('initialize', {processId: null, capabilities: {...}, rootUri: null})
        .then(() => {
            sendNotification('initialized', {});
            sendNotification('textDocument/didOpen', {textDocument: {uri, languageId: 'python', version: 1, text: code}});
        });
};

// 3. 监听推送
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // 响应：按 id 匹配 resolve
    // 诊断：data.method === 'textDocument/publishDiagnostics'
};

// 4. 用户操作时发请求
// 编辑 → didChange
// 输入. → completion
// 悬停 → hover
// 输入( → signatureHelp
```

### 注意事项

| 项 | 说明 |
|----|------|
| URI | 格式 `file:///workspace/{文件名}.py`，文件名自定义，同一连接内保持一致 |
| position | `line` 和 `character` 都从 0 开始，不是 1 |
| version | `didChange` 的 version 必须递增，否则后端忽略 |
| 重连 | WebSocket 断开后应自动重连，重新走 initialize → didOpen 流程 |
| 并发 | 每个请求的 `id` 必须唯一（递增即可），后端按 `id` 匹配响应 |
| 全量文本 | `didChange` 发完整代码，不是增量 diff |
