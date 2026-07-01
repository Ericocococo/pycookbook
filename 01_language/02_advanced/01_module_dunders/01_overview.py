"""
模块特殊属性（dunder 变量）：__file__ / __name__ / __doc__ 等
dunder = double underscore（双下划线），Python 约定的特殊名称前后各两个下划线。
Python 内置，无需安装。Python 3.12。
运行：python 01_overview.py
"""
from pathlib import Path
import os


def demo01_file():
    """① __file__ —— 当前文件路径字符串，常配合 pathlib 定位同级资源"""
    print("① __file__:")
    print("  __file__:", __file__, type(__file__))
    p = Path(__file__)
    print("  Path(__file__):", p, type(p))
    print("  .parent (脚本目录):", p.parent, type(p.parent))
    print("  .resolve (绝对路径):", p.resolve(), type(p.resolve()))


def demo02_name():
    """② __name__ —— 直接运行时为 '__main__'，被 import 时为模块名"""
    print("② __name__:")
    print("  __name__:", __name__, type(__name__))
    print("  是否直接运行:", __name__ == "__main__", type(__name__ == "__main__"))


def demo03_doc():
    """③ __doc__ —— 模块 / 函数 / 类的 docstring（文档字符串），None 表示没写"""
    print("③ __doc__:")
    print("  本模块 __doc__:", repr(__doc__), type(__doc__))
    print("  os.__doc__[:50]:", repr(os.__doc__[:50]), type(os.__doc__[:50]))
    print("  demo03_doc.__doc__:", repr(demo03_doc.__doc__), type(demo03_doc.__doc__))


def demo04_package_spec():
    """④ __package__ / __spec__ —— 模块所属包信息；顶层脚本两者均为 None
    __spec__ = ModuleSpec（模块规格），记录模块名、加载器、来源路径等。
    """
    print("④ __package__ / __spec__:")
    print("  __package__:", __package__, type(__package__))
    print("  __spec__:", __spec__, type(__spec__))
    print("  os.__package__:", os.__package__, type(os.__package__))
    print("  os.__spec__:", os.__spec__, type(os.__spec__))


def demo05_dict():
    """⑤ __dict__ —— 模块的全局命名空间（namespace）字典，即该模块里所有名字"""
    print("⑤ __dict__:")
    keys = sorted(os.__dict__.keys())[:6]
    print("  os.__dict__ 前 6 个 key:", keys, type(keys))
    print("  'path' in os.__dict__:", "path" in os.__dict__, type("path" in os.__dict__))


def demo06_cached():
    """⑥ __cached__ —— 对应的 .pyc 字节码缓存路径；顶层脚本为 None
    .pyc = Python Compiled，解释器把源码编译后缓存的二进制文件，下次导入更快。
    """
    print("⑥ __cached__:")
    # 顶层脚本里 __cached__ 变量不存在，用 globals().get 安全取值
    cached = globals().get("__cached__")
    print("  本脚本 __cached__:", cached, type(cached))
    # os 是 frozen 模块（标准库中直接内嵌进解释器的模块），没有磁盘上的 .pyc，用 getattr 安全取
    os_cached = getattr(os, "__cached__", None)
    print("  os.__cached__:", os_cached, type(os_cached))


def demo07_file_pattern():
    """⑦ 最常见的 __file__ 用法：定位脚本同级的数据目录"""
    BASE = Path(__file__).resolve().parent
    data_dir = BASE / "data"
    config   = BASE / "config.yaml"
    print("⑦ 同级资源定位模式:")
    print("  BASE:", BASE, type(BASE))
    print("  data_dir:", data_dir, type(data_dir))
    print("  config:", config, type(config))


if __name__ == "__main__":
    demo01_file()
    print()
    demo02_name()
    print()
    demo03_doc()
    print()
    demo04_package_spec()
    print()
    demo05_dict()
    print()
    demo06_cached()
    print()
    demo07_file_pattern()