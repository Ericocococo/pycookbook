"""asyncio —— 异步 IO：streams / 超时 / 在线程中运行阻塞代码

标准库。Python 3.12。
运行: python 04_streams.py

演示：
  ① asyncio.timeout / wait_for：给协程设超时
  ② asyncio.to_thread：在线程中运行阻塞函数（不阻塞事件循环）
  ③ loop.run_in_executor：老式在线程/进程中运行
  ④ asyncio.open_connection：异步 TCP 客户端（本地回声服务器）
"""
import asyncio
import time


def demo01_timeout():
    """① asyncio.timeout / wait_for：超时控制

    wait_for(coro, timeout)  超时抛 asyncio.TimeoutError
    asyncio.timeout(n)       Python 3.11+ 上下文管理器写法，更灵活
    """
    print("① 超时控制")

    async def slow_task():
        await asyncio.sleep(2)
        return "完成"

    async def main():
        # wait_for：超时抛 TimeoutError
        try:
            result = await asyncio.wait_for(slow_task(), timeout=0.3)
        except asyncio.TimeoutError:
            print("  wait_for：超时！")

        # asyncio.timeout（Python 3.11+）
        try:
            async with asyncio.timeout(0.3):
                await slow_task()
        except asyncio.TimeoutError:
            print("  asyncio.timeout：超时！")

    asyncio.run(main())


def demo02_to_thread():
    """② asyncio.to_thread：在线程中运行阻塞函数

    阻塞函数（time.sleep / 同步文件 IO / CPU 密集计算）
    直接 await 是不行的（它们不是协程），
    直接调用又会阻塞事件循环（其他协程无法运行）。

    asyncio.to_thread(func, *args) 把阻塞函数丢到线程池运行，
    返回协程，可以 await，不阻塞事件循环。
    """
    print("\n② asyncio.to_thread 运行阻塞函数")

    def blocking_io(name, delay):
        """模拟阻塞 IO（如同步读文件）"""
        time.sleep(delay)           # 阻塞调用
        return f"{name} 完成"

    async def main():
        t0 = asyncio.get_event_loop().time()
        # 并发运行 3 个阻塞函数（各自在独立线程里）
        results = await asyncio.gather(
            asyncio.to_thread(blocking_io, "任务A", 0.3),
            asyncio.to_thread(blocking_io, "任务B", 0.2),
            asyncio.to_thread(blocking_io, "任务C", 0.1),
        )
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  结果: {results}")
        print(f"  总耗时: {elapsed:.2f}s（约 0.3s，并发运行）")

    asyncio.run(main())


def demo03_run_in_executor():
    """③ loop.run_in_executor：老式写法（了解即可）

    Python 3.9 以前没有 asyncio.to_thread，用 run_in_executor。
    Python 3.9+ 推荐用 asyncio.to_thread，更简洁。

    run_in_executor(executor, func, *args)
      executor=None  使用默认线程池
      传 ProcessPoolExecutor 可以在进程中运行（适合 CPU 密集）
    """
    print("\n③ run_in_executor（旧写法）")

    def cpu_task(n):
        return sum(range(n))

    async def main():
        loop = asyncio.get_event_loop()

        # 在线程池运行
        result = await loop.run_in_executor(None, cpu_task, 1000000)
        print(f"  线程池结果: {result}")

        # 在进程池运行（CPU 密集）
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, cpu_task, 1000000)
            print(f"  进程池结果: {result}")

    asyncio.run(main())


def demo04_tcp_echo():
    """④ 异步 TCP：本地回声服务器

    asyncio.start_server  启动 TCP 服务器
    asyncio.open_connection 建立 TCP 客户端连接
    StreamReader / StreamWriter 异步读写字节流
    """
    print("\n④ 异步 TCP 回声服务器")

    async def handle_client(reader, writer):
        """处理每个客户端连接"""
        addr = writer.get_extra_info("peername")
        data = await reader.read(100)
        message = data.decode()
        writer.write(f"回声: {message}".encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def client(host, port, message):
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode())
        await writer.drain()
        data = await reader.read(100)
        writer.close()
        await writer.wait_closed()
        return data.decode()

    async def main():
        # 启动服务器
        server = await asyncio.start_server(handle_client, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        print(f"  服务器启动，端口: {port}")

        async with server:
            # 并发发 3 个请求
            results = await asyncio.gather(
                client("127.0.0.1", port, "hello"),
                client("127.0.0.1", port, "world"),
                client("127.0.0.1", port, "asyncio"),
            )
        for r in results:
            print(f"  {r}")

    asyncio.run(main())


if __name__ == "__main__":
    demo01_timeout()
    demo02_to_thread()
    demo03_run_in_executor()
    demo04_tcp_echo()
