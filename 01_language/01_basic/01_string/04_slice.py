"""字符串 —— 索引与切片

Python 3.12。
运行: python 04_slice.py

演示：
  ① 正索引与负索引
  ② 基础切片：[start:stop]
  ③ 步长：[start:stop:step]
  ④ 常用切片技巧：反转 / 隔位 / 去头去尾
  ⑤ 字符串不可变：切片返回新字符串
"""


def demo01_index():
    """① 正索引与负索引

    正索引从 0 开始，从左往右。
    负索引从 -1 开始，从右往左，-1 是最后一个字符。

    越界会抛 IndexError（切片不会越界）。
    """
    print("① 索引")

    s = "hello"
    #    01234     正索引
    #   -5-4-3-2-1 负索引

    print("  s =", s)
    print("  s[0]:", s[0])      # 'h'  第一个
    print("  s[4]:", s[4])      # 'o'  最后一个（正索引）
    print("  s[-1]:", s[-1])    # 'o'  最后一个（负索引）
    print("  s[-2]:", s[-2])    # 'l'  倒数第二个

    # 越界
    try:
        _ = s[10]
    except IndexError as e:
        print("  越界:", e)

    # 遍历字符
    print("  遍历:", list(s))


def demo02_basic_slice():
    """② 基础切片：s[start:stop]

    返回 s[start] 到 s[stop-1]（含头不含尾）。
    start 默认 0，stop 默认字符串末尾。
    切片越界不报错，自动截断。
    """
    print("\n② 基础切片")

    s = "hello world"
    #    0123456789...

    print("  s:", s)
    print("  s[0:5]:", s[0:5])      # 'hello'（0到4）
    print("  s[6:11]:", s[6:11])    # 'world'
    print("  s[:5]:", s[:5])        # 'hello'（start省略=0）
    print("  s[6:]:", s[6:])        # 'world'（stop省略=末尾）
    print("  s[:]:", s[:])          # 'hello world'（完整复制）

    # 负索引切片
    print("  s[-5:]:", s[-5:])      # 'world'（后5个）
    print("  s[:-6]:", s[:-6])      # 'hello'（去掉后6个）

    # 越界不报错
    print("  s[0:100]:", s[0:100])  # 'hello world'（自动截断）


def demo03_step():
    """③ 步长：s[start:stop:step]

    step 表示每隔几个字符取一个，默认为 1。
    step 为负数时从右往左取。
    """
    print("\n③ 步长")

    s = "0123456789"

    print("  s:", s)
    print("  s[::2]:", s[::2])        # '02468'（每隔一个）
    print("  s[::3]:", s[::3])        # '0369'（每隔两个）
    print("  s[1::2]:", s[1::2])      # '13579'（从1开始，每隔一个）
    print("  s[0:8:2]:", s[0:8:2])    # '0246'（0到7，每隔一个）

    # 负步长：从右往左
    print("  s[::-1]:", s[::-1])      # '9876543210'（反转）
    print("  s[::-2]:", s[::-2])      # '97531'（反转，每隔一个）


def demo04_tricks():
    """④ 常用切片技巧

    这些是实际代码里高频出现的切片用法。
    """
    print("\n④ 常用技巧")

    s = "hello world"

    # 反转字符串
    print("  反转:", s[::-1])                     # 'dlrow olleh'

    # 取前N个字符
    print("  前5个:", s[:5])                      # 'hello'

    # 取后N个字符
    print("  后5个:", s[-5:])                     # 'world'

    # 去掉前N个字符
    print("  去掉前6个:", s[6:])                  # 'world'

    # 去掉后N个字符
    print("  去掉后6个:", s[:-6])                 # 'hello'

    # 取中间部分（去头去尾）
    bracketed = "[hello world]"
    print("  去掉首尾[]:", bracketed[1:-1])       # 'hello world'

    # 判断回文
    word = "racecar"
    print(f"  '{word}' 是回文:", word == word[::-1])

    # 每隔一个字符取样
    data = "a1b2c3d4e5"
    letters = data[::2]
    digits = data[1::2]
    print("  字母:", letters)    # 'abcde'
    print("  数字:", digits)     # '12345'


def demo05_immutable():
    """⑤ 字符串不可变

    不能通过索引或切片赋值，所有"修改"都是创建新字符串。
    如果需要频繁修改字符，用 list 再 join 效率更高。
    """
    print("\n⑤ 不可变特性")

    s = "hello"

    # 不能赋值
    try:
        s[0] = "H"
    except TypeError as e:
        print("  不能赋值:", e)

    # 正确做法：创建新字符串
    s2 = "H" + s[1:]
    print("  修改首字母:", s2)    # 'Hello'

    # 频繁修改时：list → join
    chars = list("hello")
    chars[0] = "H"
    chars[-1] = "O"
    result = "".join(chars)
    print("  list 修改后 join:", result)    # 'HellO'

    # id 验证：每次"修改"都是新对象
    a = "hello"
    b = a.upper()
    print(f"  a id={id(a)}, b id={id(b)}, 是同一个对象: {a is b}")


if __name__ == "__main__":
    demo01_index()
    demo02_basic_slice()
    demo03_step()
    demo04_tricks()
    demo05_immutable()
