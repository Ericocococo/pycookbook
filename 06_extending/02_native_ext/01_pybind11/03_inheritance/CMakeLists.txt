cmake_minimum_required(VERSION 3.15)
project(pb_inherit LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Python（conda quant312）────────────────────────────────────
set(PYTHON_EXE "D:/ProgramData/anaconda3/envs/quant312/python.exe"
    CACHE FILEPATH "Python 解释器路径")

# ── pybind11（pip install pybind11 后从安装路径加载 CMake 模块）
execute_process(
    COMMAND "${PYTHON_EXE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)
find_package(pybind11 REQUIRED CONFIG)

# ── 扩展模块 ──────────────────────────────────────────────────
pybind11_add_module(pb_inherit src/pb_inherit.cpp)
