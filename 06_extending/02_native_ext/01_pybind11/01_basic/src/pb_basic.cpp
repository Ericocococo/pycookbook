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
