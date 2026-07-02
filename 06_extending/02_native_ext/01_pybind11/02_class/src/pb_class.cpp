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
