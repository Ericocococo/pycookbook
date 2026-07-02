# pybind11 —— C++ 与 Python 双向绑定（C++ Extension 的首选方案）

| 文件 | 内容 |
|------|------|
| `_build.py` | 内部编译工具（供各配方 import，不直接运行） |
| `01_basic.py` | 函数绑定：m.def / py::arg / 默认参数 / 重载 / lambda / return_value_policy |
| `02_class.py` | 类绑定：init / 方法 / 属性(readwrite/property) / 运算符 / pickle |
| `03_inheritance.py` | 继承与虚函数：Trampoline 类 / PYBIND11_OVERRIDE / 纯虚函数 |
| `04_stl.py` | STL 容器：vector/map/set/optional/variant/tuple 自动转换 + bind_vector |
| `05_numpy.py` | NumPy 集成：array_t / 零拷贝 unchecked / mutable_unchecked / vectorize |
| `06_exceptions.py` | 异常互转：标准异常自动映射 / register_exception / error_already_set |
| `07_callbacks.py` | 回调与 std::function：存储 Python 可调用对象 / EventEmitter 示例 |
| `08_advanced.py` | 进阶：enum / shared_ptr / GIL 释放 / py::capsule |


## 前置依赖

  pip install pybind11
  编译器：MSVC（Visual Studio Build Tools）/ GCC / Clang
  可选：pip install numpy（05_numpy.py 需要）

## 适用

- 性能关键逻辑用 C++ 实现，暴露 Python 调用接口（比纯 Python 快 10~100×）
- 让 Python 访问现有 C++ 库（比 ctypes/cffi 更 Pythonic、类型安全、支持类/继承/异常）
- C++ 主工程需要 Python 脚本层（测试 / 配置 / 胶水代码）

## 不适用

- 纯数值加速且不想写 C++ → numba / Cython 更简单
- 只调用 C 库（无 C++ 类/虚函数/模板） → ctypes / cffi 够用
- 不能安装编译器的环境 → mypyc / Cython pure-Python 模式

## 核心速查

```python
#include <pybind11/pybind11.h>
namespace py = pybind11;

int add(int a, int b) { return a + b; }

PYBIND11_MODULE(my_ext, m) {          // my_ext = Python import 名
    m.doc() = "示例模块";
    m.def("add", &add,                // 绑定函数
          py::arg("a"), py::arg("b"), // 参数名（支持关键字调用）
          "两数相加");                 // 文档字符串

    py::class_<Foo>(m, "Foo")         // 绑定类
        .def(py::init<int>())          // 构造函数
        .def_readwrite("x", &Foo::x)  // 可读写成员
        .def("bar", &Foo::bar);        // 绑定方法

    py::enum_<Color>(m, "Color")      // 绑定枚举
        .value("RED",  Color::RED)
        .value("BLUE", Color::BLUE);
}

# Python 侧构建（setup.py + setuptools）
# python setup.py build_ext --inplace

# Python 侧使用
import my_ext
my_ext.add(1, 2)        # 3
my_ext.Color.RED        # Color.RED
| 文件 | 内容 |
|------|------|
| `//` | C++ 侧（my_ext.cpp） |

```
