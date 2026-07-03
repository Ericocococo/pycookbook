"""importlib.util —— 模块检查与从任意路径加载

标准库。Python 3.12。
运行: python 02_util.py

importlib.util 提供底层工具，不直接执行导入，而是给你：
  - 查找模块规格（知道它在哪、怎么加载，但不真的导入）
  - 从文件系统任意路径加载 .py 文件（无需修改 sys.path）

演示：
  ① find_spec：检查模块/包是否存在
  ② spec_from_file_location + module_from_spec + exec_module：从路径加载模块
  ③ 加载后注册到 sys.modules：让其他代码也能用
  ④ 实际场景：插件发现——扫描目录，加载所有 .py 文件
"""
import importlib.util
import sys
import os
from pathlib import Path


def demo01_find_spec():
    """① find_spec：检查模块是否存在（不导入）

    术语：
      ModuleSpec  描述一个模块的元数据：名称、来源路径、loader、submodule_search_locations 等
      find_spec   在 sys.path 和 sys.meta_path 里搜索模块规格，找不到返回 None

    用途：
      - 判断第三方包是否已安装（比 try/import/except 更快，不执行模块代码）
      - 获取模块文件路径（不导入）
    """
    print("① find_spec 检查模块")

    # 检查标准库模块
    spec = importlib.util.find_spec("json")
    print("  json 的 spec:", spec)
    print("  json 文件位置:", spec.origin)

    # 检查不存在的模块
    spec_missing = importlib.util.find_spec("this_does_not_exist")
    print("  不存在的模块 spec:", spec_missing)   # None

    # 判断第三方包是否已安装（推荐方式）
    packages_to_check = ["numpy", "requests", "pip", "setuptools"]
    for pkg in packages_to_check:
        installed = importlib.util.find_spec(pkg) is not None
        print(f"  {pkg:12s} 已安装: {installed}")


def demo02_load_from_path():
    """② 从任意路径加载 .py 文件

    三步固定模式（Python 3.5+）：
      1. spec_from_file_location(name, path)  创建规格
      2. module_from_spec(spec)               创建空模块对象
      3. spec.loader.exec_module(mod)         执行模块代码，填充模块对象

    name 是你给它起的名字（随意，不需要和文件名一致）。
    不会修改 sys.path，不影响其他 import。
    """
    print("\n② 从路径加载模块")

    # 先创建一个临时 .py 文件作为演示
    tmp_path = Path(__file__).parent / "_tmp_plugin.py"
    tmp_path.write_text(
        "# 这是一个临时插件文件\n"
        "PLUGIN_NAME = 'demo_plugin'\n"
        "VERSION = (1, 0, 0)\n"
        "\n"
        "def greet(name):\n"
        "    return f'Hello from {PLUGIN_NAME}, {name}!'\n",
        encoding="utf-8",
    )

    try:
        # 三步加载
        spec = importlib.util.spec_from_file_location("my_plugin", tmp_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # 执行模块代码

        # 现在 mod 就是加载好的模块
        print("  模块名:", mod.__name__)
        print("  PLUGIN_NAME:", mod.PLUGIN_NAME)
        print("  VERSION:", mod.VERSION)
        print("  greet('world'):", mod.greet("world"))
    finally:
        tmp_path.unlink(missing_ok=True)      # 清理临时文件


def demo03_register_in_sys_modules():
    """③ 加载后注册到 sys.modules

    默认情况下，从路径加载的模块不在 sys.modules 里，
    其他代码无法通过 import 名称 找到它。

    如果你想让它可以被 import，需要手动注册：
      sys.modules[name] = mod

    注册后就像正常安装的包一样，import name 直接可用。
    """
    print("\n③ 注册到 sys.modules")

    tmp_path = Path(__file__).parent / "_tmp_registered.py"
    tmp_path.write_text(
        "VALUE = 42\n"
        "def hello(): return 'registered module'\n",
        encoding="utf-8",
    )

    try:
        spec = importlib.util.spec_from_file_location("my_registered_mod", tmp_path)
        mod = importlib.util.module_from_spec(spec)

        # 注册到 sys.modules（注册后才能被 import 发现）
        sys.modules["my_registered_mod"] = mod
        spec.loader.exec_module(mod)

        # 现在可以用普通 import（或 import_module）
        import importlib as _il
        retrieved = _il.import_module("my_registered_mod")
        print("  通过 import_module 获取注册的模块:", retrieved.hello())
        print("  VALUE:", retrieved.VALUE)
        print("  是同一个对象:", retrieved is mod)
    finally:
        # 清理
        sys.modules.pop("my_registered_mod", None)
        tmp_path.unlink(missing_ok=True)


def demo04_plugin_discovery():
    """④ 实际场景：扫描目录，动态加载所有插件

    插件系统的常见实现：
      1. 约定插件目录和接口（如每个 .py 文件暴露 run() 函数）
      2. 启动时扫描目录，加载所有 .py 文件
      3. 调用统一接口

    这种方式不需要修改主程序，添加插件只需放入目录即可。
    """
    print("\n④ 插件目录扫描")

    # 创建一个临时插件目录
    plugin_dir = Path(__file__).parent / "_tmp_plugins"
    plugin_dir.mkdir(exist_ok=True)

    # 写几个假插件
    plugins_source = {
        "plugin_a.py": "NAME='插件A'\ndef run(): return 'A 执行了'\n",
        "plugin_b.py": "NAME='插件B'\ndef run(): return 'B 执行了'\n",
        "plugin_c.py": "NAME='插件C'\ndef run(): return 'C 执行了'\n",
    }
    for fname, src in plugins_source.items():
        (plugin_dir / fname).write_text(src, encoding="utf-8")

    try:
        loaded = []
        for py_file in sorted(plugin_dir.glob("*.py")):
            name = py_file.stem   # 文件名去掉 .py 作为模块名
            spec = importlib.util.spec_from_file_location(name, py_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded.append(mod)
            print(f"  加载: {mod.NAME}")

        # 统一调用 run() 接口
        print("  --- 执行所有插件 ---")
        for mod in loaded:
            print(" ", mod.run())
    finally:
        # 清理
        import shutil
        shutil.rmtree(plugin_dir, ignore_errors=True)


if __name__ == "__main__":
    demo01_find_spec()
    demo02_load_from_path()
    demo03_register_in_sys_modules()
    demo04_plugin_discovery()
