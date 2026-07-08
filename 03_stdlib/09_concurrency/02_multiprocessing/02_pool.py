"""multiprocessing —— Pool 进程池

标准库。Python 3.12。
运行: python 02_pool.py

Pool 管理一组工作进程，避免频繁创建/销毁进程的开销。
把任务分发给工作进程，收集结果。

演示：
  ① map：最常用，把函数映射到列表
  ② starmap：多参数版 map
  ③ apply_async：异步提交单个任务，不阻塞
  ④ imap / imap_unordered：惰性版 map，适合大数据
  ⑤ 进程池上下文管理器（with Pool）
"""
import multiprocessing
import time


def square(x):
    """计算平方（必须在模块级定义，Pool 需要 pickle 传给子进程）"""
    return x * x


def slow_square(x):
    """慢速平方，模拟耗时任务"""
    time.sleep(0.1)
    return x * x


def add(x, y):
    """两数相加，供 starmap 演示"""
    return x + y


def demo01_map():
    """① Pool.map：最常用，同步阻塞直到所有结果返回

    map(func, iterable) 等价于 list(map(func, iterable))，
    但任务分发给多个进程并行执行，最后按原顺序返回结果列表。
    """
    print("① Pool.map")

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(square, range(10))
    print("  结果:", results)

    # 对比串行速度（slow_square 每次 sleep 0.1s）
    tasks = list(range(8))

    t0 = time.perf_counter()
    serial = [slow_square(x) for x in tasks]
    serial_t = time.perf_counter() - t0

    t0 = time.perf_counter()
    with multiprocessing.Pool(4) as pool:
        parallel = pool.map(slow_square, tasks)
    parallel_t = time.perf_counter() - t0

    print(f"  串行 {len(tasks)} 个任务: {serial_t:.2f}s")
    print(f"  进程池({4}个) {len(tasks)} 个任务: {parallel_t:.2f}s")


def demo02_starmap():
    """② Pool.starmap：多参数版 map

    map 只支持单参数函数（iterable 的每个元素作为唯一参数）。
    starmap 接受参数元组列表，把元组解包传给函数。
    """
    print("\n② Pool.starmap（多参数）")

    args = [(1, 2), (3, 4), (5, 6), (7, 8)]
    with multiprocessing.Pool(4) as pool:
        results = pool.starmap(add, args)
    print("  结果:", results)   # [3, 7, 11, 15]


def demo03_apply_async():
    """③ apply_async：异步提交，不阻塞

    apply_async 立即返回 AsyncResult 对象，不等任务完成。
    通过 AsyncResult.get() 获取结果（会阻塞直到结果就绪）。

    适合：提交任务后主进程继续做别的事，最后统一收结果。
    """
    print("\n③ apply_async 异步提交")

    with multiprocessing.Pool(4) as pool:
        # 提交所有任务（不阻塞）
        async_results = [pool.apply_async(slow_square, (x,)) for x in range(6)]

        print("  任务已提交，主进程继续做别的事...")
        time.sleep(0.05)
        print("  主进程做完了，现在收结果")

        # 收结果（每个 get() 等待对应任务完成）
        results = [ar.get(timeout=2) for ar in async_results]

    print("  结果:", results)

    # 回调函数：任务完成时自动调用
    collected = []
    with multiprocessing.Pool(4) as pool:
        for x in range(4):
            pool.apply_async(square, (x,), callback=collected.append)
        pool.close()
        pool.join()   # 等所有异步任务完成
    print("  回调收集:", sorted(collected))


def demo04_imap():
    """④ imap / imap_unordered：惰性版 map

    map 把所有结果放内存再返回列表。
    imap 返回迭代器，每有结果就 yield，适合处理大量任务。
    imap_unordered 不保证顺序，哪个先完成先 yield，延迟更低。
    """
    print("\n④ imap / imap_unordered")

    with multiprocessing.Pool(4) as pool:
        # imap：保持顺序，惰性返回
        print("  imap（保序）:", end=" ")
        for result in pool.imap(square, range(6)):
            print(result, end=" ")
        print()

        # imap_unordered：不保序，先完成先返回
        print("  imap_unordered（不保序）:", end=" ")
        for result in pool.imap_unordered(slow_square, range(6)):
            print(result, end=" ")
        print()


def demo05_context_manager():
    """⑤ with Pool：推荐写法

    with 块结束时自动调用 terminate()，清理工作进程。
    手动管理时需要 pool.close() + pool.join()：
      close()     不再接受新任务
      join()      等待所有已提交任务完成（必须在 close 后调用）
      terminate() 立即终止所有工作进程（强制）
    """
    print("\n⑤ with Pool 上下文管理器")

    # 推荐：with 语句
    with multiprocessing.Pool(2) as pool:
        result = pool.map(square, [1, 2, 3])
    print("  with Pool 结果:", result)

    # 手动管理（等价）
    pool = multiprocessing.Pool(2)
    try:
        result = pool.map(square, [4, 5, 6])
        print("  手动管理结果:", result)
    finally:
        pool.close()
        pool.join()


if __name__ == "__main__":
    demo01_map()
    demo02_starmap()
    demo03_apply_async()
    demo04_imap()
    demo05_context_manager()
