"""dunder 属性 —— 函数/方法级：__name__ / __defaults__ / __code__ / __annotations__ 等

Python 3.12。运行: python 03_function.py

演示：
  ① __name__ / __qualname__：函数名和限定名（含类名）
  ② __doc__：函数的 docstring
  ③ __defaults__ / __kwdefaults__：默认参数值
  ④ __annotations__：类型注解字典
  ⑤ __code__：字节码对象，内含 co_varnames / co_argcount 等
  ⑥ __closure__：闭包捕获的自由变量
  ⑦ __globals__ / __module__ / __dict__：函数的环境信息
"""


# ---------------------------------------------------------------------------
# ① __name__ / __qualname__
# ---------------------------------------------------------------------------

def demo01_name():
    """① __name__ 是函数名，__qualname__ 包含类名路径"""
    print("① __name__ / __qualname__")

    def outer():
        def inner():
            pass
        return inner

    print(f"  outer.__name__ = {outer.__name__}")
    print(f"  outer.__qualname__ = {outer.__qualname__}")

    f = outer()
    print(f"  inner.__name__ = {f.__name__}            # 只看自己名")
    print(f"  inner.__qualname__ = {f.__qualname__}    # 包含 outer.inner")

    # 类方法的 __qualname__
    class A:
        def method(self): pass

    print(f"  A.method.__qualname__ = {A.method.__qualname__}")  # A.method


# ---------------------------------------------------------------------------
# ② __doc__
# ---------------------------------------------------------------------------

def demo02_doc():
    """② 函数的 docstring，没写则为 None"""
    print("\n② __doc__")

    def documented(x: int) -> str:
        """将整数转为字符串。"""
        return str(x)

    def undocumented(x): pass

    print(f"  documented.__doc__   = {documented.__doc__!r}")
    print(f"  undocumented.__doc__ = {undocumented.__doc__!r}")

    # help() 内部就是读 __doc__
    print("  help() 显示的就是 __doc__ 内容")


# ---------------------------------------------------------------------------
# ③ __defaults__ / __kwdefaults__
# ---------------------------------------------------------------------------

def demo03_defaults():
    """③ __defaults__ 是位置默认参数元组，__kwdefaults__ 是关键字默认参数字典"""
    print("\n③ __defaults__ / __kwdefaults__")

    def greet(name: str, greeting: str = "Hello", *, suffix: str = "!"):
        """name 无默认，greeting 有位置默认，suffix 是 keyword-only 默认"""

    print(f"  greet.__defaults__   = {greet.__defaults__}     # ('Hello',)")
    print(f"  greet.__kwdefaults__ = {greet.__kwdefaults__}   # suffix 的默认值")

    # 无默认参数时 __defaults__ 为 None
    def simple(x): pass
    print(f"  simple.__defaults__ = {simple.__defaults__}")


# ---------------------------------------------------------------------------
# ④ __annotations__
# ---------------------------------------------------------------------------

def demo04_annotations():
    """④ __annotations__ —— 函数的类型注解字典，key 是参数名 + 'return'"""
    print("\n④ __annotations__")

    def process(data: list[int], limit: int = 10) -> bool:
        ...

    print(f"  process.__annotations__ = {process.__annotations__}")

    # 无注解时为空
    def naked(x): pass
    print(f"  naked.__annotations__   = {naked.__annotations__}")


# ---------------------------------------------------------------------------
# ⑤ __code__
# ---------------------------------------------------------------------------

def demo05_code():
    """⑤ __code__ 是字节码对象，可查参数名/参数个数/行号等"""
    print("\n⑤ __code__")

    def calc(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    code = calc.__code__
    print(f"  co_varnames = {code.co_varnames}    # 全部局部变量名")
    print(f"  co_argcount = {code.co_argcount}    # 位置参数个数(不含 *args)")
    print(f"  co_kwonlyargcount = {code.co_kwonlyargcount}  # keyword-only 参数个数")
    print(f"  co_filename = {code.co_filename}     # 定义该函数的源文件")
    print(f"  co_firstlineno = {code.co_firstlineno}  # 函数的起始行号")
    print(f"  co_consts = {code.co_consts}        # 函数内的常量元组")


# ---------------------------------------------------------------------------
# ⑥ __closure__
# ---------------------------------------------------------------------------

def demo06_closure():
    """⑥ __closure__ 是闭包捕获的外部变量元组，每个元素是一个 cell"""
    print("\n⑥ __closure__")

    def make_multiplier(factor: int):
        def multiply(x: int) -> int:
            return x * factor         # factor 是闭包捕获的自由变量
        return multiply

    double = make_multiplier(2)
    triple = make_multiplier(3)

    print(f"  double(5)  = {double(5)}")
    print(f"  triple(5)  = {triple(5)}")
    print(f"  double.__closure__[0].cell_contents = {double.__closure__[0].cell_contents}  # factor=2")
    print(f"  triple.__closure__[0].cell_contents = {triple.__closure__[0].cell_contents}  # factor=3")

    # 普通函数（非闭包）__closure__ 为 None
    def plain(x): return x + 1
    print(f"  plain.__closure__ = {plain.__closure__}")


# ---------------------------------------------------------------------------
# ⑦ __globals__ / __module__ / __dict__
# ---------------------------------------------------------------------------

def demo07_env():
    """⑦ __globals__ / __module__ / __dict__ —— 函数的环境信息"""
    print("\n⑦ 函数环境")

    def demo_func():
        pass

    # __module__ 表示函数定义在哪个模块
    print(f"  demo_func.__module__ = {demo_func.__module__!r}")

    # __globals__ 是定义该函数的模块的全局命名空间（就是模块的 __dict__）
    print(f"  '__name__' in demo_func.__globals__: {'__name__' in demo_func.__globals__}")

    # 函数也可以挂自定义属性（很少用）
    demo_func.custom_attr = 42
    print(f"  demo_func.custom_attr = {demo_func.custom_attr}")


if __name__ == "__main__":
    demo01_name()
    demo02_doc()
    demo03_defaults()
    demo04_annotations()
    demo05_code()
    demo06_closure()
    demo07_env()
