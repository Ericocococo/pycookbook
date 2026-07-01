"""
pathlib —— 文件系统操作（创建/重命名/删除）
标准库，无需安装，Python 3.4+
运行：python 05_operations.py
产出写入脚本旁 data/ 目录（已被 .gitignore 忽略）
"""
from pathlib import Path

DATA = Path(__file__).parent / "data"


def demo_mkdir():
    """① mkdir —— 创建目录"""
    d = DATA / "subdir"
    d.mkdir(parents=True, exist_ok=True)
    print("① mkdir:")
    print("  创建:", d, type(d))
    print("  is_dir:", d.is_dir(), type(d.is_dir()))


def demo_touch_rename():
    """② touch / rename / replace"""
    DATA.mkdir(exist_ok=True)
    src = DATA / "src.txt"
    dst = DATA / "dst.txt"
    dst.unlink(missing_ok=True)  # 保证幂等
    src.touch()
    print("② touch / rename:")
    print("  touch:", src, type(src))
    result = src.rename(dst)
    print("  rename ->:", result, type(result))
    print("  dst.exists:", dst.exists(), type(dst.exists()))
    print("  src.exists:", src.exists(), type(src.exists()))


def demo_unlink_rmdir():
    """③ unlink 删文件 / rmdir 删空目录"""
    DATA.mkdir(exist_ok=True)
    f = DATA / "to_delete.txt"
    f.write_text("bye")
    print("③ unlink / rmdir:")
    print("  删除前 exists:", f.exists(), type(f.exists()))
    f.unlink()
    print("  删除后 exists:", f.exists(), type(f.exists()))

    empty = DATA / "empty_dir"
    empty.mkdir(exist_ok=True)
    empty.rmdir()
    print("  rmdir 后 is_dir:", empty.is_dir(), type(empty.is_dir()))


if __name__ == "__main__":
    demo_mkdir()
    print()
    demo_touch_rename()
    print()
    demo_unlink_rmdir()
