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

## 快速上手

### 方式一：直接运行 demo.py（推荐）

`demo.py` 首次运行时自动触发 CMake 编译，之后直接输出结果，无需手动 cmake。

```bash
# 进入任意一个配方目录
cd 01_basic

# 运行（首次自动编译 C++，编译完直接跑 demo）
python demo.py
```

首次输出示例：
```
[CMake] 编译 pb_basic ...
① add(3, 4) = 7 <class 'int'>
  add(a=10, b=20) = 30
...
```

之后再运行跳过编译，直接输出结果。

### 方式二：手动 CMake 构建

#### 两套工具链 configure 命令的区别

| | MinGW | MSVC |
|---|---|---|
| **cmake / ninja 来源** | CLion 内置 | VS 自带（`Common7/IDE/...`） |
| **编译器写法** | 完整路径（`g++.exe`） | 只写 `cl.exe`，靠 vcvarsall.bat 激活的环境变量找到它 |
| **链接器** | 不指定（g++ 自带链接器，自成体系） | 显式指定 `link.exe`，防止 CLion MinGW 的 `ld.exe` 排在前面被误用 |
| **引号** | 无（路径在 `ProgramData` 下，无空格） | 有（路径含 `Program Files`，有空格必须加引号） |

---

#### 工具链一：MSVC（cl.exe）—— 推荐，兼容性最好

##### 第一步：验证工具链

打开 **Developer Command Prompt for VS 2026**（开始菜单搜索），依次运行：

```cmd
cl
```
预期：输出 `Microsoft (R) C/C++ Optimizing Compiler Version 19.x`

```cmd
link
```
预期：输出 `Microsoft (R) Incremental Linker`
> **坑**：若输出是 `GNU ld`，说明 CLion / MinGW 的 `ld.exe` 排在 MSVC 前面，会导致编译器用 cl.exe、链接器却用 ld.exe，cmake 报大量 `cannot find /nologo` 错误。遇到这种情况见下方"link.exe 被 MinGW 覆盖时"。

```cmd
where link
```
预期：第一行包含 `Microsoft Visual Studio`，不是 CLion / MinGW 路径

```cmd
"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --version
```
预期：输出 `cmake version 3.x`

```cmd
"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe" --version
```
预期：输出版本号，如 `1.12.1`

---

##### 第二步：进入配方目录，创建 build

```cmd
cd D:\workspace\pycharm_workspace\d\pycookbook\06_extending\02_native_ext\01_pybind11\01_basic
mkdir build
cd build
```

---

##### 第三步：cmake configure

**正常情况**（link 指向 MSVC）：

环境变量简写版（先设置变量，命令更简洁）：
```cmd
set CMAKE="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set NINJA="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"

%CMAKE% .. -G Ninja -DCMAKE_MAKE_PROGRAM=%NINJA% -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=cl.exe
```

完整版（直接写路径，不依赖变量）：
```cmd
"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" .. ^
  -G Ninja ^
  -DCMAKE_MAKE_PROGRAM="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_CXX_COMPILER=cl.exe
```

**link.exe 被 MinGW 覆盖时**（`where link` 第一行不是 MSVC 路径，需显式指定链接器）：

环境变量简写版：
```cmd
set CMAKE="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set NINJA="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
set CXX="D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe"
set LD="D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe"

%CMAKE% .. -G Ninja -DCMAKE_MAKE_PROGRAM=%NINJA% -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=%CXX% -DCMAKE_LINKER=%LD%
```

完整版：
```cmd
"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" .. ^
  -G Ninja ^
  -DCMAKE_MAKE_PROGRAM="D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_CXX_COMPILER="D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe" ^
  -DCMAKE_LINKER="D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe"
```

预期输出末尾：`-- Build files have been written to: ...`

---

##### 第四步：cmake build

环境变量简写版（沿用第三步设置的 `%CMAKE%`）：
```cmd
%CMAKE% --build .
```

完整版：
```cmd
"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --build .
```

预期：输出编译日志，最后一行类似 `[2/2] Linking CXX shared module pb_basic...pyd`

---

##### 第五步：运行 demo

```cmd
cd ..
python demo.py
```

---

#### 工具链二：MinGW / GCC（CLion 内置 g++）

##### 第一步：验证工具链

在任意 cmd / PowerShell / Windows Terminal 里运行（不需要激活 MSVC 环境）：

```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe" --version
```
预期：输出 `g++ (MinGW-W64 ...) x.x.x`

```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\ld.exe" --version
```
预期：输出 `GNU ld (GNU Binutils) x.x`

```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe" --version
```
预期：输出 `cmake version x.x`

```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe" --version
```
预期：输出版本号，如 `1.13.2`

---

##### 第二步：进入配方目录，创建 build

```cmd
cd D:\workspace\pycharm_workspace\d\pycookbook\06_extending\02_native_ext\01_pybind11\01_basic
mkdir build
cd build
```

---

##### 第三步：cmake configure

环境变量简写版：
```cmd
set CMAKE="D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe"
set NINJA="D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe"
set CXX="D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe"

%CMAKE% .. -G Ninja -DCMAKE_MAKE_PROGRAM=%NINJA% -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=%CXX%
```

完整版：
```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe" .. ^
  -G Ninja ^
  -DCMAKE_MAKE_PROGRAM="D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_CXX_COMPILER="D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe"
```

预期输出末尾：`-- Build files have been written to: ...`

---

##### 第四步：cmake build

环境变量简写版（沿用第三步设置的 `%CMAKE%`）：
```cmd
%CMAKE% --build .
```

完整版：
```cmd
"D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe" --build .
```

预期：输出编译日志，最后一行类似 `[2/2] Linking CXX shared module pb_basic...pyd`

---

##### 第五步：运行 demo

```cmd
cd ..
python demo.py
```

### 方式三：CLion 打开单个配方

1. `File → Open` → 选择 `01_basic/` 文件夹（CMakeLists.txt 所在目录）
2. CLion 自动识别 CMake 项目并配置工具链
3. 点击 **Build** 编译 C++ 扩展
4. 终端里运行 `python demo.py`

### 一次运行所有配方

```bash
# 在 01_pybind11/ 目录下执行
for d in 01_basic 02_class 03_inheritance 04_stl 05_numpy 06_exceptions 07_callbacks 08_advanced; do
    echo "=== $d ==="
    python $d/demo.py
done
```

---

## 前置依赖

```bash
pip install pybind11 numpy
```

工具链（与 cppcookbook 一致）：

**MSVC 工具链**（VS 自带 CMake / Ninja）

| 工具 | 路径 |
|------|------|
| vcvarsall.bat | `D:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat` |
| cl.exe | `D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe` |
| link.exe | `D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe` |
| cmake.exe | `D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe` |
| ninja.exe | `D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe` |

**MinGW 工具链**（CLion 内置 CMake / Ninja / g++）

| 工具 | 路径 |
|------|------|
| g++.exe | `D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe` |
| cmake.exe | `D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe` |
| ninja.exe | `D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe` |

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
