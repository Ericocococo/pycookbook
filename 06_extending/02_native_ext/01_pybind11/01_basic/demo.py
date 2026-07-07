"""pybind11 —— 函数绑定基础

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① m.def() 绑定普通函数与文档字符串
  ② py::arg() 关键字参数与默认值
  ③ py::overload_cast<> 选择正确的重载版本
  ④ lambda 直接内联绑定（无需独立 C++ 函数名）
  ⑤ 模块属性 m.attr() 设置常量
  ⑥ return_value_policy：reference / copy / take_ownership
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))  # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402

_m = None  # 编译后指向扩展模块


def demo01_basic():
    """① 基础函数绑定"""
    print("① add(3, 4) =", _m.add(3, 4), type(_m.add(3, 4)))
    print("  add(a=10, b=20) =", _m.add(a=10, b=20))
    print("  __doc__:", _m.add.__doc__)


def demo02_kwargs():
    """② 关键字参数与默认值"""
    print("② greet('Alice'):", _m.greet("Alice"))
    print("  greet('Bob', prefix='Hi'):", _m.greet("Bob", prefix="Hi"))
    print("  greet(name='Eve'):", _m.greet(name="Eve"))


def demo03_overload():
    """③ 重载函数"""
    print("③ power(2, 10) =", _m.power(2, 10))  # 整数次幂
    print("  power_f(2.0, 0.5) =", _m.power_f(2.0, 0.5))  # 开方 = 1.414...


def demo04_lambda():
    """④ lambda 内联绑定"""
    print("④ clamp(5.0, 0.0, 3.0) =", _m.clamp(5.0, 0.0, 3.0))  # 截到上界 3.0
    print("  clamp(-1.0, 0.0, 1.0) =", _m.clamp(-1.0, 0.0, 1.0))  # 截到下界 0.0
    print("  clamp(0.5, 0.0, 1.0)  =", _m.clamp(0.5, 0.0, 1.0))  # 不变


def demo05_attrs():
    """⑤ 模块属性"""
    print("⑤ VERSION:", _m.VERSION, type(_m.VERSION))
    print("  PI:", _m.PI, type(_m.PI))


def demo06_return_policy():
    """⑥ return_value_policy::reference"""
    msg = _m.get_msg()
    print("⑥ get_msg():", msg)
    _m.set_msg("已修改")
    print("  修改后 get_msg():", _m.get_msg())
    _m.set_msg("来自 C++ 的问候")  # 复原


if __name__ == "__main__":
    # _m = build_and_import(HERE, "pb_basic", 'auto')
    _m = build_and_import(HERE, "pb_basic", 'msvc')
    # _m = build_and_import(HERE, "pb_basic", 'mingw')
    if _m is None:
        sys.exit(0)
    demo01_basic()
    print()
    demo02_kwargs()
    print()
    demo03_overload()
    print()
    demo04_lambda()
    print()
    demo05_attrs()
    print()
    demo06_return_policy()
