"""dunder 属性 —— 模块级：__file__ / __name__ / __doc__ / __all__ / __version__ 等

dunder = double underscore，Python 约定的特殊名称前后各两个下划线。
Python 3.12。运行: python 01_module.py

演示：
  ① __file__：当前文件路径，常配合 pathlib 定位资源
  ② __name__：直接运行时为 '__main__'，被 import 时为模块名
  ③ __doc__：模块/函数/类的 docstring
  ④ __package__ / __spec__：包信息（顶层脚本两者均为 None）
  ⑤ __dict__：模块的全局命名空间字典
  ⑥ __cached__：.pyc 字节码缓存路径
  ⑦ __all__ / __version__ / __author__：约定俗成的元数据
  ⑧ __builtins__ / __loader__ / __annotations__：其他模块级属性
"""

import os
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# ① __file__
# ---------------------------------------------------------------------------

def demo01_file():
    """① __file__ —— 当前 .py 文件路径，配合 pathlib 定位同级资源"""
    print("① __file__")

    print(f"  __file__ = {__file__}")
    p = Path(__file__)
    print(f"  Path(__file__).parent      = {p.parent}")
    print(f"  Path(__file__).resolve()   = {p.resolve()}")
    # 最常见的用法：定位项目根或同级 data/ 目录
    print(f"  Path(__file__).parent / 'data' = {p.parent / 'data'}")


# ---------------------------------------------------------------------------
# ② __name__
# ---------------------------------------------------------------------------

def demo02_name():
    """② __name__ —— 直接运行时为 '__main__'，import 时为包路径"""
    print("\n② __name__")

    print(f"  __name__ = {__name__!r}")
    print(f"  是否直接运行: {__name__ == '__main__'}")

    # os 模块被 import，它的 __name__ 就是 'os'
    print(f"  os.__name__ = {os.__name__!r}")


# ---------------------------------------------------------------------------
# ③ __doc__
# ---------------------------------------------------------------------------

def demo03_doc():
    """③ __doc__ —— 对象开头的 docstring，没写则为 None"""
    print("\n③ __doc__")

    print(f"  本模块: {__doc__[:40]!r}...")
    print(f"  os.__doc__[:40]:  {os.__doc__[:40]!r}...")
    print(f"  demo03_doc.__doc__[:30]: {demo03_doc.__doc__[:30]!r}...")


# ---------------------------------------------------------------------------
# ④ __package__ / __spec__
# ---------------------------------------------------------------------------

def demo04_package_spec():
    """④ __package__ / __spec__ —— 包名和模块规格；顶层脚本两者均为 None"""
    print("\n④ __package__ / __spec__")

    print(f"  __package__ = {__package__!r}")
    print(f"  __spec__    = {__spec__!r}            # 顶层脚本为 None")

    print(f"  os.__package__ = {os.__package__!r}")
    print(f"  os.__spec__    = {os.__spec__}")          # ModuleSpec 对象


# ---------------------------------------------------------------------------
# ⑤ __dict__
# ---------------------------------------------------------------------------

def demo05_dict():
    """⑤ __dict__ —— 模块的全局命名空间字典，包含所有定义的变量和函数"""
    print("\n⑤ __dict__")

    # 看 os 模块里有哪些名字
    keys = sorted(os.__dict__.keys())[:8]
    print(f"  os.__dict__ 前 8 个 key: {keys}")
    print(f"  'path' in os.__dict__: {'path' in os.__dict__}")


# ---------------------------------------------------------------------------
# ⑥ __cached__
# ---------------------------------------------------------------------------

def demo06_cached():
    """⑥ __cached__ —— 对应的 .pyc 字节码缓存路径；顶层脚本为 None"""
    print("\n⑥ __cached__")

    cached = globals().get("__cached__")          # 顶层脚本可能没有这个属性
    print(f"  本脚本: {cached!r}")
    os_cached = getattr(os, "__cached__", None)
    print(f"  os:      {os_cached!r}")


# ---------------------------------------------------------------------------
# ⑦ __all__ / __version__ / __author__
# ---------------------------------------------------------------------------

__version__ = "1.0.0"
__author__ = "pycookbook"

def demo07_metadata():
    """⑦ __all__ / __version__ / __author__ —— 约定俗成，非内置，可被工具读取"""
    print("\n⑦ 约定俗成的元数据")

    print(f"  __version__ = {__version__!r}        # setuptools 读取包版本")
    print(f"  __author__  = {__author__!r}")

    # __all__ 控制 from module import * 导出哪些名字
    # 通常定义在模块顶部，这里演示它的值
    all_example: list[str] = ["demo01", "demo02"]  # 示意，不实际定义 __all__
    print(f"  __all__ = {all_example}  # 控制 from xx import *")


# ---------------------------------------------------------------------------
# ⑧ __builtins__ / __loader__ / __annotations__
# ---------------------------------------------------------------------------

def demo08_others():
    """⑧ 其他模块属性：内置命名空间、加载器、模块级注解"""
    print("\n⑧ 其他模块级属性")

    # __builtins__ 包含所有内置函数/异常
    builtins_mod = globals().get("__builtins__")
    if isinstance(builtins_mod, dict):
        print(f"  __builtins__[:5]: {list(builtins_mod.keys())[:5]} (REPL 模式)")
    else:
        print(f"  __builtins__ = {builtins_mod}")

    # __loader__ 记录加载此模块的加载器
    loader = globals().get("__loader__")
    print(f"  __loader__ = {loader!r}")

    # __annotations__ 模块级别的类型注解字典
    anns: dict[str, Any] = {}   # ← 这里 __annotations__ 为空，实际是 from __future__ import annotations 的效果
    print(f"  __annotations__ = {anns}  # 模块级类型注解（PEP 563 下为字符串）")


if __name__ == "__main__":
    demo01_file()
    demo02_name()
    demo03_doc()
    demo04_package_spec()
    demo05_dict()
    demo06_cached()
    demo07_metadata()
    demo08_others()
