"""threading —— Event / Condition / Semaphore 线程同步

标准库。Python 3.12。
运行: python 03_event_condition.py

演示：
  ① Event：一个线程通知另一个线程"某事发生了"
  ② Condition：更精细的通知，配合 wait / notify
  ③ Semaphore：限制同时访问资源的线程数量
  ④ Barrier：等所有线程到达同一个点再一起继续
"""
import threading
import time
import random


def demo01_event():
    """① Event：线程间信号

    术语：
      set()    设置事件（内部标志变为 True），唤醒所有在 wait() 的线程
      clear()  清除事件（内部标志变为 False）
      wait()   阻塞直到事件被 set；可传 timeout 超时返回 False
      is_set() 查询当前状态

    典型用途：一个线程等待另一个线程完成初始化后再启动。
    """
    print("① Event 信号")

    ready = threading.Event()

    def server():
        print("  [服务] 正在初始化...")
        time.sleep(0.3)
        print("  [服务] 初始化完成，发出就绪信号")
        ready.set()

    def client():
        print("  [客户端] 等待服务就绪...")
        ready.wait()          # 阻塞直到 ready.set() 被调用
        print("  [客户端] 服务已就绪，开始请求")

    t1 = threading.Thread(target=server)
    t2 = threading.Thread(target=client)
    t2.start()
    t1.start()
    t1.join()
    t2.join()


def demo02_condition():
    """② Condition：精细通知，配合生产者-消费者

    术语：
      wait()    释放内部锁并阻塞，被 notify 唤醒后重新获取锁
      notify()  唤醒一个在 wait 的线程
      notify_all() 唤醒所有在 wait 的线程

    Condition 内部包含一把 Lock，with cond 先获取锁，
    wait() 释放锁并等待，被唤醒后重新获取锁再继续。
    """
    print("\n② Condition 生产者-消费者")

    items = []
    cond = threading.Condition()
    MAX = 3

    def producer():
        for i in range(6):
            with cond:
                while len(items) >= MAX:
                    print(f"  [生产者] 队列满({len(items)}/{MAX})，等待...")
                    cond.wait()
                items.append(i)
                print(f"  [生产者] 生产 {i}，队列: {items}")
                cond.notify_all()
            time.sleep(0.05)

    def consumer(name):
        for _ in range(3):
            with cond:
                while not items:
                    cond.wait()
                item = items.pop(0)
                print(f"  [{name}] 消费 {item}，队列: {items}")
                cond.notify_all()
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


def demo03_semaphore():
    """③ Semaphore：限制并发数量

    术语：
      Semaphore(n)  内部计数器初始为 n
      acquire()     计数器 -1；为 0 时阻塞等待
      release()     计数器 +1；唤醒一个等待的线程

    典型用途：连接池（限制同时最多 N 个数据库连接）、
             限流（限制同时请求数）。
    """
    print("\n③ Semaphore 限制并发数")

    sem = threading.Semaphore(3)   # 同时最多 3 个线程执行

    def worker(n):
        with sem:
            print(f"  [工人{n}] 开始工作（当前并发受限 ≤3）")
            time.sleep(0.2)
            print(f"  [工人{n}] 完成")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def demo04_barrier():
    """④ Barrier：同步屏障

    术语：
      Barrier(n)  需要 n 个线程全部到达 wait() 才能继续
      wait()      到达屏障并等待；当 n 个线程都到达时，同时释放

    典型用途：并行计算的阶段分隔（所有线程完成第一阶段才进入第二阶段）。
    """
    print("\n④ Barrier 同步屏障")

    N = 4
    barrier = threading.Barrier(N)

    def worker(n):
        delay = random.uniform(0.1, 0.4)
        print(f"  [线程{n}] 第一阶段，耗时 {delay:.2f}s")
        time.sleep(delay)
        print(f"  [线程{n}] 到达屏障，等待其他线程...")
        barrier.wait()           # 等所有 N 个线程都到达
        print(f"  [线程{n}] 全员到齐，开始第二阶段")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    demo01_event()
    demo02_condition()
    demo03_semaphore()
    demo04_barrier()
