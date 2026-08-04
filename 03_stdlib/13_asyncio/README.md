# asyncio —— 异步 IO 与协程

Python 单线程 + 协程切换模型，适合 IO 密集型任务（网络、文件、子进程），不适合 CPU 密集型。

| 文件 | 内容 |
|------|------|
| `01_basic.py` | async def、await、asyncio.gather 并发、串行 vs 并发对比、asyncio.run |
| `02_advanced.py` | run_in_executor 阻塞丢线程池、async for 异步迭代、async with 异步上下文、Future 永久挂起 |

## 适用

- 网络服务端、WebSocket 桥接
- 大量并发 IO 请求（爬虫、API 调用）
- 子进程通信、管道读写

## 不适用

- CPU 密集计算 → `multiprocessing` 或 `concurrent.futures.ProcessPoolExecutor`
- 已有大量同步代码且不想改 → 维持 `threading` 即可

## 核心速查

```python
import asyncio

# 定义与执行
async def main():
    return 42

result = asyncio.run(main())            # 启动事件循环

# 并发：同时跑 N 个协程
results = await asyncio.gather(
    fetch(url1),
    fetch(url2),
)

# 阻塞函数丢线程池
loop = asyncio.get_event_loop()
data = await loop.run_in_executor(None, blocking_read, arg)

# 服务端永久挂起
await asyncio.Future()                  # 等价于永久不退出

# 异步迭代（WebSocket 消息流）
async for msg in websocket:
    process(msg)

# 异步上下文（自动管理连接）
async with websockets.connect(url) as ws:
    await ws.send("hello")
```
