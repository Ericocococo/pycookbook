"""高阶函数 —— 函数作为一等对象

Python 3.12。
运行: python 01_higher_order.py

高阶函数：接收函数作为参数，或返回函数作为结果（或两者兼有）。
Python 函数是一等对象——可赋值、可传参、可返回、可放进容器。

演示：
  ① 函数作为参数：map / filter / sorted
  ② 函数作为返回值：工厂模式
  ③ 自定义高阶函数
  ④ 函数列表与分发表
  ⑤ 实际场景：策略模式（替代 if/elif 链）
"""


# ---------------------------------------------------------------------------
# ① 内置高阶函数：map / filter / sorted
# ---------------------------------------------------------------------------

def demo01_builtins():
    """① map / filter / sorted：Python 内置的高阶函数"""
    print("① 内置高阶函数")

    nums = [3, 1, 4, 1, 5, 9, 2, 6]

    # map(func, iterable)：对每个元素应用 func，返回惰性 map 对象
    squares = list(map(lambda x: x * x, nums))
    print(f"  map 平方:          {squares}")

    # 可以传普通函数
    words = ["hello", "WORLD", "Python"]
    lowered = list(map(str.lower, words))
    print(f"  map str.lower:     {lowered}")

    # filter(func, iterable)：保留使 func 返回 True 的元素
    evens = list(filter(lambda x: x % 2 == 0, nums))
    print(f"  filter 偶数:       {evens}")

    # filter(None, iterable)：过滤掉假值
    mixed = [0, 1, "", "hello", None, [], [1, 2], False, True]
    truthy = list(filter(None, mixed))
    print(f"  filter None（去假值）: {truthy}")

    # sorted(iterable, key=func, reverse=bool)
    words2 = ["banana", "apple", "cherry", "date"]
    by_len = sorted(words2, key=len)
    print(f"  sorted 按长度:     {by_len}")

    # 多级排序：先按长度，长度相同按字母
    by_len_then_alpha = sorted(words2, key=lambda w: (len(w), w))
    print(f"  sorted 多级:       {by_len_then_alpha}")


# ---------------------------------------------------------------------------
# ② 函数作为返回值：工厂
# ---------------------------------------------------------------------------

def make_multiplier(factor: int):
    """工厂函数：返回一个"乘以 factor"的函数"""
    def multiplier(x):
        return x * factor
    return multiplier


def make_validator(min_val: float, max_val: float):
    """返回一个范围校验函数"""
    def validate(value: float) -> bool:
        return min_val <= value <= max_val
    return validate


def demo02_factory():
    """② 函数作为返回值：工厂模式"""
    print("\n② 工厂模式")

    double = make_multiplier(2)
    triple = make_multiplier(3)
    print(f"  double(5) = {double(5)}")
    print(f"  triple(5) = {triple(5)}")

    is_percentage = make_validator(0, 100)
    is_score = make_validator(0, 10)
    print(f"  is_percentage(85)  = {is_percentage(85)}")
    print(f"  is_percentage(150) = {is_percentage(150)}")
    print(f"  is_score(9.5)      = {is_score(9.5)}")


# ---------------------------------------------------------------------------
# ③ 自定义高阶函数
# ---------------------------------------------------------------------------

def apply_twice(func, x):
    """把 func 应用两次"""
    return func(func(x))


def compose(*funcs):
    """函数组合：compose(f, g, h)(x) = f(g(h(x)))"""
    def composed(x):
        result = x
        for f in reversed(funcs):       # 从右到左应用
            result = f(result)
        return result
    return composed


def pipeline(value, *funcs):
    """管道：pipeline(x, f, g, h) = h(g(f(x)))，从左到右"""
    result = value
    for f in funcs:
        result = f(result)
    return result


def demo03_custom():
    """③ 自定义高阶函数：apply_twice / compose / pipeline"""
    print("\n③ 自定义高阶函数")

    print(f"  apply_twice(str.upper, 'hello') = {apply_twice(str.upper, 'hello')}")
    print(f"  apply_twice(lambda x: x+1, 5)  = {apply_twice(lambda x: x + 1, 5)}")

    # 函数组合
    add1 = lambda x: x + 1
    mul2 = lambda x: x * 2
    sq = lambda x: x * x

    # compose(f, g)(x) = f(g(x))
    f = compose(sq, add1, mul2)          # sq(add1(mul2(x)))
    print(f"  compose(sq, add1, mul2)(3) = {f(3)}")  # sq(add1(6)) = sq(7) = 49

    # pipeline 从左到右更直观
    result = pipeline(3, mul2, add1, sq)  # sq(add1(mul2(3))) = sq(7) = 49
    print(f"  pipeline(3, mul2, add1, sq) = {result}")


# ---------------------------------------------------------------------------
# ④ 函数列表与分发表
# ---------------------------------------------------------------------------

def demo04_dispatch_table():
    """④ 函数放进字典：分发表替代长 if/elif"""
    print("\n④ 分发表")

    # 把操作名映射到函数——新增操作只需往字典加一行
    operations = {
        "add":  lambda a, b: a + b,
        "sub":  lambda a, b: a - b,
        "mul":  lambda a, b: a * b,
        "div":  lambda a, b: a / b if b != 0 else float("inf"),
        "pow":  lambda a, b: a ** b,
        "max":  max,
        "min":  min,
    }

    test_cases = [
        ("add", 3, 4),
        ("mul", 5, 6),
        ("pow", 2, 10),
        ("max", 7, 3),
        ("unknown", 1, 2),
    ]

    for op, a, b in test_cases:
        func = operations.get(op)
        if func:
            print(f"  {op}({a}, {b}) = {func(a, b)}")
        else:
            print(f"  {op!r}: 未知操作")


# ---------------------------------------------------------------------------
# ⑤ 实际场景：策略模式
# ---------------------------------------------------------------------------

def strategy_discount(items: list[dict], discount_func) -> float:
    """结算函数：接收商品列表和折扣策略函数"""
    total = sum(item["price"] * item["qty"] for item in items)
    return discount_func(total)


# 各种折扣策略（可随意替换，不改结算逻辑）
def no_discount(total):    return total
def vip_discount(total):   return total * 0.8
def coupon_50(total):      return max(0, total - 50)
def tiered(total):         return total * (0.7 if total > 300 else 0.9 if total > 100 else 1.0)


def demo05_strategy():
    """⑤ 策略模式：折扣规则作为参数传入"""
    print("\n⑤ 策略模式：折扣")

    cart = [
        {"name": "Python书", "price": 89, "qty": 2},
        {"name": "键盘",      "price": 150, "qty": 1},
    ]

    strategies = {
        "无折扣":   no_discount,
        "VIP 8折":  vip_discount,
        "满减50元": coupon_50,
        "阶梯折扣": tiered,
    }

    for name, func in strategies.items():
        price = strategy_discount(cart, func)
        print(f"  {name:8s}: ¥{price:.2f}")


if __name__ == "__main__":
    demo01_builtins()
    demo02_factory()
    demo03_custom()
    demo04_dispatch_table()
    demo05_strategy()
