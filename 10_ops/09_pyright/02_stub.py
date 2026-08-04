"""
Pyright 工具链 —— 类型 Stub、typeshed、VerifyTypes、版本迁移

运行方式（在项目根目录）：
  python 10_ops/09_pyright/02_stub.py
  pyright 10_ops/09_pyright/02_stub.py
"""

from __future__ import annotations

from pathlib import Path

# ──────────────────────────────────────────
# ① 什么是 .pyi 桩文件
# ──────────────────────────────────────────
def demo01_stub_concept() -> None:
    """.pyi 桩文件：只写类型签名没有实现，Pyright 优先读取。

    掌握：知道 .pyi 文件的作用和 Pyright 的类型查找顺序
    （.pyi → typeshed → .py inline 注解 → py.typed），
    学会给无类型的三方库/C 扩展补类型而不用改原始源码。
    """

    print(".pyi 文件是纯类型声明，没有实现体")
    print("适用于：无类型的 C 扩展库、三方库类型声明")


# ──────────────────────────────────────────
# ② typeshed —— Pyright 内置的标准库类型
# ──────────────────────────────────────────
def demo02_typeshed() -> None:
    """typeshed：Pyright 内置的标准库类型仓库，无需配置。

    掌握：知道标准库方法（open、os.path 等）的类型来自 typeshed 项目，
    Pyright 内置了它，所以标准库开箱即有类型检查，无需额外安装。
    """

    _p = Path("data/demo_typeshed.txt")
    print("typeshed 为标准库提供了完整类型")
    print("例如 list.sort、dict.get、Path.open 等")


# ──────────────────────────────────────────
# ③ verifytypes —— 检查包的类型完整度
# ──────────────────────────────────────────
def demo03_verifytypes() -> None:
    """--verifytypes：检查包的公共 API 类型完整度。

    掌握：学会用 pyright --verifytypes <包名> 检查自己库的类型覆盖率，
    知道需要在包根目录放 py.typed 空文件才能启用此检查。
    """

    print("pyright --verifytypes <包名> → 输出类型完整度百分比")
    print("是库作者保证类型质量的工具")


# ──────────────────────────────────────────
# ④ deprecateTypingAliases —— 从 typing 迁移到
#    collections.abc / builtins
# ──────────────────────────────────────────
def demo04_deprecate_aliases() -> None:
    """deprecateTypingAliases：把 typing.List 等旧写法迁移到内置类型。

    掌握：知道 Python 3.9+ 应该用 list[int] 而非 typing.List[int]，
    学会在 pyrightconfig.json 中开启此选项让 Pyright 自动标记旧写法。
    """

    from typing import List, Dict  # pyright: ignore[reportDeprecated]

    x: List[int] = [1, 2, 3]       # 旧写法，Pyright 会提示改用 list[int]
    y: Dict[str, int] = {"a": 1}   # 旧写法，改用 dict[str, int]

    a: list[int] = [1, 2, 3]       # 正确写法（Python 3.9+）
    b: dict[str, int] = {"a": 1}

    print(f"旧: {x}, {y}")
    print(f"新: {a}, {b}")


# ──────────────────────────────────────────
# ⑤ stubPath —— 自定义 stub 目录
# ──────────────────────────────────────────
def demo05_stub_path() -> None:
    """stubPath：在 pyrightconfig.json 中指定自定义桩文件目录。

    掌握：学会在 pyrightconfig.json 中配置 stubPath 指向 typings/ 目录，
    给没有类型的三方库放自己的 .pyi 文件覆盖默认类型。
    """

    print("stubPath 指向自定义 .pyi 目录（如 typings/）")
    print("适合为无类型的三方库补类型")


# ──────────────────────────────────────────
# main
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 40)
    print("① .pyi 桩文件概念")
    print("=" * 40)
    demo01_stub_concept()

    print("\n" + "=" * 40)
    print("② typeshed 内置类型")
    print("=" * 40)
    demo02_typeshed()

    print("\n" + "=" * 40)
    print("③ --verifytypes 类型完整度检查")
    print("=" * 40)
    demo03_verifytypes()

    print("\n" + "=" * 40)
    print("④ deprecateTypingAliases")
    print("=" * 40)
    demo04_deprecate_aliases()

    print("\n" + "=" * 40)
    print("⑤ stubPath 自定义桩目录")
    print("=" * 40)
    demo05_stub_path()
