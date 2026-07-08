"""functools.singledispatch —— 泛函数（按类型分发）

Python 3.12。
运行: python 05_singledispatch.py

singledispatch：根据第一个参数的类型，选择不同的函数实现。
类似于静态语言的函数重载，但在运行时根据类型动态分发。

演示：
  ① 基本用法：register + dispatch
  ② 多类型注册：一次注册多个类型
  ③ singledispatchmethod：用于类方法
  ④ dispatch()：手动查询分发函数
  ⑤ 实际场景 A：JSON 序列化自定义类型
  ⑥ 实际场景 B：通用处理器（替代 isinstance 链）
"""

import functools
from datetime import date, datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# ① 基本用法
# ---------------------------------------------------------------------------

@functools.singledispatch
def process(arg):
    """默认实现：不支持的类型"""
    raise NotImplementedError(f"不支持的类型: {type(arg).__name__}")


@process.register(int)
def _(arg: int) -> str:
    return f"整数: {arg} (二进制: {arg:b})"


@process.register(float)
def _(arg: float) -> str:
    return f"浮点数: {arg:.4f}"


@process.register(str)
def _(arg: str) -> str:
    return f"字符串: {arg!r} (长度 {len(arg)})"


@process.register(list)
def _(arg: list) -> str:
    return f"列表: {len(arg)} 个元素, 首个={arg[0]!r if arg else '空'}"


def demo01_basic():
    """① singledispatch 基本用法"""
    print("① 基本用法")

    for val in [42, 3.14, "hello", [1, 2, 3]]:
        print(f"  process({val!r:20}) = {process(val)}")

    try:
        process({"key": "value"})
    except NotImplementedError as e:
        print(f"  dict → NotImplementedError: {e}")


# ---------------------------------------------------------------------------
# ② 多类型注册（Python 3.11+：Union 注解）
# ---------------------------------------------------------------------------

@functools.singledispatch
def stringify(value) -> str:
    return str(value)


# 一次 register 多个类型（Python 3.11+）
@stringify.register(int)
@stringify.register(float)
@stringify.register(Decimal)
def _(value) -> str:
    return f"{value:g}"                  # 科学计数法会省略多余的零


@stringify.register(date)
@stringify.register(datetime)
def _(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value.strftime("%Y-%m-%d")


@stringify.register(bool)                # 注意：bool 要在 int 之前注册（bool 是 int 的子类）
def _(value: bool) -> str:
    return "是" if value else "否"


def demo02_multi_register():
    """② 多类型 register + 子类优先"""
    print("\n② 多类型注册")

    test_values = [
        42,
        3.14159,
        Decimal("1.2345"),
        True,
        False,
        date(2024, 1, 15),
        datetime(2024, 1, 15, 10, 30, 0),
        "hello",
    ]

    for val in test_values:
        print(f"  stringify({val!r:30}) = {stringify(val)!r}")


# ---------------------------------------------------------------------------
# ③ singledispatchmethod（类方法版本）
# ---------------------------------------------------------------------------

class Formatter:
    """用 singledispatchmethod 根据参数类型格式化输出"""

    @functools.singledispatchmethod
    def format(self, arg) -> str:
        return f"[未知类型 {type(arg).__name__}] {arg}"

    @format.register(int)
    def _(self, arg: int) -> str:
        return f"[整数] {arg:,}"

    @format.register(float)
    def _(self, arg: float) -> str:
        return f"[浮点] {arg:.2f}"

    @format.register(str)
    def _(self, arg: str) -> str:
        return f"[字符串] {arg!r}"

    @format.register(list)
    @format.register(tuple)
    def _(self, arg) -> str:
        items = ", ".join(str(x) for x in arg)
        return f"[序列({len(arg)})] [{items}]"


def demo03_method():
    """③ singledispatchmethod：类方法版"""
    print("\n③ singledispatchmethod")

    fmt = Formatter()
    for val in [1000000, 3.14159, "world", [1, 2, 3], (4, 5), {"key": "val"}]:
        print(f"  format({val!r:25}) = {fmt.format(val)}")


# ---------------------------------------------------------------------------
# ④ dispatch() 手动查询
# ---------------------------------------------------------------------------

def demo04_dispatch_query():
    """④ dispatch(type) 手动查询会分发到哪个实现"""
    print("\n④ dispatch() 查询分发函数")

    for t in [int, float, str, list, dict, bool]:
        impl = process.dispatch(t)
        print(f"  process.dispatch({t.__name__:8s}) = {impl.__qualname__}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景 A：JSON 序列化扩展
# ---------------------------------------------------------------------------

@functools.singledispatch
def to_json_serializable(obj):
    """把不能直接 JSON 序列化的对象转成可序列化的形式"""
    raise TypeError(f"对象 {type(obj).__name__} 不支持 JSON 序列化")


@to_json_serializable.register(datetime)
def _(obj: datetime):
    return obj.isoformat()


@to_json_serializable.register(date)
def _(obj: date):
    return obj.isoformat()


@to_json_serializable.register(Decimal)
def _(obj: Decimal):
    return float(obj)


@to_json_serializable.register(set)
@to_json_serializable.register(frozenset)
def _(obj):
    return sorted(obj)                   # 转成有序列表


import json


def custom_json_dump(data) -> str:
    """支持 datetime/Decimal/set 的 JSON 序列化"""
    def default(obj):
        return to_json_serializable(obj)
    return json.dumps(data, default=default, ensure_ascii=False, indent=2)


def demo05_json_serializer():
    """⑤ 实际场景：扩展 JSON 序列化"""
    print("\n⑤ JSON 序列化扩展")

    data = {
        "name": "Alice",
        "created_at": datetime(2024, 1, 15, 10, 30),
        "birthday": date(1990, 5, 20),
        "balance": Decimal("1234.56"),
        "tags": {"python", "dev", "open-source"},
    }

    print(custom_json_dump(data))


# ---------------------------------------------------------------------------
# ⑥ 实际场景 B：替代 isinstance 链
# ---------------------------------------------------------------------------

def demo06_replace_isinstance():
    """⑥ singledispatch 替代长 isinstance 链"""
    print("\n⑥ 替代 isinstance 链")

    # 传统写法（丑陋，难扩展）
    def render_bad(widget) -> str:
        if isinstance(widget, dict) and widget.get("type") == "button":
            return f"<button>{widget['label']}</button>"
        elif isinstance(widget, dict) and widget.get("type") == "input":
            return f"<input placeholder='{widget.get('placeholder', '')}' />"
        elif isinstance(widget, str):
            return f"<span>{widget}</span>"
        elif isinstance(widget, list):
            return "<div>" + "".join(render_bad(w) for w in widget) + "</div>"
        return ""

    # singledispatch 写法（易扩展，类型清晰）
    @functools.singledispatch
    def render(widget) -> str:
        return ""

    @render.register(str)
    def _(widget: str) -> str:
        return f"<span>{widget}</span>"

    @render.register(list)
    def _(widget: list) -> str:
        return "<div>" + "".join(render(w) for w in widget) + "</div>"

    # 注意：dict 按不同 type 字段区分时 singledispatch 不太合适
    # 这时候应用策略模式（字典分发）而不是 singledispatch

    widgets = ["标题文字", ["项目A", "项目B", "项目C"]]
    for w in widgets:
        print(f"  render({w!r:30}) = {render(w)}")


if __name__ == "__main__":
    demo01_basic()
    demo02_multi_register()
    demo03_method()
    demo04_dispatch_query()
    demo05_json_serializer()
    demo06_replace_isinstance()
