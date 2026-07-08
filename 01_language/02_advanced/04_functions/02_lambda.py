"""lambda —— 匿名函数

Python 3.12。
运行: python 02_lambda.py

lambda 语法：lambda 参数: 表达式
只能是单个表达式，不能有语句（赋值、for、if-else语句等）。
主要价值：在 key= / 回调 等需要"临时函数"的场合，省去命名一个单行函数的仪式感。

演示：
  ① 语法与等价的 def
  ② 适用场景：sorted / map / filter key 函数
  ③ 适用场景：回调与事件驱动
  ④ 不适用：复杂逻辑用 def 更清晰
  ⑤ 经典陷阱：lambda 捕获变量（循环里的坑）
"""


# ---------------------------------------------------------------------------
# ① 语法与等价 def
# ---------------------------------------------------------------------------

def demo01_syntax():
    """① lambda 与等价 def 对比"""
    print("① 语法对比")

    # lambda：匿名，只有表达式
    add = lambda x, y: x + y
    print(f"  lambda add(3, 4) = {add(3, 4)}")

    # 等价的 def
    def add2(x, y):
        return x + y
    print(f"  def    add(3, 4) = {add2(3, 4)}")

    # 带默认参数
    greet = lambda name, greeting="你好": f"{greeting}，{name}！"
    print(f"  greet('Alice')         = {greet('Alice')}")
    print(f"  greet('Bob', 'Hello')  = {greet('Bob', 'Hello')}")

    # 立即调用（IIFE，很少用，但语法上合法）
    result = (lambda x: x * x)(5)
    print(f"  立即调用 (lambda x: x*x)(5) = {result}")


# ---------------------------------------------------------------------------
# ② 适用场景：key 函数
# ---------------------------------------------------------------------------

def demo02_key_functions():
    """② 最佳用途：sorted / min / max 的 key 参数"""
    print("\n② key 函数场景")

    # 按字符串长度排序
    words = ["banana", "fig", "apple", "kiwi", "cherry"]
    by_len = sorted(words, key=lambda w: len(w))
    print(f"  按长度升序: {by_len}")

    # 多字段排序：先按长度，再按字母逆序
    multi = sorted(words, key=lambda w: (len(w), [-ord(c) for c in w]))
    print(f"  多字段排序: {multi}")

    # 对象列表排序
    people = [
        {"name": "Alice", "age": 30},
        {"name": "Bob",   "age": 25},
        {"name": "Carol", "age": 35},
    ]
    by_age = sorted(people, key=lambda p: p["age"])
    print(f"  按年龄: {[p['name'] for p in by_age]}")

    youngest = min(people, key=lambda p: p["age"])
    print(f"  最年轻: {youngest['name']}")

    # groupby 配合 lambda（需要先排序）
    from itertools import groupby
    data = ["apple", "ant", "bear", "bee", "cat"]
    data.sort(key=lambda w: w[0])        # groupby 要求先排序
    for letter, group in groupby(data, key=lambda w: w[0]):
        print(f"  {letter}: {list(group)}")


# ---------------------------------------------------------------------------
# ③ 回调场景
# ---------------------------------------------------------------------------

def apply_operations(value: float, *operations) -> float:
    """依次应用一组操作（每个操作是一个函数）"""
    result = value
    for op in operations:
        result = op(result)
    return result


def demo03_callbacks():
    """③ 回调场景：lambda 作为临时处理函数"""
    print("\n③ 回调场景")

    result = apply_operations(
        10,
        lambda x: x * 2,       # 乘 2
        lambda x: x + 3,       # 加 3
        lambda x: x ** 2,      # 平方
    )
    print(f"  10 → ×2 → +3 → ² = {result}")

    # 条件过滤（比单独定义 is_even 函数更省事）
    nums = range(1, 11)
    evens = list(filter(lambda x: x % 2 == 0, nums))
    print(f"  偶数: {evens}")

    # map 变换
    hex_nums = list(map(lambda x: hex(x), [255, 256, 1024]))
    print(f"  hex: {hex_nums}")


# ---------------------------------------------------------------------------
# ④ 不适用：复杂逻辑
# ---------------------------------------------------------------------------

def demo04_when_not_to_use():
    """④ lambda 不适合复杂逻辑——用 def 更清晰"""
    print("\n④ 不适用场景")

    # 反例：把复杂逻辑塞进 lambda（可读性极差）
    bad = lambda x: "正数" if x > 0 else ("负数" if x < 0 else "零")
    # 应该写成 def
    def classify(x: int) -> str:
        """分类数字符号"""
        if x > 0:
            return "正数"
        elif x < 0:
            return "负数"
        return "零"

    for n in [-3, 0, 5]:
        print(f"  classify({n:2d}) = {classify(n)}")

    # 反例：lambda 赋值给变量（PEP8 要求用 def）
    # bad_style = lambda x: x * 2   # linter 会警告
    # 正确：
    def double(x): return x * 2
    print(f"  double(7) = {double(7)}")


# ---------------------------------------------------------------------------
# ⑤ 经典陷阱：循环里的 lambda
# ---------------------------------------------------------------------------

def demo05_loop_trap():
    """⑤ 经典陷阱：lambda 捕获的是变量名，不是当前值"""
    print("\n⑤ 循环陷阱")

    # 错误写法：所有 lambda 捕获同一个变量 i
    funcs_bad = [lambda x: x + i for i in range(5)]
    # 循环结束后 i=4，所有 lambda 都用 i=4
    print(f"  坏写法 funcs_bad[0](10) = {funcs_bad[0](10)}")   # 期望 10，实际 14
    print(f"  坏写法 funcs_bad[3](10) = {funcs_bad[3](10)}")   # 期望 13，实际 14

    # 正确写法 A：默认参数捕获当前值（最常用）
    funcs_good_a = [lambda x, i=i: x + i for i in range(5)]
    print(f"  好写法A funcs_good_a[0](10) = {funcs_good_a[0](10)}")  # 10
    print(f"  好写法A funcs_good_a[3](10) = {funcs_good_a[3](10)}")  # 13

    # 正确写法 B：用工厂函数（闭包），在 03_closure.py 里有详细说明
    def make_adder(n):
        return lambda x: x + n

    funcs_good_b = [make_adder(i) for i in range(5)]
    print(f"  好写法B funcs_good_b[0](10) = {funcs_good_b[0](10)}")  # 10
    print(f"  好写法B funcs_good_b[3](10) = {funcs_good_b[3](10)}")  # 13


if __name__ == "__main__":
    demo01_syntax()
    demo02_key_functions()
    demo03_callbacks()
    demo04_when_not_to_use()
    demo05_loop_trap()
