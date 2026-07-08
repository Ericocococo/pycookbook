"""threading —— Lock / RLock / 竞态条件

标准库。Python 3.12。
运行: python 02_lock.py

演示：
  ① 竞态条件：不加锁时的错误结果
  ② Lock：互斥锁，保护共享数据
  ③ with Lock：推荐写法，自动释放
  ④ RLock：可重入锁，同一线程可以多次获取
  ⑤ 死锁演示与规避
"""
import threading
import time


def demo01_race_condition():
    """① 竞态条件（Race Condition）

    术语：
      竞态条件  多线程同时读写共享变量，结果依赖线程执行顺序，
               每次运行可能得到不同结果。

    counter += 1 在 CPU 层面是三步：读取 → 加1 → 写回
    两个线程可能同时读到同一个旧值，最终只加了一次。
    """
    print("① 竞态条件（不加锁）")

    counter = 0

    def increment():
        nonlocal counter
        for _ in range(10000):
            counter += 1     # 非原子操作，多线程下不安全

    threads = [threading.Thread(target=increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"  期望: 50000，实际: {counter}（可能小于期望，说明有丢失）")


def demo02_lock():
    """② Lock：互斥锁

    术语：
      acquire()  获取锁；若锁已被其他线程持有则阻塞等待
      release()  释放锁；必须和 acquire 配对，否则其他线程永远拿不到锁
      互斥        同一时刻只有一个线程能持有锁
    """
    print("\n② Lock 保护共享数据")

    counter = 0
    lock = threading.Lock()

    def increment():
        nonlocal counter
        for _ in range(10000):
            lock.acquire()
            counter += 1     # 临界区：只有一个线程能同时执行这里
            lock.release()

    threads = [threading.Thread(target=increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"  期望: 50000，实际: {counter}（加锁后结果正确）")


def demo03_with_lock():
    """③ with Lock：推荐写法

    with lock 等价于 acquire() + try/finally release()。
    即使临界区抛异常，锁也会被正确释放，不会死锁。
    """
    print("\n③ with Lock（推荐写法）")

    counter = 0
    lock = threading.Lock()

    def increment():
        nonlocal counter
        for _ in range(10000):
            with lock:          # 自动 acquire + release，异常安全
                counter += 1

    threads = [threading.Thread(target=increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"  结果: {counter}")

    # 实际场景：线程安全的计数器类
    class SafeCounter:
        def __init__(self):
            self._value = 0
            self._lock = threading.Lock()

        def increment(self):
            with self._lock:
                self._value += 1

        @property
        def value(self):
            with self._lock:
                return self._value

    sc = SafeCounter()
    ts = [threading.Thread(target=sc.increment) for _ in range(1000)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    print(f"  SafeCounter 结果: {sc.value}（期望 1000）")


def demo04_rlock():
    """④ RLock：可重入锁

    普通 Lock 不可重入：同一线程再次 acquire 同一个 Lock 会死锁。
    RLock 可重入：同一线程可以多次 acquire，每次 acquire 对应一次 release。

    适合：递归函数、方法之间相互调用但都需要锁保护时。
    """
    print("\n④ RLock 可重入锁")

    rlock = threading.RLock()

    def outer():
        with rlock:          # 第一次获取
            print("  outer: 获取锁")
            inner()          # 调用也需要同一把锁的函数
            print("  outer: 释放锁")

    def inner():
        with rlock:          # 同一线程再次获取，RLock 允许，普通 Lock 会死锁
            print("  inner: 再次获取同一把锁（RLock 允许）")

    t = threading.Thread(target=outer)
    t.start()
    t.join()


def demo05_deadlock():
    """⑤ 死锁演示与规避

    死锁：线程 A 持有锁1，等锁2；线程 B 持有锁2，等锁1。
    双方都在等对方释放，永远卡住。

    规避方法：
      1. 固定加锁顺序（所有线程按相同顺序获取多把锁）
      2. 使用 lock.acquire(timeout=N)，超时放弃
      3. 尽量减少持锁范围，不在持锁期间等待另一个锁
    """
    print("\n⑤ 死锁规避（超时版）")

    lock1 = threading.Lock()
    lock2 = threading.Lock()

    def task_a():
        with lock1:
            time.sleep(0.05)
            # 用 timeout 避免无限等待
            got = lock2.acquire(timeout=0.2)
            if got:
                print("  A: 获取 lock1 + lock2，完成")
                lock2.release()
            else:
                print("  A: 等待 lock2 超时，放弃（避免死锁）")

    def task_b():
        with lock2:
            time.sleep(0.05)
            got = lock1.acquire(timeout=0.2)
            if got:
                print("  B: 获取 lock2 + lock1，完成")
                lock1.release()
            else:
                print("  B: 等待 lock1 超时，放弃（避免死锁）")

    t1 = threading.Thread(target=task_a)
    t2 = threading.Thread(target=task_b)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("  （规避死锁：超时后主动放弃，而非永远等待）")


if __name__ == "__main__":
    demo01_race_condition()
    demo02_lock()
    demo03_with_lock()
    demo04_rlock()
    demo05_deadlock()
