# setup.py —— 传统 Python 包构建脚本（setuptools）

| 文件 | 内容 |
|------|------|
| `01_minimal/` | 最小 setup() 调用，核心参数速览 |
| `02_find_packages/` | find_packages / find_namespace_packages 自动发现包 |
| `03_extensions/` |  |
| `01_c_extension/` | 原生 C 扩展：Extension 对象、条件编译、numpy 头文件 |
| `02_cython/` | Cython .pyx → .c → .so 编译流程 |
| `03_cffi_ctypes/` | 不写扩展，直接调用动态库（demo.py） |
| `04_migrate/` | setup.py 与等价 pyproject.toml 并排对照 |


## 适用

- 维护含 C/C++ 扩展的老项目
- 需要在构建时执行任意 Python 逻辑
- 公司内网老构建链路，不支持 PEP 517

## 不适用

- 新纯 Python 项目 → 直接用 pyproject.toml（见 01_pyproject_toml/）
- 需要跨语言构建   → meson-python / scikit-build-core

## 核心速查

```python
from setuptools import setup, find_packages

setup(
    name="mypkg",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=["requests>=2.28"],
    extras_require={"dev": ["pytest", "ruff"]},
    entry_points={"console_scripts": ["mypkg=mypkg.cli:main"]},
)

```

## 常用命令

```bash
pip install -e .                      # 开发模式安装
pip install -e ".[dev]"               # + dev 依赖
python -m build                       # 生成 dist/
python setup.py build_ext --inplace   # 原地编译 C 扩展（调试用）
```
