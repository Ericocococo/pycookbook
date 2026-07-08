"""生成器表达式 —— (x for x in ...) vs 列表推导式

Python 3.12。
运行: python 03_generator_expr.py

生成器表达式：把列表推导式的 [] 换成 ()，得到惰性迭代器而非列表。
语法上与列表推导式完全对称；区别只在内存和时机。

演示：
  ① 语法对比：列表推导式 vs 生成器表达式
  ② 内存对比：不产生中间列表
  ③ 惰性求值：值在需要时才计算
  ④ 链式组合：多个生成器表达式串联
  ⑤ 配合内置函数：sum / any / all / max / min
  ⑥ 注意：生成器表达式只能遍历一次
"""

import sys


# ---------------------------------------------------------------------------
# ① 语法对比
# ---------------------------------------------------------------------------

def demo01_syntax():
    """① 列表推导式 vs 生成器表达式"""
    print("① 语法对比")

    data = range(1, 6)

    # 列表推导式：立即求值，返回 list
    lst = [x * x for x in data]
    print(f"  列表推导式: {lst}  type={type(lst).__name__}")

    # 生成器表达式：惰性，返回 generator
    gen = (x * x for x in data)
    print(f"  生成器表达式: {gen}  type={type(gen).__name__}")

    # 消费才能看到值
    print(f"  list(gen): {list(gen)}")

    # 带条件过滤
    evens = [x for x in range(10) if x % 2 == 0]
    evens_g = (x for x in range(10) if x % 2 == 0)
    print(f"  过滤偶数 list:  {evens}")
    print(f"  过滤偶数 gen:   {list(evens_g)}")


# ---------------------------------------------------------------------------
# ② 内存对比
# ---------------------------------------------------------------------------

def demo02_memory():
    """② 内存对比：生成器表达式不产生中间列表"""
    print("\n② 内存对比（n=1_000_000）")

    n = 1_000_000

    lst = [x * 2 for x in range(n)]
    gen = (x * 2 for x in range(n))

    print(f"  list sys.getsizeof: {sys.getsizeof(lst):>10,} bytes")
    print(f"  gen  sys.getsizeof: {sys.getsizeof(gen):>10,} bytes")

    del lst                               # 及时释放


# ---------------------------------------------------------------------------
# ③ 惰性求值
# ---------------------------------------------------------------------------

def demo03_lazy():
    """③ 惰性：值在 next() 时才计算"""
    print("\n③ 惰性求值演示")

    def expensive(x):
        print(f"  [计算] x={x}")
        return x * x

    gen = (expensive(x) for x in range(4))
    print("  生成器创建完毕，还没有计算任何值")

    print("  取第一个:", next(gen))
    print("  取第二个:", next(gen))
    # 只计算了 2 次，剩余 2 次等待消费


# ---------------------------------------------------------------------------
# ④ 链式组合
# ---------------------------------------------------------------------------

def demo04_chain():
    """④ 生成器表达式串联，构成零中间列表的管道"""
    print("\n④ 链式组合")

    # 原始数据
    raw = ("  Hello, World!  ", "  Python  ", "  foo bar  ")

    # 每个步骤都是惰性的，只在最终 list() 时触发
    stripped = (s.strip() for s in raw)
    upper = (s.upper() for s in stripped)
    result = [s for s in upper if len(s) > 5]

    print(f"  结果: {result}")


# ---------------------------------------------------------------------------
# ⑤ 配合内置函数
# ---------------------------------------------------------------------------

def demo05_builtins():
    """⑤ sum / any / all / max / min 都接受可迭代对象"""
    print("\n⑤ 配合内置函数")

    nums = range(1, 101)

    # sum 直接传生成器表达式，不产生中间列表
    total = sum(x * x for x in nums)
    print(f"  1..100 的平方和: {total}")

    words = ["", "hello", "", "world", "python"]

    # any/all 短路求值——找到第一个满足条件就停
    has_empty = any(w == "" for w in words)
    all_non_empty = all(w != "" for w in words)
    print(f"  有空字符串: {has_empty}")
    print(f"  全非空:     {all_non_empty}")

    # max/min 也接受生成器
    longest = max(words, key=len)
    print(f"  最长单词: {longest!r}")

    # 注意：当生成器表达式是函数的唯一参数时，可以省略外层括号
    s = sum(x for x in range(10))        # 不写成 sum((x for x in range(10)))
    print(f"  sum(x for x in range(10)): {s}")


# ---------------------------------------------------------------------------
# ⑥ 只能遍历一次
# ---------------------------------------------------------------------------

def demo06_one_pass():
    """⑥ 生成器只能遍历一次，耗尽后再迭代得到空"""
    print("\n⑥ 只能遍历一次")

    gen = (x for x in range(5))

    print(f"  第一次 list(): {list(gen)}")
    print(f"  第二次 list(): {list(gen)}  ← 已耗尽，返回空列表")

    # 如果需要多次遍历，存成 list，或者每次重新创建生成器表达式
    data = range(5)
    print("  重新创建生成器表达式（推荐）:")
    print(f"    第一次: {list(x for x in data)}")
    print(f"    第二次: {list(x for x in data)}")


if __name__ == "__main__":
    demo01_syntax()
    demo02_memory()
    demo03_lazy()
    demo04_chain()
    demo05_builtins()
    demo06_one_pass()
