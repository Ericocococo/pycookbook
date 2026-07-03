"""os.path —— 字符串路径函数

标准库,无需安装,Python 3.12。运行: python 01_path.py

os.path 与 pathlib 的分工:
  os.path  —— 函数式,字符串输入/输出,维护旧代码或需要纯 str 路径时使用
  pathlib  —— 面向对象封装,推荐新代码使用(见 02_pathlib)

本文件只演示 os.path 独有的字符串函数;不重复 pathlib 的 OOP 操作。

生成物放脚本旁 data/ 目录(已被 .gitignore 忽略),运行时清空重建。
"""
import os
import os.path
import shutil
import time
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备干净的工作目录"""
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()


def demo01_join_split():
    """① join / split / dirname / basename / splitext / splitdrive"""
    print("① join / split / dirname / basename / splitext / splitdrive:")

    # join:跨平台路径拼接(自动使用当前系统分隔符)
    joined = os.path.join("home", "user", "projects", "main.py")
    print("  join('home','user','projects','main.py'):", joined)

    # split:分成 (头部目录, 尾部文件名) 两部分
    p = os.path.join("home", "user", "projects", "main.py")
    head, tail = os.path.split(p)
    print("  split ->  head:", head, " tail:", tail)

    # dirname / basename:分别取目录部分和文件名部分
    print("  dirname :", os.path.dirname(p))
    print("  basename:", os.path.basename(p))

    # splitext:分离主文件名与扩展名(只取最后一个点)
    print("  splitext('main.py')      :", os.path.splitext("main.py"))
    print("  splitext('archive.tar.gz'):", os.path.splitext("archive.tar.gz"))

    # splitdrive:分离盘符与路径(Windows 有盘符,其他系统盘符为空字符串)
    if os.name == "nt":
        demo_path = r"C:\Users\user\Desktop\file.txt"
    else:
        demo_path = "/home/user/file.txt"
    drive, rest = os.path.splitdrive(demo_path)
    print(f"  splitdrive({demo_path!r})")
    print(f"    drive={drive!r}, rest={rest!r}")


def demo02_predicates():
    """② exists / isfile / isdir / isabs / islink"""
    tmp_file = WORK / "hello.txt"
    tmp_file.write_text("hi", encoding="utf-8")
    f_str = str(tmp_file)

    print("② 路径谓词(均返回 bool):")
    print("  exists(文件) :", os.path.exists(f_str),      type(os.path.exists(f_str)))
    print("  exists(目录) :", os.path.exists(str(WORK)),  type(os.path.exists(str(WORK))))
    print("  exists(不存在):", os.path.exists(str(WORK / "ghost.txt")))
    print()
    print("  isfile(文件) :", os.path.isfile(f_str))
    print("  isfile(目录) :", os.path.isfile(str(WORK)))
    print("  isdir(目录)  :", os.path.isdir(str(WORK)))
    print("  isdir(文件)  :", os.path.isdir(f_str))
    print()
    print("  isabs(绝对路径):", os.path.isabs(f_str))
    print("  isabs(相对路径):", os.path.isabs("rel/path.txt"))
    print("  islink(普通文件):", os.path.islink(f_str))   # 非符号链接返回 False


def demo03_abs_real_expand():
    """③ abspath / realpath / expanduser / expandvars / normpath"""
    print("③ 路径规范化与展开:")

    # abspath:相对路径 -> 绝对路径(cwd + 相对路径)
    print("  abspath('.')   :", os.path.abspath("."))
    print("  abspath('data'):", os.path.abspath("data"))

    # realpath:绝对路径 + 解析所有符号链接(Linux/Mac 效果更明显)
    print("  realpath('.')  :", os.path.realpath("."))

    # expanduser:展开 ~ 为用户主目录
    print("  expanduser('~')      :", os.path.expanduser("~"))
    print("  expanduser('~/docs') :", os.path.expanduser("~/docs"))

    # expandvars:展开路径中的环境变量
    # Windows 支持 %VAR% 和 $VAR;Unix 支持 $VAR 和 ${VAR}
    if os.name == "nt":
        tpl = "%USERPROFILE%\\Documents"
    else:
        tpl = "$HOME/Documents"
    expanded = os.path.expandvars(tpl)
    print(f"  expandvars({tpl!r}):", expanded)

    # normpath:规范化路径分隔符,消除冗余 ./ 和 ../
    messy = os.path.join("a", "", "b", "..", "b", ".", "c")
    clean = os.path.normpath(messy)
    print("  normpath 前:", repr(messy))
    print("  normpath 后:", repr(clean))


def demo04_size_time():
    """④ getsize / getmtime / getctime / getatime（操作 data/ 里的文件）"""
    tmp = WORK / "sample.txt"
    tmp.write_text("hello world", encoding="utf-8")
    p_str = str(tmp)

    sz  = os.path.getsize(p_str)
    mt  = os.path.getmtime(p_str)   # 修改时间 mtime（Unix 时间戳,浮点秒）
    ct  = os.path.getctime(p_str)   # Windows:创建时间; Linux:inode 变更时间
    at  = os.path.getatime(p_str)   # 最后访问时间 atime

    print("④ 文件大小与时间戳:")
    print("  文件:", tmp.name)
    print("  getsize :", sz, "字节", type(sz))
    print("  getmtime:", mt, "->", time.ctime(mt))
    print("  getctime:", ct, "->", time.ctime(ct), "(Win=创建时间, Linux=inode变更)")
    print("  getatime:", at, "->", time.ctime(at))


def demo05_common_rel():
    """⑤ commonpath / commonprefix / relpath"""
    # 用实际路径构造示例,保证跨平台正确
    base = str(WORK)
    p1 = os.path.join(base, "app", "main.py")
    p2 = os.path.join(base, "app", "utils.py")
    p3 = os.path.join(base, "lib", "helper.py")
    paths = [p1, p2, p3]

    print("⑤ commonpath / commonprefix / relpath:")
    print("  路径列表:")
    for p in paths:
        print("   ", p)

    # commonpath:返回规范化的公共前缀目录(比 commonprefix 更准确)
    cp = os.path.commonpath(paths)
    print("  commonpath   :", cp)

    # commonprefix:纯字符串前缀(可能截断到路径分隔符中间,不够精确)
    raw = os.path.commonprefix(paths)
    print("  commonprefix :", repr(raw), "(注意:纯字符串,不保证是完整目录名)")

    # relpath:计算从 start 到 path 的相对路径
    print("  relpath(p1, base):", os.path.relpath(p1, base))
    print("  relpath(p3, base):", os.path.relpath(p3, base))


if __name__ == "__main__":
    setup()
    demo01_join_split()
    print()
    demo02_predicates()
    print()
    demo03_abs_real_expand()
    print()
    demo04_size_time()
    print()
    demo05_common_rel()
    print("\n产物已生成在:", WORK)
