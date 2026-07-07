"""对象表示 —— pprint：漂亮打印

标准库。Python 3.12。
运行: python 03_pprint.py

print 打印复杂嵌套结构时，全挤在一行，难以阅读。
pprint（pretty print）自动缩进、折行，让结构一目了然。

演示：
  ① pprint vs print 对比
  ② width / depth / indent 参数
  ③ pformat：格式化为字符串（不打印）
  ④ 实际场景：打印 JSON / API 响应 / 配置字典
"""
import pprint


# 用于演示的复杂数据
SAMPLE_DATA = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com",
         "roles": ["admin", "user"], "active": True},
        {"id": 2, "name": "Bob", "email": "bob@example.com",
         "roles": ["user"], "active": False},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com",
         "roles": ["user", "moderator"], "active": True},
    ],
    "total": 3,
    "page": 1,
    "config": {
        "max_users": 100,
        "allow_registration": True,
        "password_policy": {"min_length": 8, "require_special": True},
    },
}


def demo01_pprint_vs_print():
    """① pprint vs print 对比"""
    print("① print vs pprint 对比")

    print("\n  [print] 全挤在一行，难以阅读:")
    print(" ", SAMPLE_DATA)

    print("\n  [pprint] 自动缩进，结构清晰:")
    pprint.pprint(SAMPLE_DATA, indent=2)


def demo02_params():
    """② 常用参数

    width   每行最大宽度，超出则折行（默认 80）
    depth   最大显示深度，更深的用 ... 代替（默认无限）
    indent  每级缩进空格数（默认 1）
    sort_dicts  是否对字典键排序（默认 True，Python 3.8+）
    compact 尽量在一行显示小的结构（默认 False）
    """
    print("\n② 参数控制")

    data = {"z": [1, 2, 3], "a": {"x": 1, "y": 2}, "m": "hello"}

    # width：控制折行宽度
    print("  width=40:")
    pprint.pprint(data, width=40)

    # depth：控制显示深度
    print("\n  depth=1（深层用 {...} 或 [...] 代替）:")
    pprint.pprint(SAMPLE_DATA, depth=1)

    print("\n  depth=2:")
    pprint.pprint(SAMPLE_DATA, depth=2)

    # indent：缩进空格数
    print("\n  indent=4:")
    pprint.pprint(data, indent=4)

    # sort_dicts=False：保持插入顺序
    print("\n  sort_dicts=False（保持键的原始顺序）:")
    pprint.pprint(data, sort_dicts=False)


def demo03_pformat():
    """③ pformat：格式化为字符串

    pprint.pformat(obj) 返回格式化字符串，不打印。
    适合写入日志、保存到变量、和其他字符串拼接。
    """
    print("\n③ pformat")

    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    data = {"key": "value", "list": [1, 2, 3]}

    # 写日志时格式化复杂对象
    formatted = pprint.pformat(data, width=40)
    print("  pformat 结果:")
    print("  " + formatted.replace("\n", "\n  "))

    # 拼接进字符串
    msg = "响应数据:\n" + pprint.pformat(SAMPLE_DATA, depth=2, indent=2)
    print("\n  拼接后的消息（前5行）:")
    for line in msg.splitlines()[:5]:
        print(" ", line)


def demo04_practical():
    """④ 实际场景"""
    print("\n④ 实际场景")

    # 场景一：打印 API 响应（JSON 解析后的 dict）
    import json
    json_str = '{"status": "ok", "data": {"items": [1,2,3], "count": 3}}'
    response = json.loads(json_str)
    print("  API 响应:")
    pprint.pprint(response, indent=2)

    # 场景二：快速查看模块/对象的所有属性
    import os
    attrs = {k: getattr(os, k) for k in dir(os) if not k.startswith("_")}
    # 太多了，只看前5个
    subset = dict(list(attrs.items())[:5])
    print("\n  os 模块前5个属性:")
    pprint.pprint(subset, indent=2)

    # 场景三：对比两个字典的差异（结合 pformat）
    config_old = {"host": "localhost", "port": 5432, "db": "mydb"}
    config_new = {"host": "10.0.0.1", "port": 5432, "db": "mydb", "ssl": True}
    print("\n  旧配置:")
    pprint.pprint(config_old)
    print("  新配置:")
    pprint.pprint(config_new)


if __name__ == "__main__":
    demo01_pprint_vs_print()
    demo02_params()
    demo03_pformat()
    demo04_practical()
