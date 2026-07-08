"""concurrent.futures —— as_completed / wait / Future 进阶

标准库。Python 3.12。
运行: python 03_as_completed.py

演示：
  ① as_completed：哪个先完成先处理（不等全部完成）
  ② wait：等待指定条件（全部完成 / 任意完成 / 任意异常）
  ③ 超时处理
  ④ 取消 Future
  ⑤ 综合场景：带重试的并发任务
"""
import concurrent.futures
import time
import random


def fetch(url, delay):
    """模拟网络请求"""
    time.sleep(delay)
    return f"{url} ({delay:.2f}s)"


def fetch_with_error(url, delay, fail=False):
    """可能失败的请求"""
    time.sleep(delay)
    if fail:
        raise ConnectionError(f"{url} 连接失败")
    return f"{url} 成功"


def demo01_as_completed():
    """① as_completed：先完成先处理

    executor.map 按提交顺序返回结果（慢任务会阻塞快任务的结果）。
    as_completed 按完成顺序 yield Future，适合"完成一个处理一个"。
    """
    print("① as_completed（完成即处理）")

    urls = [(f"url_{i}", random.uniform(0.1, 0.4)) for i in range(6)]

    print("  [map] 按提交顺序（慢任务阻塞）:")
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        for result in ex.map(fetch, *zip(*urls)):
            print(f"    {result}")
    print(f"  map 总耗时: {time.perf_counter()-t0:.2f}s")

    print("  [as_completed] 按完成顺序（快任务优先）:")
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        future_to_url = {ex.submit(fetch, url, delay): url for url, delay in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            print(f"    {future.result()}")
    print(f"  as_completed 总耗时: {time.perf_counter()-t0:.2f}s")


def demo02_wait():
    """② wait：等待指定条件

    wait(futures, timeout, return_when) 返回 (done, not_done)。
    return_when:
      ALL_COMPLETED    默认，全部完成
      FIRST_COMPLETED  任意一个完成即返回
      FIRST_EXCEPTION  任意一个抛异常即返回
    """
    print("\n② wait 等待条件")

    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        futures = [ex.submit(fetch, f"url_{i}", random.uniform(0.1, 0.5))
                   for i in range(6)]

        # 等第一个完成
        done, not_done = concurrent.futures.wait(
            futures, return_when=concurrent.futures.FIRST_COMPLETED
        )
        print(f"  FIRST_COMPLETED: done={len(done)}, not_done={len(not_done)}")
        print(f"  第一个完成: {list(done)[0].result()}")

        # 等全部完成
        done, _ = concurrent.futures.wait(futures)
        print(f"  ALL_COMPLETED: {len(done)} 个全部完成")


def demo03_timeout():
    """③ 超时处理

    as_completed(futures, timeout)  超时抛 TimeoutError
    future.result(timeout)          单个 Future 超时抛 TimeoutError
    wait(futures, timeout)          超时返回当前已完成集合（不抛异常）
    """
    print("\n③ 超时处理")

    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        futures = [ex.submit(fetch, f"url_{i}", 0.3) for i in range(4)]

        # as_completed 超时：只处理超时前完成的
        print("  as_completed timeout=0.15（只处理已完成的）:")
        try:
            for f in concurrent.futures.as_completed(futures, timeout=0.15):
                print(f"    {f.result()}")
        except concurrent.futures.TimeoutError:
            print("    超时，还有任务未完成")

        # 等剩余任务
        concurrent.futures.wait(futures)


def demo04_cancel():
    """④ 取消 Future

    future.cancel() 只能取消还未开始的任务（在队列里等待的）。
    已经开始执行的任务无法取消。
    """
    print("\n④ 取消 Future")

    # 提交 10 个任务，线程池只有 2 个线程，后面的任务在排队
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(fetch, f"url_{i}", 0.2) for i in range(8)]

        # 尝试取消后面的任务
        cancelled = 0
        for f in futures[2:]:    # 前 2 个已在执行，后面的在排队
            if f.cancel():
                cancelled += 1

        print(f"  成功取消 {cancelled} 个任务（未开始的才能取消）")
        done = [f for f in futures if f.done() and not f.cancelled()]
        print(f"  完成执行的: {len(done)} 个")


def demo05_retry():
    """⑤ 综合场景：带重试的并发任务"""
    print("\n⑤ 带重试的并发任务")

    MAX_RETRY = 2

    def fetch_with_retry(url):
        for attempt in range(MAX_RETRY + 1):
            try:
                delay = random.uniform(0.1, 0.3)
                fail = random.random() < 0.4   # 40% 失败概率
                return fetch_with_error(url, delay, fail)
            except ConnectionError as e:
                if attempt == MAX_RETRY:
                    return f"{url} 最终失败: {e}"
                time.sleep(0.05)   # 重试前等待

    urls = [f"api_{i}" for i in range(8)]

    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        results = list(ex.map(fetch_with_retry, urls))

    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    demo01_as_completed()
    demo02_wait()
    demo03_timeout()
    demo04_cancel()
    demo05_retry()
