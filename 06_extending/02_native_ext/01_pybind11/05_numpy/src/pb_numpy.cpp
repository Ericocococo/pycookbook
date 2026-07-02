#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>   // NumPy 支持
#include <cmath>
#include <stdexcept>
namespace py = pybind11;

// ① 接收 1D double 数组，求和
double array_sum(py::array_t<double> arr) {
    // 调用 unchecked<1>() 前无需检查维数，但不安全（边界不检查）
    auto r = arr.unchecked<1>();   // r 是只读访问器，r(i) 取元素
    double s = 0.0;
    for (py::ssize_t i = 0; i < r.shape(0); ++i)
        s += r(i);
    return s;
}

// ③ 就地乘以系数（mutable 访问）
void array_scale(py::array_t<double> arr, double factor) {
    auto r = arr.mutable_unchecked<1>();  // 可写访问器
    for (py::ssize_t i = 0; i < r.shape(0); ++i)
        r(i) *= factor;
}

// ② 也可用 buffer_info（更通用，支持任意类型 / 步长）
double array_mean(py::array_t<double> arr) {
    py::buffer_info buf = arr.request();  // 获取底层缓冲区信息
    if (buf.ndim != 1)
        throw std::invalid_argument("只接受 1D 数组");
    double* ptr = static_cast<double*>(buf.ptr);
    double s = 0.0;
    for (py::ssize_t i = 0; i < buf.shape[0]; ++i)
        s += ptr[i];
    return s / buf.shape[0];
}

// ④ 返回新数组：linspace
py::array_t<double> linspace(double start, double stop, int num) {
    if (num < 2) throw std::invalid_argument("num 须 >= 2");
    py::array_t<double> result(num);          // 构造形状为 (num,) 的数组
    auto r = result.mutable_unchecked<1>();
    double step = (stop - start) / (num - 1);
    for (int i = 0; i < num; ++i)
        r(i) = start + i * step;
    return result;
}

// ⑤ 2D 矩阵：提取对角线
py::array_t<double> diag(py::array_t<double> mat) {
    auto r = mat.unchecked<2>();     // 2 维只读访问器
    if (r.shape(0) != r.shape(1))
        throw std::invalid_argument("矩阵须为方阵");
    int n = static_cast<int>(r.shape(0));
    py::array_t<double> d(n);
    auto w = d.mutable_unchecked<1>();
    for (int i = 0; i < n; ++i)
        w(i) = r(i, i);
    return d;
}

// 矩阵逐元素加法（演示 2D 写访问）
py::array_t<double> mat_add(py::array_t<double> a, py::array_t<double> b) {
    auto ra = a.unchecked<2>();
    auto rb = b.unchecked<2>();
    if (ra.shape(0) != rb.shape(0) || ra.shape(1) != rb.shape(1))
        throw std::invalid_argument("形状不匹配");
    int rows = static_cast<int>(ra.shape(0));
    int cols = static_cast<int>(ra.shape(1));
    py::array_t<double> c({rows, cols});
    auto rc = c.mutable_unchecked<2>();
    for (int i = 0; i < rows; ++i)
        for (int j = 0; j < cols; ++j)
            rc(i, j) = ra(i, j) + rb(i, j);
    return c;
}

// ⑥ 标量函数：x^2 + sin(x)
double scalar_func(double x) { return x * x + std::sin(x); }

PYBIND11_MODULE(pb_numpy, m) {
    m.doc() = "NumPy 集成——pybind11 配方 05";

    m.def("array_sum",   &array_sum,   py::arg("arr"));
    m.def("array_scale", &array_scale, py::arg("arr"), py::arg("factor"),
          "就地乘以 factor（直接修改传入数组）");
    m.def("array_mean",  &array_mean,  py::arg("arr"));
    m.def("linspace",    &linspace,    py::arg("start"), py::arg("stop"), py::arg("num"));
    m.def("diag",        &diag,        py::arg("mat"));
    m.def("mat_add",     &mat_add,     py::arg("a"), py::arg("b"));

    // ⑥ py::vectorize：接受标量或任意形状数组，自动按元素调用
    m.def("vfunc", py::vectorize(scalar_func), py::arg("x"),
          "向量化 x^2 + sin(x)，自动支持标量、1D、2D 输入");
}
