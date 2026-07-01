"""
pathlib —— 路径对象创建与基础属性
标准库，无需安装，Python 3.4+
运行：python 01_basic.py
"""
from pathlib import Path, PurePosixPath, PureWindowsPath


def demo01_create():
    """① 创建 Path 对象的几种方式"""
    p1 = Path("a/b/c.txt")       # 相对路径字符串
    p2 = Path("a", "b", "c.txt") # 多段拼接
    p3 = Path.home()              # 用户主目录（home directory）
    p4 = Path.cwd()               # cwd = current working directory，当前工作目录
    print("① 创建方式:")
    print("  字符串:", p1, type(p1))
    print("  多段:", p2, type(p2))
    print("  home:", p3, type(p3))
    print("  cwd:", p4, type(p4))


def demo02_attributes():
    """② 路径各部分属性"""
    p = Path("/data/logs/app.log.gz")
    print("② 属性拆解:", p)
    print("  .name:", p.name, type(p.name))             # 含扩展名的文件名
    print("  .stem:", p.stem, type(p.stem))              # stem = 词干，去掉最后一个后缀的文件名
    print("  .suffix:", p.suffix, type(p.suffix))        # suffix = 后缀，最后一个扩展名（含点）
    print("  .suffixes:", p.suffixes, type(p.suffixes))  # 所有后缀组成的列表（多后缀如 .tar.gz）
    print("  .parent:", p.parent, type(p.parent))        # 上级目录
    print("  .parts:", p.parts, type(p.parts))           # 路径各段拆成元组
    print("  .anchor:", p.anchor, type(p.anchor))        # anchor = 锚点，路径根部分（Unix: /；Windows: C:\）
    print("  .drive:", p.drive, type(p.drive))           # drive = 驱动器，Windows 盘符；Unix 为空字符串


def demo03_pure():
    """③ PurePath —— 纯路径，不访问文件系统，可在任何平台计算跨平台路径"""
    # PurePosixPath：按 POSIX（Portable Operating System Interface，可移植操作系统接口）规则解析
    posix = PurePosixPath("/etc/nginx/nginx.conf")
    # PureWindowsPath：按 Windows 规则解析（盘符、反斜杠），任何平台都可用
    win   = PureWindowsPath("C:/Users/tom/doc.txt")
    print("③ PurePath:")
    print("  PurePosixPath:", posix, type(posix))
    print("  PureWindowsPath:", win, type(win))
    print("  win.drive:", win.drive, type(win.drive))
    print("  win.root:", win.root, type(win.root))
    print("  win.parts:", win.parts, type(win.parts))


if __name__ == "__main__":
    demo01_create()
    print()
    demo02_attributes()
    print()
    demo03_pure()