"""
pathlib —— 文件系统查询与目录遍历
标准库，无需安装，Python 3.4+
运行：python 03_query.py
"""
from pathlib import Path


def demo01_exists():
    """① 存在性与类型判断"""
    here = Path(__file__).parent
    f    = Path(__file__)
    print("① 存在性与类型:")
    print("  目录 exists:", here.exists(), type(here.exists()))
    print("  目录 is_dir:", here.is_dir(), type(here.is_dir()))
    print("  目录 is_file:", here.is_file(), type(here.is_file()))
    print("  文件 is_file:", f.is_file(), type(f.is_file()))
    print("  不存在路径:", Path("no_such").exists(), type(Path("no_such").exists()))


def demo02_stat():
    """② stat —— 调用系统的 stat() 获取文件元数据（不读文件内容）"""
    p  = Path(__file__)
    st = p.stat()
    print("② stat:", p.name)
    print("  st_size (字节):", st.st_size, type(st.st_size))          # st_size = 文件大小（字节数）
    print("  st_mtime:", st.st_mtime, type(st.st_mtime))              # st_mtime = modification time，修改时间（Unix 时间戳，浮点秒数）
    print("  stat 对象:", st, type(st))


def demo03_glob():
    """③ glob / rglob / iterdir 目录遍历"""
    stdlib = Path(__file__).parent.parent   # 03_stdlib/
    # rglob = recursive glob，递归匹配；glob = 通配符匹配（源自 Unix glob 命令）
    py_files = sorted(stdlib.rglob("*.py"))
    print("③ rglob('*.py') 结果（前 5 条）:")
    for f in py_files[:5]:
        print(" ", f, type(f))
    print("  共找到:", len(py_files), type(len(py_files)))

    # iterdir = iterate directory，遍历目录中的直接子项（不递归）
    print("  iterdir(本目录):")
    for item in Path(__file__).parent.iterdir():
        print("   ", item.name, type(item))


if __name__ == "__main__":
    demo01_exists()
    print()
    demo02_stat()
    print()
    demo03_glob()