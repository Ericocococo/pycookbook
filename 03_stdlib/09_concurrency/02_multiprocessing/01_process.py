"""multiprocessing —— Process 创建与进程隔离

标准库。Python 3.12。
运行: python 01_process.py

线程共享内存，进程拥有独立内存空间。
进程能真正并行利用多核（绕过 GIL），适合 CPU 密集型任务。

Windows 注意：multiprocessing 在 Windows 用 spawn 方式创建进程，
必须在 if __name__ == "__main__": 下启动进程，否则子进程会无限递归导入。

演示：
  ① Process 基础：创建 / start / join
  ② 进程隔离：子进程修改变量不影响父进程
  ③ 传参与返回值
  ④ 进程 ID 与信息
  ⑤ 对比线程：CPU 密集任务下的速度差异
"""
import multiprocessing
import os
import time


def demo01_basic():
    """① Process 基础

    API 和 threading.Thread 几乎相同：
      target  子进程执行的函数
      args    位置参数元组
      start() 启动子进程
      join()  等待子进程结束
    """
    print("① Process 基础")

    def worker(name):
        print(f"  [{name}] PID={os.getpid()}, 开始")
        time.sleep(0.2)
        print(f"  [{name}] 结束")

    p1 = multiprocessing.Process(target=worker, args=("进程A",))
    p2 = multiprocessing.Process(target=worker, args=("进程B",))

    p1.start()
    p2.start()
    print(f"  父进程 PID={os.getpid()}")
    p1.join()
    p2.join()
    print("  所有子进程结束")


def demo02_isolation():
    """② 进程隔离：子进程修改不影响父进程

    线程共享内存，子线程修改变量父线程能看到。
    进程有独立内存，子进程修改变量父进程看不到（彻底隔离）。

    这是进程比线程更安全的原因，也是进程间必须用 Queue/Pipe 通信的原因。
    """
    print("\n② 进程隔离")

    counter = 0   # 父进程的变量

    def modify():
        global counter          # 子进程有自己的 counter 副本
        counter = 9999
        print(f"  [子进程] counter = {counter}（子进程内部）")

    p = multiprocessing.Process(target=modify)
    p.start()
    p.join()
    print(f"  [父进程] counter = {counter}（子进程修改无效，仍是 0）")


def _square(x):
    """计算平方，供 demo03 使用（必须定义在模块级别，Windows 才能 pickle）"""
    return x * x


def demo03_return_value():
    """③ 进程无法直接返回值

    子进程的 return 值父进程拿不到（独立内存）。
    需要通过 multiprocessing.Queue / Pipe / Value 传回结果。
    """
    print("\n③ 返回值（用 Queue 传递）")

    result_q = multiprocessing.Queue()

    def worker(x, q):
        q.put(x * x)

    processes = [multiprocessing.Process(target=worker, args=(i, result_q))
                 for i in range(5)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    results = []
    while not result_q.empty():
        results.append(result_q.get())
    print("  结果:", sorted(results))


def _cpu_task(n):
    """CPU 密集型任务：计算 n 的阶乘，供 demo05 使用"""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def demo04_process_info():
    """④ 进程信息"""
    print("\n④ 进程信息")

    def show_info(name):
        p = multiprocessing.current_process()
        print(f"  [{name}] name={p.name}, pid={p.pid}, ppid={os.getppid()}")

    processes = [multiprocessing.Process(target=show_info, args=(f"子进程{i}",),
                                          name=f"Worker-{i}")
                 for i in range(3)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()


def demo05_vs_thread():
    """⑤ 进程 vs 线程：CPU 密集任务速度对比

    CPU 密集任务：多进程能真正并行（多核），多线程因 GIL 只能单核串行。
    IO 密集任务：多线程够用，进程的启动开销反而是负担。
    """
    print("\n⑤ CPU 密集任务：进程 vs 线程速度对比")
    import threading

    tasks = [500000] * 4

    # 串行
    t0 = time.perf_counter()
    for n in tasks:
        _cpu_task(n)
    serial_time = time.perf_counter() - t0

    # 多线程（GIL 限制，实际串行）
    t0 = time.perf_counter()
    threads = [threading.Thread(target=_cpu_task, args=(n,)) for n in tasks]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    thread_time = time.perf_counter() - t0

    # 多进程（真正并行）
    t0 = time.perf_counter()
    procs = [multiprocessing.Process(target=_cpu_task, args=(n,)) for n in tasks]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    proc_time = time.perf_counter() - t0

    print(f"  串行:   {serial_time:.3f}s")
    print(f"  多线程: {thread_time:.3f}s（GIL 限制，接近串行）")
    print(f"  多进程: {proc_time:.3f}s（多核并行，更快）")


if __name__ == "__main__":
    demo01_basic()
    demo02_isolation()
    demo03_return_value()
    demo04_process_info()
    demo05_vs_thread()
