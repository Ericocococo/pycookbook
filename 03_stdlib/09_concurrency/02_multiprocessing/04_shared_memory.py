"""multiprocessing —— 共享内存：Value / Array / Manager

标准库。Python 3.12。
运行: python 04_shared_memory.py

进程默认内存隔离。需要共享状态时有三种方案：
  Value / Array   低级共享内存，速度快，只支持简单类型
  Manager         高级，支持 list/dict/Queue 等，但有网络序列化开销
  SharedMemory    Python 3.8+，原始字节共享，最高效（配合 numpy 使用）

演示：
  ① Value：共享单个数值
  ② Array：共享数组
  ③ Manager：共享 list / dict
  ④ 共享内存注意：加锁保护
"""
import multiprocessing
import ctypes
import time


def _increment_value(val, lock, n):
    """给共享 Value 加 n 次 1，供演示用"""
    for _ in range(n):
        with lock:
            val.value += 1


def demo01_value():
    """① Value：共享单个数值

    术语：
      Value(typecode, init)  创建共享数值
        typecode  C 类型代码：'i'=int, 'd'=double, 'b'=byte...
        init      初始值
      val.value   读写共享值

    不加锁时有竞态条件（和线程一样）。
    Value 内置了一把 Lock：val.get_lock()，也可以传自己的 lock。
    """
    print("① Value 共享数值")

    # 不加锁（可能出现竞态条件）
    val = multiprocessing.Value('i', 0)
    procs = [multiprocessing.Process(target=lambda: [setattr(val, 'value', val.value + 1) for _ in range(1000)])
             for _ in range(4)]
    # 实际上 lambda 和 setattr 方式在这里有点复杂，改用函数

    def unsafe_inc(v):
        for _ in range(1000):
            v.value += 1

    val2 = multiprocessing.Value('i', 0)
    procs = [multiprocessing.Process(target=unsafe_inc, args=(val2,)) for _ in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print(f"  不加锁，期望 4000，实际: {val2.value}（可能小于期望）")

    # 加锁
    val3 = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()
    procs = [multiprocessing.Process(target=_increment_value, args=(val3, lock, 1000))
             for _ in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print(f"  加锁后，期望 4000，实际: {val3.value}")


def _fill_array(arr, start, val):
    """填充数组，供演示用"""
    for i in range(start, start + 3):
        arr[i] = val


def demo02_array():
    """② Array：共享数组

    Array(typecode, size_or_init) 创建共享数组。
    可以像列表一样用下标访问，支持切片。
    """
    print("\n② Array 共享数组")

    arr = multiprocessing.Array('i', 6)   # 6个整数的共享数组，初始为 0

    procs = [
        multiprocessing.Process(target=_fill_array, args=(arr, 0, 111)),
        multiprocessing.Process(target=_fill_array, args=(arr, 3, 222)),
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    print(f"  共享数组: {list(arr)}")   # [111, 111, 111, 222, 222, 222]


def _append_to_list(lst, value):
    """向 Manager list 追加元素"""
    lst.append(value)
    time.sleep(0.01)


def _update_dict(d, key, value):
    """向 Manager dict 写入键值"""
    d[key] = value


def demo03_manager():
    """③ Manager：支持高级数据结构

    Manager 启动一个单独的管理进程，其他进程通过代理对象操作。
    支持：list、dict、Queue、Lock、Event、Semaphore、Value、Array、Namespace

    优点：支持复杂数据结构，API 友好
    缺点：每次操作都要跨进程序列化，比 Value/Array 慢
    """
    print("\n③ Manager 共享 list / dict")

    with multiprocessing.Manager() as manager:
        # 共享 list
        shared_list = manager.list()
        procs = [multiprocessing.Process(target=_append_to_list, args=(shared_list, i))
                 for i in range(5)]
        for p in procs:
            p.start()
        for p in procs:
            p.join()
        print(f"  共享 list: {sorted(shared_list)}")

        # 共享 dict
        shared_dict = manager.dict()
        procs = [multiprocessing.Process(target=_update_dict, args=(shared_dict, f"key{i}", i * 10))
                 for i in range(4)]
        for p in procs:
            p.start()
        for p in procs:
            p.join()
        print(f"  共享 dict: {dict(shared_dict)}")


def demo04_shared_memory_raw():
    """④ SharedMemory（Python 3.8+）：原始共享内存块

    最高效的共享方式，直接操作字节，适合配合 numpy 数组使用。
    不会自动序列化，需要手动处理数据格式。
    """
    print("\n④ SharedMemory 原始共享内存")

    from multiprocessing import shared_memory
    import struct

    # 创建 4 个 int（每个 4 字节）的共享内存块
    shm = shared_memory.SharedMemory(create=True, size=4 * 4)

    def writer(shm_name):
        shm = shared_memory.SharedMemory(name=shm_name)
        for i in range(4):
            struct.pack_into('i', shm.buf, i * 4, (i + 1) * 100)
        shm.close()

    p = multiprocessing.Process(target=writer, args=(shm.name,))
    p.start()
    p.join()

    # 父进程读取
    values = [struct.unpack_from('i', shm.buf, i * 4)[0] for i in range(4)]
    print(f"  SharedMemory 读取: {values}")   # [100, 200, 300, 400]

    shm.close()
    shm.unlink()   # 必须显式释放


if __name__ == "__main__":
    demo01_value()
    demo02_array()
    demo03_manager()
    demo04_shared_memory_raw()
