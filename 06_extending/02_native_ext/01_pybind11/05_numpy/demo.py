"""pybind11 —— NumPy 数组集成

三方库。C++17 + Python 3.12。
安装: pip install pybind11 numpy   编译器: MSVC / GCC / Clang
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① py::array_t<T>：接收 / 返回 NumPy 数组（零拷贝）
  ② unchecked<N>()：无边界检查的快速只读访问（N = 维数）
  ③ mutable_unchecked<N>()：就地修改数组
  ④ 返回新 ndarray：用 py::array_t<T>(shape) 创建并填充
  ⑤ 2D 矩阵访问：unchecked<2>()
  ⑥ py::vectorize()：把标量函数自动向量化
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



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
    _m = build_and_import(HERE, "pb_numpy")
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
