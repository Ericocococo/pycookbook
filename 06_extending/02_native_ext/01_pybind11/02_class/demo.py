"""pybind11 —— 类绑定

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① py::class_<T> 基础：构造函数、实例方法
  ② 属性：def_readwrite / def_readonly / def_property_readonly / def_property
  ③ 特殊方法：__repr__ / __str__ / __bool__ / __hash__ / __len__
  ④ 运算符重载：使用 py::self（需 #include <pybind11/operators.h>）
  ⑤ 静态方法 def_static 与工厂函数
  ⑥ pickle 支持：__getstate__ / __setstate__
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402


import pickle

_m = None  # 编译后指向扩展模块


def demo01_init_methods():
    """① 构造函数与实例方法"""
    v = _m.Vector2D(3.0, 4.0)
    print("① Vector2D(3, 4)")
    print("  v.x, v.y =", v.x, v.y)
    print("  v.length =", v.length)
    print("  v.dot(Vector2D(1,0)) =", v.dot(_m.Vector2D(1, 0)))


def demo02_properties():
    """② 属性访问"""
    v = _m.Vector2D(3.0, 4.0)
    print("② v.normalized:", v.normalized.x, v.normalized.y)
    v.x = 0.0
    print("  改 x=0 后 v.length:", v.length)
    v.x_int = 5              # 通过 setter 赋值
    print("  v.x_int=5 后 v.x:", v.x, type(v.x))


def demo03_special():
    """③ 特殊方法"""
    v = _m.Vector2D(3.0, 4.0)
    z = _m.Vector2D.zero()
    print("③ repr:", repr(v))
    print("  str:", str(v))
    print("  bool(v):", bool(v), "  bool(zero):", bool(z))
    print("  hash(v):", hex(hash(v)))
    print("  len(v):", len(v))


def demo04_operators():
    """④ 运算符重载"""
    a = _m.Vector2D(1.0, 2.0)
    b = _m.Vector2D(3.0, 4.0)
    print("④ a + b:", repr(a + b))
    print("  a - b:", repr(a - b))
    print("  a * 2.0:", repr(a * 2.0))
    print("  a == b:", a == b)
    print("  a < b (按模长):", a < b)


def demo05_static():
    """⑤ 静态方法"""
    print("⑤ zero():",   repr(_m.Vector2D.zero()))
    print("  unit_x():", repr(_m.Vector2D.unit_x()))
    print("  unit_y():", repr(_m.Vector2D.unit_y()))


def demo06_pickle():
    """⑥ pickle 序列化"""
    v = _m.Vector2D(1.5, 2.5)
    data = pickle.dumps(v)
    v2 = pickle.loads(data)
    print("⑥ 原始:", repr(v))
    print("  序列化字节数:", len(data))
    print("  反序列化:", repr(v2))
    print("  相等:", v == v2)


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_class")
    if _m is None:
        sys.exit(0)
    demo01_init_methods()
    print()
    demo02_properties()
    print()
    demo03_special()
    print()
    demo04_operators()
    print()
    demo05_static()
    print()
    demo06_pickle()
