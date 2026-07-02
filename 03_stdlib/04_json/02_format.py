"""json —— 格式化输出:控制字符编码、缩进、排序、分隔符

标准库。Python 3.12。运行: python 02_format.py

这些都是 dumps/dump 的关键字参数,决定输出的"长相"。
"""
import json

DATA = {"name": "张三", "city": "北京", "age": 30, "tags": ["a", "b"]}


def demo01_ensure_ascii():
    """① ensure_ascii:是否把非 ASCII 字符(如中文)转义成 \\uXXXX"""
    print("① ensure_ascii:")
    print("  默认 True :", json.dumps({"city": "北京"}))                  # \\u5317\\u4eac
    print("  设为 False:", json.dumps({"city": "北京"}, ensure_ascii=False))  # 北京
    # 落盘给人看、或存中文,几乎总是要 ensure_ascii=False


def demo02_indent():
    """② indent:缩进美化,None(默认)为紧凑单行,给数字则按空格缩进换行"""
    print("② indent 缩进:")
    print("  紧凑(默认):", json.dumps(DATA, ensure_ascii=False))
    print("  indent=2:")
    print(json.dumps(DATA, ensure_ascii=False, indent=2))


def demo03_sort_keys():
    """③ sort_keys:按 key 字母序排序输出(便于 diff 对比、结果稳定)"""
    print("③ sort_keys=True:")
    print(json.dumps(DATA, ensure_ascii=False, indent=2, sort_keys=True))


def demo04_separators():
    """④ separators:自定义分隔符 (项分隔, 键值分隔),常用于压缩体积"""
    print("④ separators:")
    print("  默认       :", json.dumps(DATA, ensure_ascii=False))
    # 去掉所有多余空格,网络传输最省字节
    compact = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))
    print("  紧凑无空格 :", compact)


if __name__ == "__main__":
    demo01_ensure_ascii()
    print()
    demo02_indent()
    print()
    demo03_sort_keys()
    print()
    demo04_separators()
