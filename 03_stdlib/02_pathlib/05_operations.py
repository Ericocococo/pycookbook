"""
pathlib —— 文件系统操作（创建/重命名/删除）
标准库，无需安装，Python 3.4+
运行：python 05_operations.py
产出写入脚本旁 data/ 目录（已被 .gitignore 忽略）
"""
from pathlib import Path

DATA = Path(__file__).parent / "data"


def demo01_mkdir():
    """① mkdir —— make directory，创建目录"""
    d = DATA / "subdir"
    # parents=True：同时创建所有缺失的父目录（等同于 mkdir -p）
    # exist_ok=True：目录已存在时不抛 FileExistsError
    d.mkdir(parents=True, exist_ok=True)
    print("① mkdir:")
    print("  创建:", d, type(d))
    print("  is_dir:", d.is_dir(), type(d.is_dir()))


def demo02_touch_rename():
    """② touch / rename / replace"""
    DATA.mkdir(exist_ok=True)
    src = DATA / "src.txt"
    dst = DATA / "dst.txt"
    # missing_ok=True：文件不存在时不抛 FileNotFoundError（保证幂等可重复运行）
    dst.unlink(missing_ok=True)
    # touch：源自 Unix touch 命令，文件不存在则创建，已存在则更新访问/修改时间
    src.touch()
    print("② touch / rename:")
    print("  touch:", src, type(src))
    result = src.rename(dst)
    print("  rename ->:", result, type(result))
    print("  dst.exists:", dst.exists(), type(dst.exists()))
    print("  src.exists:", src.exists(), type(src.exists()))


def demo03_unlink_rmdir():
    """③ unlink 删文件 / rmdir 删空目录"""
    DATA.mkdir(exist_ok=True)
    f = DATA / "to_delete.txt"
    f.write_text("bye")
    print("③ unlink / rmdir:")
    print("  删除前 exists:", f.exists(), type(f.exists()))
    # unlink：源自 Unix unlink 系统调用，移除目录项（删除文件）
    f.unlink()
    print("  删除后 exists:", f.exists(), type(f.exists()))

    empty = DATA / "empty_dir"
    empty.mkdir(exist_ok=True)
    # rmdir = remove directory，只能删空目录；非空目录用 shutil.rmtree
    empty.rmdir()
    print("  rmdir 后 is_dir:", empty.is_dir(), type(empty.is_dir()))


if __name__ == "__main__":
    demo01_mkdir()
    print()
    demo02_touch_rename()
    print()
    demo03_unlink_rmdir()