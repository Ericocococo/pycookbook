import sys
from setuptools import setup, Extension

try:
    import numpy as np
    numpy_inc = [np.get_include()]
except ImportError:
    numpy_inc = []

extensions = [
    Extension(
        name="mypkg._speedups",
        sources=["src/mypkg/_speedups.c"],
        include_dirs=["include"] + numpy_inc,
        libraries=["m"],                    # 链接 libm
        extra_compile_args=["-O3"],
    ),
]

if sys.platform == "linux":
    extensions.append(Extension(
        "mypkg._epoll",
        sources=["src/mypkg/_epoll.c"],
    ))

setup(
    name="mypkg",
    version="0.1.0",
    python_requires=">=3.10",
    ext_modules=extensions,
)
