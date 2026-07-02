"""pybind11 —— 回调函数与 std::function

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① std::function<R(Args)> 接收 Python 可调用对象（需 #include <pybind11/functional.h>）
  ② py::function：直接持有 Python callable，延迟调用
  ③ 存储回调：C++ 类持有 py::function，稍后触发（EventEmitter 模式）
  ④ C++ 调用 Python 函数时的 GIL 注意事项
  ⑤ 高阶函数：vec_map / vec_filter / vec_reduce
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



_m = None


def demo01_std_function():
    """① std::function 接收 Python callable"""
    result = _m.apply_int(lambda x: x * x, 7)
    print("① apply_int(x^2, 7):", result, type(result))

    result2 = _m.apply_double(lambda x: x ** 0.5, 2.0)
    print("  apply_double(sqrt, 2.0):", round(result2, 6))

    # 传普通函数也可以
    import math
    print("  apply_double(math.sin, pi/2):", round(_m.apply_double(math.sin, 3.14159 / 2), 4))


def demo02_py_function():
    """② py::function 直接持有"""
    log = []
    _m.call_twice(lambda x: log.append(x), "hello")
    print("② call_twice 结果:", log)


def demo03_higher_order():
    """③ 高阶函数：map / filter / reduce"""
    nums = list(range(1, 11))
    mapped  = _m.vec_map(nums, lambda x: x * x)
    filtered = _m.vec_filter(nums, lambda x: x % 2 == 0)
    total    = _m.vec_reduce(nums, lambda a, b: a + b, 0)
    print("③ vec_map([1..10], x^2):", mapped)
    print("  vec_filter([1..10], even):", filtered)
    print("  vec_reduce([1..10], +, 0):", total)


def demo04_event_emitter():
    """④ EventEmitter：C++ 持有 Python 回调"""
    ee = _m.EventEmitter()
    log = []

    ee.on("data", lambda d: log.append(f"handler1: {d}"))
    ee.on("data", lambda d: log.append(f"handler2: {d!r}"))
    ee.on("close", lambda _: log.append("closed"))

    print("④ listener_count('data'):", ee.listener_count("data"))
    ee.emit("data", "hello")
    ee.emit("data", 42)
    ee.emit("close")
    ee.emit("unknown")   # 没有注册，静默忽略

    for entry in log:
        print(" ", entry)


def demo05_error_in_callback():
    """⑤ 回调抛异常的处理"""
    def bad_callback(x):
        if isinstance(x, int) and x < 0:
            raise ValueError(f"不接受负数: {x}")
        return x

    print("⑤ safe_call(正常):", _m.safe_call(bad_callback, 5))
    try:
        _m.safe_call(bad_callback, -1)
    except ValueError as e:
        print("  safe_call(负数) 捕获:", e)


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_cb")
    if _m is None:
        sys.exit(0)
    demo01_std_function()
    print()
    demo02_py_function()
    print()
    demo03_higher_order()
    print()
    demo04_event_emitter()
    print()
    demo05_error_in_callback()
