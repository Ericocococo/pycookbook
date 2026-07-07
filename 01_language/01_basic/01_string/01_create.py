"""字符串 —— 创建方式

Python 3.12。
运行: python 01_create.py

演示：
  ① 单引号 / 双引号 / 三引号
  ② 转义字符
  ③ raw 字符串（r"..."）：不处理转义
  ④ 字符串拼接与重复
  ⑤ bytes 字面量
"""


def demo01_quotes():
    """① 引号的三种形式

    单引号和双引号完全等价，选哪个取决于字符串内容是否含引号。
    三引号（''' 或 \"\"\"）可以跨行，常用于多行文本和 docstring。
    """
    print("① 引号形式")

    s1 = 'hello'
    s2 = "hello"
    print("  单引号 == 双引号:", s1 == s2)      # True，完全等价

    # 字符串内含引号时，用另一种引号包裹
    s3 = "it's a dog"                           # 内含单引号，外用双引号
    s4 = 'say "hello"'                          # 内含双引号，外用单引号
    print("  含单引号:", s3)
    print("  含双引号:", s4)

    # 三引号：可以跨行，保留换行和缩进
    s5 = """第一行
第二行
第三行"""
    print("  三引号多行:")
    print(s5)

    # 三引号也可以用于单行（但通常不这么做）
    s6 = """单行三引号"""
    print("  单行三引号:", s6)


def demo02_escape():
    """② 转义字符

    反斜杠 \\ 开头的字符序列，表示无法直接写出的字符。

    常用转义：
      \\n   换行
      \\t   制表符（Tab）
      \\\\   字面反斜杠
      \\'   单引号
      \\"   双引号
      \\r   回车（Windows 换行符的一部分）
      \\0   空字符
      \\uXXXX  Unicode 字符（4位十六进制）
    """
    print("\n② 转义字符")

    print("  换行:\\n →", "第一行\n  第二行")
    print("  制表符:\\t →", "姓名\t年龄")
    print("  反斜杠:\\\\ →", "C:\\Users\\Alice")
    print("  Unicode:\\u4e2d\\u6587 →", "中文")   # 中文


def demo03_raw_string():
    """③ raw 字符串：r"..."

    在引号前加 r，反斜杠不再作为转义符，原样保留。

    适用场景：
      - Windows 文件路径（避免 \\n \\t 被误解析）
      - 正则表达式（\\d \\w 等不被提前转义）
    """
    print("\n③ raw 字符串")

    # 普通字符串：\n 被解析为换行
    normal = "C:\name\test"
    print("  普通:", repr(normal))    # 'C:\name\test' 里 \n 和 \t 变成控制字符

    # raw 字符串：\n \t 原样保留
    raw = r"C:\name\test"
    print("  raw:  ", repr(raw))     # 'C:\\name\\test'

    # 正则表达式里必须用 raw
    import re
    pattern = r"\d{3}-\d{4}"        # 匹配 "123-4567"
    print("  正则匹配:", re.search(pattern, "电话: 123-4567").group())


def demo04_concat():
    """④ 字符串拼接与重复

    + 拼接：清晰但低效（每次创建新字符串）
    * 重复：重复字符串 N 次
    join：拼接多个字符串的高效方式（推荐）
    """
    print("\n④ 拼接与重复")

    # + 拼接
    s = "hello" + ", " + "world"
    print("  + 拼接:", s)

    # 字面量相邻自动拼接（编译期合并，不创建中间对象）
    s2 = ("hello"
          ", "
          "world")
    print("  字面量相邻:", s2)

    # * 重复
    print("  * 重复:", "ha" * 3)     # 'hahaha'
    print("  分隔线:", "-" * 20)

    # join：拼接列表元素，效率最高
    words = ["python", "is", "great"]
    print("  join:", " ".join(words))
    print("  join 逗号:", ",".join(words))


def demo05_bytes():
    """⑤ bytes 字面量

    bytes 是字节序列，存储二进制数据（网络、文件、加密）。
    字面量写法：b"..." 或 b'...'，只能包含 ASCII 字符（0-127）。

    与 str 的区别：
      str   → 文本，Unicode 字符，人类可读
      bytes → 字节，二进制数据，需要指定编码才能转为 str
    """
    print("\n⑤ bytes")

    b = b"hello"
    print("  bytes 字面量:", b)
    print("  类型:", type(b))
    print("  长度（字节数）:", len(b))     # 5
    print("  第一个字节:", b[0])           # 104（'h' 的 ASCII 码）

    # bytes 只接受 0-127 的字节值
    b2 = b"\x00\xff\x7f"
    print("  十六进制字节:", b2)

    # str → bytes（编码）
    s = "你好"
    b3 = s.encode("utf-8")
    print("  '你好' 编码为 utf-8:", b3)   # b'\xe4\xbd\xa0\xe5\xa5\xbd'
    print("  字节数:", len(b3))            # 6（每个汉字3字节）

    # bytes → str（解码）
    s2 = b3.decode("utf-8")
    print("  解码回 str:", s2)


if __name__ == "__main__":
    demo01_quotes()
    demo02_escape()
    demo03_raw_string()
    demo04_concat()
    demo05_bytes()
