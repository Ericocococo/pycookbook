# pybind11 —— C++ 与 Python 双向绑定（C++ Extension 的首选方案）

每个子目录是一个独立的 CMake 项目，可直接用 CLion 打开。

| 目录 | 内容 |
|------|------|
| `01_basic/` | 函数绑定：`m.def` / `py::arg` / 默认参数 / 重载 / lambda / `return_value_policy` |
| `02_class/` | 类绑定：`init` / 方法 / 属性(`readwrite`/`property`) / 运算符 / pickle |
| `03_inheritance/` | 继承与虚函数：Trampoline 类 / `PYBIND11_OVERRIDE` / 纯虚函数 / `keep_alive` |
| `04_stl/` | STL 容器：`vector`/`map`/`set`/`optional`/`variant`/`tuple` 自动转换 + `bind_vector` |
| `05_numpy/` | NumPy 集成：`array_t` / 零拷贝 `unchecked` / `mutable_unchecked` / `vectorize` |
| `06_exceptions/` | 异常互转：标准异常自动映射 / `register_exception` / `error_already_set` |
| `07_callbacks/` | 回调与 `std::function`：存储 Python callable / EventEmitter 示例 |
| `08_advanced/` | 进阶：`enum` / `shared_ptr` / GIL 管理 / `py::capsule` / bytes |
| `_cmake_build.py` | 共享编译辅助（供各 `demo.py` import，不直接运行） |

## 每个子目录的结构

```
01_basic/
├── CMakeLists.txt   ← 独立 CMake 项目，CLion 可直接打开
├── src/
│   └── pb_basic.cpp ← C++ 绑定源码
└── demo.py          ← Python 侧演示（首次运行自动触发 CMake 编译）
```

## 前置依赖

```bash
pip install pybind11 numpy
```

工具链（与 cppcookbook 一致）：

| 工具 | 路径 |
|------|------|
| MSVC cl.exe | `D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe` |
| CMake 4.2.2 | `D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe` |
| Ninja 1.13.2 | `D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe` |
| vcvarsall.bat | `D:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat` |

## 适用

- 性能关键逻辑用 C++ 实现，暴露 Python 调用接口（比纯 Python 快 10~100×）
- 让 Python 访问现有 C++ 库（比 ctypes/cffi 更 Pythonic、类型安全、支持类/继承/异常）
- C++ 主工程需要 Python 脚本层（测试 / 配置 / 胶水代码）

## 不适用

- 纯数值加速且不想写 C++ → numba / Cython 更简单
- 只调用 C 库（无 C++ 类/虚函数/模板） → ctypes / cffi 够用
- 不能安装 MSVC/GCC 的环境 → mypyc / Cython pure-Python 模式

## 核心速查

```cpp
// src/my_ext.cpp
#include <pybind11/pybind11.h>
namespace py = pybind11;

int add(int a, int b) { return a + b; }

PYBIND11_MODULE(my_ext, m) {
    m.doc() = "示例模块";
    m.def("add", &add, py::arg("a"), py::arg("b"), "两数相加");
}
```

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(my_ext LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

execute_process(
    COMMAND "python.exe" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
find_package(pybind11 REQUIRED CONFIG)
pybind11_add_module(my_ext src/my_ext.cpp)
```

```python
# demo.py
from _cmake_build import build_and_import
m = build_and_import(Path(__file__).parent, "my_ext")
print(m.add(1, 2))   # 3
```
