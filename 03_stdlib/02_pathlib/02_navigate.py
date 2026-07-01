"""
pathlib —— 路径拼接与导航
标准库，无需安装，Python 3.4+
运行：python 02_navigate.py
"""
from pathlib import Path


def demo01_join():
    """① / 运算符拼接路径"""
    base = Path("/data")
    p1 = base / "logs" / "app.log"
    p2 = base / Path("conf/nginx.conf")
    print("① / 拼接:")
    print("  base / 'logs' / 'app.log':", p1, type(p1))
    print("  base / Path(...):", p2, type(p2))


def demo02_modify():
    """② 修改路径各部分（纯计算，不访问磁盘）"""
    p = Path("/data/app.log.gz")
    print("② 修改路径部分:", p)
    print("  with_name('app2.log'):", p.with_name("app2.log"), type(p.with_name("app2.log")))
    print("  with_stem('app2'):", p.with_stem("app2"), type(p.with_stem("app2")))    # stem = 词干
    print("  with_suffix('.bak'):", p.with_suffix(".bak"), type(p.with_suffix(".bak")))


def demo03_resolve_relative():
    """③ resolve 转绝对路径；relative_to 求相对路径；parents 向上遍历"""
    p = Path(__file__).resolve()   # resolve：展开 ./ ../ 符号链接，返回规范化的绝对路径
    print("③ resolve / relative_to / parents:")
    print("  __file__ resolved:", p, type(p))
    print("  parent:", p.parent, type(p.parent))
    print("  parents[1]:", p.parents[1], type(p.parents[1]))
    print("  所有 parents:", list(p.parents), type(list(p.parents)))
    rel = p.relative_to(p.parents[1])   # relative_to：以指定路径为基准，计算当前路径的相对部分
    print("  relative_to parents[1]:", rel, type(rel))


if __name__ == "__main__":
    demo01_join()
    print()
    demo02_modify()
    print()
    demo03_resolve_relative()