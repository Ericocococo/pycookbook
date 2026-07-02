"""json —— 反序列化钩子:解析时介入,把 JSON 还原成想要的 Python 类型

标准库。Python 3.12。运行: python 04_hooks.py

hook(钩子)= loads 在解析过程中回调你的函数,让你改写解析结果。
"""
import json
from datetime import datetime
from decimal import Decimal


def demo01_object_hook():
    """① object_hook:每解析出一个 JSON object(dict)就调用一次,可改写它"""
    raw = '{"time": "2026-07-02T10:30:00", "age": 30}'

    def restore(d):
        if "time" in d:
            d["time"] = datetime.fromisoformat(d["time"])  # 字符串 -> datetime
        return d

    obj = json.loads(raw, object_hook=restore)
    print("① object_hook 还原:", obj)
    print("  time 字段类型:", type(obj["time"]))


def demo02_restore_custom_object():
    """② 配合类型标记还原自定义对象(对应 03 的 __type__ 约定)"""
    raw = '{"__type__": "Point", "x": 3, "y": 4}'

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y
        def __repr__(self):
            return f"Point(x={self.x}, y={self.y})"

    def restore(d):
        if d.get("__type__") == "Point":
            return Point(d["x"], d["y"])
        return d

    obj = json.loads(raw, object_hook=restore)
    print("② 还原自定义对象:", obj, type(obj))


def demo03_parse_float():
    """③ parse_float:控制小数怎么解析,金额用 Decimal 避免二进制浮点精度丢失"""
    raw = '{"price": 9.99, "rate": 0.1}'
    default = json.loads(raw)
    print("③ 默认 float 解析:", default["price"], type(default["price"]))

    dec = json.loads(raw, parse_float=Decimal)
    print("  parse_float=Decimal:", dec["price"], type(dec["price"]))
    # float 的 0.1 + 0.2 != 0.3,财务计算务必用 Decimal


def demo04_parse_int():
    """④ parse_int:控制整数怎么解析(如需要转成别的类型时)"""
    raw = '{"count": 100}'
    obj = json.loads(raw, parse_int=float)   # 把整数当浮点读
    print("④ parse_int=float:", obj["count"], type(obj["count"]))


if __name__ == "__main__":
    demo01_object_hook()
    print()
    demo02_restore_custom_object()
    print()
    demo03_parse_float()
    print()
    demo04_parse_int()
