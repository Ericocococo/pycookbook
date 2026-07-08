"""multiprocessing —— Queue / Pipe 进程间通信

标准库。Python 3.12。
运行: python 03_queue_pipe.py

进程有独立内存，必须通过 IPC（进程间通信）传递数据：
  Queue  多生产者多消费者，线程/进程安全
  Pipe   两个端点的双向管道，速度比 Queue 快，但只适合两个进程

演示：
  ① Queue：进程间传递数据
  ② Queue 生产者-消费者
  ③ Pipe：双向管道
  ④ Pipe 双向通信
"""
import multiprocessing
import time


def demo01_queue_basic():
    """① multiprocessing.Queue 基础

    multiprocessing.Queue 和 queue.Queue 接口相同，但支持跨进程通信。
    内部通过管道 + 锁实现，进程安全。
    """
    print("① Queue 基础")

    q = multiprocessing.Queue()

    def producer(q):
        for i in range(5):
            q.put(i)
            print(f"  [生产] 放入 {i}")
            time.sleep(0.05)
        q.put(None)   # 结束信号

    def consumer(q):
        while True:
            item = q.get()
            if item is None:
                break
            print(f"  [消费] 取出 {item}")

    p1 = multiprocessing.Process(target=producer, args=(q,))
    p2 = multiprocessing.Process(target=consumer, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def _worker_with_result(task_q, result_q):
    """从任务队列取任务，结果放入结果队列"""
    while True:
        task = task_q.get()
        if task is None:
            break
        result = task ** 2
        result_q.put(result)


def demo02_queue_producer_consumer():
    """② Queue 多进程生产者-消费者"""
    print("\n② Queue 多进程生产者-消费者")

    task_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()
    N_WORKERS = 3

    workers = [multiprocessing.Process(target=_worker_with_result,
                                        args=(task_q, result_q))
               for _ in range(N_WORKERS)]
    for w in workers:
        w.start()

    # 提交任务
    for i in range(9):
        task_q.put(i)
    # 发送结束信号
    for _ in range(N_WORKERS):
        task_q.put(None)

    for w in workers:
        w.join()

    results = []
    while not result_q.empty():
        results.append(result_q.get())
    print("  结果:", sorted(results))


def demo03_pipe_basic():
    """③ Pipe：双向管道

    术语：
      Pipe()  返回 (conn1, conn2) 两个连接端点
      send(obj)  发送对象（内部 pickle 序列化）
      recv()     接收对象（阻塞直到有数据）
      close()    关闭端点

    Pipe 速度比 Queue 快（没有锁开销），但只适合两个进程一对一通信。
    注意：同一端点不能多进程同时读写（不安全），多对多用 Queue。
    """
    print("\n③ Pipe 基础")

    parent_conn, child_conn = multiprocessing.Pipe()

    def child_process(conn):
        msg = conn.recv()
        print(f"  [子进程] 收到: {msg!r}")
        conn.send(f"回复: {msg}")
        conn.close()

    p = multiprocessing.Process(target=child_process, args=(child_conn,))
    p.start()
    child_conn.close()   # 父进程关掉子进程那一端（重要！否则 recv 可能阻塞）

    parent_conn.send("你好，子进程")
    reply = parent_conn.recv()
    print(f"  [父进程] 收到回复: {reply!r}")
    parent_conn.close()
    p.join()


def _ping_pong(conn, name, n):
    """乒乓通信：收到消息后回一条"""
    for i in range(n):
        msg = conn.recv()
        print(f"  [{name}] 收到: {msg}")
        conn.send(f"{name}回应{i}")
    conn.close()


def demo04_pipe_bidirectional():
    """④ Pipe 双向通信

    Pipe 默认双向（duplex=True），两端都可以 send/recv。
    适合实现请求-响应模式。
    """
    print("\n④ Pipe 双向通信")

    conn1, conn2 = multiprocessing.Pipe(duplex=True)

    p = multiprocessing.Process(target=_ping_pong, args=(conn2, "子进程", 3))
    p.start()
    conn2.close()   # 父进程关掉子进程那端

    for i in range(3):
        conn1.send(f"父进程消息{i}")
        reply = conn1.recv()
        print(f"  [父进程] 收到回复: {reply}")

    conn1.close()
    p.join()


if __name__ == "__main__":
    demo01_queue_basic()
    demo02_queue_producer_consumer()
    demo03_pipe_basic()
    demo04_pipe_bidirectional()
