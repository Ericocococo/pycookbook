"""importlib —— import_module 动态导入与 reload 热重载

标准库。Python 3.12。
运行: python 01_import_module.py

静态导入（import json）在源码里写死模块名，编译时确定。
动态导入在运行时才决定导入哪个模块——模块名可以是变量、配置值、用户输入。

演示：
  ① import_module：基础动态导入
  ② 相对导入：用 package 参数处理相对模块名
  ③ reload：热重载，不重启进程更新已导入的模块
  ④ 与 __import__ 对比：为什么推荐 import_module
  ⑤ 实际场景：插件加载器（根据名称列表批量导入）
"""
import importlib
import sys
import types


def demo01_import_module():
    """① import_module：基础动态导入

    importlib.import_module(name) 等价于 import <name>，
    但模块名是运行时的字符串，可以来自配置、用户输入等。

    返回值是模块对象，和 import 拿到的完全一样。
    """
    print("① import_module 基础")

    # 等价于 import json
    json = importlib.import_module("json")
    print("  模块类型:", type(json))
    print("  json.dumps({'a': 1}):", json.dumps({"a": 1}))

    # 导入子模块（等价于 import os.path）
    ospath = importlib.import_module("os.path")
    print("  os.path.sep:", ospath.sep)

    # 模块名来自变量——这是动态导入的核心价值
    module_names = ["json", "os", "sys"]
    modules = {name: importlib.import_module(name) for name in module_names}
    print("  批量导入:", list(modules.keys()))


def demo02_relative_import():
    """② 相对导入（package 参数）

    相对导入（from . import xxx）在动态场景用 package 参数实现：
      import_module(".utils", package="myapp")
      等价于 from myapp import utils

    注意：相对导入要求 package 已经在 sys.modules 里（即已被导入过）。
    """
    print("\n② 相对导入")

    # 演示：导入 os.path，等价于 from os import path
    path_mod = importlib.import_module(".path", package="os")
    print("  相对导入 os.path:", path_mod)

    # 绝对导入（最常用，不需要 package）
    # import_module("os.path") 也可以，效果相同
    path_mod2 = importlib.import_module("os.path")
    print("  绝对导入 os.path:", path_mod2)
    print("  两种方式拿到同一个对象:", path_mod is path_mod2)


def demo03_reload():
    """③ reload：热重载模块

    importlib.reload(module) 重新执行模块代码，更新模块对象的属性。
    用途：
      - 开发调试时，修改了源文件不重启进程就生效
      - 运行时配置文件（用 .py 写的配置）动态更新

    注意：
      - 已经从模块里 from mod import func 取出的引用不会自动更新
      - 只更新模块对象本身，sys.modules 里的条目仍是同一个对象
    """
    print("\n③ reload 热重载")

    import json
    old_id = id(json)

    importlib.reload(json)
    new_id = id(json)

    print("  reload 前 json id:", old_id)
    print("  reload 后 json id:", new_id)
    print("  是同一个对象（模块对象复用，内容被重新执行）:", old_id == new_id)

    # 演示 from ... import 的陷阱
    from json import dumps as old_dumps
    importlib.reload(json)
    # old_dumps 仍然是 reload 前的函数引用，不会自动更新
    print("  from json import dumps 的引用仍然有效（但不跟随 reload）:", callable(old_dumps))


def demo04_vs_builtin_import():
    """④ 与 __import__ 对比

    __import__ 是 Python import 语句的底层实现，接口反直觉：
      __import__("os.path") 返回的是顶层包 os，不是 os.path！
      要拿 os.path 还得再 getattr(os, "path")。

    import_module 行为符合直觉：
      import_module("os.path") 直接返回 os.path 模块。

    结论：除非写底层 import hook，永远用 import_module，不用 __import__。
    """
    print("\n④ 与 __import__ 对比")

    # __import__ 的反直觉行为
    result = __import__("os.path")
    print("  __import__('os.path') 返回:", result)            # <module 'os'>，不是 os.path！
    print("  类型:", type(result).__name__, "名称:", result.__name__)

    # import_module 符合直觉
    result2 = importlib.import_module("os.path")
    print("  import_module('os.path') 返回:", result2)        # <module 'posixpath'>
    print("  类型:", type(result2).__name__, "名称:", result2.__name__)


def demo05_plugin_loader():
    """⑤ 实际场景：插件加载器

    根据配置列表动态加载模块，是插件系统的最简实现。
    每个"插件"是一个标准 Python 模块，暴露统一的接口（如 run 函数）。
    """
    print("\n⑤ 插件加载器")

    # 模拟配置：要加载的标准库模块列表（当作"插件"演示）
    plugin_config = ["json", "base64", "hashlib"]

    plugins = {}
    errors = []

    for name in plugin_config:
        try:
            plugins[name] = importlib.import_module(name)
            print(f"  ✓ 加载插件: {name}")
        except ImportError as e:
            errors.append(name)
            print(f"  ✗ 加载失败: {name} — {e}")

    print(f"  成功 {len(plugins)} 个，失败 {len(errors)} 个")

    # 用加载到的模块做点事
    if "json" in plugins:
        result = plugins["json"].dumps({"plugin": "loaded"})
        print("  json 插件调用结果:", result)


if __name__ == "__main__":
    demo01_import_module()
    demo02_relative_import()
    demo03_reload()
    demo04_vs_builtin_import()
    demo05_plugin_loader()
