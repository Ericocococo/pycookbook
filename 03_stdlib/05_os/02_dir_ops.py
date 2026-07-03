"""os —— 目录操作

标准库,无需安装,Python 3.12。运行: python 02_dir_ops.py

涵盖:getcwd / listdir / scandir(DirEntry) / makedirs / rmdir / removedirs / walk
生成物放脚本旁 data/ 目录(已被 .gitignore 忽略),运行时清空重建。
"""
import os
import shutil
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净的工作目录"""
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()


def demo01_getcwd_listdir():
    """① getcwd / listdir（带简单过滤）"""
    print("① getcwd / listdir:")
    cwd = os.getcwd()
    print("  getcwd():", cwd, type(cwd))

    # 准备几个测试条目
    (WORK / "alpha.txt").write_text("1", encoding="utf-8")
    (WORK / "beta.py").write_text("x=1", encoding="utf-8")
    (WORK / "gamma.csv").write_text("x,y", encoding="utf-8")
    (WORK / "subdir").mkdir()

    entries = os.listdir(str(WORK))          # 返回字符串列表(无顺序保证)
    print("  listdir(WORK):", sorted(entries), type(entries))

    # 简单过滤:只保留 .txt 文件
    txts = [e for e in entries if e.endswith(".txt")]
    print("  过滤 .txt:", sorted(txts))

    # 过滤:只保留目录
    dirs = [e for e in entries if os.path.isdir(os.path.join(str(WORK), e))]
    print("  过滤目录  :", sorted(dirs))


def demo02_scandir():
    """② scandir:DirEntry 的 name / path / is_file / is_dir / stat"""
    print("② scandir(DirEntry 有属性缓存,比 listdir+stat 快):")

    # DirEntry 在迭代时把 is_file/is_dir/stat 缓存在 OS 底层目录项里
    # 通常比 listdir + os.stat 少一次系统调用
    with os.scandir(str(WORK)) as it:
        entries = sorted(it, key=lambda e: e.name)

    for entry in entries:
        s = entry.stat()                     # stat 结果也被缓存
        print(
            f"  {entry.name:<14}"
            f" is_file={entry.is_file()}"
            f" is_dir={entry.is_dir()}"
            f" size={s.st_size:>5} B"
        )


def demo03_makedirs_rmdir():
    """③ makedirs（exist_ok=True）/ rmdir / removedirs"""
    print("③ makedirs / rmdir / removedirs:")

    deep = WORK / "lvl1" / "lvl2" / "lvl3"
    os.makedirs(str(deep), exist_ok=True)    # 递归创建多层目录
    print("  makedirs 创建深层目录,存在:", deep.exists())

    # rmdir:只能删空目录(非空会报 OSError)
    os.rmdir(str(deep))
    print("  rmdir(lvl3) 后 lvl3 存在:", deep.exists(),
          "  lvl2 存在:", deep.parent.exists())

    # removedirs:向上递归删除空目录,遇到非空目录停止(不报错)
    os.removedirs(str(deep.parent))          # 删 lvl2,再尝试删 lvl1
    print("  removedirs 后 lvl1 存在:", (WORK / "lvl1").exists())

    # exist_ok=True 幂等性:同一目录创建两次不报错
    os.makedirs(str(WORK / "idempotent"), exist_ok=True)
    os.makedirs(str(WORK / "idempotent"), exist_ok=True)
    print("  exist_ok=True 重复调用不报错 ✓")


def demo04_walk():
    """④ os.walk:topdown=True/False，三元组(root, dirs, files)，dirnames 剪枝"""
    # 构建示例目录树
    root_dir = WORK / "tree"
    (root_dir / "src" / "utils").mkdir(parents=True)
    (root_dir / "src" / "main.py").write_text("print(1)", encoding="utf-8")
    (root_dir / "src" / "utils" / "helper.py").write_text("x=1", encoding="utf-8")
    (root_dir / "tests").mkdir()
    (root_dir / "tests" / "test_main.py").write_text("pass", encoding="utf-8")
    (root_dir / "README.md").write_text("# README", encoding="utf-8")
    (root_dir / ".git").mkdir()              # 模拟 .git 目录,用于演示剪枝

    print("④ os.walk(topdown=True,默认从根到叶):")
    for root, dirs, files in os.walk(str(root_dir)):
        rel = os.path.relpath(root, str(root_dir))
        print(f"  root={rel!r:<20} dirs={sorted(dirs)}  files={sorted(files)}")

    print("\n  topdown=False(从叶到根):")
    for root, dirs, files in os.walk(str(root_dir), topdown=False):
        rel = os.path.relpath(root, str(root_dir))
        print(f"  root={rel!r}")

    print("\n  dirnames 剪枝:原地修改 dirs[:] 跳过 .git 等隐藏目录:")
    for root, dirs, files in os.walk(str(root_dir)):
        # 原地修改 dirs 才能让 walk 真正跳过这些子树
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        rel = os.path.relpath(root, str(root_dir))
        print(f"  root={rel!r:<20} dirs={sorted(dirs)}  files={sorted(files)}")


if __name__ == "__main__":
    setup()
    demo01_getcwd_listdir()
    print()
    demo02_scandir()
    print()
    demo03_makedirs_rmdir()
    print()
    demo04_walk()
    print("\n产物已生成在:", WORK)
