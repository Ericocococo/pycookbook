# 03_extensions —— 从 Python 调用 C 代码的三种方式

| 文件 | 内容 |
|------|------|
| `01_c_extension/` | 原生 C 扩展：Extension 对象、条件编译、numpy 头文件 |
| `02_cython/` | Cython：.pyx → .c → .so，类 Python 语法写 C 速度代码 |
| `03_cffi_ctypes/` | CFFI / ctypes：不写扩展，直接调用现有动态库（demo.py） |


## 适用

- 需要调用 C/C++ 代码提升性能
- 封装现有 C 库给 Python 使用（CFFI/ctypes）
- 用类 Python 语法写高性能数值计算（Cython）

## 不适用

- 纯 Python 性能优化 → numba / numpy vectorize
- 大型 C++/CUDA 项目 → scikit-build-core / meson-python

## 常用命令

```bash
pip install -e .                          # 自动编译 C/Cython 扩展并安装
python setup.py build_ext --inplace       # 原地编译（调试用）
pip install cython numpy                  # Cython 编译前提
pip install cffi                          # CFFI 依赖
```
