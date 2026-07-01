from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name="mypkg",
    version="0.1.0",
    python_requires=">=3.10",
    ext_modules=cythonize(
        "src/mypkg/*.pyx",
        language_level=3,   # 必须：用 Python 3 语义
        annotate=True,      # 生成 .html 标注哪些行仍有 Python 开销
    ),
    include_dirs=[np.get_include()],
)
