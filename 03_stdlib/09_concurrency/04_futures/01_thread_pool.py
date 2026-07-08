"""concurrent.futures —— ThreadPoolExecutor

标准库。Python 3.12。
运行: python 01_thread_pool.py

concurrent.futures 是线程池和进程池的高层封装：
  ThreadPoolExecutor  线程池，适合 IO 密集任务
  ProcessPoolExecutor 进程池，适合 CPU 密集任务
  两者接口完全相同，切换只需改一行

演示：
  ① submit：提交单个任务，返回 Future
  ② map：批量提交，按顺序返回结果
  ③ Future 对象：result / done / cancel / add_done_callback
  ④ 上下文管理器：with ThreadPoolExecutor
  ⑤ 实际场景：并发下载（模拟）
"""
import concurrent.futures
import time
import threading


def fetch(url, delay=0.2):
    """模拟网络请求（阻塞 IO）"""
    time.sleep(delay)
    return f"{url} -> {threading.current_thread().name}"


def demo01_submit():
    """① submit：提交单个任务，立即返回 Future

    术语：
      Future  代表"未来某个时刻的结果"，是异步计算的占位符
      submit(fn, *args, **kwargs) 把任务交给线程池，立即返回 Future（非阻塞）
      future.result(timeout)       阻塞等待结果；超时抛 TimeoutError
    """
    print("① submit + Future")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务，立即返回 Future（任务已在后台运行）
        f1 = executor.submit(fetch, "url_A", 0.2)
        f2 = executor.submit(fetch, "url_B", 0.1)
        f3 = executor.submit(fetch, "url_C", 0.3)

        print(f"  任务已提交，f1 done={f1.done()}")

        # 获取结果（阻塞直到该任务完成）
        print(f"  f2 结果: {f2.result()}")    # B 先完成
        print(f"  f1 结果: {f1.result()}")
        print(f"  f3 结果: {f3.result()}")


def demo02_map():
    """② executor.map：批量提交，按顺序返回

    map(fn, iterable) 等价于 list(map(fn, iterable))，
    但在线程池里并行执行，结果按输入顺序返回（不是完成顺序）。
    """
    print("\n② executor.map")

    urls = [f"url_{i}" for i in range(6)]

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch, urls))
    elapsed = time.perf_counter() - t0

    print(f"  结果: {results}")
    print(f"  耗时: {elapsed:.2f}s（6个任务，4个并发，约 0.4s）")


def demo03_future_api():
    """③ Future 对象完整 API

    done()          是否已完成（完成/异常/取消）
    running()       是否正在运行
    cancelled()     是否已取消
    result(timeout) 获取结果；抛出执行中的异常
    exception()     获取执行中的异常（无异常返回 None）
    cancel()        尝试取消（已开始执行的无法取消）
    add_done_callback(fn)  完成时自动回调
    """
    print("\n③ Future API")

    def bad_task():
        raise ValueError("任务失败了")

    with concurrent.futures.ThreadPoolExecutor(1) as executor:
        # 正常任务
        f = executor.submit(fetch, "url_X", 0.1)
        f.add_done_callback(lambda fut: print(f"  [回调] 完成: {fut.result()}"))
        time.sleep(0.15)
        print(f"  f.done()={f.done()}, f.result()={f.result()}")

        # 异常任务
        f_bad = executor.submit(bad_task)
        try:
            f_bad.result()
        except ValueError as e:
            print(f"  异常任务: {e}")
        print(f"  f_bad.exception(): {f_bad.exception()}")


def demo04_context_manager():
    """④ with ThreadPoolExecutor：推荐写法

    with 块结束时自动 shutdown(wait=True)：
      等待所有已提交任务完成，再关闭线程池。
    手动控制时用 executor.shutdown(wait=True/False)。
    """
    print("\n④ with 上下文管理器")

    # max_workers：线程数，默认 min(32, cpu_count+4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(fetch, f"url_{i}") for i in range(4)]
    # with 块结束，所有任务已完成
    print("  所有任务完成:", [f.result() for f in futures])


def demo05_practical():
    """⑤ 实际场景：并发请求多个 URL"""
    print("\n⑤ 并发请求（模拟）")

    import random
    urls = {f"https://api.example.com/data/{i}": random.uniform(0.1, 0.4)
            for i in range(8)}

    t0 = time.perf_counter()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(fetch, url, delay): url
                         for url, delay in urls.items()}
        # as_completed：哪个先完成先处理（见 03_as_completed.py）
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            results[url] = future.result()

    elapsed = time.perf_counter() - t0
    print(f"  完成 {len(results)} 个请求，耗时 {elapsed:.2f}s")


if __name__ == "__main__":
    demo01_submit()
    demo02_map()
    demo03_future_api()
    demo04_context_manager()
    demo05_practical()
