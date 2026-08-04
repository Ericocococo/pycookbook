"""typing 进阶 —— Union、Optional、Literal、TypedDict、Final、assert_type

Python 3.12。
运行: python 02_advanced.py
类型检查: pyright 02_advanced.py

演示：
  ① Union：X | Y 声明一个参数接受多种类型
  ② Optional：T | None 标注可能返回空的函数
  ③ Literal：把取值限制到几个具体字面量
  ④ TypedDict：给 dict 的每个 key 声明精确类型
  ⑤ assert_type：运行时零开销的类型断言
  ⑥ Final：声明常量，禁止重新赋值
"""

from typing import Final, TypeAlias, Literal


# ---------------------------------------------------------------------------
# ① Union
# ---------------------------------------------------------------------------

def demo01_union():
    """① str | int 声明"接受 str 或 int"，传其他类型直接报错"""
    print("① Union 联合类型")

    def parse_int(value: str | int) -> int:
        if isinstance(value, int):
            return value
        return int(value)

    print(f"  parse_int('42'): {parse_int('42')}")
    print(f"  parse_int(42):   {parse_int(42)}")

    # bool 是 int 的子类型，所以 parse_int(True) 不会报错


# ---------------------------------------------------------------------------
# ② Optional
# ---------------------------------------------------------------------------

def demo02_optional():
    """② -> str | None 标注可能返回空，调用方必须先判空"""
    print("\n② Optional")

    def find_user(uid: int) -> str | None:
        db = {1: "Alice", 2: "Bob"}
        return db.get(uid)

    user = find_user(3)
    # user.upper()               # ← Pyright 报错
    if user is not None:
        print(f"  {user.upper()}  # 先判空再使用")
    else:
        print("  user 为 None")


# ---------------------------------------------------------------------------
# ③ Literal
# ---------------------------------------------------------------------------

Mode: TypeAlias = Literal["read", "write"]


def demo03_literal():
    """③ Literal["read", "write"] 只允许这两个值，比 str 更精确"""
    print("\n③ Literal 精确值类型")

    def open_file(mode: Mode) -> str:
        return "opened for reading" if mode == "read" else "opened for writing"

    print(f"  open_file('read'):  {open_file('read')}")
    print(f"  open_file('write'): {open_file('write')}")
    # open_file("delete")       # ← Pyright 报错：不在 "read" | "write" 中


# ---------------------------------------------------------------------------
# ④ TypedDict
# ---------------------------------------------------------------------------

def demo04_typeddict():
    """④ TypedDict 让 Pyright 知道 dict 每个 key 的类型"""
    print("\n④ TypedDict 带类型的字典")

    from typing import TypedDict

    class User(TypedDict):
        name: str
        age: int
        email: str

    user: User = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    print(f"  user['name']: {user['name']}")

    # total=False：所有 key 都是可选的
    class PartialUser(TypedDict, total=False):
        name: str | None
        age: int | None

    empty: PartialUser = {}
    print(f"  empty dict ok: {empty}")


# ---------------------------------------------------------------------------
# ⑤ assert_type
# ---------------------------------------------------------------------------

def demo05_assert_type():
    """⑤ assert_type 断言 Pyright 推断的类型是否符合预期（运行时零开销）"""
    print("\n⑤ assert_type 类型断言")

    from typing import assert_type

    def pick(flag: bool) -> str | int:
        return "hello" if flag else 42

    y = pick(True)
    assert_type(y, str | int)    # ✅ 匹配
    # assert_type(y, str)        # ❌ 实际是 str | int，不是 str

    print("  assert_type(y, str | int) ✓")


# ---------------------------------------------------------------------------
# ⑥ Final
# ---------------------------------------------------------------------------

def demo06_final():
    """⑥ Final 声明常量，重新赋值直接报错"""
    print("\n⑥ Final 常量")

    MAX_RETRIES: Final = 3
    # MAX_RETRIES = 5             # ← Pyright 报错

    print(f"  MAX_RETRIES: {MAX_RETRIES}")


if __name__ == "__main__":
    demo01_union()
    demo02_optional()
    demo03_literal()
    demo04_typeddict()
    demo05_assert_type()
    demo06_final()
