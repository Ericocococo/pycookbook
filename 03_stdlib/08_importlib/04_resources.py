"""importlib.resources —— 访问包内嵌资源文件

标准库。Python 3.12。
运行: python 04_resources.py

传统方式用 __file__ 拼路径来读取包内数据文件：
  data_path = Path(__file__).parent / "data" / "config.json"

这在本地开发可以，但打包成 wheel / zip / 冻结可执行文件（PyInstaller）后，
__file__ 可能不存在或路径错误。

importlib.resources 是官方标准方式，在所有场景下都能正确找到文件。

演示目录结构：
  _demo_pkg/
    __init__.py
    data/
      __init__.py   ← 让 data 成为子包，resources 才能访问
      config.json
      words.txt

演示：
  ① files()：获取资源路径对象（推荐，Python 3.9+）
  ② 读取文本文件
  ③ 读取二进制文件
  ④ 列出资源目录内容
  ⑤ as_file()：把资源导出为临时实体文件（兼容需要路径的第三方库）
  ⑥ 与 __file__ 拼路径的对比
"""
import importlib.resources as res
import json
import sys
from pathlib import Path

# 把当前目录加入 sys.path，让 _demo_pkg 可以被导入
sys.path.insert(0, str(Path(__file__).parent))


def demo01_files():
    """① files()：获取资源路径对象（Traversable）

    术语：
      Traversable  类路径对象，支持 / 操作符拼接子路径、read_text()、read_bytes()、
                   iterdir() 等，但不一定是真实磁盘路径（zip 内部也可以）

    res.files(package) 返回包目录对应的 Traversable，
    然后用 / 拼子路径，和 pathlib.Path 一样直觉。
    """
    print("① files() 获取资源路径")

    # 获取 _demo_pkg 的根目录
    pkg_root = res.files("_demo_pkg")
    print("  包根目录:", pkg_root)
    print("  类型:", type(pkg_root).__name__)

    # 拼子路径访问文件
    config_ref = pkg_root / "data" / "config.json"
    print("  config.json 路径对象:", config_ref)


def demo02_read_text():
    """② 读取文本文件

    read_text(encoding=...) 直接返回字符串，最常用。
    """
    print("\n② 读取文本文件")

    # 方式一：files() + / + read_text（推荐）
    text = (res.files("_demo_pkg") / "data" / "words.txt").read_text(encoding="utf-8")
    print("  words.txt 内容:")
    for line in text.splitlines():
        print("   ", line)

    # 方式二：直接访问 JSON
    json_text = (res.files("_demo_pkg") / "data" / "config.json").read_text(encoding="utf-8")
    config = json.loads(json_text)
    print("  config.json 解析结果:", config)


def demo03_read_bytes():
    """③ 读取二进制文件

    图片、模型权重、SQLite 数据库等二进制资源用 read_bytes()。
    """
    print("\n③ 读取二进制")

    raw = (res.files("_demo_pkg") / "data" / "config.json").read_bytes()
    print("  读取到字节数:", len(raw))
    print("  前 20 字节:", raw[:20])


def demo04_iterdir():
    """④ 列出资源目录内容

    iterdir() 像 Path.iterdir()，返回目录下所有条目的 Traversable。
    """
    print("\n④ 列出资源目录")

    data_dir = res.files("_demo_pkg") / "data"
    print("  data/ 目录下的文件:")
    for item in data_dir.iterdir():
        print(f"    {item.name}")


def demo05_as_file():
    """⑤ as_file()：导出为临时实体路径

    某些第三方库（如 sqlite3.connect、PIL.Image.open）只接受真实文件路径，
    不接受 Traversable 对象。as_file() 把资源导出为临时文件，用完自动删除。

    用法：with res.as_file(traversable) as path:
    """
    print("\n⑤ as_file() 导出临时路径")

    config_ref = res.files("_demo_pkg") / "data" / "config.json"

    with res.as_file(config_ref) as path:
        print("  临时路径类型:", type(path).__name__)
        print("  路径:", path)
        print("  文件存在:", path.exists())
        # 这里可以把 path 传给任何只接受路径的库
        content = json.loads(path.read_text(encoding="utf-8"))
        print("  读取结果:", content)

    # with 块结束后，如果资源本来就是磁盘文件，path 仍然存在（不会删除真实文件）
    # 如果资源在 zip 里，as_file 会创建临时文件并在退出时删除


def demo06_vs_file_path():
    """⑥ 与 __file__ 拼路径对比

    __file__ 方式的问题：
      - 打包成 zip 时 __file__ 不存在
      - 打包成冻结可执行（PyInstaller）时路径错误
      - 直接依赖文件系统，在某些只读环境里不可用

    importlib.resources 方式：
      - 在所有场景下都能找到资源
      - 明确声明"这是包的资源"，不依赖运行时目录

    在本地开发阶段两种方式效果一样；
    只要代码可能被打包发布，就应该用 importlib.resources。
    """
    print("\n⑥ __file__ 拼路径 vs importlib.resources")

    # __file__ 方式（脆弱）
    old_way = Path(__file__).parent / "_demo_pkg" / "data" / "config.json"
    print("  __file__ 方式路径:", old_way)
    print("  当前存在:", old_way.exists())

    # importlib.resources 方式（健壮）
    new_way = res.files("_demo_pkg") / "data" / "config.json"
    content = new_way.read_text(encoding="utf-8")
    print("  importlib.resources 读取成功，长度:", len(content), "字节")
    print("  在打包环境下 importlib.resources 仍能工作，__file__ 方式可能失败")


if __name__ == "__main__":
    demo01_files()
    demo02_read_text()
    demo03_read_bytes()
    demo04_iterdir()
    demo05_as_file()
    demo06_vs_file_path()
