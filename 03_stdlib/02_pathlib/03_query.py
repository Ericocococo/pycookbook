"""
pathlib —— 文件系统查询与目录遍历
标准库，无需安装，Python 3.4+
运行：python 03_query.py
"""
from pathlib import Path


def demo_exists():
    """① 存在性与类型判断"""
    here = Path(__file__).parent
    f    = Path(__file__)
    print("① 存在性与类型:")
    print("  目录 exists:", here.exists(), type(here.exists()))
    print("  目录 is_dir:", here.is_dir(), type(here.is_dir()))
    print("  目录 is_file:", here.is_file(), type(here.is_file()))
    print("  文件 is_file:", f.is_file(), type(f.is_file()))
    print("  不存在路径:", Path("no_such").exists(), type(Path("no_such").exists()))


def demo_stat():
    """② stat —— 获取文件元数据"""
    p  = Path(__file__)
    st = p.stat()
    print("② stat:", p.name)
    print("  st_size (字节):", st.st_size, type(st.st_size))
    print("  st_mtime:", st.st_mtime, type(st.st_mtime))
    print("  stat 对象:", st, type(st))


def demo_glob():
    """③ glob / rglob / iterdir 遍历"""
    stdlib = Path(__file__).parent.parent   # 03_stdlib/
    py_files = sorted(stdlib.rglob("*.py"))
    print("③ rglob('*.py') 结果（前 5 条）:")
    for f in py_files[:5]:
        print(" ", f, type(f))
    print("  共找到:", len(py_files), type(len(py_files)))

    print("  iterdir(本目录):")
    for item in Path(__file__).parent.iterdir():
        print("   ", item.name, type(item))


if __name__ == "__main__":
    demo_exists()
    print()
    demo_stat()
    print()
    demo_glob()
