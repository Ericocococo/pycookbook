"""pybind11 —— 异常互转

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① C++ 标准异常自动映射到 Python 异常（pybind11 内置表）
  ② 自定义 C++ 异常注册：py::register_exception<> 映射到 Python RuntimeError 子类
  ③ 自定义异常继承层次：register_exception_translator
  ④ py::error_already_set：C++ 捕获 Python 抛出的异常
  ⑤ 从 C++ 主动抛出 Python 内置异常（pybind11 便捷 API）
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



_m = None


def demo01_std_exceptions():
    """① 标准异常自动映射"""
    mapping = {
        "domain":   ValueError,
        "invalid":  ValueError,
        "range":    IndexError,
        "runtime":  RuntimeError,
        "overflow": OverflowError,
    }
    print("① 标准异常映射：")
    for kind, expected in mapping.items():
        try:
            _m.throw_std(kind)
        except expected as e:
            print(f"  {kind:10s} -> {type(e).__name__}: {e}")


def demo02_custom_exception():
    """② 自定义异常"""
    print("② 自定义异常：")
    for sql in ["", "bad", "SELECT 1"]:
        label = repr(sql)
        try:
            _m.db_query(sql)
            print(f"  db_query({label:15}) -> OK")
        except _m.ConnectionError as e:
            print(f"  db_query({label:15}) -> ConnectionError: {e}")
        except _m.DatabaseError as e:
            print(f"  db_query({label:15}) -> DatabaseError: {e}")


def demo03_exception_hierarchy():
    """③ 异常继承关系"""
    try:
        _m.db_query("")
    except _m.DatabaseError as e:
        # ConnectionError 是 DatabaseError 的子类，catch 到了
        print("③ 用 DatabaseError 捕获 ConnectionError:", type(e).__name__)
    print("  issubclass:", issubclass(_m.ConnectionError, _m.DatabaseError))


def demo04_error_already_set():
    """④ error_already_set：C++ 捕获 Python 异常"""
    def bad_func(x):
        if x > 0:
            raise ValueError(f"x={x} 不合法（Python 抛出）")

    print("④ 传入会抛异常的 Python 函数：")
    try:
        _m.call_py_func(bad_func, 5)
    except ValueError as e:
        print("  最终 Python 侧捕获到:", e)


def demo05_raise_python():
    """⑤ 从 C++ 抛出 Python 内置异常"""
    kinds = ["ValueError", "KeyError", "TypeError", "IndexError"]
    print("⑤ 从 C++ 主动抛出内置异常：")
    for k in kinds:
        try:
            _m.raise_python_exc(k)
        except Exception as e:
            print(f"  {k}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_except")
    if _m is None:
        sys.exit(0)
    demo01_std_exceptions()
    print()
    demo02_custom_exception()
    print()
    demo03_exception_hierarchy()
    print()
    demo04_error_already_set()
    print()
    demo05_raise_python()
