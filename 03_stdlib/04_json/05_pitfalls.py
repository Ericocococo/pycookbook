"""json —— 常见陷阱与排错

标准库。Python 3.12。运行: python 05_pitfalls.py

JSON 语法比 Python 字面量严格得多,这里集中演示最容易踩的坑。
报错分支用 try/except 捕获后打印说明,不让程序中断。
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def demo01_single_quote():
    """① 单引号不是合法 JSON —— JSON 字符串必须用双引号"""
    print("① 单引号:")
    try:
        json.loads("{'a': 1}")             # Python 里合法,JSON 里非法
    except json.JSONDecodeError as e:
        print("  JSONDecodeError:", e)     # 报错类型,便于 except 精确捕获


def demo02_trailing_comma():
    """② 尾逗号非法 —— JSON 不允许最后一个元素后带逗号(和 Python 不同)"""
    print("② 尾逗号:")
    try:
        json.loads('{"a": 1, "b": 2,}')
    except json.JSONDecodeError as e:
        print("  JSONDecodeError:", e)


def demo03_nan_infinity():
    """③ NaN / Infinity:Python 默认允许(非标准 JSON),严格模式需关闭"""
    print("③ NaN / Infinity:")
    print("  默认允许(非标准):", json.dumps(float("nan")))   # 输出 NaN
    try:
        json.dumps(float("inf"), allow_nan=False)            # 严格模式报错
    except ValueError as e:
        print("  allow_nan=False:", e)


def demo04_key_coerced():
    """④ 非字符串 key 被静默转成字符串 —— 反序列化后回不到原类型"""
    print("④ key 被转字符串:")
    s = json.dumps({1: "a", True: "b", 2.0: "c"})
    print("  序列化:", s)                  # 数字/布尔 key 全变字符串
    print("  反序列化:", json.loads(s))     # {"1": ..., "2.0": ...},1 不再是 int


def demo05_chinese_to_file():
    """⑤ 中文落盘:必须 ensure_ascii=False + encoding='utf-8' 双管齐下"""
    path = DATA_DIR / "cn.json"
    # 只给 ensure_ascii=False 还不够,open 也要指定 utf-8,否则 Windows 可能乱码
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"城市": "北京"}, f, ensure_ascii=False, indent=2)
    print("⑤ 中文落盘内容:")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    demo01_single_quote()
    print()
    demo02_trailing_comma()
    print()
    demo03_nan_infinity()
    print()
    demo04_key_coerced()
    print()
    demo05_chinese_to_file()
