# Monaco + Pyright LSP —— 浏览器端代码编辑器 + 语言服务完整 Demo

> 把前两步学到的 LSP 协议和 Monaco Editor 串起来，跑通一个完整的
> **浏览器写 Python、Pyright 实时检查 + 补全 + 悬浮文档** 的闭环。

## 架构

```
浏览器(Monaco Editor)  ←WebSocket→  Bridge(Python)  ←stdio 管道→  Pyright
        前端页面                    桥接服务                    语言服务器
```

- **前端**：Monaco Editor（CDN 加载），通过 WebSocket 发送 LSP 请求
- **桥接**：Python 进程，双向转发 WebSocket ↔ Pyright stdio，并可拦截响应注入自定义补全
- **后端**：pyright-langserver 子进程，提供类型检查、补全、悬浮文档

## 文件说明

| 文件 | 内容 |
|------|------|
| [01_http_server.py](01_http_server.py) | HTTP 服务，托管 Monaco Editor 前端页面（FastAPI） |
| [02_lsp_bridge_ws.py](02_lsp_bridge_ws.py) | LSP 桥接服务 —— websockets 方案（极简，单依赖） |
| [03_lsp_bridge_fastapi.py](03_lsp_bridge_fastapi.py) | LSP 桥接服务 —— FastAPI 方案（可混合 HTTP+WS，有 /docs） |
| [client/ws_client.py](client/ws_client.py) | WebSocket 客户端，命令行测试 LSP 请求/响应 |
| [templates/index.html](templates/index.html) | Monaco Editor 前端页面（补全、诊断、悬浮文档） |
| [interface/](interface/) | ntrade 量化交易 API 接口定义（类型 stub），供 Pyright 提供补全 |

## interface 包——让 Pyright 提供真实的交易 API 补全

[interface/](interface/) 目录是 ntrade 量化平台的 **接口声明包**（只有签名和文档，没有实现），包含：

| 模块 | 内容 |
|------|------|
| [nttype.py](interface/nttype.py) | 数据类型：`StockAccount`、`NtAsset`、`NtOrder`、`NtTrade`、`NtPosition` 等 |
| [ntconstant.py](interface/ntconstant.py) | 常量：买卖方向、报价类型、市场、委托状态、账号状态 |
| [ntdata.py](interface/ntdata.py) | 行情函数：`get_market_data_ex`、`subscribe_quote`、`get_full_tick` 等 |
| [nttrader.py](interface/nttrader.py) | 交易类 `NtQuantTrader` + 模块级下单/查询函数 |
| [ntcontext.py](interface/ntcontext.py) | 策略上下文 Protocol `INTradeContext`（init/handlebar 模式） |
| [ntresult.py](interface/ntresult.py) | 回测结果 `BacktestResult` TypedDict |

**工作原理**：桥接服务拦截前端的 `initialize` 请求，注入 `rootUri` 指向本目录，
Pyright 发现 `interface/` 包后自动为 `from interface import ntdata` 等语句提供补全和类型检查。
前端使用虚拟路径 `file:///workspace/main.py`，桥接层透明重写为磁盘真实路径。

## 两种桥接方案对比

| 维度 | websockets 方案 | FastAPI 方案 |
|------|-----------------|-------------|
| 依赖 | `websockets` | `fastapi` + `uvicorn` |
| 端口 | `ws://127.0.0.1:3001` | `ws://127.0.0.1:3002/lsp` |
| 路由 | 无（纯 WebSocket） | 有（`/lsp`、`/health`、`/docs`） |
| 适合 | 极简场景 | 需要混合 HTTP + WebSocket |

## 运行方式

```bash
# 前提：安装 pyright
npm install -g pyright

# ① 启动桥接服务（二选一）
python 10_ops/09_pyright/04_monaco_lsp/02_lsp_bridge_ws.py --serve       # 方案一
python 10_ops/09_pyright/04_monaco_lsp/03_lsp_bridge_fastapi.py --serve  # 方案二

# ② 启动前端页面服务
python 10_ops/09_pyright/04_monaco_lsp/01_http_server.py --serve

# ③ 浏览器打开 http://127.0.0.1:8080

# 可选：命令行测试客户端
python 10_ops/09_pyright/04_monaco_lsp/client/ws_client.py
```

## 核心速查

```python
# ① 桥接核心：读写 LSP 消息（Content-Length 头 + JSON 体）
def _read_lsp_message(stdout) -> bytes | None:
    """从 pyright stdout 按 Content-Length 协议读一条消息"""

def _write_lsp_message(stdin, raw: bytes) -> None:
    header = f"Content-Length: {len(raw)}\r\n\r\n".encode()
    stdin.write(header + raw)

# ② 注入 rootUri——让 Pyright 找到 interface 包
if msg.get("method") == "initialize":
    msg["params"]["rootUri"] = _WORKSPACE_URI  # file:///...../04_monaco_lsp

# ③ 虚拟路径透明重写
text = text.replace("file:///workspace/", _REAL_PREFIX)  # 前端→Pyright
text = text.replace(_REAL_PREFIX, "file:///workspace/")  # Pyright→前端

# ④ 拦截补全响应，注入自定义函数（桥接层追加，非 Pyright 原生）
if "result" in data and isinstance(data.get("result"), dict):
    items = data["result"].get("items")
    if items is not None:
        items.extend(CUSTOM_COMPLETIONS)
```
