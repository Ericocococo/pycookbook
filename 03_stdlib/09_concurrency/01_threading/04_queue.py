"""threading —— Queue 线程安全队列

标准库。Python 3.12。
运行: python 04_queue.py

queue.Queue 是线程安全的 FIFO 队列，内部封装了 Lock + Condition，
是多线程间传递数据的推荐方式，比手动 Lock 更简单安全。

演示：
  ① Queue 基础：put / get / qsize / empty
  ② 生产者-消费者模式（最常见用法）
  ③ 任务完成通知：task_done / join
  ④ 其他队列：LifoQueue（栈）/ PriorityQueue（优先级）
  ⑤ 实际场景：线程池手动实现（Worker + Queue）
"""
import queue
import threading
import time
import random


def demo01_basic():
    """① Queue 基础

    术语：
      put(item)        放入元素；队列满时阻塞（默认无上限）
      put_nowait(item) 队列满时立刻抛 queue.Full
      get()            取出元素；队列空时阻塞
      get_nowait()     队列空时立刻抛 queue.Empty
      qsize()          当前元素数（不精确，仅供参考）
      empty() / full() 队列是否空/满
    """
    print("① Queue 基础")

    q = queue.Queue(maxsize=3)   # 最大容量 3

    q.put("A")
    q.put("B")
    q.put("C")
    print(f"  队列满: {q.full()}, 大小: {q.qsize()}")

    # put_nowait 队列满时抛 Full
    try:
        q.put_nowait("D")
    except queue.Full:
        print("  队列已满，put_nowait 抛 Full")

    print(f"  get: {q.get()}")
    print(f"  get: {q.get()}")
    print(f"  剩余: {q.qsize()}")


def demo02_producer_consumer():
    """② 生产者-消费者模式

    生产者往队列放任务，消费者从队列取任务。
    Queue 负责线程同步，生产者和消费者不需要手动加锁。

    用 None 作为"毒丸（poison pill）"信号通知消费者退出。
    """
    print("\n② 生产者-消费者")

    q = queue.Queue(maxsize=5)
    CONSUMERS = 2

    def producer():
        for i in range(8):
            q.put(i)
            print(f"  [生产] 生产任务 {i}，队列大小: {q.qsize()}")
            time.sleep(0.05)
        # 每个消费者发一个毒丸
        for _ in range(CONSUMERS):
            q.put(None)

    def consumer(name):
        while True:
            item = q.get()
            if item is None:        # 收到毒丸，退出
                print(f"  [{name}] 收到退出信号")
                break
            print(f"  [{name}] 处理任务 {item}")
            time.sleep(0.1)

    threads = [
        threading.Thread(target=producer),
        threading.Thread(target=consumer, args=("消费者A",)),
        threading.Thread(target=consumer, args=("消费者B",)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def demo03_task_done():
    """③ task_done / join：等待所有任务处理完

    q.join()     阻塞，直到队列里每个 item 都调用了 task_done()
    task_done()  通知队列"这个 item 已处理完"

    对比 join(timeout)：Thread.join 等线程结束，Queue.join 等任务处理完。
    """
    print("\n③ task_done / join")

    q = queue.Queue()

    def worker():
        while True:
            item = q.get()
            if item is None:
                q.task_done()
                break
            time.sleep(0.05)
            print(f"  处理完成: {item}")
            q.task_done()    # 必须调用，否则 q.join() 永远阻塞

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    for i in range(5):
        q.put(i)
    q.put(None)     # 停止信号

    q.join()        # 等所有任务 task_done
    print("  所有任务已处理完毕")


def demo04_other_queues():
    """④ LifoQueue（后进先出）/ PriorityQueue（优先级队列）

    LifoQueue     栈结构，最后放入的最先取出
    PriorityQueue 优先级最小的最先取出（最小堆）
                  put((priority, item))，priority 越小越先出
    """
    print("\n④ 其他队列类型")

    # LifoQueue（栈）
    lifo = queue.LifoQueue()
    for i in [1, 2, 3]:
        lifo.put(i)
    print("  LifoQueue（后进先出）:", [lifo.get() for _ in range(3)])

    # PriorityQueue
    pq = queue.PriorityQueue()
    pq.put((3, "低优先级"))
    pq.put((1, "高优先级"))
    pq.put((2, "中优先级"))
    print("  PriorityQueue（优先级出队）:")
    while not pq.empty():
        priority, item = pq.get()
        print(f"    优先级={priority}: {item}")


def demo05_worker_pool():
    """⑤ 实际场景：用 Queue 实现简单线程池

    固定数量的 Worker 线程持续从队列取任务，主线程往队列放任务。
    这是 concurrent.futures.ThreadPoolExecutor 的简化版原理。
    """
    print("\n⑤ 简单线程池（Queue 实现）")

    task_q = queue.Queue()
    result_q = queue.Queue()
    N_WORKERS = 3

    def worker(wid):
        while True:
            task = task_q.get()
            if task is None:
                task_q.task_done()
                break
            # 模拟处理
            result = task ** 2
            result_q.put((task, result))
            task_q.task_done()

    # 启动工人
    workers = [threading.Thread(target=worker, args=(i,), daemon=True)
               for i in range(N_WORKERS)]
    for w in workers:
        w.start()

    # 提交任务
    for task in range(1, 9):
        task_q.put(task)
    for _ in range(N_WORKERS):
        task_q.put(None)   # 停止信号

    task_q.join()

    # 收结果
    results = []
    while not result_q.empty():
        results.append(result_q.get())
    print("  结果:", sorted(results))


if __name__ == "__main__":
    demo01_basic()
    demo02_producer_consumer()
    demo03_task_done()
    demo04_other_queues()
    demo05_worker_pool()
