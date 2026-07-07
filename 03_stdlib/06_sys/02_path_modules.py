"""sys —— 模块搜索路径与已加载模块

标准库。Python 3.12。运行: python 02_path_modules.py
"""
import sys


def demo01_sys_path():
    """① sys.path：当前模块搜索路径列表；临时插入路径；.pth 文件说明"""
    print("① sys.path —— 模块搜索路径")
    print("  共", len(sys.path), "条路径:")
    for i, p in enumerate(sys.path):
        print(f"  [{i}]", p if p else "(空字符串 = 当前工作目录)")

    # 临时插入路径（insert 到最前面，优先被搜索到）
    tmp_path = "/tmp/my_lib"
    sys.path.insert(0, tmp_path)
    print()
    print("  插入临时路径后 sys.path[0]:", sys.path[0])
    sys.path.pop(0)   # 演示完毕，撤回，避免影响后续 import
    print("  撤回后 sys.path[0]:", sys.path[0] if sys.path[0] else "(空字符串)")

    print()
    print("  .pth 文件说明:")
    print("    site-packages 目录里的 *.pth 文件，每行一个路径（或注释 #）")
    print("    Python 启动时由 site 模块自动将这些路径追加到 sys.path")
    print("    等价于手动 sys.path.append(...)，但无需修改代码即可持久化")


def demo02_sys_modules():
    """② sys.modules：已加载模块缓存 dict；查看/删除模块缓存"""
    print("② sys.modules —— 已加载模块缓存")

    # ── import 前后对比 ───────────────────────────────────────────────────────
    # 注意：os / sys / json 等常用模块在 Python 启动时已被自动加载，
    # 用它们演示会导致 import 前后都是 True，看不出变化。
    # colorsys 是标准库里不会被自动加载的模块，适合演示。

    # 确保 colorsys 不在缓存里（万一之前被加载过）
    sys.modules.pop("colorsys", None)

    print("  'colorsys' import 前:", "colorsys" in sys.modules)   # False
    import colorsys  # noqa: F401
    print("  'colorsys' import 后:", "colorsys" in sys.modules)   # True
    print("  缓存对象:", sys.modules["colorsys"])

    # ── pop 清除缓存 ──────────────────────────────────────────────────────────
    # sys.modules.pop(name, None) 比 del sys.modules[name] 更安全：
    # key 不存在时返回 None 而不是抛 KeyError
    print()
    sys.modules.pop("colorsys", None)
    print("  pop 后 'colorsys' 在缓存里:", "colorsys" in sys.modules)   # False

    # ── 重新加载验证（id 变化）────────────────────────────────────────────────
    # pop 后重新 import，Python 会从磁盘重新加载，产生新的模块对象
    print()
    import textwrap
    id_before = id(sys.modules["textwrap"])
    sys.modules.pop("textwrap", None)
    import textwrap  # noqa: F811
    id_after = id(sys.modules["textwrap"])
    print("  textwrap pop 前 id:", id_before)
    print("  textwrap 重新 import 后 id:", id_after)
    print("  id 不同（新对象）:", id_before != id_after)

    # ── 实际用途 ──────────────────────────────────────────────────────────────
    print()
    print("  实际用途：")
    print("    - pybind11 扩展重新编译后，pop 旧缓存让 import_module 加载新 .pyd")
    print("    - 强制重新加载某个模块（生产代码建议用 importlib.reload()，更安全）")
    print("    - 临时隔离测试，避免模块状态污染")


def demo03_builtin_modules():
    """③ sys.builtin_module_names：内置模块（无文件，直接编译进解释器）"""
    print("③ sys.builtin_module_names —— 内置模块")
    print("  共", len(sys.builtin_module_names), "个内置模块")
    print("  前 10 个:", sys.builtin_module_names[:10])
    print()
    print("  'sys' 在内置模块中:", "sys" in sys.builtin_module_names)   # True
    print("  'json' 在内置模块中:", "json" in sys.builtin_module_names) # False（json 是 .py 文件）
    print("  '_json' 在内置模块中:", "_json" in sys.builtin_module_names) # True（C 加速层）
    print()
    print("  区别: 内置模块（builtin）直接嵌在解释器二进制里，没有对应 .py 文件")
    print("        冻结模块（frozen）也无 .py 文件，但以字节码形式嵌入")
    print("        普通标准库模块（如 json）有 .py 源文件，在 sys.prefix 下可以找到")


def demo04_stdlib_names():
    """④ sys.stdlib_module_names（Python 3.10+）：标准库模块全集"""
    print("④ sys.stdlib_module_names —— 标准库模块全集（Python 3.10+）")
    if not hasattr(sys, "stdlib_module_names"):
        print("  当前 Python 版本不支持该属性（需要 3.10+）")
        return

    stdlib = sys.stdlib_module_names
    print("  共", len(stdlib), "个标准库模块")
    samples = ["os", "sys", "json", "pathlib", "asyncio", "typing", "numpy", "requests"]
    print("  常见模块是否在标准库中:")
    for m in samples:
        print(f"    '{m}':", m in stdlib)


def demo05_import_hooks():
    """⑤ sys.meta_path / sys.path_hooks：import 机制钩子（简要说明）"""
    print("⑤ import 机制钩子（简要）")

    print("  sys.meta_path 有", len(sys.meta_path), "个 meta finder:")
    for finder in sys.meta_path:
        # meta finder 可能是类（直接看 __name__）也可能是实例（看 type.__name__）
        name = getattr(finder, "__name__", None) or type(finder).__name__
        print("    -", name)

    print()
    print("  sys.path_hooks 有", len(sys.path_hooks), "个 path hook:")
    for hook in sys.path_hooks:
        name = getattr(hook, "__name__", None) or getattr(hook, "__qualname__", repr(hook))
        print("    -", name)

    print()
    print("  import 执行流程（简化）:")
    print("    1. 检查 sys.modules 缓存，命中则直接返回")
    print("    2. 依次调用 sys.meta_path 里每个 finder 的 find_spec()")
    print("    3. BuiltinImporter  → 查内置模块")
    print("    4. FrozenImporter   → 查冻结模块")
    print("    5. PathFinder       → 遍历 sys.path，对每个路径调用 sys.path_hooks")
    print("       工厂函数创建 FileFinder，再由 FileFinder 找到 .py / .pyd 文件")


if __name__ == "__main__":
    # demo01_sys_path()
    # print()

    demo02_sys_modules()
    print()

    # demo03_builtin_modules()
    # print()

    # demo04_stdlib_names()
    # print()

    # demo05_import_hooks()
