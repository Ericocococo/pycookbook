"""对象表示 —— repr / str / ascii / __repr__ / __str__

Python 3.12。
运行: python 01_repr_str.py

repr 和 str 是两种"把对象变成字符串"的方式，用途不同：
  str(obj)   → 给人看的，友好，可读
  repr(obj)  → 给开发者看的，精确，通常可以 eval 还原

演示：
  ① str vs repr 的区别
  ② ascii()：非 ASCII 字符用 \\uXXXX 转义
  ③ 自定义类实现 __str__ 和 __repr__
  ④ f-string 里的 !s / !r / !a 转换符
  ⑤ repr 在调试中的价值
"""


def demo01_str_vs_repr():
    """① str vs repr 的核心区别

    str：  可读性优先，隐藏细节
    repr： 精确性优先，暴露类型和结构，通常满足 eval(repr(obj)) == obj

    区别在字符串上最明显：
      str("hello")  → hello       （不带引号，直接打印内容）
      repr("hello") → 'hello'     （带引号，说明它是字符串）
    """
    print("① str vs repr")

    values = [
        "hello",            # 字符串
        "hello\nworld",     # 含换行
        42,
        3.14,
        None,
        True,
        [1, 2, 3],
        {"key": "value"},
    ]

    print(f"  {'值':25s} {'str()':25s} {'repr()'}")
    print("  " + "-" * 70)
    for v in values:
        print(f"  {str(v):25s} {repr(v)}")

    # 核心差异：字符串里的特殊字符
    s = "第一行\n第二行\t结尾"
    print(f"\n  str():  {str(s)}")      # 换行符生效，真的换行
    print(f"  repr(): {repr(s)}")      # 换行符显示为 \n，一目了然


def demo02_ascii():
    """② ascii()：非 ASCII 字符转义

    ascii(obj) 类似 repr()，但把所有非 ASCII 字符（如中文、emoji）
    替换为 \\\\uXXXX 或 \\\\UXXXXXXXX 转义序列。

    用途：
      - 生成只含 ASCII 的日志，方便传输和存储
      - 调试时确认字符串是否含隐藏的 Unicode 字符
    """
    print("\n② ascii()")

    values = ["hello", "你好", "café", "emoji: 🎉", "hello\nworld"]
    for v in values:
        print(f"  repr()  : {repr(v)}")
        print(f"  ascii() : {ascii(v)}")
        print()


def demo03_custom_class():
    """③ 自定义类的 __str__ 和 __repr__

    __str__    str(obj) 和 print(obj) 调用，给用户看
    __repr__   repr(obj) 调用，给开发者看，建议格式：ClassName(field=value, ...)

    只实现一个时：
      只有 __repr__：str() 会 fallback 到 __repr__（推荐先实现这个）
      只有 __str__： repr() 仍显示默认的 <ClassName object at 0x...>

    原则：__repr__ 要能让开发者"看一眼就知道对象的状态"。
    """
    print("\n③ 自定义 __str__ / __repr__")

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __str__(self):
            # 用户友好：简洁
            return f"({self.x}, {self.y})"

        def __repr__(self):
            # 开发者友好：精确，可还原
            return f"Point(x={self.x!r}, y={self.y!r})"

    p = Point(3, 4)
    print(f"  str(p):   {str(p)}")        # (3, 4)
    print(f"  repr(p):  {repr(p)}")       # Point(x=3, y=4)
    print(f"  print(p): ", end=""); print(p)  # 调用 __str__

    # 列表里的元素用 repr（不是 str）
    points = [Point(1, 2), Point(3, 4)]
    print(f"  列表里:   {points}")        # 列表用 repr 展示元素

    # 只有 __repr__ 的情况
    class SimplePoint:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            return f"SimplePoint({self.x}, {self.y})"

    sp = SimplePoint(1, 2)
    print(f"\n  只有 __repr__ 时:")
    print(f"  repr(sp): {repr(sp)}")
    print(f"  str(sp):  {str(sp)}")    # fallback 到 __repr__


def demo04_fstring_conversion():
    """④ f-string 里的转换符 !s / !r / !a

    f"{value!s}"  → 等价于 f"{str(value)}"
    f"{value!r}"  → 等价于 f"{repr(value)}"
    f"{value!a}"  → 等价于 f"{ascii(value)}"

    最常用：!r，调试时显示带引号的字符串，一眼看出内容。
    """
    print("\n④ f-string 转换符")

    s = "hello\nworld"
    name = "你好"

    print(f"  默认  f'{{s}}':  {s}")          # 换行生效
    print(f"  !s    f'{{s!s}}': {s!s}")        # 同默认
    print(f"  !r    f'{{s!r}}': {s!r}")        # 'hello\\nworld'，调试利器
    print(f"  !a    f'{{name!a}}': {name!a}")  # '\\u4f60\\u597d'


def demo05_repr_debug():
    """⑤ repr 在调试中的价值

    repr 能暴露肉眼看不到的差异：
      - 字符串两端的空格
      - 换行符 vs 空格
      - Unicode 字符
      - None vs 空字符串
    """
    print("\n⑤ repr 调试价值")

    # 场景：两个看起来一样的字符串，比较却不相等
    a = "hello "     # 末尾有空格
    b = "hello"

    print(f"  a == b: {a == b}")          # False
    print(f"  str: '{a}' == '{b}'")       # 肉眼看不出差异
    print(f"  repr: {repr(a)} == {repr(b)}")   # 立刻看出空格

    # 场景：None vs 空字符串
    values = [None, "", "0", 0, False]
    print("\n  容易混淆的值（用 repr 区分）:")
    for v in values:
        print(f"    repr: {repr(v):10s}  bool: {bool(v)}")


if __name__ == "__main__":
    demo01_str_vs_repr()
    demo02_ascii()
    demo03_custom_class()
    demo04_fstring_conversion()
    demo05_repr_debug()
