# Monaco Editor + Pyright LSP 桥接

通过 Python 服务端将 Monaco Editor 与 Pyright 语言服务器对接，实现 5 个代码编辑功能。

## 架构

```
浏览器                     同事的 HTTP                     你的 WebSocket               Pyright
┌──────────────┐     8080  ┌────────────┐  3001 或 3002  ┌────────────┐    stdio     ┌──────────────┐
│ Monaco Editor │ ←──────→ │ HTTP 服务   │               │ LSP 桥接   │ ←────────→  │ pyright-lang │
│               │          │ 提供页面    │               │ 拦截+注入  │             │   server     │
│               │ ───────────────────────────────────→  │            │             │              │
│               │         ws://127.0.0.1:3001           │            │             │              │
└──────────────┘ WebSocket └────────────┘               └────────────┘             └──────────────┘
```

分工：
- **01_http_server.py**（同事）—— 提供 Monaco Editor 前端页面，纯 HTTP
- **02_lsp_bridge_ws.py**（你，方案一）—— WebSocket 桥接，纯 `websockets` 库
- **03_lsp_bridge_fastapi.py**（你，方案二）—— WebSocket 桥接，FastAPI 框架

## WebSocket 两种方案对比

| | websockets 方案 | FastAPI 方案 |
|---|---|---|
| 文件 | `02_lsp_bridge_ws.py` | `03_lsp_bridge_fastapi.py` |
| 依赖 | `pip install websockets` | `pip install fastapi uvicorn` |
| 启动 | `python 02_lsp_bridge_ws.py --serve` | `python 03_lsp_bridge_fastapi.py --serve` |
| 端口 | 3001 | 3002 |
| 连接 URL | `ws://127.0.0.1:3001` | `ws://127.0.0.1:3002/lsp` |
| HTTP 端点 | 无 | `/health`、`/docs` 等 |
| 底层 | websockets 库直接处理 | 通过 ASGI 层转发到 websockets 库 |
| 优势 | 极简，单一依赖 | 扩展性强，可加路由/中间件 |

**核心区别**：FastAPI 的 WebSocket 底层用的就是 websockets 库，只是多包了 ASGI 转发层。纯 WebSocket 场景性能差异可忽略。

## 功能

| 功能 | 实现方式 |
|---|---|
| 语法高亮 | Monaco Monarch 语法规则（前端） |
| 红色波浪线 | Pyright `publishDiagnostics` → Monaco Markers |
| 自动补全 | Pyright `completion` + 自定义函数注入 |
| 代码折叠 | Monaco 内置 + Pyright `foldingRange` |
| 悬浮文档 | Pyright `hover` → Monaco Hover Provider |

## 运行

```bash
# 安装依赖
pip install websockets fastapi uvicorn
npm install -g pyright

# 终端 1：启动 LSP 桥接（二选一）
python 10_ops/09_pyright/04_monaco_lsp/02_lsp_bridge_ws.py --serve      # websockets 方案
python 10_ops/09_pyright/04_monaco_lsp/03_lsp_bridge_fastapi.py --serve  # FastAPI 方案

# 终端 2：启动前端页面（同事的）
python 10_ops/09_pyright/04_monaco_lsp/01_http_server.py --serve

# 浏览器打开 http://127.0.0.1:8080
# 前端 HTML 里默认连 websockets 方案，切换方式见里面的注释
```

## 工作流程

```
Monaco 编辑器                你的 LSP 桥接                 Pyright
     │                           │                            │
     │── 用户输入 "query_" ──→   │                            │
     │                           │── 转发补全请求 ──→          │
     │                           │                            │
     │                           │←── 返回 Pyright 补全项 ──  │
     │                           │                            │
     │                           │ ★ 注入 CUSTOM_COMPLETIONS  │
     │                           │                            │
     │←── 合并后的补全列表 ────  │                            │
     │                           │                            │
     │  弹出：                   │                            │
     │    query_stock (自定义)   │                            │
     │    query (Pyright)        │                            │
```

## 自定义补全的两种方案

### 方案 A：服务端拦截注入（动态）

02_lsp_bridge.py 中拦截 Pyright 的补全响应，追加自定义项：

```python
CUSTOM_COMPLETIONS = [
    {
        "label": "query_stock",
        "kind": 3,  # Function
        "detail": "(code: str, start: str, end: str) -> DataFrame",
        "documentation": {"kind": "markdown", "value": "查询股票行情数据"},
    },
]

# 拦截补全响应，注入自定义函数
if "result" in data and isinstance(data.get("result"), dict):
    items = data["result"].get("items")
    if items is not None:
        items.extend(CUSTOM_COMPLETIONS)
```

### 方案 B：.pyi 桩文件（静态，推荐）

如果自定义函数是固定的，写 `.pyi` 文件更干净——Pyright 原生支持，不用拦截：

```python
# stubs/our_api.pyi
from pandas import DataFrame, Series

def query_stock(code: str, start: str, end: str) -> DataFrame:
    """查询股票行情数据"""
    ...

def calc_ma(df: DataFrame, window: int = 20) -> Series:
    """计算移动平均线"""
    ...
```

然后 `pyrightconfig.json` 配置：

```json
{"stubPath": "stubs"}
```

这样 Pyright 自动补全、悬浮文档、类型检查全都有，不需要在服务端拦截。

### 怎么选

| 方案 | 适用场景 |
|---|---|
| A 服务端拦截注入 | 补全项是动态的（如从数据库查、按用户角色变化） |
| B .pyi 桩文件 | 函数是固定的，只是没有类型注解（推荐） |

## 文件

| 文件 | 说明 |
|---|---|
| 01_http_server.py | 同事负责：提供 Monaco Editor 前端页面（FastAPI） |
| 02_lsp_bridge_ws.py | 你负责，方案一：纯 `websockets` 库，极简 |
| 03_lsp_bridge_fastapi.py | 你负责，方案二：FastAPI 框架，扩展性强 |
| templates/index.html | Monaco Editor 前端：语法高亮规则 + LSP 客户端 |
