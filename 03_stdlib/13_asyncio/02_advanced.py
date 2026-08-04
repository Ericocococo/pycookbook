"""asyncio 进阶 —— 线程池、异步迭代、异步上下文、服务常驻

Python 3.12。
运行: python 02_advanced.py

演示：
  ① run_in_executor：阻塞代码丢线程池，不卡事件循环
  ② async for：异步迭代器，每次迭代都 await 下一次数据
  ③ async with：异步上下文管理器，进入/退出都需要等待
  ④ yield / await / async yield：三种暂停机制对比
  ⑤ asyncio.Future：永久挂起，服务端不退出
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# ---------------------------------------------------------------------------
# ① run_in_executor
# ---------------------------------------------------------------------------

def demo01_executor():
    """① run_in_executor：阻塞函数丢线程池，事件循环不被卡住"""
    print("① run_in_executor 丢线程池")

    def blocking_read(n: int) -> str:
        time.sleep(0.3)                   # 同步阻塞，会卡线程
        return f"读到 {n} 字节"

    async def main():
        loop = asyncio.get_event_loop()

        # ── 方式一：None = 用默认线程池 ──
        # 默认线程数 = min(32, os.cpu_count() + 4)，偶尔用完全够
        data = await loop.run_in_executor(None, blocking_read, 100)
        print(f"  默认池: {data}")

        # ── 方式二：传 ThreadPoolExecutor 实例，控制线程数 ──
        pool = ThreadPoolExecutor(max_workers=2)
        data2 = await loop.run_in_executor(pool, blocking_read, 50)
        print(f"  自定义池(2线程): {data2}")

        # 多个阻塞并发
        results = await asyncio.gather(
            loop.run_in_executor(None, blocking_read, 50),
            loop.run_in_executor(None, blocking_read, 100),
        )
        print(f"  并发两个: {results}")
        pool.shutdown()

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ② async for
# ---------------------------------------------------------------------------

def demo02_async_for():
    """② async for：每次迭代都 await 下一次数据，如 WebSocket 消息流"""
    print("\n② async for 异步迭代")

    async def data_stream():
        for i in range(4):
            await asyncio.sleep(0.05)
            yield f"消息{i}"

    async def main():
        async for msg in data_stream():
            print(f"  收到: {msg}")

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ③ async with
# ---------------------------------------------------------------------------

def demo03_async_with():
    """③ async with：进入退出都需要等待，如数据库连接 / WebSocket"""
    print("\n③ async with 异步上下文")

    class AsyncConn:
        async def __aenter__(self):
            print("  连接中...")
            await asyncio.sleep(0.1)
            print("  已连接")
            return self

        async def __aexit__(self, *args):
            print("  关闭连接")
            await asyncio.sleep(0.05)

        async def send(self, msg: str):
            print(f"  发送: {msg}")

    async def main():
        async with AsyncConn() as conn:
            await conn.send("hello")

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ④ yield / await / async yield 对比
# ---------------------------------------------------------------------------

def demo04_yield_await():
    """④ 三种暂停机制：yield 逐个产出 / await 异步等待 / async yield 两者结合"""
    print("\n④ yield / await / async yield 对比")

    # ── yield：同步生成器，逐个产出 ──
    def count_up(n: int):
        """普通生成器，每次 next() 跑到下一个 yield 暂停"""
        for i in range(n):
            print(f"    yield 产出 {i}")
            yield i

    print("  yield 演示:")
    for x in count_up(2):
        print(f"    拿到: {x}")

    # ── await：异步等待 IO ──
    async def fetch(msg: str):
        """await 暂停自己，等 IO 完成再继续"""
        print(f"    await 开始 {msg}")
        await asyncio.sleep(0.05)          # 模拟异步 IO
        print(f"    await 完成 {msg}")
        return msg.upper()

    async def await_demo():
        print("  await 演示:")
        result = await fetch("hello")      # 暂停，等 fetch 跑完
        print(f"    拿到: {result}")

    asyncio.run(await_demo())

    # ── async yield：先异步等，再产出 ──
    async def stream():
        """异步生成器：每次迭代先 await 等 IO，再 yield 产出"""
        for msg in ["A", "B"]:
            data = await fetch(msg)        # 先异步等 IO
            yield data                     # 再产出给调用方

    async def async_yield_demo():
        print("  async yield 演示:")
        async for item in stream():        # async for 逐次取值
            print(f"    拿到: {item}")

    asyncio.run(async_yield_demo())

    print()
    print(f"  关键区别:")
    print(f"    yield  → 同步逐个产出，不涉及 IO 等待")
    print(f"    await  → 异步等 IO，拿到结果后继续")
    print(f"    async yield → 每产出一个之前先 await 等 IO")


# ---------------------------------------------------------------------------
# ⑤ Future 永久挂起
# ---------------------------------------------------------------------------

def demo05_future():
    """⑤ await asyncio.Future()：永久挂起，服务端不退出"""
    print("\n⑤ Future 永久挂起")

    async def start_server():
        print("  服务器启动中...")
        await asyncio.sleep(0.5)
        print("  服务器就绪，等待请求...")
        # await asyncio.Future()  # 实际用这句，这里演示不挂

    asyncio.run(start_server())

    print("  实际服务端写法:")
    print("    await asyncio.Future()  # 永不 resolve，取代 while True + sleep")


if __name__ == "__main__":
    # demo01_executor()
    # demo02_async_for()
    # demo03_async_with()
    # demo04_yield_await()
    demo05_future()
