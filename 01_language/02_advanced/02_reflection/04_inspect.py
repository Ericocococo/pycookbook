"""反射 —— inspect 模块：深度自省

标准库。Python 3.12。
运行: python 04_inspect.py

inspect 是 getattr 家族的"重武器"版本：
  - 不只是"有没有"，而是"详细是什么"
  - 能拿到参数签名、源代码、调用栈、类继承链

演示：
  ① getmembers()：列举对象所有成员（可过滤）
  ② signature()：函数/方法的参数签名
  ③ getsource() / getsourcelines()：读取源代码
  ④ 类型判断谓词：isfunction / isclass / ismethod / isbuiltin
  ⑤ currentframe() / stack()：调用栈自省
  ⑥ 综合场景：自动生成函数的帮助文档
"""
import inspect


# 用于演示的示例类和函数
class Shape:
    """几何形状基类"""
    color: str = "black"

    def __init__(self, color: str = "black"):
        self.color = color

    def area(self) -> float:
        """返回面积，子类实现"""
        raise NotImplementedError

    @classmethod
    def from_string(cls, s: str) -> "Shape":
        """从字符串解析"""
        return cls()

    @staticmethod
    def validate_color(color: str) -> bool:
        """校验颜色名"""
        return isinstance(color, str) and len(color) > 0


class Circle(Shape):
    """圆形"""
    def __init__(self, radius: float, color: str = "black"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2


def greet(name: str, greeting: str = "你好", *, loud: bool = False) -> str:
    """打招呼函数

    Args:
        name: 对象名称
        greeting: 招呼语
        loud: 是否大写输出
    """
    msg = f"{greeting}, {name}!"
    return msg.upper() if loud else msg


# ---------------------------------------------------------------------------
# ① getmembers()
# ---------------------------------------------------------------------------

def demo01_getmembers():
    """① getmembers()：列举所有成员

    inspect.getmembers(obj) 返回 (name, value) 元组列表，
    等价于 [(n, getattr(obj, n)) for n in dir(obj)]，但更健壮（处理 descriptor 边界情况）。

    第二参数是过滤谓词（predicate），常用：
      inspect.isfunction / ismethod / isclass / isbuiltin / isdatadescriptor
    """
    print("① getmembers()")

    c = Circle(5)

    # 只看方法
    methods = inspect.getmembers(c, predicate=inspect.ismethod)
    print("  Circle 实例方法:")
    for name, method in methods:
        if not name.startswith("_"):
            print(f"    {name}: {method}")

    # 类上的函数（未绑定）
    functions = inspect.getmembers(Circle, predicate=inspect.isfunction)
    print("  Circle 类函数（不含双下划线）:")
    for name, fn in functions:
        if not name.startswith("_"):
            print(f"    {name}")

    # 只看属性（非方法）
    attrs = [(n, v) for n, v in inspect.getmembers(c)
             if not callable(v) and not n.startswith("_")]
    print("  非方法属性:", attrs)


# ---------------------------------------------------------------------------
# ② signature()
# ---------------------------------------------------------------------------

def demo02_signature():
    """② signature()：函数参数签名

    inspect.signature(func) 返回 Signature 对象，包含：
      - parameters：OrderedDict，键是参数名，值是 Parameter 对象
      - return_annotation：返回值类型注解

    Parameter 对象包含：
      - name           参数名
      - kind           参数类型（POSITIONAL_ONLY / POSITIONAL_OR_KEYWORD / VAR_POSITIONAL / KEYWORD_ONLY / VAR_KEYWORD）
      - default        默认值（Parameter.empty 表示无默认值）
      - annotation     类型注解

    用途：框架在运行时检查函数接口（FastAPI 就大量用这个实现参数注入）。
    """
    print("\n② signature()")

    sig = inspect.signature(greet)
    print("  函数签名:", sig)

    for name, param in sig.parameters.items():
        kind_name = param.kind.name   # 参数类别字符串
        default = "(无默认值)" if param.default is inspect.Parameter.empty else repr(param.default)
        annotation = param.annotation if param.annotation is not inspect.Parameter.empty else "未注解"
        print(f"    {name}: kind={kind_name}, default={default}, annotation={annotation}")

    print("  返回值注解:", sig.return_annotation)

    # 用 bind() 模拟调用，验证参数合法性
    try:
        bound = sig.bind("Alice", loud=True)
        bound.apply_defaults()     # 填充有默认值的参数
        print("  bind 结果:", dict(bound.arguments))
    except TypeError as e:
        print("  参数错误:", e)


# ---------------------------------------------------------------------------
# ③ getsource()
# ---------------------------------------------------------------------------

def demo03_getsource():
    """③ getsource()：读取源代码

    inspect.getsource(obj) 返回对象（函数/类/模块/方法）的源代码字符串。
    inspect.getsourcelines(obj) 返回 (lines, start_lineno) 元组。
    inspect.getfile(obj) 返回定义所在的文件路径。

    注意：只对有源文件的对象有效（内置函数、C 扩展不行）。
    """
    print("\n③ getsource()")

    # 获取函数源码
    src = inspect.getsource(greet)
    print("  greet 函数源码:")
    for line in src.splitlines():
        print("   ", line)

    # 源码行号
    lines, start = inspect.getsourcelines(Circle.area)
    print(f"\n  Circle.area 从第 {start} 行开始，共 {len(lines)} 行")

    # 文件路径
    try:
        file = inspect.getfile(Circle)
        print("  定义文件:", file)
    except TypeError as e:
        print("  无源文件:", e)


# ---------------------------------------------------------------------------
# ④ 类型判断谓词
# ---------------------------------------------------------------------------

def demo04_predicates():
    """④ inspect 的类型判断谓词

    inspect 提供一批 isXxx 函数，比 isinstance(obj, types.FunctionType) 更语义化：
      isfunction(obj)    普通函数（def 定义，非 lambda 非方法）
      ismethod(obj)      绑定方法（实例.方法）
      isclass(obj)       类
      isbuiltin(obj)     内置函数（len/print 等）
      ismodule(obj)      模块
      isgeneratorfunction(obj)  生成器函数
      iscoroutinefunction(obj)  async def 函数
    """
    print("\n④ 类型判断谓词")

    import math

    async def async_fn(): pass
    def gen_fn(): yield 1
    def plain_fn(): pass
    c = Circle(3)

    tests = [
        ("普通函数", plain_fn),
        ("lambda", lambda: None),
        ("生成器函数", gen_fn),
        ("async 函数", async_fn),
        ("实例方法", c.area),
        ("类", Circle),
        ("内置 len", len),
        ("模块 math", math),
        ("整数 42", 42),
    ]

    header = f"  {'对象':16s} {'isfunction':10s} {'ismethod':10s} {'isclass':8s} {'isbuiltin':10s} {'isgenfunc':10s} {'iscoroutine':11s}"
    print(header)
    for label, obj in tests:
        print(f"  {label:16s} "
              f"{str(inspect.isfunction(obj)):10s}"
              f"{str(inspect.ismethod(obj)):10s}"
              f"{str(inspect.isclass(obj)):8s}"
              f"{str(inspect.isbuiltin(obj)):10s}"
              f"{str(inspect.isgeneratorfunction(obj)):10s}"
              f"{str(inspect.iscoroutinefunction(obj)):11s}")


# ---------------------------------------------------------------------------
# ⑤ 调用栈自省
# ---------------------------------------------------------------------------

def demo05_stack():
    """⑤ currentframe() / stack()：调用栈

    inspect.currentframe()  返回当前帧对象（FrameInfo 的基础）
    inspect.stack()         返回从当前帧到最顶层的调用栈列表

    每个 FrameInfo 包含：
      frame           帧对象（包含局部变量、全局变量）
      filename        源文件路径
      lineno          当前行号
      function        函数名
      code_context    源码行（列表）

    用途：日志记录当前调用位置、调试工具、测试断言框架。
    """
    print("\n⑤ 调用栈")

    def get_caller_info(depth=1):
        """返回调用者的函数名和行号"""
        frame_info = inspect.stack()[depth]
        return f"{frame_info.function}:{frame_info.lineno}"

    def level_a():
        return get_caller_info(depth=1)   # 谁调用了 get_caller_info

    def level_b():
        return level_a()

    print("  调用者:", level_b())

    # 打印当前调用栈（简化）
    stack = inspect.stack()
    print("  当前调用栈（前 4 帧）:")
    for fi in stack[:4]:
        print(f"    {fi.function}() in {fi.filename.split('/')[-1].split(chr(92))[-1]}:{fi.lineno}")


# ---------------------------------------------------------------------------
# ⑥ 综合场景：自动生成帮助文档
# ---------------------------------------------------------------------------

def demo06_auto_doc():
    """⑥ 综合场景：自动生成函数帮助摘要

    框架通常用 inspect 自动提取函数信息生成 API 文档或 CLI 帮助。
    """
    print("\n⑥ 自动生成帮助摘要")

    def describe(func):
        """提取函数的签名 + 文档字符串摘要"""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or "（无文档）"   # getdoc 会自动去除缩进

        lines = [f"  函数: {func.__name__}{sig}"]
        lines.append(f"  说明: {doc.splitlines()[0]}")
        lines.append("  参数:")
        for name, param in sig.parameters.items():
            ann = "" if param.annotation is inspect.Parameter.empty else f": {param.annotation.__name__ if hasattr(param.annotation, '__name__') else param.annotation}"
            default = "" if param.default is inspect.Parameter.empty else f" = {param.default!r}"
            lines.append(f"    {name}{ann}{default}  [{param.kind.name}]")
        return "\n".join(lines)

    print(describe(greet))
    print()
    print(describe(Circle.__init__))


if __name__ == "__main__":
    demo01_getmembers()
    demo02_signature()
    demo03_getsource()
    demo04_predicates()
    demo05_stack()
    demo06_auto_doc()
