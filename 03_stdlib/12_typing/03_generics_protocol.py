"""typing 高级 —— 泛型（TypeVar / Generic）、Protocol 结构子类型

Python 3.12。
运行: python 03_generics_protocol.py
类型检查: pyright 03_generics_protocol.py

演示：
  ① 泛型函数：TypeVar 让参数和返回值类型自动关联
  ② 多 TypeVar：多个独立的泛型参数，各自推断互不干扰
  ③ 泛型类：Generic[T] 让类的所有方法共享同一个类型参数
  ④ Bound TypeVar：限制泛型只能是某类型或其子类
  ⑤ Protocol：按结构匹配，不需要显式继承（鸭子类型）
  ⑥ 标准库 Protocol：Sequence、Iterable、Callable
  ⑦ Iterator[T]：标注生成器的 yield 类型
"""

from typing import Iterator, Sequence, TypeVar

T = TypeVar("T")
U = TypeVar("U")


# ---------------------------------------------------------------------------
# ① 泛型函数
# ---------------------------------------------------------------------------

def demo01_generic_function():
    """① def first(items: list[T]) -> T | None —— T 自动关联入参类型"""
    print("① 泛型函数")

    def first(items: list[T]) -> T | None:
        return items[0] if items else None

    n = first([1, 2, 3])        # T → int，返回 int | None
    s = first(["a", "b", "c"])  # T → str，返回 str | None

    print(f"  first([1,2,3]):     {n}")
    print(f"  first(['a','b','c']): {s}")


# ---------------------------------------------------------------------------
# ② 多个 TypeVar
# ---------------------------------------------------------------------------

def demo02_multi_typevar():
    """② pair(left: T, right: U) → tuple[T, U]，各自独立推断"""
    print("\n② 多 TypeVar")

    def pair(left: T, right: U) -> tuple[T, U]:
        return (left, right)

    p1 = pair(1, "one")         # tuple[int, str]
    p2 = pair("a", "b")         # tuple[str, str]

    print(f"  pair(1, 'one'): {p1}")
    print(f"  pair('a', 'b'):  {p2}")


# ---------------------------------------------------------------------------
# ③ 泛型类
# ---------------------------------------------------------------------------

def demo03_generic_class():
    """③ class Stack(Generic[T]) —— push 类型不对直接报错"""
    print("\n③ 泛型类")

    from typing import Generic

    class Stack(Generic[T]):
        def __init__(self):
            self._items: list[T] = []

        def push(self, item: T):
            self._items.append(item)

        def pop(self) -> T | None:
            return self._items.pop() if self._items else None

    int_stack = Stack[int]()
    int_stack.push(1)
    int_stack.push(2)
    print(f"  int_stack.pop(): {int_stack.pop()}")

    # int_stack.push("hello")   # ← Pyright 报错：Stack[int] 只接受 int

    str_stack = Stack[str]()
    str_stack.push("hello")
    print(f"  str_stack.pop(): {str_stack.pop()}")


# ---------------------------------------------------------------------------
# ④ Bound TypeVar
# ---------------------------------------------------------------------------

def demo04_bound_typevar():
    """④ TypeVar("T", bound=int | float) —— 只接受数值类型"""
    print("\n④ Bound TypeVar")

    Number = TypeVar("Number", bound=int | float)

    def double(x: Number) -> Number:
        return x * 2          # pyright: ignore[reportReturnType]

    print(f"  double(5):    {double(5)}")
    print(f"  double(3.14): {double(3.14)}")
    # double("hello")          # ← 报错：str 不满足 bound


# ---------------------------------------------------------------------------
# ⑤ Protocol
# ---------------------------------------------------------------------------

def demo05_protocol():
    """⑤ Protocol 类不需要继承，实现了相同方法签名就算满足"""
    print("\n⑤ Protocol 结构子类型")

    from typing import Protocol

    class Drawable(Protocol):
        def draw(self) -> str: ...

    class Circle:
        def draw(self) -> str:
            return "⭕ 画一个圆"

    class Square:
        def draw(self) -> str:
            return "⬛ 画一个正方形"

    def render(things: list[Drawable]):
        for t in things:
            print(f"  {t.draw()}")

    render([Circle(), Square()])


# ---------------------------------------------------------------------------
# ⑥ 标准库 Protocol
# ---------------------------------------------------------------------------

def demo06_builtin_protocol():
    """⑥ Sequence[str] 接受 list、tuple 等任何序列，比 list[str] 更灵活"""
    print("\n⑥ 标准库 Protocol")

    def process(items: Sequence[str]) -> str:
        return ", ".join(items)

    print(f"  传 tuple: {process(('a', 'b', 'c'))}")
    print(f"  传 list:  {process(['x', 'y'])}")


# ---------------------------------------------------------------------------
# ⑦ Iterator[T]
# ---------------------------------------------------------------------------

def demo07_iterator():
    """⑦ -> Iterator[int] 标注 yield 类型，for 循环知道每个元素是 int"""
    print("\n⑦ Iterator[T] 泛型")

    def count_up_to(n: int) -> Iterator[int]:
        for i in range(n):
            yield i

    print(f"  count_up_to(5): {list(count_up_to(5))}")


if __name__ == "__main__":
    demo01_generic_function()
    demo02_multi_typevar()
    demo03_generic_class()
    demo04_bound_typevar()
    demo05_protocol()
    demo06_builtin_protocol()
    demo07_iterator()
