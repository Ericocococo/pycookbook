"""
Pyright 配置特性 —— 同一段代码在不同配置下的表现差异

使用方式（在项目根目录）：
  # 用当前配置（basic 模式）检查
  pyright 10_ops/09_pyright/01_config.py

  # 模拟 strict 模式检查（会多出一堆报错）
  pyright 10_ops/09_pyright/01_config.py --level error
"""

from typing import Any

# ──────────────────────────────────────────
# ① Optional 成员访问（reportOptionalMemberAccess）
# ──────────────────────────────────────────
def demo01_optional_access() -> None:
    """Optional 成员访问：对可能为 None 的变量调方法。

    掌握：知道同一个问题在 basic 模式只是 warning，strict 模式会升级为 error，
    理解 Pyright 配置级别对报错严格程度的影响。
    """

    maybe: str | None = None

    # basic 模式下：warning（"maybe" 可能为 None）
    # strict 模式下：error
    print(maybe.upper())  # pyright: ignore[reportAttributeAccessIssue]


# ──────────────────────────────────────────
# ② 隐式 Any（reportMissingTypeArgs / reportUnknownMemberType）
# ──────────────────────────────────────────
def demo02_implicit_any() -> None:
    """隐式 Any：未注解的参数/返回值被推断为 Any，类型检查失效。

    掌握：理解未加注解的函数为什么"什么都不报错"——参数是 Any，
    这就是 strict 模式强制要求所有函数加注解的原因。
    """

    # 空列表被推断为 list[Any]
    items: list[Any] = []

    # 函数参数和返回值都没注解
    def secret(x):  # pyright 会推断参数和返回值都是 Any
        return x

    _result = secret(42)       # _result 是 Any
    _result = secret("hello")  # 也不报错

    print("items:", items)
    print("secret('hello'):", secret("hello"))


# ──────────────────────────────────────────
# ③ 私有成员访问（reportPrivateUsage）
# ──────────────────────────────────────────
def demo03_private_usage() -> None:
    """私有成员访问：从类外部访问 _ 前缀的属性/方法。

    掌握：知道 reportPrivateUsage 规则的作用——开启后从类外部
    访问 _xxx 会被提示，帮助团队维护封装边界。
    """

    class MyClass:
        def __init__(self) -> None:
            self._secret = "internal"

        def _private_method(self) -> str:
            return "secret"

    obj = MyClass()
    # reportPrivateUsage 开启时，下面两行会报 information
    print(obj._secret)            # pyright: ignore[reportPrivateUsage]
    print(obj._private_method())  # pyright: ignore[reportPrivateUsage]


# ──────────────────────────────────────────
# ④ 未使用变量 / 导入（reportUnusedVariable / reportUnusedImport）
# ──────────────────────────────────────────
def demo04_unused() -> None:
    """未使用变量：检测声明了但没用到的变量和导入。

    掌握：知道 Pyright 会标记未使用的变量/导入，
    以及用 _ 前缀命名来消除误报的惯用写法。
    """

    # 用 _ 前缀表示"我知道没用，故意的"
    _unused_var = 42
    print("demo04_unused done")


# ──────────────────────────────────────────
# ⑤ 类型一致性（reportGeneralTypeIssues）
# ──────────────────────────────────────────
def demo05_type_consistency() -> None:
    """类型一致性：标注和实际值类型不匹配时报错。

    掌握：理解 Pyright 最基本的检查——声明 int 就不能赋 str，
    列表 list[int] 里不能混入 str 元素。
    """

    # 类型标注和实际值不匹配
    count: int = "not a number"  # pyright: ignore[reportAssignmentType]
    del count

    # 列表元素类型不一致
    numbers: list[int] = [1, 2, "three"]  # pyright: ignore[reportAssignmentType]
    del numbers

    print("demo05_type_consistency done")


# ──────────────────────────────────────────
# ⑥ Strict 模式额外会报的
# ──────────────────────────────────────────
def demo06_strict_extra() -> None:
    """Strict 额外检查：要求所有函数的参数和返回值都加注解。

    掌握：知道 basic 和 strict 模式的核心区别——basic 容忍未注解函数，
    strict 全部报错，根据项目需要选择合适的检查级别。
    """

    # 函数返回值不加注解（strict 下 reportUnknownParameterType 报错）
    def guess(x):  # 返加值未注解 → Any
        return x

    # 函数参数不加类型（strict 下 reportUnknownParameterType 报错）
    def process(data, flag):  # 参数未注解 → Any
        return None if flag else data

    _result = guess(42)
    _result = process("hello", True)
    print("_result:", _result)


# ──────────────────────────────────────────
# main
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("本文件演示 Pyright 配置对检查结果的影响")
    print()
    print("当前 pyrightconfig.json 是 basic 模式，效果：")
    print("  - Optional 访问 → warning")
    print("  - 未用变量     → warning（已开启 reportUnusedVariable）")
    print("  - 类型不匹配   → error（已开启 reportGeneralTypeIssues）")
    print("  - 隐式 Any     → 部分检查")
    print("  - 私有访问     → information（已开启 reportPrivateUsage）")
    print()
    print("对比运行（跳开当前配置，用 strict 模式检查）：")
    print("  1. 临时换目录（避免加载当前 pyrightconfig.json）:")
    print("     cd /tmp && pyright <原路径>/01_config.py")
    print("  2. 或临时修改配置: 把 typeCheckingMode 改为 strict")
    print()
