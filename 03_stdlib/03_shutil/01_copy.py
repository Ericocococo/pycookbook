"""shutil —— 复制文件与目录

标准库,无需安装,Python 3.12。运行: python 01_copy.py

生成物统一放脚本旁的 data/ 目录(已被根 .gitignore 忽略),运行时清空重建,
运行后可在 IDE 里直接查看产物。

复制函数区别一览:
  copyfile  只复制内容,目标必须是文件路径,不复制权限
  copy      复制内容 + 权限模式(mode),目标可以是目录
  copy2     复制内容 + 全部元数据(权限 + 时间戳等),最接近 cp -p
  copytree  递归复制整个目录树
"""
import shutil
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净的工作目录(data/ 已被 .gitignore 全局忽略)"""
    if WORK.exists():
        shutil.rmtree(WORK)               # 递归删除旧产物,保证每次运行幂等
    WORK.mkdir()


def demo01_copyfile_copy():
    """① copyfile / copy / copy2 的区别"""
    src = WORK / "src.txt"
    src.write_text("hello", encoding="utf-8")

    # copyfile:目标须是文件名,只拷内容
    r1 = shutil.copyfile(src, WORK / "a.txt")

    # copy:目标可给目录,自动沿用原文件名;并复制权限
    (WORK / "sub").mkdir()
    r2 = shutil.copy(src, WORK / "sub")

    # copy2:额外保留时间戳等元数据
    r3 = shutil.copy2(src, WORK / "b.txt")

    print("① 三种复制:")
    print("  copyfile ->", Path(r1).name, type(r1))
    print("  copy 到目录 ->", Path(r2).name, "(自动用原名)")
    print("  copy2 ->", Path(r3).name)

    # 验证 copy2 保留了修改时间(mtime 一致)
    print(src.stat())
    print(Path(r3).stat())
    same_mtime = src.stat().st_mtime == Path(r3).stat().st_mtime
    print("  copy2 保留 mtime:", same_mtime)


def demo02_copytree():
    """② copytree:递归复制整个目录树"""
    src = WORK / "project"
    (src / "logs").mkdir(parents=True)
    (src / "main.py").write_text("print(1)", encoding="utf-8")
    (src / "logs" / "run.log").write_text("log", encoding="utf-8")

    dst = WORK / "backup"
    shutil.copytree(src, dst)             # 目标目录不能已存在(除非 dirs_exist_ok)
    print("② copytree 递归复制:")
    for p in sorted(dst.rglob("*")):
        print("  ", p.relative_to(dst).as_posix())


def demo03_ignore_and_exist():
    """③ ignore 排除模式 + dirs_exist_ok 允许目标已存在(3.8+)"""
    src = WORK / "proj2"
    (src / "logs").mkdir(parents=True)
    (src / "main.py").write_text("x", encoding="utf-8")
    (src / "temp.pyc").write_text("x", encoding="utf-8")
    (src / "logs" / "a.log").write_text("x", encoding="utf-8")

    dst = WORK / "clean"
    # ignore_patterns:生成排除函数,支持通配符(类似 .gitignore)
    shutil.copytree(
        src, dst,
        ignore=shutil.ignore_patterns("*.pyc", "*.log"),
    )
    print("③ ignore 排除 *.pyc / *.log:")
    for p in sorted(dst.rglob("*")):
        print("  ", p.relative_to(dst).as_posix())

    # dirs_exist_ok=True:目标已存在也不报错(合并写入)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print("  dirs_exist_ok=True 二次复制未报错")


def demo04_copymode_copystat():
    """④ 只复制元数据:copymode(权限) / copystat(权限+时间)"""
    a = WORK / "meta_a.txt"
    b = WORK / "meta_b.txt"
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    # 只把 a 的权限模式复制给 b(不动内容)
    shutil.copymode(a, b)
    print("④ copymode / copystat(只搬元数据,不搬内容):")
    print("  copymode 后 b 内容仍是:", b.read_text(encoding="utf-8"))
    shutil.copystat(a, b)                 # 权限 + 访问/修改时间
    print("  copystat 后 b.mtime==a.mtime:",
          a.stat().st_mtime == b.stat().st_mtime)


if __name__ == "__main__":
    setup()
    demo01_copyfile_copy()
    # print()
    # demo02_copytree()
    # print()
    # demo03_ignore_and_exist()
    # print()
    # demo04_copymode_copystat()
    # print("\n产物已生成在:", WORK)
