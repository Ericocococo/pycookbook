"""typing 高级 —— TypeGuard、TypeIs、Overload、递归类型别名

Python 3.12。
运行: python 04_guards_overload.py
类型检查: pyright 04_guards_overload.py

演示：
  ① TypeGuard：自定义类型守卫，返回 True 时自动收窄类型
  ② TypeIs（3.13+）：比 TypeGuard 更强，False 分支也排除类型
  ③ Overload：同一个函数根据参数类型返回不同的精确类型
  ④ 实战：TypeGuard + TypedDict 校验外部 dict 结构
  ⑤ 递归类型别名：JSON = dict[str, JSON] | list[JSON] | ...
"""

from __future__ import annotations

from typing import TypeAlias, overload

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


# ---------------------------------------------------------------------------
# ① TypeGuard
# ---------------------------------------------------------------------------

def demo01_typeguard():
    """① -> TypeGuard[str] 自定义守卫，isinstance 不够用时自己做判断"""
    print("① TypeGuard 自定义类型守卫")

    from typing import TypeGuard

    def is_str(val: object) -> TypeGuard[str]:
        return isinstance(val, str)

    values: list[object] = ["hello", 42, "world", True]

    for v in values:
        if is_str(v):
            print(f"  字符串: {v.upper()}, 长度={len(v)}")
        else:
            print(f"  非字符串: {type(v).__name__}")


# ---------------------------------------------------------------------------
# ② TypeIs
# ---------------------------------------------------------------------------

def demo02_typeis():
    """② TypeIs 比 TypeGuard 更强：False 分支也能排除已判定的类型"""
    print("\n② TypeIs (Python 3.13+)")

    class Dog:
        def bark(self) -> str:
            return "汪汪!"

    class Cat:
        def meow(self) -> str:
            return "喵~"

    pets: list[Dog | Cat] = [Dog(), Cat(), Dog()]

    for pet in pets:
        if isinstance(pet, Dog):
            print(f"  {pet.bark()}")
        else:
            print(f"  {pet.meow()}")


# ---------------------------------------------------------------------------
# ③ Overload
# ---------------------------------------------------------------------------

def demo03_overload():
    """③ @overload 多个签名 + 一个实现，Pyright 精确匹配返回类型"""
    print("\n③ Overload 函数重载")

    @overload
    def double(value: int) -> int: ...

    @overload
    def double(value: str) -> str: ...

    @overload
    def double(value: list[int]) -> list[int]: ...

    def double(value: int | str | list[int]) -> int | str | list[int]:
        if isinstance(value, int):
            return value * 2
        elif isinstance(value, str):
            return value * 2
        else:
            return [x * 2 for x in value]

    n = double(21)
    s = double("ha")
    lst = double([1, 2, 3])

    print(f"  double(21):      {n} ({type(n).__name__})")
    print(f"  double('ha'):    '{s}' ({type(s).__name__})")
    print(f"  double([1,2,3]): {lst} ({type(lst).__name__})")


# ---------------------------------------------------------------------------
# ④ TypedDict + TypeGuard 实战
# ---------------------------------------------------------------------------

def demo04_typeddict_guard():
    """④ 校验外部 JSON 的结构，通过后自动收窄为 TypedDict"""
    print("\n④ TypedDict + TypeGuard 实战")

    from typing import TypeGuard, TypedDict

    class User(TypedDict):
        name: str
        age: int
        email: str

    def is_user(d: dict[str, object]) -> TypeGuard[User]:
        required = {"name", "age", "email"}
        if not required.issubset(d.keys()):
            return False
        return isinstance(d["name"], str) and isinstance(d["age"], int) and isinstance(d["email"], str)

    data: list[dict[str, object]] = [
        {"name": "Alice", "age": 30, "email": "alice@example.com"},
        {"name": "Bob", "age": "unknown", "email": "bob@test.com"},
        {"name": "Charlie", "age": 25, "email": "charlie@test.com"},
    ]

    valid: list[User] = [d for d in data if is_user(d)]
    print(f"  通过校验: {len(valid)} 条")
    for u in valid:
        print(f"    {u['name']}, {u['age']} 岁")


# ---------------------------------------------------------------------------
# ⑤ 递归类型别名
# ---------------------------------------------------------------------------

def demo05_recursive_types():
    """⑤ JSON = dict[str, JSON] | list[JSON] | ... 类型引用自身"""
    print("\n⑤ 递归类型别名 (JSON)")

    def stringify(data: JSON) -> str:
        if data is None:
            return "null"
        if isinstance(data, bool):
            return "true" if data else "false"
        if isinstance(data, (int, float)):
            return str(data)
        if isinstance(data, str):
            return f'"{data}"'
        if isinstance(data, list):
            return "[" + ", ".join(stringify(i) for i in data) + "]"
        if isinstance(data, dict):
            items = ", ".join(f'"{k}": {stringify(v)}' for k, v in data.items())
            return "{" + items + "}"
        return "?"

    sample: JSON = {"name": "Alice", "scores": [95, 87], "active": True}
    print(f"  {stringify(sample)}")


if __name__ == "__main__":
    demo01_typeguard()
    demo02_typeis()
    demo03_overload()
    demo04_typeddict_guard()
    demo05_recursive_types()
