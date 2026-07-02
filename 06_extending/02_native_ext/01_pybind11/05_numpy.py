"""pybind11 —— NumPy 数组集成

三方库。C++17 + Python 3.12。
安装: pip install pybind11 numpy   编译器: MSVC / GCC / Clang
运行: python 05_numpy.py

演示：
  ① py::array_t<T>：接收 / 返回 NumPy 数组（零拷贝）
  ② unchecked<N>()：无边界检查的快速只读访问（N = 维数）
  ③ mutable_unchecked<N>()：就地修改数组
  ④ 返回新 ndarray：用 py::array_t<T>(shape) 创建并填充
  ⑤ 2D 矩阵访问：unchecked<2>()
  ⑥ py::vectorize()：把标量函数自动向量化
"""

CPP = r"""
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
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

_m = None


def demo01_sum_mean():
    """① 接收数组——array_sum / array_mean"""
    import numpy as np
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    print("① array_sum([1..5]):", _m.array_sum(arr))
    print("  array_mean([1..5]):", _m.array_mean(arr))


def demo02_inplace():
    """② 就地修改——array_scale（mutable_unchecked）"""
    import numpy as np
    arr = np.array([1.0, 2.0, 3.0])
    print("② 修改前:", arr)
    _m.array_scale(arr, 10.0)
    print("  修改后 (*10):", arr)        # 原地修改，无拷贝


def demo03_linspace():
    """③ 返回新数组——linspace"""
    arr = _m.linspace(0.0, 1.0, 6)
    print("③ linspace(0,1,6):", arr)
    print("  类型:", type(arr))


def demo04_2d():
    """④ 2D 矩阵操作"""
    import numpy as np
    mat = np.array([[1.0, 2.0, 3.0],
                    [4.0, 5.0, 6.0],
                    [7.0, 8.0, 9.0]])
    d = _m.diag(mat)
    print("④ diag([[1,2,3],[4,5,6],[7,8,9]]):", d)

    a = np.ones((2, 3))
    b = np.full((2, 3), 2.0)
    print("  mat_add(ones, 2*ones):\n", _m.mat_add(a, b))


def demo05_vectorize():
    """⑤ py::vectorize 自动向量化"""
    import numpy as np
    # 标量调用
    print("⑤ vfunc(1.0):", _m.vfunc(1.0))
    # 1D 数组
    x = np.linspace(0, 2, 5)
    print("  vfunc(linspace(0,2,5)):", _m.vfunc(x))
    # 2D 数组
    x2d = np.array([[0.0, 1.0], [2.0, 3.0]])
    print("  vfunc(2D):\n", _m.vfunc(x2d))


if __name__ == "__main__":
    _m = build_and_import("pb_numpy", CPP)
    if _m is None:
        sys.exit(0)
    demo01_sum_mean()
    print()
    demo02_inplace()
    print()
    demo03_linspace()
    print()
    demo04_2d()
    print()
    demo05_vectorize()
