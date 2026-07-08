"""functools.wraps / update_wrapper —— 装饰器元信息保留

Python 3.12。
运行: python 02_wraps.py

装饰器的核心问题：wrapper 函数把原函数"盖住"了，
导致 __name__ / __doc__ / __annotations__ / __module__ 都变成 wrapper 的。
@wraps(func) 把原函数的这些属性复制过来，让工具链（help、introspection、pytest）能正常工作。

演示：
  ① 不加 @wraps 的问题
  ② @wraps 修复
  ③ @wraps 复制了哪些属性
  ④ __wrapped__：透过装饰器访问原函数
  ⑤ update_wrapper：手动等价写法（用于类装饰器）
  ⑥ 实际场景：inspect.signature 与 @wraps 的配合
"""

import functools
import inspect


# ---------------------------------------------------------------------------
# ① 不加 @wraps 的问题
# ---------------------------------------------------------------------------

def bad_log(func):
    """没有 @wraps 的装饰器"""
    def wrapper(*args, **kwargs):
        """我是 wrapper 的 docstring"""
        print(f"  [log] 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@bad_log
def add(x: int, y: int) -> int:
    """返回两数之和"""
    return x + y


def demo01_problem():
    """① 不加 @wraps 导致元信息丢失"""
    print("① 不加 @wraps 的问题")

    print(f"  add.__name__ = {add.__name__!r}")       # 'wrapper'  ← 错的
    print(f"  add.__doc__  = {add.__doc__!r}")        # wrapper 的 docstring ← 错的
    print(f"  add.__annotations__ = {add.__annotations__}")  # {} ← 丢失了
    print(f"  add(1, 2) = {add(1, 2)}")


# ---------------------------------------------------------------------------
# ② @wraps 修复
# ---------------------------------------------------------------------------

def good_log(func):
    """加了 @wraps 的装饰器"""
    @functools.wraps(func)             # 关键：复制 func 的元信息
    def wrapper(*args, **kwargs):
        """我是 wrapper 的 docstring（不会被外部看到）"""
        print(f"  [log] 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@good_log
def multiply(x: int, y: int) -> int:
    """返回两数之积"""
    return x * y


def demo02_fixed():
    """② @wraps 修复元信息"""
    print("\n② @wraps 修复")

    print(f"  multiply.__name__ = {multiply.__name__!r}")       # 'multiply' ✓
    print(f"  multiply.__doc__  = {multiply.__doc__!r}")        # 原 docstring ✓
    print(f"  multiply.__annotations__ = {multiply.__annotations__}")  # 原注解 ✓
    print(f"  multiply(3, 4) = {multiply(3, 4)}")


# ---------------------------------------------------------------------------
# ③ @wraps 复制的属性
# ---------------------------------------------------------------------------

WRAPPER_ASSIGNMENTS = functools.WRAPPER_ASSIGNMENTS   # 默认复制的属性名列表


def demo03_what_is_copied():
    """③ @wraps 默认复制的属性"""
    print("\n③ @wraps 复制的属性")

    print(f"  functools.WRAPPER_ASSIGNMENTS = {WRAPPER_ASSIGNMENTS}")
    # ('__module__', '__name__', '__qualname__', '__annotations__',
    #  '__annotate__', '__doc__', '__dict__', '__wrapped__')

    # 验证每个属性
    def original(x: int) -> str:
        """原函数文档"""
        return str(x)

    original.custom_attr = "我是自定义属性"

    @functools.wraps(original)
    def wrapper(*args, **kwargs):
        return original(*args, **kwargs)

    for attr in WRAPPER_ASSIGNMENTS:
        orig_val = getattr(original, attr, "<不存在>")
        wrap_val = getattr(wrapper, attr, "<不存在>")
        match = "✓" if orig_val == wrap_val else "✗"
        print(f"  {match} {attr}: {wrap_val!r}")

    # __wrapped__ 指向原函数
    print(f"\n  wrapper.__wrapped__ is original: {wrapper.__wrapped__ is original}")


# ---------------------------------------------------------------------------
# ④ __wrapped__：透过装饰器访问原函数
# ---------------------------------------------------------------------------

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        t = time.perf_counter()
        r = func(*args, **kwargs)
        print(f"  [{func.__name__}] {(time.perf_counter()-t)*1000:.3f} ms")
        return r
    return wrapper


@timer
def compute(n: int) -> int:
    """计算 1..n 的平方和"""
    return sum(i * i for i in range(n))


def demo04_wrapped():
    """④ __wrapped__：访问装饰器链下面的原函数"""
    print("\n④ __wrapped__ 访问原函数")

    # 正常调用（经过装饰器）
    result = compute(1000)
    print(f"  compute(1000) = {result}")

    # 通过 __wrapped__ 绕过装饰器（测试时有用）
    raw = compute.__wrapped__(1000)
    print(f"  compute.__wrapped__(1000) = {raw}（无计时）")

    # inspect.unwrap 可以解开多层装饰器
    original = inspect.unwrap(compute)
    print(f"  inspect.unwrap(compute).__name__ = {original.__name__!r}")


# ---------------------------------------------------------------------------
# ⑤ update_wrapper：类装饰器中的等价写法
# ---------------------------------------------------------------------------

class LogDecorator:
    """类实现的装饰器，用 update_wrapper 代替 @wraps"""

    def __init__(self, func):
        # update_wrapper 等价于在函数装饰器里用 @wraps
        functools.update_wrapper(self, func)
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"  [LogDeco] #{self.call_count} 调用 {self.func.__name__}")
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return functools.partial(self, obj)


@LogDecorator
def divide(a: float, b: float) -> float:
    """安全除法"""
    return a / b if b != 0 else float("inf")


def demo05_update_wrapper():
    """⑤ update_wrapper 用于类装饰器"""
    print("\n⑤ update_wrapper（类装饰器）")

    print(f"  divide.__name__ = {divide.__name__!r}")    # 'divide' ✓
    print(f"  divide.__doc__  = {divide.__doc__!r}")     # 原 docstring ✓
    print(f"  divide(10, 3)  = {divide(10, 3):.4f}")
    print(f"  divide(5, 0)   = {divide(5, 0)}")
    print(f"  调用次数: {divide.call_count}")


# ---------------------------------------------------------------------------
# ⑥ inspect.signature 与 @wraps
# ---------------------------------------------------------------------------

def demo06_signature():
    """⑥ @wraps 让 inspect.signature 能正确显示原函数签名"""
    print("\n⑥ inspect.signature 与 @wraps")

    def validate_args(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @validate_args
    def create_user(name: str, age: int, role: str = "user") -> dict:
        """创建新用户"""
        return {"name": name, "age": age, "role": role}

    # 有 @wraps，signature 指向原函数
    sig = inspect.signature(create_user)
    print(f"  signature: {sig}")
    for name, param in sig.parameters.items():
        print(f"    {name}: default={param.default!r}, annotation={param.annotation}")

    # help() 也正常工作
    print(f"\n  help(create_user).__doc__ = {create_user.__doc__!r}")


if __name__ == "__main__":
    demo01_problem()
    demo02_fixed()
    demo03_what_is_copied()
    demo04_wrapped()
    demo05_update_wrapper()
    demo06_signature()
