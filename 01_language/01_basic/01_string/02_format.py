"""字符串 —— 格式化

Python 3.12。
运行: python 02_format.py

演示：
  ① f-string 基础（Python 3.6+，推荐）
  ② f-string 表达式与调用
  ③ 数字格式：宽度 / 精度 / 千分位 / 进制
  ④ 对齐与填充
  ⑤ 日期格式化
  ⑥ str.format()（旧写法，兼容 3.6 以前）
  ⑦ % 格式化（更旧，了解即可）
"""
from datetime import datetime


def demo01_fstring_basic():
    """① f-string 基础

    f"..." 字符串，花括号 {} 里写变量名或表达式，运行时求值替换。
    是目前 Python 最推荐的格式化方式：简洁、可读、速度快。
    """
    print("① f-string 基础")

    name = "Alice"
    age = 30
    score = 99.5

    print(f"  姓名: {name}")
    print(f"  年龄: {age}")
    print(f"  得分: {score}")

    # 花括号内可以是任意变量
    city = "北京"
    print(f"  {name} 住在 {city}，今年 {age} 岁")

    # 调试用 = 语法（Python 3.8+）：变量名=值，快速打印
    x = 42
    print(f"  {x = }")          # 输出 x = 42，调试时很方便
    print(f"  {name = }")       # 输出 name = 'Alice'


def demo02_fstring_expr():
    """② f-string 里可以写任意表达式

    花括号里不只是变量，可以是计算、调用、条件、推导式等。
    """
    print("\n② f-string 表达式")

    a, b = 3, 4

    # 计算
    print(f"  {a} + {b} = {a + b}")
    print(f"  {a} * {b} = {a * b}")

    # 调用方法
    s = "hello world"
    print(f"  大写: {s.upper()}")
    print(f"  长度: {len(s)}")

    # 三元表达式
    score = 75
    print(f"  成绩: {score}，{'及格' if score >= 60 else '不及格'}")

    # 嵌套引号（用不同引号区分）
    data = {"name": "Bob"}
    print(f"  字典取值: {data['name']}")


def demo03_number_format():
    """③ 数字格式化

    f"{value:格式说明符}"
    格式说明符：[填充][对齐][宽度][,][.精度][类型]

    类型：
      d   整数
      f   浮点数（固定小数位）
      e   科学计数法
      %   百分比
      b   二进制
      o   八进制
      x   十六进制
    """
    print("\n③ 数字格式")

    n = 1234567.891

    print(f"  默认:        {n}")
    print(f"  2位小数:     {n:.2f}")          # 1234567.89
    print(f"  千分位:      {n:,.2f}")         # 1,234,567.89
    print(f"  科学计数:    {n:.2e}")          # 1.23e+06
    print(f"  百分比:      {0.756:.1%}")      # 75.6%

    # 整数进制
    num = 255
    print(f"  十进制:  {num:d}")
    print(f"  二进制:  {num:b}")              # 11111111
    print(f"  八进制:  {num:o}")              # 377
    print(f"  十六进制:{num:x}")              # ff
    print(f"  十六进制:{num:X}")              # FF（大写）
    print(f"  带前缀:  {num:#x}")             # 0xff


def demo04_align():
    """④ 对齐与填充

    f"{value:[填充字符][对齐方式][宽度]}"
    对齐方式：
      <   左对齐（str 默认）
      >   右对齐（数字默认）
      ^   居中
      =   符号后填充（仅数字）
    """
    print("\n④ 对齐与填充")

    # 基础对齐
    for name, score in [("Alice", 99), ("Bob", 75), ("Charlie", 60)]:
        print(f"  {name:<10} {score:>5} 分")  # 姓名左对齐10位，分数右对齐5位

    print()

    # 填充字符
    print(f"  {'标题':^20}")          # 居中，空格填充
    print(f"  {'标题':=^20}")         # 居中，= 填充
    print(f"  {'标题':-^20}")         # 居中，- 填充

    print()

    # 数字填充
    for i in range(1, 6):
        print(f"  第 {i:02d} 条")     # 宽度2，0填充：01 02 03...


def demo05_datetime_format():
    """⑤ 日期时间格式化

    f-string 里可以直接用 strftime 格式符，或者先格式化再嵌入。
    """
    print("\n⑤ 日期格式")

    now = datetime.now()

    # 直接在 f-string 里用格式说明符
    print(f"  完整日期时间: {now:%Y-%m-%d %H:%M:%S}")
    print(f"  仅日期:       {now:%Y-%m-%d}")
    print(f"  仅时间:       {now:%H:%M}")
    print(f"  年/月/日:     {now:%Y}/{now:%m}/{now:%d}")
    print(f"  星期:         {now:%A}")    # 英文星期


def demo06_format_method():
    """⑥ str.format()

    Python 3.6 以前的主流写法，现在遇到旧代码时能看懂即可。
    花括号 {} 是占位符，按位置或名称替换。
    """
    print("\n⑥ str.format()")

    # 按位置
    print("  {}年{}月{}日".format(2026, 7, 6))

    # 指定索引
    print("  {0} 和 {1}，再说一遍 {0}".format("苹果", "香蕉"))

    # 按名称
    print("  {name} 今年 {age} 岁".format(name="Alice", age=30))

    # 格式说明符同样适用
    print("  {:.2f}".format(3.14159))
    print("  {:>10}".format("right"))


def demo07_percent_format():
    """⑦ % 格式化（最老，了解即可）

    Python 2 时代遗留，现在基本只在 logging 模块里还会见到。
    """
    print("\n⑦ % 格式化（旧）")

    name = "Alice"
    score = 99.5

    print("  %s 得了 %.1f 分" % (name, score))
    print("  整数: %d，十六进制: %x" % (255, 255))

    # logging 模块仍用这种格式（延迟求值，不格式化就不消耗）
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("用户 %s 登录", name)   # 日志里仍推荐 % 格式


if __name__ == "__main__":
    demo01_fstring_basic()
    demo02_fstring_expr()
    demo03_number_format()
    demo04_align()
    demo05_datetime_format()
    demo06_format_method()
    demo07_percent_format()
