"""os —— 文件操作

标准库,无需安装,Python 3.12。运行: python 03_file_ops.py

涵盖:remove / unlink / rename / replace / stat / access / chmod / link / symlink
生成物放脚本旁 data/ 目录(已被 .gitignore 忽略),运行时清空重建。

⚠ Windows 下创建符号链接需要管理员权限或开发者模式,脚本会优雅跳过。
"""
import os
import shutil
import stat
import time
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净的工作目录"""
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()


def demo01_remove():
    """① remove / unlink 删除文件"""
    f1 = WORK / "to_delete.txt"
    f2 = WORK / "also_delete.txt"
    f1.write_text("bye", encoding="utf-8")
    f2.write_text("bye", encoding="utf-8")

    print("① remove / unlink:")
    print("  删除前 f1 存在:", f1.exists())
    os.remove(str(f1))                       # 删除文件,不存在则 FileNotFoundError
    print("  os.remove 后 f1 存在:", f1.exists())

    os.unlink(str(f2))                       # unlink 是 remove 的别名(POSIX 命名习惯)
    print("  os.unlink 后 f2 存在:", f2.exists())

    # 安全删除:先检查存在性,避免异常
    missing = WORK / "ghost.txt"
    if os.path.exists(str(missing)):
        os.remove(str(missing))
    else:
        print("  ghost.txt 不存在,安全跳过")


def demo02_rename_replace():
    """② rename / replace（原子替换）"""
    print("② rename / replace:")

    src = WORK / "original.txt"
    src.write_text("原始内容", encoding="utf-8")

    dst = WORK / "renamed.txt"
    os.rename(str(src), str(dst))            # 同盘内接近原子;目标已存在的行为因 OS 而异
    print("  rename 后 original 存在:", src.exists(), "  renamed 存在:", dst.exists())

    # replace:Python 3.3+,原子性更好,目标已存在时直接覆盖(不报错)
    old_content = WORK / "old.txt"
    new_target = WORK / "final.txt"
    old_content.write_text("即将被覆盖", encoding="utf-8")
    new_target.write_text("旧内容", encoding="utf-8")

    os.replace(str(old_content), str(new_target))  # 原子覆盖 new_target
    print("  replace 覆盖后内容:", new_target.read_text(encoding="utf-8"))
    print("  replace 后 old.txt 存在:", old_content.exists())


def demo03_stat():
    """③ stat:st_size / st_mtime / st_mode / st_ino 等字段含义"""
    f = WORK / "stat_demo.txt"
    f.write_text("hello stat", encoding="utf-8")

    r = os.stat(str(f))
    print("③ os.stat() 字段含义:")
    print("  st_size  :", r.st_size, "字节(文件大小)")
    print("  st_mtime :", r.st_mtime, "->", time.ctime(r.st_mtime), "(最后修改时间)")
    print("  st_ctime :", r.st_ctime, "->", time.ctime(r.st_ctime),
          "(Win=创建时间 / Linux=inode变更时间)")
    print("  st_atime :", r.st_atime, "->", time.ctime(r.st_atime), "(最后访问时间)")
    print("  st_mode  :", oct(r.st_mode), "(权限位 + 文件类型掩码)")
    print("  st_ino   :", r.st_ino, "(inode 号,Windows NTFS 有值,FAT32 为 0)")
    print("  st_nlink :", r.st_nlink, "(硬链接数)")


def demo04_access():
    """④ access：F_OK / R_OK / W_OK / X_OK"""
    f = WORK / "access_test.txt"
    f.write_text("test", encoding="utf-8")
    f_str = str(f)

    print("④ os.access(路径, 模式):检查真实权限(不同于 stat 的所有者权限)")
    print("  F_OK(存在)   :", os.access(f_str, os.F_OK), type(os.access(f_str, os.F_OK)))
    print("  R_OK(可读)   :", os.access(f_str, os.R_OK))
    print("  W_OK(可写)   :", os.access(f_str, os.W_OK))
    print("  X_OK(可执行) :", os.access(f_str, os.X_OK))
    print("  F_OK(不存在) :", os.access(str(WORK / "ghost.txt"), os.F_OK))


def demo05_chmod():
    """⑤ chmod：修改权限位（Windows 只支持只读/可写两档）"""
    f = WORK / "chmod_test.txt"
    f.write_text("test data", encoding="utf-8")
    f_str = str(f)

    print("⑤ os.chmod(修改权限位):")
    print("  修改前 W_OK:", os.access(f_str, os.W_OK))

    # stat.S_IREAD = 0o444(只读);stat.S_IWRITE = 0o200(可写)
    os.chmod(f_str, stat.S_IREAD)            # 设为只读
    print("  chmod(S_IREAD=只读) 后 W_OK:", os.access(f_str, os.W_OK))

    os.chmod(f_str, stat.S_IREAD | stat.S_IWRITE)  # 恢复可写
    print("  chmod(S_IREAD|S_IWRITE) 恢复后 W_OK:", os.access(f_str, os.W_OK))

    if os.name != "nt":
        # Unix 完整权限位示例(Windows 会忽略执行位等)
        os.chmod(f_str, 0o644)               # rw-r--r--
        print("  chmod(0o644) mode:", oct(os.stat(f_str).st_mode))


def demo06_link_symlink():
    """⑥ link / symlink / readlink（Windows 需管理员或开发者模式,否则优雅跳过）"""
    src = WORK / "linkable.txt"
    src.write_text("被链接的文件内容", encoding="utf-8")
    src_str = str(src)

    print("⑥ link / symlink / readlink:")

    # 硬链接:两个目录项指向同一 inode(修改任一文件另一个也变)
    hard = WORK / "hardlink.txt"
    try:
        os.link(src_str, str(hard))
        same_inode = os.stat(src_str).st_ino == os.stat(str(hard)).st_ino
        print("  硬链接创建成功  inode 相同:", same_inode)
        print("  硬链接 nlink:", os.stat(src_str).st_nlink, "(应为 2)")
    except OSError as e:
        print("  硬链接跳过:", e)

    # 符号链接:快捷方式,指向目标路径字符串
    sym = WORK / "symlink.txt"
    try:
        os.symlink(src_str, str(sym))
        print("  符号链接创建成功  islink:", os.path.islink(str(sym)))
        print("  readlink ->", os.readlink(str(sym)))
        print("  通过链接读到内容:", sym.read_text(encoding="utf-8"))
    except (OSError, NotImplementedError) as e:
        print("  符号链接跳过(Windows 需管理员权限或开发者模式):",
              type(e).__name__, e)


if __name__ == "__main__":
    setup()
    demo01_remove()
    print()
    demo02_rename_replace()
    print()
    demo03_stat()
    print()
    demo04_access()
    print()
    demo05_chmod()
    print()
    demo06_link_symlink()
    print("\n产物已生成在:", WORK)
