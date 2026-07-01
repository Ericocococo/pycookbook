"""
pathlib —— 路径对象创建与基础属性
标准库，无需安装，Python 3.4+
运行：python 01_basic.py
"""
from pathlib import Path, PurePosixPath, PureWindowsPath


def demo_create():
    """① 创建 Path 对象的几种方式"""
    p1 = Path("a/b/c.txt")       # 相对路径字符串
    p2 = Path("a", "b", "c.txt") # 多段拼接
    p3 = Path.home()              # 用户主目录
    p4 = Path.cwd()               # 当前工作目录
    print("① 创建方式:")
    print("  字符串:", p1, type(p1))
    print("  多段:", p2, type(p2))
    print("  home:", p3, type(p3))
    print("  cwd:", p4, type(p4))


def demo_attributes():
    """② 路径各部分属性"""
    p = Path("/data/logs/app.log.gz")
    print("② 属性拆解:", p)
    print("  .name:", p.name, type(p.name))
    print("  .stem:", p.stem, type(p.stem))
    print("  .suffix:", p.suffix, type(p.suffix))
    print("  .suffixes:", p.suffixes, type(p.suffixes))
    print("  .parent:", p.parent, type(p.parent))
    print("  .parts:", p.parts, type(p.parts))
    print("  .anchor:", p.anchor, type(p.anchor))
    print("  .drive:", p.drive, type(p.drive))


def demo_pure():
    """③ PurePath —— 不访问文件系统的纯路径，可跨平台计算"""
    posix = PurePosixPath("/etc/nginx/nginx.conf")
    win   = PureWindowsPath("C:/Users/tom/doc.txt")
    print("③ PurePath:")
    print("  PurePosixPath:", posix, type(posix))
    print("  PureWindowsPath:", win, type(win))
    print("  win.drive:", win.drive, type(win.drive))
    print("  win.root:", win.root, type(win.root))
    print("  win.parts:", win.parts, type(win.parts))


if __name__ == "__main__":
    demo_create()
    print()
    demo_attributes()
    print()
    demo_pure()
