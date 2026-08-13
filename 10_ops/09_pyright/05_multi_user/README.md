# 多用户 LSP 桥接 —— 三种架构对比

> 同一个 Monaco + Pyright 项目，用三种不同的方式支持多用户并发。
> 从"简单但费内存"到"省内存但需路由"，渐进演示后端架构选型。

## 架构对比

```
阶段1（一连接一进程）        阶段2（共享 Pyright）         阶段3（进程池）
──────────────────        ──────────────────         ──────────────────
用户A ─→ Pyright_A        用户A ─┐                  用户A ─┐
用户B ─→ Pyright_B        用户B ─┼→ 1个Pyright      用户B ─┼→ Worker_0
用户C ─→ Pyright_C        用户C ─┘                  用户C ─┤→ Worker_1
                                                    用户D ─┘→ Worker_2
内存: N × 150MB           内存: 150MB               内存: M × 150MB
路由: 不需要              路由: session + URI        路由: 调度 + session
```

## 文件说明

每个阶段目录完全自包含（各自有 interface/、templates/、client/、http_server.py），可独立运行。

| 目录 | 内容 | HTTP 端口 | WS 端口 |
|------|------|----------|---------|
| [01_per_process/](01_per_process/) | 阶段1：一连接一进程，天然隔离 | 8081 | 3001 |
| [02_shared_pyright/](02_shared_pyright/) | 阶段2：共享 Pyright，URI + ID 路由 | 8082 | 3002 |
| [03_process_pool/](03_process_pool/) | 阶段3：N 个 Worker，最少连接调度 | 8083 | 3003 |

每个阶段目录内的文件：

| 文件 | 作用 |
|------|------|
| `bridge.py` | WebSocket 桥接服务（核心，各阶段不同） |
| `http_server.py` | 前端页面 HTTP 服务 |
| `templates/index.html` | Monaco Editor 前端（补全、诊断、悬浮、参数提示） |
| `client/ws_client.py` | 多用户并发测试客户端 |
| `interface/` | ntrade 量化 API 接口定义（Pyright 据此提供补全） |

## 运行方式

```bash
# 前提
npm install -g pyright
pip install fastapi uvicorn websockets

# 以阶段3为例（其他阶段同理，换目录即可）

# ① 启动桥接服务（开发，单 worker）
python 10_ops/09_pyright/05_multi_user/03_process_pool/bridge.py --serve

# ② 启动前端页面
python 10_ops/09_pyright/05_multi_user/03_process_pool/http_server.py --serve

# ③ 浏览器打开 http://127.0.0.1:8083

# ④ 多用户压测
python 10_ops/09_pyright/05_multi_user/03_process_pool/client/ws_client.py --port 3003 --users 3
```

### bridge.py 参数

```bash
python bridge.py --serve [--host HOST] [--port PORT] [--workers N] [--pool-size M]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--serve` | 必填 | 启动服务 |
| `--host` | 127.0.0.1 | 监听地址，生产部署用 0.0.0.0 |
| `--port` | 3001/3002/3003 | WebSocket 端口 |
| `--workers` | 1 | uvicorn worker 进程数，提高连接吞吐 |
| `--pool-size` | 3 | Pyright Worker 数量（仅阶段3） |

```bash
# 开发（默认）
python bridge.py --serve

# 生产（4 个 uvicorn worker）
python bridge.py --serve --host 0.0.0.0 --workers 4

# 阶段3 完整配置（4 个 uvicorn worker × 3 个 Pyright = 12 个 Pyright 进程）
python bridge.py --serve --host 0.0.0.0 --workers 4 --pool-size 3
```

## 核心机制

### 三层架构

```
浏览器 Monaco Editor  ←WebSocket→  Python Bridge  ←stdio 管道→  Pyright
      前端客户端              中间层（桥接）            后端服务
```

WebSocket 服务用 asyncio 并发处理所有连接，变化的只是 bridge 和 Pyright 之间的关系。

### 两层扩展：uvicorn workers × Pyright 进程池

```
                         Pyright 层                uvicorn 层
                       （分析计算）              （连接吞吐）
                       ─────────               ─────────
阶段1                   N 个（每连接1个）         默认 1 个
阶段2                   1 个（共享）              默认 1 个
阶段3                   M 个（进程池）            默认 1 个
阶段3 + --workers 4    4 × M 个                  4 个
```

生产部署示意（`--workers 4 --pool-size 3`）：

```
nginx（限流 + 负载均衡）
  │
  ├→ uvicorn worker 0 → bridge → Pyright_0, Pyright_1, Pyright_2
  ├→ uvicorn worker 1 → bridge → Pyright_3, Pyright_4, Pyright_5
  ├→ uvicorn worker 2 → bridge → Pyright_6, Pyright_7, Pyright_8
  └→ uvicorn worker 3 → bridge → Pyright_9, Pyright_10, Pyright_11

4 × 3 = 12 个 Pyright，每个扛 ~50 用户 → 总承载 ~600 用户
```

Pyright 池解决"算得慢"，uvicorn workers 解决"接不住"。

### 阶段2/3 的路由三件套

```python
# ① URI 文件名隔离——每个用户的代码用不同文件名，不建子目录
"file:///workspace/main.py"
  → "file:///真实路径/_s_a1b2c3d4.py"   # 用户A
  → "file:///真实路径/_s_c5d6e7f8.py"   # 用户B
# 文件不存在于磁盘，只在 Pyright 内存中（didOpen 提供内容）

# ② 请求 ID 去重——避免多用户 ID 冲突
用户A {id:1} → bridge 改写 → {id:1001} → Pyright
用户B {id:1} → bridge 改写 → {id:1002} → Pyright

# ③ 出站路由
响应 {id:1001} → 查映射表 → 改回 {id:1} → 发给用户A
诊断 {uri:".../_s_a1b2c3d4.py"} → 从文件名提取 session → 发给用户A
```

### 阶段2/3 的关键处理

```python
# Pyright 初始化后发服务端请求（workspace/configuration 等），必须回响应
if "id" in data and "method" in data and data["id"] not in _id_map:
    resp = {"jsonrpc": "2.0", "id": data["id"], "result": None}
    _write_lsp_message(_pyright.stdin, json.dumps(resp).encode())

# Windows 盘符大小写统一（Pyright 返回 d%3A 而非 D:）
from urllib.parse import unquote
uri = unquote(uri)  # file:///d%3A/path → file:///d:/path

# 补全排序——typing 符号排到末尾
if label in _DEMOTE_NAMES or label.startswith("_"):
    item["sortText"] = "zz" + item.get("sortText", label)
```

### 阶段3 调度策略

```python
def _pick_worker() -> PyrightWorker:
    """最少连接数优先"""
    return min(_workers, key=lambda w: w.load)
```

查看各 Worker 负载：`GET http://127.0.0.1:3003/status`

## 并发压测结果

测试环境：Windows + Python 3.12 + Pyright 1.1.x，阶段3（3 个 Worker）。

### 不同涌入速度（补全请求响应时间）

| 场景 | 用户数 | 涌入方式 | 成功率 | 补全 P50 | 补全最慢 |
|------|--------|---------|--------|---------|---------|
| 瞬间涌入 | 20 | 同一毫秒 | 100% | 11ms | 407ms |
| 快速涌入 | 30 | 每 50ms | 100% | 2ms | 10ms |
| 正常上线 | 50 | 每 200ms | 100% | 7ms | 17ms |
| 限流后 | 50 | 每 500ms | 100% | 9ms | 20ms |

### 结论

- **Pyright 处理速度不是瓶颈**：50 用户并发补全平均 7ms，单次请求毫秒级
- **瓶颈在 TCP 连接握手**：瞬间涌入太多连接会超出 TCP backlog，导致握手超时
- **nginx 限流的作用**：把"瞬间涌入"变成"排队进入"，将 P99 从 407ms 降到 20ms
- 真实场景用户逐个打开页面，**50 个在线用户一个 Pyright 进程绑绑有余**

### 容量规划建议

| 用户规模 | 方案 | 启动命令 | 内存 |
|---------|------|---------|------|
| ~20 | 阶段2 | `python bridge.py --serve` | ~150MB |
| 20~100 | 阶段3 | `python bridge.py --serve --pool-size 5` | ~750MB |
| 100~500 | 阶段3 + 多 worker | `python bridge.py --serve --workers 4 --pool-size 3` | ~1.8GB |
| 500+ | 阶段3 + 多 worker + nginx | 同上，前面加 nginx 限流 | 按需 |

### 生产部署参考

```bash
# bridge 启动（阶段3，4 worker × 3 Pyright = 12 个 Pyright 进程）
cd 03_process_pool
python bridge.py --serve --host 0.0.0.0 --port 3003 --workers 4 --pool-size 3
```

```nginx
# nginx 限流 + WebSocket 反代
limit_req_zone $binary_remote_addr zone=ws_limit:10m rate=10r/s;

server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8083;
    }

    location /lsp {
        limit_req zone=ws_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:3003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 踩坑记录

开发过程中遇到的关键问题，部署时注意：

| 问题 | 原因 | 解决 |
|------|------|------|
| 阶段2/3 无诊断 | Pyright 把 `d:` 编码成 `d%3A`，URI 匹配失败 | `unquote(uri)` 解码后再匹配 |
| 阶段2/3 无诊断 | Pyright 发 `workspace/configuration` 请求无人回复，阻塞后续处理 | reader 检测服务端请求并回空响应 |
| 多连接同时到达崩溃 | `_initialize_pyright()` 并发调用，两个线程同时读 stdout | `asyncio.Lock` 保证只初始化一次 |
| reader 崩溃 | Pyright 某些通知的 `params` 是数组不是字典 | `isinstance(params, dict)` 类型检查 |
| Windows/Linux 路径不兼容 | `file:///D:/path`（Win）vs `file:///home/path`（Linux） | 检测盘符自动选择 URI 格式 |
