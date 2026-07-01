"""CFFI / ctypes：不写扩展，直接调用现有动态库（.so / .dll）"""

import ctypes
import ctypes.util
import math

# ── ctypes：标准库，调用系统数学库 ────────────────────────────────────────
libname = ctypes.util.find_library("m")
if libname:
    libm = ctypes.CDLL(libname)
    libm.sin.restype  = ctypes.c_double
    libm.sin.argtypes = [ctypes.c_double]
    print("ctypes  sin(π/6) =", libm.sin(math.pi / 6))   # 0.5

# ── CFFI：直接粘贴 C 头文件声明，更安全 ──────────────────────────────────
try:
    import cffi
    ffi = cffi.FFI()
    ffi.cdef("double sin(double x); double cos(double x);")
    lib = ffi.dlopen(ctypes.util.find_library("m"))
    print("cffi    sin(π/6) =", lib.sin(math.pi / 6))
    print("cffi    cos(0)   =", lib.cos(0.0))
except ImportError:
    print("cffi 未安装：pip install cffi")

# ── ctypes 结构体 ─────────────────────────────────────────────────────────
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

p = Point(3.0, 4.0)
print(f"ctypes  Point({p.x}, {p.y})")
