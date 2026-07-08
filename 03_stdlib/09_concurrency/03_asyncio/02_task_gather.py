"""asyncio —— Task 与 gather 并发执行

标准库。Python 3.12。
运行: python 02_task_gather.py

直接 await 协程是顺序执行。
要并发执行多个协程，用 asyncio.gather 或 asyncio.create_task。

演示：
  ① asyncio.gather：并发等待多个协程
  ② asyncio.create_task：后台运行，不立即等待
  ③ gather vs 顺序：速度对比
  ④ 异常处理：gather 的 return_exceptions
  ⑤ asyncio.wait：更精细的控制（超时 / 任意完成）
  ⑥ TaskGroup（Python 3.11+）：结构化并发
"""
import asyncio
import time


async def fetch(url, delay):
    """模拟网络请求"""
    await asyncio.sleep(delay)
    return f"{url} -> {delay}s"


def demo01_gather():
    """① asyncio.gather：并发等待多个协程

    gather(*coros) 同时启动所有协程，等全部完成后返回结果列表。
    总耗时 ≈ 最慢的那个，而不是所有耗时之和。
    结果顺序与传入顺序一致（不是完成顺序）。
    """
    print("① asyncio.gather 并发")

    async def main():
        t0 = asyncio.get_event_loop().time()
        results = await asyncio.gather(
            fetch("url_A", 0.3),
            fetch("url_B", 0.1),
            fetch("url_C", 0.2),
        )
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  结果（按传入顺序）: {results}")
        print(f"  总耗时: {elapsed:.2f}s（约 0.3s，不是 0.6s）")

    asyncio.run(main())


def demo02_create_task():
    """② asyncio.create_task：后台运行

    create_task(coro) 立即将协程包装成 Task 放入事件循环，
    无需 await 它就开始运行（与其他协程并发）。
    Task 有自己的生命周期，可以取消、查询状态。

    术语：
      Task   对协程的包装，是事件循环调度的基本单位
      done() / cancelled() / result() 查询 Task 状态
    """
    print("\n② create_task 后台任务")

    async def main():
        # 立即创建任务（开始运行），主协程继续做别的
        task_a = asyncio.create_task(fetch("A", 0.2), name="task_A")
        task_b = asyncio.create_task(fetch("B", 0.1), name="task_B")

        print(f"  任务已创建，A done={task_a.done()}, B done={task_b.done()}")

        # 主协程做点事
        await asyncio.sleep(0.05)
        print(f"  sleep 0.05 后，B done={task_b.done()}")

        # 等待任务完成并获取结果
        result_a = await task_a
        result_b = await task_b
        print(f"  结果 A: {result_a}")
        print(f"  结果 B: {result_b}")

    asyncio.run(main())


def demo03_gather_vs_sequential():
    """③ gather vs 顺序：速度对比"""
    print("\n③ 并发 vs 顺序速度对比")

    urls = [("url_1", 0.2), ("url_2", 0.2), ("url_3", 0.2), ("url_4", 0.2)]

    async def sequential():
        t0 = asyncio.get_event_loop().time()
        results = []
        for url, delay in urls:
            r = await fetch(url, delay)
            results.append(r)
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  顺序执行: {elapsed:.2f}s（约 0.8s）")

    async def concurrent():
        t0 = asyncio.get_event_loop().time()
        results = await asyncio.gather(*[fetch(url, delay) for url, delay in urls])
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  并发执行: {elapsed:.2f}s（约 0.2s）")

    asyncio.run(sequential())
    asyncio.run(concurrent())


def demo04_gather_exceptions():
    """④ gather 异常处理

    默认情况下，任意一个协程抛异常，gather 立即抛出该异常（其他任务继续运行但结果被丢弃）。
    return_exceptions=True：把异常当作正常结果返回，不中断其他任务。
    """
    print("\n④ gather 异常处理")

    async def bad_fetch(url, delay, fail=False):
        await asyncio.sleep(delay)
        if fail:
            raise ValueError(f"{url} 请求失败")
        return f"{url} 成功"

    async def main():
        # return_exceptions=True：异常作为结果返回，不中断
        results = await asyncio.gather(
            bad_fetch("A", 0.1),
            bad_fetch("B", 0.1, fail=True),
            bad_fetch("C", 0.1),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                print(f"  失败: {r}")
            else:
                print(f"  成功: {r}")

    asyncio.run(main())


def demo05_wait():
    """⑤ asyncio.wait：更精细的控制

    wait(tasks, timeout, return_when) 返回 (done_set, pending_set)。
    return_when 可选：
      ALL_COMPLETED  （默认）全部完成
      FIRST_COMPLETED 任意一个完成就返回
      FIRST_EXCEPTION 任意一个抛异常就返回
    """
    print("\n⑤ asyncio.wait")

    async def main():
        tasks = [
            asyncio.create_task(fetch("fast", 0.1)),
            asyncio.create_task(fetch("slow", 0.4)),
            asyncio.create_task(fetch("mid", 0.2)),
        ]

        # 等待第一个完成即返回
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        print(f"  第一个完成: {[t.result() for t in done]}")
        print(f"  仍在运行: {len(pending)} 个")

        # 取消剩余任务
        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

    asyncio.run(main())


def demo06_task_group():
    """⑥ TaskGroup（Python 3.11+）：结构化并发

    TaskGroup 保证所有任务在 with 块结束时都完成（或被取消）。
    任意一个任务抛异常，组内其他任务自动取消，异常向外传播。
    比 gather 更安全：不会留下"游离的 Task"。
    """
    print("\n⑥ TaskGroup（Python 3.11+）")

    async def main():
        results = []
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(fetch("A", 0.2))
            t2 = tg.create_task(fetch("B", 0.1))
            t3 = tg.create_task(fetch("C", 0.15))
        # with 块结束时，所有任务已完成
        results = [t1.result(), t2.result(), t3.result()]
        print(f"  结果: {results}")

    asyncio.run(main())


if __name__ == "__main__":
    demo01_gather()
    demo02_create_task()
    demo03_gather_vs_sequential()
    demo04_gather_exceptions()
    demo05_wait()
    demo06_task_group()
