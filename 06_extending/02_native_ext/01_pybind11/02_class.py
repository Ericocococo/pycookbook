"""pybind11 —— 类绑定

三方库。C++17 + Python 3.12。
安装: pip install pybind11   编译器: MSVC / GCC / Clang
运行: python 02_class.py

演示：
  ① py::class_<T> 基础：构造函数、实例方法
  ② 属性：def_readwrite / def_readonly / def_property_readonly / def_property
  ③ 特殊方法：__repr__ / __str__ / __bool__ / __hash__ / __len__
  ④ 运算符重载：使用 py::self（需 #include <pybind11/operators.h>）
  ⑤ 静态方法 def_static 与工厂函数
  ⑥ pickle 支持：__getstate__ / __setstate__
"""

CPP = r"""
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>  // py::self 运算符语法糖
#include <string>
#include <sstream>
#include <cmath>
#include <stdexcept>
namespace py = pybind11;

class Vector2D {
public:
    double x, y;

    Vector2D(double x = 0.0, double y = 0.0) : x(x), y(y) {}

    // 方法
    double length() const { return std::sqrt(x * x + y * y); }
    double dot(const Vector2D& o) const { return x * o.x + y * o.y; }
    Vector2D normalized() const {
        double len = length();
        if (len == 0.0) throw std::domain_error("零向量无法归一化");
        return {x / len, y / len};
    }

    // 运算符
    Vector2D operator+(const Vector2D& o) const { return {x + o.x, y + o.y}; }
    Vector2D operator-(const Vector2D& o) const { return {x - o.x, y - o.y}; }
    Vector2D operator*(double s)          const { return {x * s,   y * s};   }
    bool     operator==(const Vector2D& o) const { return x == o.x && y == o.y; }
    bool     operator< (const Vector2D& o) const { return length() < o.length(); }

    explicit operator bool() const { return x != 0.0 || y != 0.0; }

    std::string repr() const {
        std::ostringstream ss;
        ss << "Vector2D(" << x << ", " << y << ")";
        return ss.str();
    }

    // pickle：序列化为 tuple（(x, y)），反序列化从 tuple 恢复
    py::tuple getstate() const { return py::make_tuple(x, y); }
    static Vector2D setstate(py::tuple t) {
        if (t.size() != 2) throw std::runtime_error("pickle 状态长度不对");
        return Vector2D(t[0].cast<double>(), t[1].cast<double>());
    }

    // 工厂方法（静态）
    static Vector2D zero()   { return {0.0, 0.0}; }
    static Vector2D unit_x() { return {1.0, 0.0}; }
    static Vector2D unit_y() { return {0.0, 1.0}; }
};

PYBIND11_MODULE(pb_class, m) {
    py::class_<Vector2D>(m, "Vector2D",
        "二维向量类（pybind11 类绑定示例）")

        // ① 构造函数，支持默认参数
        .def(py::init<double, double>(),
             py::arg("x") = 0.0, py::arg("y") = 0.0)

        // ② 属性
        .def_readwrite("x", &Vector2D::x, "x 分量（可读写）")
        .def_readwrite("y", &Vector2D::y, "y 分量（可读写）")
        .def_property_readonly("length",
             &Vector2D::length, "向量模长（只读计算属性）")
        .def_property_readonly("normalized",
             &Vector2D::normalized, "单位向量（只读）")
        // def_property：自定义 getter + setter
        .def_property("x_int",
            [](const Vector2D& v) { return static_cast<int>(v.x); },
            [](Vector2D& v, int xi)  { v.x = static_cast<double>(xi); },
            "x 的整数版（演示 getter/setter）")

        // ③ 普通方法
        .def("dot", &Vector2D::dot, py::arg("other"), "与另一向量做点积")

        // ③ 特殊方法
        .def("__repr__", &Vector2D::repr)
        .def("__str__", [](const Vector2D& v) {
            std::ostringstream ss;
            ss << "(" << v.x << ", " << v.y << ")";
            return ss.str();
        })
        .def("__bool__",  [](const Vector2D& v) { return bool(v); })
        .def("__hash__",  [](const Vector2D& v) {
            // 简单哈希合并（仅演示，实际应用需更健壮）
            size_t h1 = std::hash<double>{}(v.x);
            size_t h2 = std::hash<double>{}(v.y);
            return h1 ^ (h2 << 32 | h2 >> 32);
        })
        .def("__len__", [](const Vector2D&) { return 2; })

        // ④ 运算符（py::self 语法）
        .def(py::self + py::self)         // __add__
        .def(py::self - py::self)         // __sub__
        .def(py::self * double())         // __mul__（标量乘法）
        .def(py::self == py::self)        // __eq__
        .def(py::self < py::self)         // __lt__（用于排序）

        // ⑤ 静态方法（工厂函数）
        .def_static("zero",   &Vector2D::zero,   "零向量 (0, 0)")
        .def_static("unit_x", &Vector2D::unit_x, "x 轴单位向量 (1, 0)")
        .def_static("unit_y", &Vector2D::unit_y, "y 轴单位向量 (0, 1)")

        // ⑥ pickle 支持
        .def("__getstate__", &Vector2D::getstate)
        .def("__setstate__", &Vector2D::setstate);
}
"""

import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

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
    _m = build_and_import("pb_class", CPP)
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
