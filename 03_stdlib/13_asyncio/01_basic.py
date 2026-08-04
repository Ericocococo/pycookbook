"""asyncio 基础 —— async/await、并发、事件循环

Python 3.12。
运行: python 01_basic.py

背景：Python 的 GIL 让多线程无法并行计算，但 IO 密集任务（网络、文件读写）
大部分时间在等，asyncio 用单线程 + 协程切换来并发处理，不浪费 CPU。

演示：
  ① async def：定义协程，调用返回 coroutine 对象，不立即执行
  ② await：暂停当前协程，等另一个协程跑完再继续
  ③ asyncio.gather：多个协程一起跑，全部完成才返回
  ④ 串行 vs 并发：依次 await = 串行，gather = 并发
  ⑤ asyncio.run：启动事件循环，跑完协程后关闭循环
"""

import asyncio
import time


# ---------------------------------------------------------------------------
# ① async def
# ---------------------------------------------------------------------------

def demo01_define():
    """① async def vs 普通函数：协程调用不执行，普通函数调用即执行"""
    print("① async def 对比普通函数")

    # ── 普通函数 ──
    def normal_hello(name: str) -> str:
        return f"hello, {name}"

    ret = normal_hello("world")         # 调用即执行，直接拿到返回值
    print(f"  普通函数: 调用 → {type(ret).__name__} '{ret}'")

    # ── 协程函数 ──
    async def async_hello(name: str) -> str:
        return f"hello, {name}"

    coro = async_hello("world")         # 调用不执行，返回 coroutine 对象
    print(f"  协程函数: 调用 → {type(coro).__name__} (还没执行)")

    # 方式一：asyncio.run() —— 在普通代码里启动协程
    result = asyncio.run(coro)
    print(f"            run() → {type(result).__name__} '{result}'")

    # 方式二：await —— 在另一个 async 函数里执行协程
    async def call_async():
        inner = async_hello("await")
        return await inner             # ← await 执行协程，拿到 str 返回值

    result2 = asyncio.run(call_async())
    print(f"            await → {type(result2).__name__} '{result2}'")

    print()
    print(f"  关键区别:")
    print(f"    普通函数: 调用即执行, 拿到 str")
    print(f"    协程函数: 调用拿到 coroutine, 必须 run() 或 await 才执行")
    print(f"    run() 用于普通代码, await 用于 async 函数内部")


# ---------------------------------------------------------------------------
# ② await
# ---------------------------------------------------------------------------

def demo02_await():
    """② await 暂停，等另一个协程完成才继续"""
    print("\n② await 暂停等待")

    async def fetch(uid: int) -> str:
        await asyncio.sleep(0.1)              # 模拟 IO 等待
        return f"data_{uid}"

    async def main():
        print("  开始请求")
        data = await fetch(42)
        print(f"  结果: {data}")
        print("  继续执行")

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ③ gather 并发
# ---------------------------------------------------------------------------

def demo03_gather():
    """③ gather 让多个协程同时跑，全部完成才返回"""
    print("\n③ gather 并发执行")

    async def download(url: str, delay: float) -> str:
        print(f"  开始: {url}")
        await asyncio.sleep(delay)
        print(f"  完成: {url}")
        return f"content of {url}"

    async def main():
        start = time.time()
        results = await asyncio.gather(
            download("a.txt", 1.5),
            download("b.txt", 1.1),
            download("c.txt", 1.3),
        )
        print(f"  全部完成，耗时 {time.time() - start:.1f}s")
        print(f"  结果: {results}")

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ④ 串行 vs 并发
# ---------------------------------------------------------------------------

def demo04_serial_vs_concurrent():
    """④ 关键区别：依次 await = 串行，gather = 并发"""
    print("\n④ 串行 vs 并发对比")

    async def task(name: str, delay: float):
        await asyncio.sleep(delay)
        print(f"  {name} 完成")
        return name

    async def serial():
        r1 = await task("A", 1)
        r2 = await task("B", 2)
        r3 = await task("C", 3)
        return r1, r2, r3

    async def concurrent():
        return await asyncio.gather(
            task("A", 1),
            task("B", 2),
            task("C", 3),
        )

    async def main():
        start = time.time()
        await serial()
        print(f"  串行耗时: {time.time() - start:.1f}s\n")

        start = time.time()
        await concurrent()
        print(f"  并发耗时: {time.time() - start:.1f}s")

    asyncio.run(main())


# ---------------------------------------------------------------------------
# ⑤ asyncio.run
# ---------------------------------------------------------------------------

def demo05_run():
    """⑤ asyncio.run() 创建事件循环、跑完协程、关闭循环"""
    print("\n⑤ asyncio.run 事件循环")

    async def main():
        print("  事件循环在跑")
        await asyncio.sleep(0.01)
        print("  跑完了")
        return "结果"

    result = asyncio.run(main())
    print(f"  返回值: {result}")

    # ⚠ asyncio.run() 一次只能跑一个协程
    # 服务端要这样写：
    #
    #   async def start():
    #       await websockets.serve(handler, host, port)
    #       await asyncio.Future()  # 永久挂起
    #   asyncio.run(start())


if __name__ == "__main__":
    # demo01_define()
    # demo02_await()
    # demo03_gather()
    # demo04_serial_vs_concurrent()
    demo05_run()
