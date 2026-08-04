"""dunder 属性 —— 类级：__init__ / __repr__ / __eq__ / __slots__ / 运算符重载

Python 3.12。运行: python 02_class.py

类的特殊方法分五类：
  ① 生命周期：__init__ / __new__ / __del__
  ② 字符串：  __repr__ / __str__
  ③ 比较/哈希：__eq__ / __lt__ / __hash__ / __bool__
  ④ 容器模拟：__getitem__ / __setitem__ / __iter__ / __contains__
  ⑤ 其他：    __call__ / __enter__ / __slots__ / __class__
"""

import dataclasses
import typing


# ---------------------------------------------------------------------------
# ① __init__ / __new__ / __del__
# ---------------------------------------------------------------------------

def demo01_lifecycle():
    """① __init__ / __new__ / __del__ —— 实例的出生到死亡"""
    print("① 生命周期")

    class Lifecycle:
        def __new__(cls, name: str):
            """__new__ 创建实例（在 __init__ 之前），很少需要覆盖"""
            print("  __new__ 被调用")
            return super().__new__(cls)

        def __init__(self, name: str):
            """__init__ 初始化实例属性，最常用的 dunder"""
            self.name = name
            print(f"  __init__ 被调用: name={name!r}")

        def __del__(self):
            """__del__ 在对象被垃圾回收时调用，不保证立即执行"""
            print(f"  __del__ 被调用: name={self.name!r}")

    obj = Lifecycle("Alice")
    del obj                     # 显式删除 → 触发 __del__
    print("  退出 demo01 后 Python 可能还会触发更多 __del__")


# ---------------------------------------------------------------------------
# ② __repr__ / __str__
# ---------------------------------------------------------------------------

def demo02_string():
    """② __repr__ 给开发者看，__str__ 给用户看"""
    print("\n② 字符串表示")

    class Point:
        def __init__(self, x: int, y: int):
            self.x, self.y = x, y

        def __repr__(self):
            """开发者看到的样子——eval(repr(obj)) 应能重建对象"""
            return f"Point(x={self.x}, y={self.y})"

        def __str__(self):
            """用户看到的样子——print(obj) 或 str(obj) 时调用"""
            return f"({self.x}, {self.y})"

    p = Point(3, 4)
    print(f"  repr(p): {repr(p)}           # 给开发者")
    print(f"  str(p):  {p}                 # 给用户")

    # dataclass 自动生成 __repr__ / __eq__
    @dataclasses.dataclass
    class Vec:
        x: int
        y: int

    v = Vec(3, 4)
    print(f"  dataclass repr: {v}          # 自动生成")


# ---------------------------------------------------------------------------
# ③ __eq__ / __lt__ / __hash__ / __bool__
# ---------------------------------------------------------------------------

def demo03_comparison():
    """③ __eq__ / __hash__ / __bool__ / __len__ —— 比较与真假判断"""
    print("\n③ 比较 / 哈希 / 真假")

    class Person:
        def __init__(self, name: str, age: int):
            self.name, self.age = name, age

        def __eq__(self, other):
            """== 运算符，定义"相等"的含义"""
            if not isinstance(other, Person):
                return NotImplemented
            return self.name == other.name and self.age == other.age

        def __hash__(self):
            """hash(obj) 返回哈希值，放到 set/dict key 的先决条件"""
            return hash((self.name, self.age))

        def __lt__(self, other):
            """< 运算符，仅此一个即可让 sorted() 工作"""
            if not isinstance(other, Person):
                return NotImplemented
            return self.age < other.age

        def __repr__(self):
            return f"Person({self.name!r}, {self.age})"

    a = Person("Alice", 30)
    b = Person("Alice", 30)
    c = Person("Bob", 25)

    print(f"  a == b: {a == b}")
    print(f"  a == c: {a == c}")
    print(f"  hash(a): {hash(a)}")
    print(f"  sorted([a, c]): {sorted([a, c])}")

    # __bool__ / __len__ —— if obj / bool(obj)
    class Basket:
        def __init__(self): self.items: list[str] = []

        def __len__(self): return len(self.items)

        def __bool__(self): return len(self.items) > 0       # 优先于 __len__

    basket = Basket()
    print(f"  空篮子 bool: {bool(basket)}")


# ---------------------------------------------------------------------------
# ④ __getitem__ / __setitem__ / __iter__ / __contains__
# ---------------------------------------------------------------------------

def demo04_container():
    """④ 容器模拟：让自定义类像 list/dict 一样用 []、for、in"""
    print("\n④ 容器模拟")

    class Shelf:
        """模拟一个只读书架，用 [] 取值，for 遍历，in 查找"""

        def __init__(self, books: list[str]):
            self._books = books

        def __getitem__(self, idx: int) -> str:
            """obj[i] 取值"""
            return self._books[idx]

        def __len__(self):
            return len(self._books)

        def __contains__(self, item: str) -> bool:
            """item in obj"""
            return item in self._books

        def __iter__(self):
            """for item in obj"""
            return iter(self._books)

        def __repr__(self):
            return f"Shelf({self._books})"

    shelf = Shelf(["Python", "Rust", "Go"])
    print(f"  shelf[0]: {shelf[0]}")
    print(f"  'Go' in shelf: {'Go' in shelf}")
    print(f"  for x in shelf: ", end="")
    for book in shelf:
        print(book, end=" ")
    print()


# ---------------------------------------------------------------------------
# ⑤ __call__ / __enter__ / __slots__ / __class__
# ---------------------------------------------------------------------------

def demo05_others():
    """⑤ __call__ / __enter__ / __slots__ / __class__ —— 其他高频 dunder"""
    print("\n⑤ 其他高频 dunder")

    # ── __call__：让实例像函数一样调用 ──
    class Multiplier:
        def __init__(self, factor: int):
            self.factor = factor

        def __call__(self, x: int) -> int:
            return self.factor * x

    double = Multiplier(2)
    print(f"  double(5) = {double(5)}        # 实例可调用")

    # ── __enter__ / __exit__：上下文管理器 ──
    class Trace:
        def __enter__(self):
            print("  __enter__: 进入 with 块")
            return self

        def __exit__(self, *args):
            print("  __exit__: 退出 with 块")

    with Trace():
        print("    with 中间")

    # ── __slots__：限制实例属性，节省内存 ──
    class Point2D:
        __slots__ = ("x", "y")           # 只能有 x 和 y，省掉 __dict__
        def __init__(self, x, y): self.x, self.y = x, y

    p = Point2D(1, 2)
    print(f"  Point2D(1,2).x = {p.x}      # __slots__ 无 __dict__")

    # ── __class__：实例指向自己的类 ──
    print(f"  实例 __class__ = {p.__class__}")


if __name__ == "__main__":
    demo01_lifecycle()
    demo02_string()
    demo03_comparison()
    demo04_container()
    demo05_others()
