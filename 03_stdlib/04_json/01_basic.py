"""json —— 四个核心函数 与 Python <-> JSON 类型映射

标准库。Python 3.12。运行: python 01_basic.py

记忆口诀:带 s 的(dumpS/loadS)对字符串,不带 s 的对文件对象。
"""
import json
from pathlib import Path

# demo 产出写到脚本旁 data/ 目录(已被 .gitignore 忽略)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def demo01_dumps_loads():
    """① dumps / loads:对象 <-> JSON 字符串(内存中转换,最常用)"""
    data = {"name": "张三", "age": 30, "skills": ["Python", "SQL"], "vip": True}

    s = json.dumps(data)               # 序列化(serialize):对象 -> 字符串
    print("① dumps 结果:", s)          # 中文默认被转义成 \\uXXXX,见 02_format
    print("  返回值类型:", type(s))

    obj = json.loads(s)                # 反序列化(deserialize):字符串 -> 对象
    print("  loads 还原:", obj)
    print("  取字段 name:", obj["name"], type(obj["name"]))


def demo02_dump_load():
    """② dump / load:对象 <-> 文件(第一个参数是对象,第二个是打开的文件)"""
    data = {"city": "北京", "temp": 25.5}
    path = DATA_DIR / "demo.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)             # 直接写入文件,不返回字符串
    print("② 已写入:", path.name, "内容:", path.read_text(encoding="utf-8"))

    with open(path, encoding="utf-8") as f:
        obj = json.load(f)             # 从文件读回
    print("  load 还原:", obj, "  与原对象相等:", obj == data)


def demo03_type_mapping():
    """③ 类型映射:Python 与 JSON 的对应关系"""
    print("③ Python -> JSON 类型映射:")
    print("  dict -> object, list/tuple -> array, str -> string")
    print("  int/float -> number, True/False -> true/false, None -> null")

    # 注意 1:dict 的 key 会被强制转成字符串
    print("  key 强转字符串:", json.dumps({1: "a", 2: "b"}))       # {"1": "a", "2": "b"}
    # 注意 2:tuple 序列化成 array,反序列化回来是 list(丢失元组类型)
    back = json.loads(json.dumps((1, 2, 3)))
    print("  tuple 变 list:", back, type(back))
    # 注意 3:None 对应 null
    print("  None -> null:", json.dumps({"x": None}))


if __name__ == "__main__":
    demo01_dumps_loads()
    print()
    demo02_dump_load()
    print()
    demo03_type_mapping()
