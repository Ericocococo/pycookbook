"""shutil —— 归档与压缩(打包 / 解包)

标准库。Python 3.12。运行: python 03_archive.py

生成物放脚本旁 data/ 目录(已被 .gitignore 忽略),运行时清空重建。

支持格式(get_archive_formats()):
  zip    ZIP(需 zlib)      gztar  tar.gz
  tar    未压缩 tar         bztar  tar.bz2      xztar  tar.xz
"""
import shutil
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净工作目录,并造一个待打包的源目录 src/"""
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    src = WORK / "src"
    (src / "logs").mkdir(parents=True)
    (src / "main.py").write_text("print('hi')", encoding="utf-8")
    (src / "readme.txt").write_text("说明文件", encoding="utf-8")
    (src / "logs" / "run.log").write_text("log line", encoding="utf-8")
    return src


def demo01_formats():
    """① 查看当前环境支持哪些归档格式"""
    print("① 支持的归档格式:")
    for name, desc in shutil.get_archive_formats():
        print(f"  {name:8} {desc}")


def demo02_make_archive(src: Path):
    """② make_archive 打包:base_name 不带扩展名,format 决定扩展名"""
    # base_name 是"不含扩展名的目标路径",root_dir 是要打包的目录
    zip_path = shutil.make_archive(
        base_name=str(WORK / "backup"),   # -> data/backup.zip
        format="zip",
        root_dir=src,                     # 打包 src/ 里的内容
    )
    targz_path = shutil.make_archive(
        base_name=str(WORK / "backup"),
        format="gztar",                   # -> data/backup.tar.gz
        root_dir=src,
    )
    print("② make_archive 打包:")
    print("  zip   ->", Path(zip_path).name, f"({Path(zip_path).stat().st_size} 字节)")
    print("  gztar ->", Path(targz_path).name, f"({Path(targz_path).stat().st_size} 字节)")


def demo03_unpack():
    """③ unpack_archive 解包:格式可由扩展名自动推断"""
    zip_path = WORK / "backup.zip"
    out = WORK / "unpacked"
    shutil.unpack_archive(str(zip_path), str(out))   # 自动识别 zip
    print("③ unpack_archive 解包:")
    for p in sorted(out.rglob("*")):
        print("  ", p.relative_to(out).as_posix())


def demo04_base_dir():
    """④ base_dir:让归档内的文件带上一层目录前缀"""
    src_parent = WORK        # root_dir
    # base_dir='src' -> 归档内路径形如 src/main.py,而非直接 main.py
    p = shutil.make_archive(
        base_name=str(WORK / "with_prefix"),
        format="zip",
        root_dir=src_parent,
        base_dir="src",
    )
    out = WORK / "unpacked2"
    shutil.unpack_archive(p, str(out))
    print("④ base_dir 加目录前缀:")
    for x in sorted(out.rglob("*")):
        print("  ", x.relative_to(out).as_posix())


if __name__ == "__main__":
    src = setup()
    demo01_formats()
    print()
    demo02_make_archive(src)
    print()
    demo03_unpack()
    print()
    demo04_base_dir()
    print("\n产物已生成在:", WORK)
