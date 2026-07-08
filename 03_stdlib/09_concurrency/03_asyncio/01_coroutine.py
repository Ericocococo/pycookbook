"""asyncio —— 协程与事件循环基础

标准库。Python 3.12。
运行: python 01_coroutine.py

协程（coroutine）是可以暂停和恢复的函数。
asyncio 用单线程事件循环调度协程，在 IO 等待时切换到其他协程，
实现高并发而不需要多线程/进程的开销。

演示：
  ① async / await 基础
  ② asyncio.run：运行协程入口
  ③ await 的含义：让出控制权
  ④ asyncio.sleep：异步等待（不阻塞事件循环）
  ⑤ 协程链式调用
"""
import asyncio
import time


def demo01_syntax():
    """① async / await 语法

    术语：
      async def   定义协程函数（返回协程对象，不是立即执行）
      await       挂起当前协程，等待右侧的可等待对象完成
                  可等待对象：协程 / Task / Future
      事件循环     asyncio 的调度核心，负责运行协程、处理 IO 事件
    """
    print("① async/await 语法")

    async def hello():
        print("  hello 协程开始")
        await asyncio.sleep(0)   # 让出控制权（即使等待时间为 0）
        print("  hello 协程结束")
        return "done"

    # 调用 async def 不会执行，只返回协程对象
    coro = hello()
    print(f"  hello() 返回的是: {type(coro).__name__}（协程对象，还没执行）")
    coro.close()   # 不再使用这个协程对象，显式关闭避免 RuntimeWarning

    # 用 asyncio.run 运行
    result = asyncio.run(hello())
    print(f"  运行结果: {result!r}")


def demo02_asyncio_run():
    """② asyncio.run：程序入口

    asyncio.run(coro) 是运行协程的标准方式（Python 3.7+）：
      1. 创建新的事件循环
      2. 运行 coro 直到完成
      3. 关闭事件循环，清理资源

    每个程序通常只调用一次 asyncio.run（在最顶层）。
    不能在已运行的事件循环里调用 asyncio.run（会报错）。
    """
    print("\n② asyncio.run")

    async def main():
        print("  协程开始执行")
        result = 1 + 1
        print(f"  计算结果: {result}")
        return result

    result = asyncio.run(main())
    print(f"  asyncio.run 返回: {result}")


def demo03_await_meaning():
    """③ await 的含义：让出控制权

    await 不是"等待"（阻塞），而是"把控制权还给事件循环"：
      - 当前协程挂起，事件循环可以去运行其他协程
      - 等待的操作完成后，事件循环恢复当前协程

    对比 time.sleep（阻塞）和 asyncio.sleep（不阻塞）：
    """
    print("\n③ await vs 阻塞")

    async def blocking_demo():
        print("  [阻塞 sleep] 开始，整个事件循环被卡住")
        time.sleep(0.1)    # 阻塞！其他协程无法运行
        print("  [阻塞 sleep] 结束")

    async def async_demo():
        print("  [异步 sleep] 开始，事件循环可以运行其他协程")
        await asyncio.sleep(0.1)   # 不阻塞，让出控制权
        print("  [异步 sleep] 结束")

    asyncio.run(blocking_demo())
    asyncio.run(async_demo())


def demo04_sleep_and_order():
    """④ asyncio.sleep 与执行顺序

    单独 await asyncio.sleep 没有并发效果（还是顺序执行）。
    要并发执行多个协程，需要 asyncio.gather 或 Task（见下一个文件）。
    """
    print("\n④ 顺序执行 vs 并发（预告）")

    async def task(name, delay):
        print(f"  [{name}] 开始")
        await asyncio.sleep(delay)
        print(f"  [{name}] 结束")

    async def sequential():
        """顺序执行：总耗时 = 各任务耗时之和"""
        t0 = asyncio.get_event_loop().time()
        await task("A", 0.2)
        await task("B", 0.2)
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  顺序执行总耗时: {elapsed:.2f}s（约 0.4s）")

    asyncio.run(sequential())


def demo05_chain():
    """⑤ 协程链式调用

    协程可以 await 其他协程，形成调用链。
    和普通函数调用一样，只是中间可能有 IO 等待。
    """
    print("\n⑤ 协程链式调用")

    async def fetch_data(url):
        print(f"  [fetch] 开始获取 {url}")
        await asyncio.sleep(0.1)    # 模拟网络请求
        return f"{url} 的数据"

    async def process_data(raw):
        print(f"  [process] 处理: {raw[:10]}...")
        await asyncio.sleep(0.05)   # 模拟处理
        return raw.upper()

    async def pipeline(url):
        raw = await fetch_data(url)     # 等 fetch 完
        result = await process_data(raw) # 等 process 完
        return result

    result = asyncio.run(pipeline("https://example.com"))
    print(f"  最终结果: {result}")


if __name__ == "__main__":
    demo01_syntax()
    demo02_asyncio_run()
    demo03_await_meaning()
    demo04_sleep_and_order()
    demo05_chain()
