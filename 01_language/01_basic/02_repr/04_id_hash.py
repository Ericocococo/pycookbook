"""对象表示 —— id / hash / is vs ==

Python 3.12。
运行: python 04_id_hash.py

演示：
  ① id()：对象的唯一标识（内存地址）
  ② is vs ==：身份比较 vs 值比较
  ③ hash()：哈希值，决定对象能否放进 set/dict
  ④ __hash__ / __eq__：自定义哈希和相等
  ⑤ 小整数缓存和字符串驻留：is 的陷阱
"""


def demo01_id():
    """① id()：对象唯一标识

    id(obj) 返回对象的唯一整数标识，在 CPython 里就是内存地址。
    同一个对象在其生命周期内 id 不变。
    不同对象的 id 可能相同（对象销毁后，新对象可以复用地址）。
    """
    print("① id()")

    a = [1, 2, 3]
    b = a           # b 和 a 指向同一个对象
    c = [1, 2, 3]   # c 是新对象，内容相同但不是同一个

    print(f"  a id={id(a)}")
    print(f"  b id={id(b)}  (b = a，同一个对象)")
    print(f"  c id={id(c)}  (c 是新列表，不同对象)")
    print(f"  id(a) == id(b): {id(a) == id(b)}")   # True
    print(f"  id(a) == id(c): {id(a) == id(c)}")   # False

    # 修改 a，b 也会变（因为是同一个对象）
    a.append(4)
    print(f"  修改 a 后，b = {b}")   # [1, 2, 3, 4]


def demo02_is_vs_equal():
    """② is vs ==：最容易混淆的区别

    ==   值相等（调用 __eq__）：内容是否相同
    is   身份相同（比较 id）：是否是同一个对象

    规则：
      is None / is not None  → 始终用 is，因为 None 是单例
      比较值是否相等         → 始终用 ==
      永远不要用 is 比较字符串、整数、列表等（结果不稳定）
    """
    print("\n② is vs ==")

    a = [1, 2, 3]
    b = [1, 2, 3]   # 内容相同，但不同对象

    print(f"  a == b: {a == b}")    # True（值相等）
    print(f"  a is b: {a is b}")    # False（不是同一个对象）

    # None 比较必须用 is
    x = None
    print(f"\n  None 比较:")
    print(f"  x is None:  {x is None}")   # 正确写法
    print(f"  x == None:  {x == None}")   # 能用但不推荐

    # is 的正确使用场景：单例（None / True / False）
    print(f"\n  True/False 是单例:")
    print(f"  True is True:   {True is True}")
    print(f"  False is False: {False is False}")


def demo03_hash():
    """③ hash()：哈希值

    hash(obj) 返回对象的整数哈希值。
    哈希值决定对象在 dict / set 中的存储位置。

    可哈希的对象：数字、字符串、元组（含不可哈希元素的除外）、frozenset
    不可哈希的对象：list、dict、set（可变对象）

    规则：
      相等的对象必须有相同的哈希值（a == b → hash(a) == hash(b)）
      反之不成立（哈希碰撞是正常的）
    """
    print("\n③ hash()")

    # 可哈希类型
    hashables = [42, 3.14, "hello", (1, 2, 3), True, None]
    for v in hashables:
        print(f"  hash({v!r:15}) = {hash(v)}")

    # 不可哈希类型
    print()
    for v in [[1, 2], {"a": 1}, {1, 2}]:
        try:
            hash(v)
        except TypeError as e:
            print(f"  hash({v!r}) → {e}")

    # 相等的值哈希相同
    print(f"\n  hash(1) == hash(1.0) == hash(True): "
          f"{hash(1) == hash(1.0) == hash(True)}")  # True！
    print(f"  1 == 1.0 == True: {1 == 1.0 == True}")


def demo04_custom_hash():
    """④ 自定义 __hash__ 和 __eq__

    定义了 __eq__ 的类，__hash__ 会被自动设为 None（不可哈希）。
    如果想让对象可以放进 set/dict，必须同时定义 __hash__。

    规则：__eq__ 相等的两个对象，__hash__ 必须返回相同值。
    """
    print("\n④ 自定义 __hash__ / __eq__")

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __eq__(self, other):
            if not isinstance(other, Point):
                return NotImplemented
            return self.x == other.x and self.y == other.y

        def __hash__(self):
            # 用 tuple 的哈希（相等的 Point 哈希相同）
            return hash((self.x, self.y))

        def __repr__(self):
            return f"Point({self.x}, {self.y})"

    p1 = Point(1, 2)
    p2 = Point(1, 2)   # 内容相同
    p3 = Point(3, 4)

    print(f"  p1 == p2: {p1 == p2}")          # True
    print(f"  p1 is p2: {p1 is p2}")          # False（不同对象）
    print(f"  hash(p1) == hash(p2): {hash(p1) == hash(p2)}")  # True

    # 可以放进 set 和 dict 了
    s = {p1, p2, p3}
    print(f"  set{{{p1}, {p2}, {p3}}} = {s}")   # p1 和 p2 是同一个元素，只保留一个

    d = {p1: "point1"}
    print(f"  用 p2 查 dict（p1 == p2）: {d[p2]}")   # 能找到，因为相等


def demo05_intern():
    """⑤ 小整数缓存与字符串驻留（is 的陷阱）

    CPython 优化：
      小整数（-5 到 256）会被缓存，同一个值总是同一个对象
      简单字符串字面量会被"驻留"（intern），可能是同一个对象

    这导致 is 比较整数/字符串时结果不稳定，严重依赖实现细节。
    这是永远不应该用 is 比较值的根本原因。
    """
    print("\n⑤ 小整数缓存与字符串驻留（陷阱）")

    # 小整数缓存：-5 到 256 是同一个对象
    a = 100
    b = 100
    print(f"  a = b = 100: a is b = {a is b}")   # True（缓存）

    c = 1000
    d = 1000
    print(f"  c = d = 1000: c is d = {c is d}")  # False（超出缓存范围）

    # 字符串驻留
    s1 = "hello"
    s2 = "hello"
    print(f"\n  s1 = s2 = 'hello': s1 is s2 = {s1 is s2}")   # True（驻留）

    s3 = "hello world"
    s4 = "hello world"
    print(f"  含空格的字符串: s3 is s4 = {s3 is s4}")         # 可能 True 也可能 False

    # 结论
    print("\n  结论：不要用 is 比较整数/字符串，用 ==")
    print(f"  100 == 100: {100 == 100}")     # 永远可靠
    print(f"  'hello' == 'hello': {'hello' == 'hello'}")  # 永远可靠


if __name__ == "__main__":
    demo01_id()
    demo02_is_vs_equal()
    demo03_hash()
    demo04_custom_hash()
    demo05_intern()
