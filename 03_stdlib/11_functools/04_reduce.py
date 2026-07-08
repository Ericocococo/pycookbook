"""functools.reduce —— 归约为单个值

Python 3.12。
运行: python 04_reduce.py

reduce(func, iterable[, initializer])：
  从左到右把 iterable 用 func 两两归约为一个值。
  reduce(f, [a, b, c, d]) = f(f(f(a, b), c), d)

与 itertools.accumulate 的区别：
  reduce   → 只返回最终值（一个值）
  accumulate → 返回所有中间值的序列（惰性）

演示：
  ① 手动等价展开
  ② initializer 的作用
  ③ 配合 operator 模块（避免 lambda）
  ④ reduce vs accumulate 对比
  ⑤ 实际场景 A：嵌套字典安全取值
  ⑥ 实际场景 B：合并多个字典
  ⑦ 实际场景 C：函数组合（compose）
"""

import functools
import operator
import itertools


# ---------------------------------------------------------------------------
# ① 手动等价
# ---------------------------------------------------------------------------

def demo01_equivalent():
    """① reduce 的等价展开"""
    print("① reduce 等价展开")

    nums = [1, 2, 3, 4, 5]

    # reduce(lambda a, b: a + b, nums) 等价于：
    result_manual = nums[0]
    for n in nums[1:]:
        result_manual = result_manual + n

    result_reduce = functools.reduce(lambda a, b: a + b, nums)

    print(f"  手动累加: {result_manual}")
    print(f"  reduce:   {result_reduce}")
    print(f"  sum():    {sum(nums)}  ← 大多数时候优先用内置函数")

    # 展示每一步
    def verbose_add(a, b):
        r = a + b
        print(f"    {a} + {b} = {r}")
        return r

    print("  reduce 每步:")
    functools.reduce(verbose_add, nums)


# ---------------------------------------------------------------------------
# ② initializer
# ---------------------------------------------------------------------------

def demo02_initializer():
    """② initializer：空序列时的默认值 / 改变归约起点"""
    print("\n② initializer")

    nums = [1, 2, 3, 4]
    add = operator.add

    # 无 initializer：第一个元素作为初始值
    print(f"  reduce(add, [1,2,3,4])        = {functools.reduce(add, nums)}")

    # 有 initializer：从 initializer 开始
    print(f"  reduce(add, [1,2,3,4], 100)   = {functools.reduce(add, nums, 100)}")

    # 空序列时：无 initializer 会 TypeError，有则返回 initializer
    try:
        functools.reduce(add, [])
    except TypeError as e:
        print(f"  reduce(add, []) → TypeError: {e}")

    print(f"  reduce(add, [], 0)            = {functools.reduce(add, [], 0)}")

    # 实际场景：合并列表时加初始 []
    lists = [[1, 2], [3, 4], [5]]
    flat = functools.reduce(operator.add, lists, [])
    print(f"  reduce(add, lists, []) = {flat}")


# ---------------------------------------------------------------------------
# ③ 配合 operator 模块
# ---------------------------------------------------------------------------

def demo03_operator():
    """③ operator 模块：避免 lambda，速度更快"""
    print("\n③ 配合 operator 模块")

    nums = [2, 3, 4, 5]

    # 乘积（lambda 写法 vs operator 写法）
    prod_lambda = functools.reduce(lambda a, b: a * b, nums)
    prod_op = functools.reduce(operator.mul, nums)
    print(f"  乘积 lambda: {prod_lambda}")
    print(f"  乘积 operator.mul: {prod_op}")

    # 最大值（等价于 max()，但演示 reduce 可以做任何二元操作）
    max_val = functools.reduce(operator.gt and (lambda a, b: a if a > b else b), nums)
    # 更清晰：直接用 max
    print(f"  最大值: {max(nums)}  (此处优先用 max)")

    # 字典合并（Python 3.9+ 有 | 运算符）
    dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
    merged = functools.reduce(operator.or_, dicts)
    print(f"  字典 | 合并: {merged}")


# ---------------------------------------------------------------------------
# ④ reduce vs accumulate
# ---------------------------------------------------------------------------

def demo04_vs_accumulate():
    """④ reduce（最终值）vs accumulate（中间值序列）"""
    print("\n④ reduce vs accumulate")

    nums = [1, 2, 3, 4, 5]

    final = functools.reduce(operator.add, nums)
    intermediates = list(itertools.accumulate(nums, operator.add))

    print(f"  reduce:     {final}          ← 只有最终结果")
    print(f"  accumulate: {intermediates}  ← 所有中间值（前缀和）")

    # 什么时候用哪个：
    # - 只关心最终结果 → reduce（或直接用 sum/max/min 等内置函数）
    # - 需要中间值（running total、前缀积、running max）→ accumulate

    # 运行最大值
    prices = [10, 8, 12, 11, 15, 9, 14]
    running_max = list(itertools.accumulate(prices, max))
    print(f"\n  股价:         {prices}")
    print(f"  历史最高(acc): {running_max}")
    print(f"  最终最高(red): {functools.reduce(max, prices)}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景 A：嵌套字典安全取值
# ---------------------------------------------------------------------------

def demo05_nested_get():
    """⑤ reduce 安全访问嵌套字典"""
    print("\n⑤ 嵌套字典安全取值")

    data = {
        "user": {
            "profile": {
                "address": {
                    "city": "北京",
                    "zip": "100000",
                }
            }
        }
    }

    def deep_get(d: dict, *keys, default=None):
        """用 reduce 逐层取值，任意一层不存在返回 default"""
        try:
            return functools.reduce(lambda obj, key: obj[key], keys, d)
        except (KeyError, TypeError):
            return default

    print(f"  city: {deep_get(data, 'user', 'profile', 'address', 'city')}")
    print(f"  zip:  {deep_get(data, 'user', 'profile', 'address', 'zip')}")
    print(f"  不存在的键: {deep_get(data, 'user', 'settings', 'theme', default='default')}")


# ---------------------------------------------------------------------------
# ⑥ 实际场景 B：合并多个字典
# ---------------------------------------------------------------------------

def demo06_merge_dicts():
    """⑥ reduce 合并多个字典（后者覆盖前者）"""
    print("\n⑥ 合并多个字典")

    defaults = {"debug": False, "log_level": "INFO", "timeout": 30}
    env_config = {"log_level": "WARNING", "db_url": "postgresql://localhost/dev"}
    user_config = {"timeout": 60, "debug": True}

    configs = [defaults, env_config, user_config]

    # 后者覆盖前者（优先级：user > env > defaults）
    merged = functools.reduce(lambda a, b: {**a, **b}, configs)
    print(f"  合并结果:")
    for k, v in merged.items():
        print(f"    {k}: {v!r}")

    # Python 3.9+ 等价写法
    merged2 = functools.reduce(operator.or_, configs)
    print(f"  | 运算符合并: {merged == merged2}")


# ---------------------------------------------------------------------------
# ⑦ 实际场景 C：函数组合
# ---------------------------------------------------------------------------

def demo07_compose():
    """⑦ 用 reduce 实现函数组合（从右到左）"""
    print("\n⑦ 函数组合")

    def compose(*funcs):
        """compose(f, g, h)(x) = f(g(h(x)))，从右到左"""
        return functools.reduce(lambda f, g: lambda x: f(g(x)), funcs)

    strip = str.strip
    upper = str.upper
    exclaim = lambda s: s + "!!!"

    # 从右到左：先 strip，再 upper，再 exclaim
    shout = compose(exclaim, upper, strip)
    result = shout("  hello, world  ")
    print(f"  shout('  hello, world  ') = {result!r}")

    # 管道（从左到右）
    def pipe(*funcs):
        return functools.reduce(lambda f, g: lambda x: g(f(x)), funcs)

    whisper = pipe(strip, upper, exclaim)
    print(f"  pipe 版本（同样效果）: {whisper('  hello, world  ')!r}")


if __name__ == "__main__":
    demo01_equivalent()
    demo02_initializer()
    demo03_operator()
    demo04_vs_accumulate()
    demo05_nested_get()
    demo06_merge_dicts()
    demo07_compose()
