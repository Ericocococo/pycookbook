"""concurrent.futures —— ProcessPoolExecutor

标准库。Python 3.12。
运行: python 02_process_pool.py

ProcessPoolExecutor 与 ThreadPoolExecutor 接口完全相同，
区别是任务在独立进程中执行，可以真正利用多核。

适合：CPU 密集型任务（数值计算、图像处理、加密等）。
注意：
  - 函数和参数必须可 pickle（不能是 lambda、嵌套函数）
  - Windows 必须在 if __name__ == "__main__": 下运行
  - 进程启动有开销，任务太轻反而比线程慢

演示：
  ① 基础用法（与 ThreadPoolExecutor 对比）
  ② CPU 密集任务加速效果
  ③ 不可 pickle 的坑
  ④ initializer：进程初始化钩子
"""
import concurrent.futures
import time
import math


def is_prime(n):
    """判断是否是质数（CPU 密集）"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def count_primes(limit):
    """统计 [2, limit] 内的质数个数"""
    return sum(1 for n in range(2, limit) if is_prime(n))


def demo01_basic():
    """① 基础用法：和 ThreadPoolExecutor 接口完全相同"""
    print("① ProcessPoolExecutor 基础")

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(count_primes, 10000) for _ in range(4)]
        results = [f.result() for f in futures]
    print(f"  每段 [2,10000) 的质数数: {results}")
    print(f"  （都是 {results[0]}，四个进程各自独立计算）")


def demo02_speedup():
    """② CPU 密集任务：进程池 vs 线程池 vs 串行

    CPU 密集任务：
      - 串行：单核，一个接一个
      - 线程池：多线程，但 GIL 限制，实际还是单核串行
      - 进程池：多进程，真正多核并行，速度提升明显
    """
    print("\n② CPU 密集加速效果对比")

    tasks = [500000] * 4   # 4 个相同任务

    # 串行
    t0 = time.perf_counter()
    for n in tasks:
        count_primes(n)
    serial_t = time.perf_counter() - t0

    # 线程池（GIL 限制，实际和串行差不多）
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        list(ex.map(count_primes, tasks))
    thread_t = time.perf_counter() - t0

    # 进程池（真正并行）
    t0 = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(4) as ex:
        list(ex.map(count_primes, tasks))
    proc_t = time.perf_counter() - t0

    print(f"  串行:   {serial_t:.2f}s")
    print(f"  线程池: {thread_t:.2f}s（GIL 限制，接近串行）")
    print(f"  进程池: {proc_t:.2f}s（多核并行，约 {serial_t/proc_t:.1f}x 加速）")


def demo03_pickle_constraint():
    """③ 可 pickle 约束

    ProcessPoolExecutor 用 pickle 把函数和参数传给子进程。
    以下类型不可 pickle，会报 PicklingError：
      - lambda 函数
      - 嵌套（局部）函数
      - 未绑定的方法（在某些情况下）

    解决方案：把函数定义在模块级别（文件顶层）。
    """
    print("\n③ pickle 约束")

    # 正常：模块级函数可以 pickle
    with concurrent.futures.ProcessPoolExecutor(2) as ex:
        results = list(ex.map(count_primes, [10000, 20000]))
    print(f"  模块级函数正常: {results}")

    # 不行：lambda 不可 pickle
    try:
        with concurrent.futures.ProcessPoolExecutor(2) as ex:
            f = ex.submit(lambda x: x * x, 5)   # lambda 不可 pickle
            f.result()
    except Exception as e:
        print(f"  lambda 提交失败: {type(e).__name__}: {e}")


_worker_state = None   # 进程级全局变量


def _init_worker(state):
    """进程初始化函数，每个工作进程启动时调用一次"""
    global _worker_state
    _worker_state = state
    print(f"  [初始化] 进程已初始化，state={state!r}")


def _task_with_state(x):
    """使用进程级状态的任务"""
    return x * _worker_state


def demo04_initializer():
    """④ initializer：进程初始化钩子

    ProcessPoolExecutor(initializer=fn, initargs=(args,))
    每个工作进程启动时调用一次 initializer，
    适合：建立数据库连接、加载模型、初始化昂贵资源。
    """
    print("\n④ initializer 进程初始化")

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=2,
        initializer=_init_worker,
        initargs=("已初始化",),
    ) as ex:
        results = list(ex.map(_task_with_state, [1, 2, 3, 4]))
    print(f"  结果: {results}")


if __name__ == "__main__":
    demo01_basic()
    demo02_speedup()
    demo03_pickle_constraint()
    demo04_initializer()
