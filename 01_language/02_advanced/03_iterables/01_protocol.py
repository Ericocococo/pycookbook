"""迭代协议 —— Iterable / Iterator / __iter__ / __next__

Python 3.12。
运行: python 01_protocol.py

for 循环的本质是两次协议调用：
  1. iter(obj)  → 调用 obj.__iter__()，得到迭代器
  2. next(it)   → 重复调用 it.__next__()，直到 StopIteration

演示：
  ① for 循环等价展开（手动 iter/next）
  ② 手写迭代器类（__iter__ + __next__）
  ③ 可迭代对象 vs 迭代器的区别
  ④ 用 collections.abc 做类型检查
  ⑤ 实际场景：分块读取大文件
"""

import collections.abc


# ---------------------------------------------------------------------------
# ① for 循环等价展开
# ---------------------------------------------------------------------------

def demo01_for_equivalent():
    """① for 的本质：iter() + next() 循环"""
    print("① for 循环等价展开")

    data = [10, 20, 30]

    # Python 实际执行的等价逻辑
    it = iter(data)                      # 调用 data.__iter__()
    while True:
        try:
            item = next(it)              # 调用 it.__next__()
            print(f"  item: {item}")
        except StopIteration:
            break                        # 生成完毕，退出循环


# ---------------------------------------------------------------------------
# ② 手写迭代器类
# ---------------------------------------------------------------------------

class CountDown:
    """从 n 倒数到 1 的迭代器。

    同一个对象既是 Iterable 也是 Iterator——__iter__ 返回 self。
    """

    def __init__(self, n: int):
        self.n = n
        self._current = n

    def __iter__(self):
        # 迭代器的 __iter__ 惯例返回 self
        return self

    def __next__(self) -> int:
        if self._current <= 0:
            raise StopIteration          # 发出"结束"信号
        value = self._current
        self._current -= 1
        return value


def demo02_custom_iterator():
    """② 手写迭代器类：CountDown"""
    print("\n② 手写迭代器 CountDown")

    cd = CountDown(5)
    for n in cd:
        print(f"  {n}")

    # 迭代器只能走一遍——消耗完后再迭代什么都没有
    print("  再次迭代（已耗尽）:", list(CountDown(3).__iter__().__iter__()))
    cd2 = CountDown(3)
    list(cd2)                            # 耗尽
    print("  耗尽后 list():", list(cd2))


# ---------------------------------------------------------------------------
# ③ Iterable vs Iterator
# ---------------------------------------------------------------------------

class NumberRange:
    """可迭代对象（Iterable），但自身不是迭代器。

    __iter__ 每次返回一个新迭代器，因此可以多次 for 循环。
    """

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def __iter__(self):
        # 每次调用都创建新的迭代器对象
        return RangeIterator(self.start, self.stop)


class RangeIterator:
    """NumberRange 的迭代器（有状态，一次性）。"""

    def __init__(self, start: int, stop: int):
        self._current = start
        self._stop = stop

    def __iter__(self):
        return self                      # 迭代器自身也是可迭代的（规范要求）

    def __next__(self) -> int:
        if self._current >= self._stop:
            raise StopIteration
        value = self._current
        self._current += 1
        return value


def demo03_iterable_vs_iterator():
    """③ Iterable vs Iterator：可迭代对象可反复消费，迭代器只能走一遍"""
    print("\n③ Iterable vs Iterator")

    r = NumberRange(1, 4)

    print("  第一次 for:", list(r))     # [1, 2, 3]
    print("  第二次 for:", list(r))     # [1, 2, 3]，因为 __iter__ 返回新迭代器

    it = iter(r)                         # 拿出一个迭代器
    print("  迭代器 next():", next(it), next(it))
    list(it)                             # 耗尽
    print("  耗尽后 next():", end=" ")
    try:
        next(it)
    except StopIteration:
        print("StopIteration")


# ---------------------------------------------------------------------------
# ④ collections.abc 类型检查
# ---------------------------------------------------------------------------

def demo04_abc_check():
    """④ 用 collections.abc 检查是否满足协议"""
    print("\n④ collections.abc 类型检查")

    objects = {
        "list [1,2]":          [1, 2],
        "iter([1,2])":         iter([1, 2]),
        "NumberRange":         NumberRange(1, 3),
        "RangeIterator":       RangeIterator(1, 3),
        "str 'abc'":           "abc",
        "int 42":              42,
    }

    for name, obj in objects.items():
        is_it = isinstance(obj, collections.abc.Iterable)
        is_tor = isinstance(obj, collections.abc.Iterator)
        print(f"  {name:<20s}  Iterable={is_it}  Iterator={is_tor}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景：分块读取
# ---------------------------------------------------------------------------

def chunked(iterable, size: int):
    """把任意可迭代对象切成固定大小的块，返回生成器。

    不把全部数据装入内存——每次只持有 `size` 个元素。
    """
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(it))
        except StopIteration:
            if chunk:
                yield chunk
            return
        yield chunk


def demo05_chunked():
    """⑤ 实际场景：分块处理大数据集"""
    print("\n⑤ chunked 分块迭代")

    data = range(1, 12)                  # 模拟 11 条记录
    for i, batch in enumerate(chunked(data, 4), start=1):
        print(f"  批次 {i}: {batch}")


if __name__ == "__main__":
    demo01_for_equivalent()
    demo02_custom_iterator()
    demo03_iterable_vs_iterator()
    demo04_abc_check()
    demo05_chunked()
