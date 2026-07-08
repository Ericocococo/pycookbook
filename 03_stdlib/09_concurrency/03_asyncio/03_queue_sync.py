"""asyncio —— 异步同步原语：Queue / Event / Lock / Semaphore

标准库。Python 3.12。
运行: python 03_queue_sync.py

asyncio 提供了和 threading 对应的异步版本同步原语，
区别是：threading 的是阻塞的（等待时占用线程），
asyncio 的是非阻塞的（等待时让出事件循环）。

演示：
  ① asyncio.Queue：异步生产者-消费者
  ② asyncio.Event：协程间信号
  ③ asyncio.Lock：保护共享状态
  ④ asyncio.Semaphore：限制并发数（限流）
"""
import asyncio


def demo01_queue():
    """① asyncio.Queue：异步安全队列

    和 queue.Queue 接口相同，但 put/get 是协程（需要 await）。
    在事件循环内使用，不阻塞线程。
    """
    print("① asyncio.Queue 生产者-消费者")

    async def producer(q):
        for i in range(6):
            await q.put(i)
            print(f"  [生产] 放入 {i}，队列大小: {q.qsize()}")
            await asyncio.sleep(0.05)
        await q.put(None)   # 毒丸

    async def consumer(name, q):
        while True:
            item = await q.get()
            if item is None:
                q.task_done()
                break
            print(f"  [{name}] 消费 {item}")
            await asyncio.sleep(0.1)
            q.task_done()

    async def main():
        q = asyncio.Queue(maxsize=3)
        await asyncio.gather(
            producer(q),
            consumer("消费者A", q),
        )

    asyncio.run(main())


def demo02_event():
    """② asyncio.Event：协程间信号

    和 threading.Event 相同语义：
      set()    触发事件
      clear()  清除事件
      wait()   异步等待事件触发（协程挂起，不阻塞事件循环）
    """
    print("\n② asyncio.Event 信号")

    async def server(ready_event):
        print("  [服务] 初始化中...")
        await asyncio.sleep(0.3)
        print("  [服务] 初始化完成")
        ready_event.set()

    async def client(ready_event):
        print("  [客户端] 等待服务就绪...")
        await ready_event.wait()
        print("  [客户端] 服务就绪，开始请求")

    async def main():
        event = asyncio.Event()
        await asyncio.gather(server(event), client(event))

    asyncio.run(main())


def demo03_lock():
    """③ asyncio.Lock：保护共享状态

    async with lock 等待获取锁，获取后执行临界区代码，退出时释放。
    注意：asyncio.Lock 只在单线程事件循环里有意义（保护协程间共享状态）；
    如果涉及多线程，用 threading.Lock。
    """
    print("\n③ asyncio.Lock")

    async def main():
        counter = 0
        lock = asyncio.Lock()

        async def increment():
            nonlocal counter
            for _ in range(1000):
                async with lock:
                    counter += 1

        await asyncio.gather(*[increment() for _ in range(5)])
        print(f"  期望 5000，实际: {counter}")

    asyncio.run(main())


def demo04_semaphore():
    """④ asyncio.Semaphore：限制并发数

    典型用途：限制同时请求的数量（限流），
    比如爬虫最多 5 个并发请求，避免被封 IP 或压垮服务器。
    """
    print("\n④ asyncio.Semaphore 限流")

    async def fetch(sem, url, delay):
        async with sem:   # 最多 3 个并发
            print(f"  [开始] {url}")
            await asyncio.sleep(delay)
            print(f"  [完成] {url}")
            return f"{url} done"

    async def main():
        sem = asyncio.Semaphore(3)   # 同时最多 3 个
        urls = [(f"url_{i}", 0.2) for i in range(8)]
        results = await asyncio.gather(*[fetch(sem, url, delay) for url, delay in urls])
        print(f"  共完成 {len(results)} 个请求")

    asyncio.run(main())


if __name__ == "__main__":
    demo01_queue()
    demo02_event()
    demo03_lock()
    demo04_semaphore()
