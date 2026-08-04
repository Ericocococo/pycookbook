"""typing 基础 —— 类型推断、类型注解、类型收窄、Optional、Any

Python 3.12。
运行: python 01_basic.py
类型检查: pyright 01_basic.py

演示：
  ① 类型推断：Pyright 自动根据赋值推断变量类型
  ② 显式注解：给函数参数和返回值标注 : int、-> str
  ③ 类型收窄：if/elif/else 逐步缩小 int | str | None 的类型范围
  ④ Optional：变量可能为 None 时强制先判空再使用
  ⑤ Any 传染性：Any 兼容一切，类型检查器完全放行
"""

import json


# ---------------------------------------------------------------------------
# ① 类型推断
# ---------------------------------------------------------------------------

def demo01_inference():
    """① 不写注解时 Pyright 自动推断，但加注解才有约束"""
    print("① 类型推断")

    x = 42                     # 推断为 int
    y = "hello"                # 推断为 str
    z = [1, 2, 3]              # 推断为 list[int]

    print(f"  x: {x!r} ({type(x).__name__})")
    print(f"  y: {y!r} ({type(y).__name__})")
    print(f"  z: {z!r} ({type(z).__name__})")

    # 无注解时可以重新赋值不同类型
    x = "world"                # 合法：类型从 int 变成 str
    print(f"  重新赋值后 x: {x!r} ({type(x).__name__})")

    # 加了注解就不行了
    # count: int = 42
    # count = "hello"          # ← Pyright 报错


# ---------------------------------------------------------------------------
# ② 显式类型注解
# ---------------------------------------------------------------------------

def demo02_annotations():
    """② 给函数参数和返回值标注类型，传错直接报错"""
    print("\n② 显式类型注解")

    def add(a: int, b: int) -> int:
        return a + b

    def repeat(msg: str, times: int = 1) -> list[str]:
        return [msg] * times

    print(f"  add(3, 4): {add(3, 4)}")
    print(f"  repeat('hi', 2): {repeat('hi', 2)}")


# ---------------------------------------------------------------------------
# ③ 类型收窄
# ---------------------------------------------------------------------------

def demo03_narrowing():
    """③ is None / isinstance 让类型在每个分支里越来越精确"""
    print("\n③ 类型收窄 (Type Narrowing)")

    def process(val: int | str | None) -> str:
        if val is None:
            return "收到 None"
        elif isinstance(val, int):
            return f"整数翻倍: {val * 2}"
        else:
            return f"字符串翻转: {val[::-1]}"

    print(f"  process(42):    {process(42)}")
    print(f"  process('hello'): {process('hello')}")
    print(f"  process(None):  {process(None)}")


# ---------------------------------------------------------------------------
# ④ Optional 与 None 检查
# ---------------------------------------------------------------------------

def demo04_optional():
    """④ str | None 表示可能为 None，必须判空才能使用"""
    print("\n④ Optional 与 None 检查")

    name: str | None = None

    # print(name.upper())       # ← Pyright 报错：name 可能是 None

    if name is not None:
        print(f"  name.upper(): {name.upper()}")
    else:
        print(f"  name 是 None")


# ---------------------------------------------------------------------------
# ⑤ Any 的传染性
# ---------------------------------------------------------------------------

def demo05_any():
    """⑤ json.loads() 返回 Any，从它派生的变量全变 Any，类型检查失效"""
    print("\n⑤ Any 的传染性")

    raw = json.loads('{"name": "Alice", "age": 30}')
    print(f"  raw: {raw}")
    print(f"  raw['name']: {raw['name']}")

    age = raw["age"]           # age 也是 Any
    try:
        result = age + "岁"     # 运行时 TypeError，Pyright 检测不到
    except TypeError:
        print(f"  age + '岁' → TypeError —— Pyright 查不出，因为 age 是 Any")


if __name__ == "__main__":
    demo01_inference()
    demo02_annotations()
    demo03_narrowing()
    demo04_optional()
    demo05_any()
