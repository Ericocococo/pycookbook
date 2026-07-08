"""闭包 —— 自由变量捕获 / nonlocal / 工厂模式

Python 3.12。
运行: python 03_closure.py

闭包：内层函数引用了外层函数中的变量，即使外层函数已返回，那个变量依然存活。
"自由变量"指既不是内层函数的局部变量、也不是全局变量的那些变量。

演示：
  ① 最简闭包：自由变量捕获
  ② __closure__ 与 cell 对象：查看闭包捕获的值
  ③ nonlocal：在闭包内赋值自由变量
  ④ 工厂模式：生成专用函数
  ⑤ 经典陷阱：循环里的闭包（与 lambda 同款坑）
  ⑥ 闭包 vs 类：什么时候各自更合适
"""


# ---------------------------------------------------------------------------
# ① 最简闭包
# ---------------------------------------------------------------------------

def outer(message: str):
    """外层函数：message 是自由变量"""
    def inner():
        # inner 捕获了 outer 的局部变量 message
        # 即使 outer 已经 return，message 依然存活
        print(f"  message = {message!r}")
    return inner


def demo01_basic():
    """① 最简闭包：外层返回后，内层仍能访问外层变量"""
    print("① 最简闭包")

    say_hello = outer("hello")
    say_world = outer("world")

    # outer("hello") 已经执行完毕，但 message 还活着
    say_hello()
    say_world()
    # 每个返回的 inner 持有各自独立的 message
    say_hello()


# ---------------------------------------------------------------------------
# ② __closure__ 查看内部结构
# ---------------------------------------------------------------------------

def demo02_inspect_closure():
    """② __closure__：查看闭包捕获了什么"""
    print("\n② 查看 __closure__")

    def make_power(exp):
        def power(base):
            return base ** exp
        return power

    square = make_power(2)
    cube = make_power(3)

    print(f"  square.__closure__: {square.__closure__}")
    # cell_contents 取出 cell 里存的值
    print(f"  square 捕获的 exp: {square.__closure__[0].cell_contents}")
    print(f"  cube   捕获的 exp: {cube.__closure__[0].cell_contents}")

    print(f"  square(4) = {square(4)}")
    print(f"  cube(3)   = {cube(3)}")


# ---------------------------------------------------------------------------
# ③ nonlocal
# ---------------------------------------------------------------------------

def make_counter(start: int = 0, step: int = 1):
    """带状态的计数器：用 nonlocal 修改自由变量"""
    count = start                        # 自由变量

    def increment():
        nonlocal count                   # 声明要修改外层的 count（不声明则赋值会创建局部变量）
        count += step
        return count

    def reset():
        nonlocal count
        count = start

    def current():
        return count                     # 只读不需要 nonlocal

    return increment, reset, current


def demo03_nonlocal():
    """③ nonlocal：在闭包内修改自由变量"""
    print("\n③ nonlocal 计数器")

    inc, reset, cur = make_counter(start=0, step=2)
    print(f"  inc() = {inc()}")          # 2
    print(f"  inc() = {inc()}")          # 4
    print(f"  inc() = {inc()}")          # 6
    print(f"  cur() = {cur()}")          # 6
    reset()
    print(f"  reset 后 cur() = {cur()}") # 0


# ---------------------------------------------------------------------------
# ④ 工厂模式
# ---------------------------------------------------------------------------

def make_multiplier(factor: float):
    """生成"乘以 factor"的函数"""
    def mul(x):
        return x * factor
    return mul


def make_validator(min_val, max_val, name: str = "值"):
    """生成带描述的范围校验函数"""
    def validate(value) -> tuple[bool, str]:
        if min_val <= value <= max_val:
            return True, f"{name} {value} 合法"
        return False, f"{name} {value} 超出范围 [{min_val}, {max_val}]"
    return validate


def demo04_factory():
    """④ 工厂：生成带预设参数的专用函数"""
    print("\n④ 工厂模式")

    double = make_multiplier(2)
    tax = make_multiplier(1.13)         # 含税价
    print(f"  double(5) = {double(5)}")
    print(f"  税后 100  = {tax(100):.2f}")

    check_age = make_validator(0, 120, "年龄")
    check_pct = make_validator(0.0, 1.0, "百分比")

    for age in [25, -1, 150]:
        ok, msg = check_age(age)
        print(f"  {'✓' if ok else '✗'} {msg}")

    for pct in [0.5, 1.5]:
        ok, msg = check_pct(pct)
        print(f"  {'✓' if ok else '✗'} {msg}")


# ---------------------------------------------------------------------------
# ⑤ 循环陷阱
# ---------------------------------------------------------------------------

def demo05_loop_trap():
    """⑤ 经典陷阱：循环里创建的闭包共享同一个变量"""
    print("\n⑤ 循环陷阱")

    # 所有 action 都引用同一个 i（Python 的 for 变量没有块作用域）
    actions_bad = []
    for i in range(3):
        def action():
            return i                     # 捕获的是变量 i，不是当时的值
        actions_bad.append(action)

    # 循环结束后 i=2，所有 action() 都返回 2
    print(f"  坏写法: {[a() for a in actions_bad]}")   # [2, 2, 2]

    # 修复 A：用工厂函数，每次调用创建新的作用域
    def make_action(val):
        def action():
            return val                   # 捕获的是 val，每次调用 make_action 都是新的 val
        return action

    actions_good = [make_action(i) for i in range(3)]
    print(f"  工厂修复: {[a() for a in actions_good]}")  # [0, 1, 2]

    # 修复 B：默认参数（见 02_lambda.py）
    actions_good2 = [(lambda i=i: i) for i in range(3)]
    print(f"  默认参数修复: {[a() for a in actions_good2]}")  # [0, 1, 2]


# ---------------------------------------------------------------------------
# ⑥ 闭包 vs 类
# ---------------------------------------------------------------------------

class Counter:
    """用类实现计数器——状态多时，类更清晰"""

    def __init__(self, start: int = 0):
        self._count = start

    def increment(self):
        self._count += 1
        return self._count

    def reset(self):
        self._count = 0

    @property
    def value(self):
        return self._count


def make_counter_closure(start: int = 0):
    """用闭包实现计数器——状态少时，闭包更轻量"""
    count = start
    def inc():
        nonlocal count
        count += 1
        return count
    def reset():
        nonlocal count
        count = 0
    return inc, reset


def demo06_closure_vs_class():
    """⑥ 闭包 vs 类：各自适合的场景"""
    print("\n⑥ 闭包 vs 类")

    # 闭包：适合状态简单、只需要一两个方法
    inc, reset = make_counter_closure()
    print(f"  闭包计数器: {inc()} {inc()} {inc()}")
    reset()
    print(f"  reset 后: {inc()}")

    # 类：状态多、需要继承、需要 repr/序列化时更合适
    c = Counter(10)
    print(f"  类计数器: {c.increment()} {c.increment()}")
    print(f"  类计数器 value 属性: {c.value}")


if __name__ == "__main__":
    demo01_basic()
    demo02_inspect_closure()
    demo03_nonlocal()
    demo04_factory()
    demo05_loop_trap()
    demo06_closure_vs_class()
