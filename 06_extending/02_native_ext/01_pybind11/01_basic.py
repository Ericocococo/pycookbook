"""pybind11 —— 函数绑定基础

三方库。C++17 + Python 3.12。
安装: pip install pybind11   编译器: MSVC / GCC / Clang
运行: python 01_basic.py

演示：
  ① m.def() 绑定普通函数与文档字符串
  ② py::arg() 关键字参数与默认值
  ③ py::overload_cast<> 选择正确的重载版本
  ④ lambda 直接内联绑定（无需独立 C++ 函数名）
  ⑤ 模块属性 m.attr() 设置常量
  ⑥ return_value_policy：reference / copy / take_ownership
"""

CPP = r"""
#include <pybind11/pybind11.h>
#include <string>
#include <cmath>
namespace py = pybind11;

// ① 普通函数
int add(int a, int b) { return a + b; }

// ② 带默认参数的函数
std::string greet(const std::string& name,
                  const std::string& prefix = "Hello") {
    return prefix + ", " + name + "!";
}

// ③ 重载：两个同名函数，参数类型不同
double power(double base, int exp) {
    double r = 1.0;
    for (int i = 0; i < exp; ++i) r *= base;
    return r;
}
double power(double x, double y) { return std::pow(x, y); }

// ⑥ 全局对象（演示 return_value_policy::reference）
static std::string g_msg = "来自 C++ 的问候";

PYBIND11_MODULE(pb_basic, m) {
    m.doc() = "函数绑定基础——pybind11 配方 01";

    // ① 基础：m.def(名称, 函数指针, 文档字符串, 参数注解)
    m.def("add", &add, "两整数求和",
          py::arg("a"), py::arg("b"));

    // ② 默认参数：py::arg("name") = value
    m.def("greet", &greet,
          py::arg("name"), py::arg("prefix") = "Hello",
          "问候语，prefix 有默认值 Hello");

    // ③ 重载：overload_cast<参数类型...>(&fn) 精确选取版本
    m.def("power", py::overload_cast<double, int>(&power),
          py::arg("base"), py::arg("exp"), "整数次幂：base^exp");
    m.def("power_f", py::overload_cast<double, double>(&power),
          py::arg("x"), py::arg("y"), "浮点次幂：x^y");

    // ④ lambda 直接内联，类型由编译器推导，无需独立 C++ 函数
    m.def("clamp", [](double v, double lo, double hi) -> double {
        if (v < lo) return lo;
        if (v > hi) return hi;
        return v;
    }, py::arg("v"), py::arg("lo"), py::arg("hi"),
       "将 v 截断到 [lo, hi]");

    // ⑤ 模块属性：m.attr 设置模块级常量
    m.attr("VERSION") = "1.0";
    m.attr("PI")      = 3.141592653589793;

    // ⑥ return_value_policy
    //   copy（默认）     : 拷贝给 Python，最安全，适合小对象
    //   reference        : 返回 C++ 对象的引用，Python 不拥有，生命周期由 C++ 管理
    //   take_ownership   : Python 负责 delete，配合裸 new 分配的对象使用
    m.def("get_msg", []() -> const std::string& { return g_msg; },
          py::return_value_policy::reference,
          "返回全局字符串引用（C++ 管理生命周期）");
    m.def("set_msg", [](const std::string& s) { g_msg = s; });
}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

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
    print("③ power(2, 10) =", _m.power(2, 10))           # 整数次幂
    print("  power_f(2.0, 0.5) =", _m.power_f(2.0, 0.5))  # 开方 = 1.414...


def demo04_lambda():
    """④ lambda 内联绑定"""
    print("④ clamp(5.0, 0.0, 3.0) =", _m.clamp(5.0, 0.0, 3.0))    # 截到上界 3.0
    print("  clamp(-1.0, 0.0, 1.0) =", _m.clamp(-1.0, 0.0, 1.0))   # 截到下界 0.0
    print("  clamp(0.5, 0.0, 1.0)  =", _m.clamp(0.5, 0.0, 1.0))    # 不变


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
    _m = build_and_import("pb_basic", CPP)
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
