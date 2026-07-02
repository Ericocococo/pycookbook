"""json —— 序列化 json 不认识的类型(datetime / Decimal / 自定义对象)

标准库。Python 3.12。运行: python 03_custom_types.py

json 默认只认 dict/list/str/int/float/bool/None。遇到其它类型会抛 TypeError,
需要告诉它"怎么转成能序列化的东西"。两种方式:default 函数 或 自定义 Encoder。
"""
import json
from datetime import datetime
from decimal import Decimal


def demo01_default_error():
    """① 不处理直接序列化 datetime 会报 TypeError"""
    print("① 未处理的类型:")
    try:
        json.dumps({"time": datetime(2026, 7, 2, 10, 30)})
    except TypeError as e:
        print("  TypeError:", e)


def demo02_default_func():
    """② default:传一个函数,dumps 遇到无法序列化的对象时调用它做转换"""
    def to_serializable(o):
        if isinstance(o, datetime):
            return o.isoformat()       # datetime -> ISO 字符串
        if isinstance(o, Decimal):
            return float(o)            # Decimal -> float
        raise TypeError(f"不支持的类型: {type(o)}")

    payload = {"time": datetime(2026, 7, 2, 10, 30), "price": Decimal("9.99")}
    s = json.dumps(payload, default=to_serializable, ensure_ascii=False)
    print("② default 函数:", s)


def demo03_encoder_class():
    """③ 自定义 Encoder:逻辑复杂/想复用时,继承 JSONEncoder 重写 default"""
    class MyEncoder(json.JSONEncoder):
        # Encoder = 编码器,负责把对象编码成 JSON;default 只在遇到未知类型时被调用
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)  # 交回父类处理(会对真正不支持的类型抛错)

    s = json.dumps({"t": datetime(2026, 7, 2, 10, 30)}, cls=MyEncoder)
    print("③ 自定义 Encoder(cls=...):", s)


class Point:
    """一个自定义类,演示如何序列化任意对象"""
    def __init__(self, x, y):
        self.x, self.y = x, y


def demo04_custom_object():
    """④ 自定义对象:用 default 把实例转成 dict(可加类型标记便于还原)"""
    def encode(o):
        if isinstance(o, Point):
            return {"__type__": "Point", "x": o.x, "y": o.y}
        raise TypeError(f"不支持: {type(o)}")

    s = json.dumps(Point(3, 4), default=encode)
    print("④ 自定义对象 -> dict:", s)   # 还原见 04_hooks.py 的 object_hook


if __name__ == "__main__":
    demo01_default_error()
    print()
    demo02_default_func()
    print()
    demo03_encoder_class()
    print()
    demo04_custom_object()
