"""反射 —— vars / dir / callable / type / isinstance / issubclass

Python 3.12。
运行: python 02_introspection.py

这一批内置函数都是"问对象问题"的工具：
  vars / dir     ← 有什么属性？
  type           ← 是什么类型？
  isinstance     ← 是某种类型吗？
  issubclass     ← 是某个类的子类吗？
  callable       ← 能被调用吗？

演示：
  ① vars()：看实例属性字典（__dict__）
  ② dir()：探索对象所有名称（含继承链）
  ③ type()：获取精确类型
  ④ isinstance()：类型判断（推荐方式，支持继承和联合类型）
  ⑤ issubclass()：检查类继承关系
  ⑥ callable()：判断是否可调用
  ⑦ 综合场景：运行时检查接口合规性
"""


class Animal:
    kingdom = "动物界"   # 类属性

    def __init__(self, name, sound):
        self.name = name    # 实例属性
        self.sound = sound

    def speak(self):
        return f"{self.name} 说 {self.sound}"


class Dog(Animal):
    def __init__(self, name):
        super().__init__(name, "汪")
        self.tricks = []

    def learn(self, trick):
        self.tricks.append(trick)


# ---------------------------------------------------------------------------
# ① vars()
# ---------------------------------------------------------------------------

def demo01_vars():
    """① vars()：实例属性字典

    vars(obj) 返回 obj.__dict__，只包含"这个实例自己的属性"，
    不含类属性、继承来的属性、内置方法。

    直接修改 vars() 返回的 dict 等价于 setattr（同一个对象）。
    """
    print("① vars()")

    dog = Dog("旺财")
    dog.learn("握手")

    print("  vars(dog):", vars(dog))    # {'name': '旺财', 'sound': '汪', 'tricks': ['握手']}

    # vars() 返回的就是 __dict__ 本身（同一个对象）
    print("  是同一个对象:", vars(dog) is dog.__dict__)

    # 类的 vars() 包含类体里定义的所有东西（方法、类属性）
    cls_vars = vars(Dog)
    print("  Dog 类里定义的名称:", [k for k in cls_vars if not k.startswith("__")])

    # vars() 不带参数 = 当前局部作用域（等同于 locals()）
    x = 1
    y = 2
    print("  局部 vars():", {k: v for k, v in vars().items() if not k.startswith("_")})


# ---------------------------------------------------------------------------
# ② dir()
# ---------------------------------------------------------------------------

def demo02_dir():
    """② dir()：探索对象所有可用名称

    dir(obj) 收集 obj 自身 + 所有父类中的属性/方法名，排序去重。
    返回字符串列表，是交互式探索的利器。

    dir 的规则：
      - 实例：实例 __dict__ + 类 __dict__ + 父类 __dict__（MRO 顺序）
      - 类：类 __dict__ + 父类 __dict__
      - 模块：模块里所有名称

    注意：dir 可以被 __dir__ 魔法方法重写，不保证完整性。
    """
    print("\n② dir()")

    dog = Dog("旺财")

    all_names = dir(dog)
    print("  dir(dog) 总数:", len(all_names))

    # 过滤掉双下划线的内置名称，看用户定义的
    user_attrs = [n for n in all_names if not n.startswith("_")]
    print("  用户定义属性:", user_attrs)

    # 常见用法：找出所有可调用方法
    methods = [n for n in dir(dog) if callable(getattr(dog, n)) and not n.startswith("_")]
    print("  可调用方法:", methods)

    # dir 不带参数 = 当前作用域的名称（和 vars() 类似但返回键列表）
    loc_dir = [n for n in dir() if not n.startswith("_")]
    print("  局部 dir():", loc_dir)


# ---------------------------------------------------------------------------
# ③ type()
# ---------------------------------------------------------------------------

def demo03_type():
    """③ type()：获取精确类型

    type(obj) 返回 obj 的类型，等价于 obj.__class__。
    与 isinstance 的区别：type 不认继承，isinstance 认。

    type 还有三参数用法：type(name, bases, dict) 动态创建类（元类编程）。
    """
    print("\n③ type()")

    dog = Dog("旺财")
    print("  type(dog):", type(dog))                 # <class '__main__.Dog'>
    print("  type(dog) is Dog:", type(dog) is Dog)   # True
    print("  type(dog) is Animal:", type(dog) is Animal)   # False！

    # 对比 isinstance（推荐用 isinstance 做类型判断）
    print("  isinstance(dog, Dog):", isinstance(dog, Dog))       # True
    print("  isinstance(dog, Animal):", isinstance(dog, Animal)) # True（认继承）

    # type 的常见合法用途：精确匹配类型（不想接受子类）
    values = [1, True, 1.0]   # True 是 bool，bool 是 int 的子类
    for v in values:
        print(f"  {v!r}: type={type(v).__name__}, isinstance(int)={isinstance(v, int)}, type is int={type(v) is int}")


# ---------------------------------------------------------------------------
# ④ isinstance()
# ---------------------------------------------------------------------------

def demo04_isinstance():
    """④ isinstance()：类型判断的推荐方式

    isinstance(obj, cls_or_tuple) 支持：
      - 单个类：isinstance(x, int)
      - 类的元组：isinstance(x, (int, float))  ← 检查是否是其中任意一种
      - 抽象基类（ABC）：isinstance(x, Iterable)
      - Python 3.10+ 联合类型：isinstance(x, int | float)

    永远用 isinstance，不要用 type(x) == SomeType（不支持继承）。
    """
    print("\n④ isinstance()")

    dog = Dog("旺财")

    # 支持继承
    print("  dog 是 Dog:", isinstance(dog, Dog))
    print("  dog 是 Animal:", isinstance(dog, Animal))
    print("  dog 是 object:", isinstance(dog, object))   # 所有类都是 object 子类

    # 元组：一次检查多个类型（常用于数值兼容处理）
    for val in [1, 1.5, "hi", True, None]:
        is_num = isinstance(val, (int, float))
        print(f"  {val!r:6} 是数字类型: {is_num}")

    # 抽象基类：检查协议而非具体类型（更 duck-typing）
    from collections.abc import Iterable, Callable, Mapping
    for obj in [[1, 2], "abc", 42, {}, len]:
        print(f"  {type(obj).__name__:8s}  Iterable={isinstance(obj, Iterable)}  "
              f"Callable={isinstance(obj, Callable)}  Mapping={isinstance(obj, Mapping)}")


# ---------------------------------------------------------------------------
# ⑤ issubclass()
# ---------------------------------------------------------------------------

def demo05_issubclass():
    """⑤ issubclass()：类继承关系检查

    issubclass(cls, parent) 检查 cls 是否是 parent 的子类（含自身）。
    用于检查"类"而不是"实例"。
    """
    print("\n⑤ issubclass()")

    print("  Dog 是 Animal 的子类:", issubclass(Dog, Animal))
    print("  Animal 是 Dog 的子类:", issubclass(Animal, Dog))   # False
    print("  Dog 是自身的子类:", issubclass(Dog, Dog))           # True（定义如此）
    print("  Dog 是 object 的子类:", issubclass(Dog, object))   # True

    # 同样支持元组
    from collections.abc import Iterable, Sized
    print("  list 是 Iterable:", issubclass(list, Iterable))
    print("  list 是 Sized:", issubclass(list, Sized))

    # 常见用法：插件系统验证插件继承了基类
    class Plugin:
        def run(self): ...

    class MyPlugin(Plugin):
        def run(self): return "done"

    candidate = MyPlugin
    if issubclass(candidate, Plugin) and candidate is not Plugin:
        print("  MyPlugin 是合法插件")


# ---------------------------------------------------------------------------
# ⑥ callable()
# ---------------------------------------------------------------------------

def demo06_callable():
    """⑥ callable()：判断是否可调用

    callable(obj) 等价于 hasattr(obj, "__call__")。
    函数、方法、类（调用即实例化）、实现了 __call__ 的对象都返回 True。
    """
    print("\n⑥ callable()")

    class Adder:
        def __call__(self, x, y):
            return x + y

    add = Adder()

    tests = [
        ("函数 len",     len),
        ("lambda",       lambda x: x),
        ("类 Dog",       Dog),        # 类本身可调用（调用 = 实例化）
        ("实例 Dog()",   Dog("旺财")), # 普通实例不可调用
        ("Adder()",      add),         # 实现了 __call__ 的实例可调用
        ("整数 42",      42),
        ("字符串 'hi'",  "hi"),
        ("内置 print",   print),
    ]

    for label, obj in tests:
        print(f"  {label:16s}: callable={callable(obj)}")


# ---------------------------------------------------------------------------
# ⑦ 综合场景：接口合规性检查
# ---------------------------------------------------------------------------

def demo07_interface_check():
    """⑦ 综合场景：运行时检查插件接口合规性

    框架通常要求插件实现特定接口（方法名 + 签名）。
    用 hasattr + callable + isinstance 在加载时验证，
    比运行时才发现 AttributeError 友好得多。
    """
    print("\n⑦ 接口合规性检查")

    REQUIRED_METHODS = ["setup", "process", "teardown"]

    class GoodPlugin:
        def setup(self):    print("    初始化")
        def process(self, data): return data
        def teardown(self): print("    清理")

    class BadPlugin:
        def setup(self): pass
        # 缺少 process 和 teardown

    class WrongPlugin:
        setup = "not a method"  # 有这个名字，但不可调用
        def process(self, data): return data
        def teardown(self): pass

    def validate_plugin(cls):
        errors = []
        for method in REQUIRED_METHODS:
            if not hasattr(cls, method):
                errors.append(f"缺少方法: {method}")
            elif not callable(getattr(cls, method)):
                errors.append(f"{method} 不可调用")
        return errors

    for cls in [GoodPlugin, BadPlugin, WrongPlugin]:
        errors = validate_plugin(cls)
        status = "✓ 合规" if not errors else f"✗ {'; '.join(errors)}"
        print(f"  {cls.__name__:14s}: {status}")


if __name__ == "__main__":
    demo01_vars()
    demo02_dir()
    demo03_type()
    demo04_isinstance()
    demo05_issubclass()
    demo06_callable()
    demo07_interface_check()
