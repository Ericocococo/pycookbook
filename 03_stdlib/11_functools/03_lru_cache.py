"""functools.lru_cache / cache —— 结果缓存

Python 3.12。
运行: python 03_lru_cache.py

lru_cache(maxsize=128)：最近最少使用缓存。
相同参数调用时直接返回缓存值，不重复计算。
参数必须可哈希（不能是 list / dict）。

@cache（Python 3.9+）= @lru_cache(maxsize=None)，无上限缓存。

演示：
  ① 最基本用法：斐波那契加速
  ② cache_info() 和 cache_clear()
  ③ maxsize 的影响：有限缓存 vs 无限缓存
  ④ 参数限制：必须可哈希
  ⑤ 实际场景 A：记忆化递归（树路径计数）
  ⑥ 实际场景 B：昂贵计算结果的缓存
  ⑦ 注意：lru_cache 不适合有副作用或非纯函数
"""

import functools
import time


# ---------------------------------------------------------------------------
# ① 最基本用法
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def fib_cached(n: int) -> int:
    """带缓存的斐波那契（记忆化递归）"""
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def fib_naive(n: int) -> int:
    """无缓存的斐波那契（指数复杂度）"""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def demo01_basic():
    """① lru_cache 让递归从指数变线性"""
    print("① lru_cache 斐波那契")

    t0 = time.perf_counter()
    r1 = fib_naive(35)
    t1 = time.perf_counter()
    print(f"  无缓存 fib(35) = {r1:>10,}  耗时 {(t1-t0)*1000:.1f} ms")

    fib_cached.cache_clear()            # 确保从空缓存开始
    t0 = time.perf_counter()
    r2 = fib_cached(35)
    t1 = time.perf_counter()
    print(f"  有缓存 fib(35) = {r2:>10,}  耗时 {(t1-t0)*1000:.3f} ms")

    # 大数（无缓存会超时）
    print(f"  fib(200) = {fib_cached(200)}")


# ---------------------------------------------------------------------------
# ② cache_info 和 cache_clear
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=4)
def slow_square(n: int) -> int:
    """模拟耗时计算"""
    time.sleep(0.001)
    return n * n


def demo02_cache_info():
    """② cache_info() 查看命中率，cache_clear() 清空"""
    print("\n② cache_info / cache_clear")

    slow_square.cache_clear()

    for n in [1, 2, 3, 1, 2, 4, 5, 1]:   # 5 不在 maxsize=4 的窗口里
        result = slow_square(n)
        info = slow_square.cache_info()
        print(f"  square({n}) = {result:3d}  "
              f"hits={info.hits}  misses={info.misses}  "
              f"currsize={info.currsize}/{info.maxsize}")

    # CacheInfo 是一个 namedtuple
    info = slow_square.cache_info()
    print(f"\n  最终 CacheInfo: {info}")
    hit_rate = info.hits / (info.hits + info.misses) * 100 if (info.hits + info.misses) else 0
    print(f"  命中率: {hit_rate:.1f}%")

    slow_square.cache_clear()
    print(f"  清空后 currsize = {slow_square.cache_info().currsize}")


# ---------------------------------------------------------------------------
# ③ maxsize 对比
# ---------------------------------------------------------------------------

def demo03_maxsize():
    """③ maxsize=None 无上限 vs 有上限"""
    print("\n③ maxsize 影响")

    @functools.lru_cache(maxsize=2)
    def tiny_cache(n):
        return n * 10

    # 缓存容量只有 2，访问第三个不同值时会淘汰最旧的
    for n in [1, 2, 3, 1]:
        tiny_cache(n)
        print(f"  tiny_cache({n})  currsize={tiny_cache.cache_info().currsize}")

    # @cache 等价于 @lru_cache(maxsize=None)
    @functools.cache
    def unlimited(n):
        return n * 100

    for n in range(5):
        unlimited(n)
    print(f"\n  @cache currsize={unlimited.cache_info().currsize}  maxsize={unlimited.cache_info().maxsize}")


# ---------------------------------------------------------------------------
# ④ 参数必须可哈希
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=128)
def cached_with_tuple(data: tuple, factor: int) -> list:
    """参数必须可哈希——用 tuple 代替 list"""
    return [x * factor for x in data]


def demo04_hashable():
    """④ 参数哈希性：list→tuple，dict→frozenset"""
    print("\n④ 参数哈希限制")

    # 正确：传 tuple（可哈希）
    result = cached_with_tuple((1, 2, 3), 5)
    print(f"  cached_with_tuple((1,2,3), 5) = {result}")

    # 错误演示：直接传 list 会 TypeError
    try:
        # 不能这样调：functools.lru_cache 会 TypeError: unhashable type: 'list'
        functools.lru_cache(maxsize=128)(lambda data: data)([1, 2, 3])
    except TypeError as e:
        print(f"  传 list 的错误: {e}")

    # 解决方案：调用处手动转换
    my_list = [1, 2, 3]
    result2 = cached_with_tuple(tuple(my_list), factor=10)
    print(f"  tuple(my_list) 转换后 = {result2}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景 A：记忆化树路径计数
# ---------------------------------------------------------------------------

@functools.cache
def count_paths(rows: int, cols: int) -> int:
    """从左上角到右下角，只能向右或向下，有多少种路径？（动态规划）"""
    if rows == 1 or cols == 1:
        return 1
    return count_paths(rows - 1, cols) + count_paths(rows, cols - 1)


def demo05_path_count():
    """⑤ 记忆化 DP：网格路径计数"""
    print("\n⑤ 记忆化 DP（路径计数）")

    for r, c in [(3, 3), (5, 5), (10, 10), (20, 20)]:
        paths = count_paths(r, c)
        print(f"  {r}×{c} 网格路径数: {paths:,}")

    print(f"  缓存命中情况: {count_paths.cache_info()}")


# ---------------------------------------------------------------------------
# ⑥ 实际场景 B：昂贵计算
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=256)
def analyze_text(text: str) -> dict:
    """模拟耗时的文本分析（词频统计）"""
    time.sleep(0.05)                    # 模拟 50ms 延迟
    words = text.lower().split()
    freq: dict = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq


def demo06_expensive_computation():
    """⑥ 缓存昂贵计算：相同输入不重复计算"""
    print("\n⑥ 缓存昂贵文本分析")

    texts = [
        "python is great python is easy",
        "data science with python",
        "python is great python is easy",  # 重复，命中缓存
    ]

    for text in texts:
        t0 = time.perf_counter()
        result = analyze_text(text)
        elapsed = (time.perf_counter() - t0) * 1000
        info = analyze_text.cache_info()
        print(f"  [{elapsed:5.1f}ms] hits={info.hits}  {dict(list(result.items())[:3])}...")


# ---------------------------------------------------------------------------
# ⑦ 不适用场景
# ---------------------------------------------------------------------------

def demo07_caveats():
    """⑦ lru_cache 不适合有副作用或结果随时间变化的函数"""
    print("\n⑦ 注意事项")

    import time as _time

    @functools.cache
    def get_time() -> float:
        """错误示范：有副作用（返回当前时间），结果应该每次不同"""
        return _time.time()

    t1 = get_time()
    _time.sleep(0.01)
    t2 = get_time()
    print(f"  get_time() 两次结果相同（被缓存了，虽然时间过了）: {t1 == t2}")
    print(f"  → 随时间/状态变化的函数不要用 lru_cache")

    # 正确做法：明确把"时间"作为参数传入，让缓存 key 能区分
    @functools.cache
    def fetch_price(symbol: str, date: str) -> float:
        """日期作为参数→相同日期和股票的价格可以缓存"""
        return 100.0                    # 模拟
    print(f"  → 把可变维度变成参数（如日期），让函数变纯函数")


if __name__ == "__main__":
    demo01_basic()
    demo02_cache_info()
    demo03_maxsize()
    demo04_hashable()
    demo05_path_count()
    demo06_expensive_computation()
    demo07_caveats()
