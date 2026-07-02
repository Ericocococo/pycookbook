"""shutil —— 移动与删除

标准库。Python 3.12。运行: python 02_move_remove.py

生成物放脚本旁 data/ 目录(已被 .gitignore 忽略),运行时清空重建。

⚠ rmtree 会递归删除整个目录树,不可逆,务必确认路径正确!
"""
import shutil
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净的工作目录"""
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()


def demo01_move_file():
    """① move 移动文件 / 顺带重命名"""
    src = WORK / "a.txt"
    src.write_text("data", encoding="utf-8")
    (WORK / "dst").mkdir()

    # 移动到目录:文件名不变
    r1 = shutil.move(str(src), str(WORK / "dst"))
    print("① move 文件:")
    print("  移动到目录 ->", Path(r1).relative_to(WORK).as_posix())

    # 移动到不存在的路径 = 重命名
    r2 = shutil.move(r1, str(WORK / "dst" / "renamed.txt"))
    print("  移动并改名 ->", Path(r2).relative_to(WORK).as_posix())


def demo02_move_dir():
    """② move 移动整个目录"""
    src = WORK / "logs"
    src.mkdir()
    (src / "a.log").write_text("x", encoding="utf-8")

    dst = WORK / "archive"
    shutil.move(str(src), str(dst))       # 跨盘时自动退化为"复制+删除源"
    print("② move 目录:")
    print("  logs 存在:", src.exists(), " archive 存在:", dst.exists())
    print("  archive 内容:", [p.name for p in dst.iterdir()])


def demo03_rmtree():
    """③ rmtree 递归删除目录树"""
    tree = WORK / "trash"
    (tree / "sub").mkdir(parents=True)
    (tree / "sub" / "f.txt").write_text("x", encoding="utf-8")
    print("③ rmtree 删除前存在:", tree.exists())
    shutil.rmtree(tree)                   # 整棵删掉
    print("  rmtree 删除后存在:", tree.exists())


def demo04_rmtree_onexc():
    """④ rmtree 错误处理:ignore_errors / onexc 回调(3.12+ 取代 onerror)"""
    # 删除不存在的路径:默认抛异常,ignore_errors=True 则静默
    shutil.rmtree(WORK / "not_exist", ignore_errors=True)
    print("④ rmtree 错误处理:")
    print("  ignore_errors=True 删不存在的路径未报错")

    # onexc:每个删除失败的项都会回调(3.12 新增,参数为异常对象)
    errors = []

    def on_exc(func, path, exc):
        """删除失败回调:func=出错的函数, path=出错路径, exc=异常对象"""
        errors.append(Path(path).name)

    shutil.rmtree(WORK / "still_not_exist", onexc=on_exc)
    print("  onexc 回调捕获失败项数:", len(errors))


if __name__ == "__main__":
    setup()
    demo01_move_file()
    print()
    demo02_move_dir()
    print()
    demo03_rmtree()
    print()
    demo04_rmtree_onexc()
    print("\n产物已生成在:", WORK)
