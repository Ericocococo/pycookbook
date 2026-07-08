"""无参装饰器 —— @deco 基本形式

Python 3.12。
运行: python 04_decorator.py

装饰器：接收函数并返回新函数的高阶函数。
@deco 是语法糖，等价于 func = deco(func)。
配合 @wraps 保留原函数的 __name__ / __doc__ / __annotations__ 等元信息。

演示：
  ① 装饰器本质：手动等价写法
  ② @wraps：保留函数元信息（为什么必须加）
  ③ 实用 demo A：计时器
  ④ 实用 demo B：日志
  ⑤ 实用 demo C：重试（含异常处理）
  ⑥ 堆叠多个装饰器的执行顺序
"""

import time
import functools


# ---------------------------------------------------------------------------
# ① 装饰器本质
# ---------------------------------------------------------------------------

def shout(func):
    """简单装饰器：把函数返回值转成大写"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return str(result).upper()
    return wrapper


def demo01_basic():
    """① 装饰器本质：@deco 等价于 func = deco(func)"""
    print("① 装饰器本质")

    # 手动等价写法
    def greet(name: str) -> str:
        return f"hello, {name}"

    shouted_greet = shout(greet)        # 等价于 @shout
    print(f"  手动: {shouted_greet('alice')}")

    # 语法糖写法
    @shout
    def greet2(name: str) -> str:
        return f"hello, {name}"

    print(f"  @deco: {greet2('alice')}")

    # 装饰后 greet2 已经是 wrapper，不是原来的 greet2
    print(f"  greet2.__name__ = {greet2.__name__!r}")   # 'wrapper'，元信息丢失了！


# ---------------------------------------------------------------------------
# ② @wraps
# ---------------------------------------------------------------------------

def better_shout(func):
    """加了 @wraps 的装饰器：保留元信息"""
    @functools.wraps(func)              # 把 func 的元信息复制给 wrapper
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return str(result).upper()
    return wrapper


@better_shout
def greet_polite(name: str) -> str:
    """礼貌地问候"""
    return f"hello, {name}"


def demo02_wraps():
    """② @wraps 保留 __name__ / __doc__ / __wrapped__"""
    print("\n② @wraps 的重要性")

    print(f"  greet_polite('Bob') = {greet_polite('Bob')}")
    print(f"  __name__     = {greet_polite.__name__!r}")      # 'greet_polite'，正确
    print(f"  __doc__      = {greet_polite.__doc__!r}")       # 原 docstring
    print(f"  __wrapped__  = {greet_polite.__wrapped__}")     # 原函数引用


# ---------------------------------------------------------------------------
# ③ 计时器
# ---------------------------------------------------------------------------

def timeit(func):
    """计时装饰器：打印函数耗时"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [{func.__name__}] 耗时 {elapsed * 1000:.3f} ms")
        return result
    return wrapper


@timeit
def slow_sum(n: int) -> int:
    """模拟耗时计算"""
    total = 0
    for i in range(n):
        total += i
    return total


def demo03_timeit():
    """③ 计时器装饰器"""
    print("\n③ 计时器")
    result = slow_sum(1_000_000)
    print(f"  结果: {result}")


# ---------------------------------------------------------------------------
# ④ 日志
# ---------------------------------------------------------------------------

def log_call(func):
    """日志装饰器：记录调用参数和返回值"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"  → 调用 {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"  ← {func.__name__} 返回 {result!r}")
        return result
    return wrapper


@log_call
def divide(a: float, b: float) -> float:
    """除法"""
    return a / b


@log_call
def greet_user(name: str, formal: bool = False) -> str:
    prefix = "您好" if formal else "嗨"
    return f"{prefix}，{name}！"


def demo04_logging():
    """④ 日志装饰器"""
    print("\n④ 日志装饰器")
    divide(10, 3)
    greet_user("Alice", formal=True)


# ---------------------------------------------------------------------------
# ⑤ 重试
# ---------------------------------------------------------------------------

def retry(func):
    """重试装饰器：失败时最多重试 3 次（固定次数版；带参数版见 05_decorator_args.py）"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(1, 4):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"  [{func.__name__}] 第 {attempt} 次失败: {e}")
                if attempt == 3:
                    raise
    return wrapper


import random
_call_count = 0

@retry
def flaky_api() -> str:
    """模拟不稳定的 API，前两次必失败"""
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ConnectionError("网络超时")
    return "成功响应"


def demo05_retry():
    """⑤ 重试装饰器"""
    print("\n⑤ 重试装饰器")
    global _call_count
    _call_count = 0
    result = flaky_api()
    print(f"  最终结果: {result!r}")


# ---------------------------------------------------------------------------
# ⑥ 堆叠多个装饰器
# ---------------------------------------------------------------------------

def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"**{func(*args, **kwargs)}**"
    return wrapper


def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"_{func(*args, **kwargs)}_"
    return wrapper


@bold
@italic
def say(text: str) -> str:
    return text


def demo06_stacking():
    """⑥ 堆叠：从下往上应用，从外往里执行"""
    print("\n⑥ 堆叠多个装饰器")

    # @bold @italic func 等价于 bold(italic(func))
    # 调用时：bold.wrapper → italic.wrapper → func
    print(f"  @bold @italic say('hello') = {say('hello')}")

    # 验证顺序
    def mark(label):
        def deco(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                print(f"    [{label}] 进入")
                r = func(*args, **kwargs)
                print(f"    [{label}] 退出")
                return r
            return wrapper
        return deco

    @mark("A")
    @mark("B")
    @mark("C")
    def target():
        print("    [target] 执行")

    target()
    # 输出顺序：A进 → B进 → C进 → target → C退 → B退 → A退


if __name__ == "__main__":
    demo01_basic()
    demo02_wraps()
    demo03_timeit()
    demo04_logging()
    demo05_retry()
    demo06_stacking()
