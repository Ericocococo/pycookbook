"""字符串 —— 常用方法

Python 3.12。
运行: python 03_methods.py

str 的方法全部返回新字符串，原字符串不变（字符串不可变）。

演示：
  ① 查找：find / index / count / in
  ② 替换：replace / translate
  ③ 分割与合并：split / rsplit / splitlines / join
  ④ 大小写：upper / lower / title / capitalize / swapcase
  ⑤ 去空白：strip / lstrip / rstrip
  ⑥ 判断：startswith / endswith / isdigit / isalpha / isspace
  ⑦ 填充：center / ljust / rjust / zfill
"""


def demo01_find():
    """① 查找

    find(sub)       返回第一次出现的索引，找不到返回 -1
    index(sub)      同 find，但找不到抛 ValueError
    rfind / rindex  从右往左找
    count(sub)      统计出现次数
    in              最简洁的"是否包含"判断
    """
    print("① 查找")

    s = "hello world, hello python"

    # in / not in：最常用
    print("  'hello' in s:", "hello" in s)       # True
    print("  'java' in s:", "java" in s)          # False

    # find：找到返回索引，找不到返回 -1
    print("  find('hello'):", s.find("hello"))    # 0（第一次）
    print("  rfind('hello'):", s.rfind("hello"))  # 13（最后一次）
    print("  find('java'):", s.find("java"))      # -1

    # index：找不到抛异常
    try:
        s.index("java")
    except ValueError as e:
        print("  index 找不到:", e)

    # count：统计次数
    print("  count('hello'):", s.count("hello"))  # 2
    print("  count('l'):", s.count("l"))          # 5

    # 指定搜索范围
    print("  find('hello', 5):", s.find("hello", 5))   # 从索引5开始找，返回13


def demo02_replace():
    """② 替换

    replace(old, new)        把所有 old 替换成 new
    replace(old, new, count) 最多替换 count 次
    translate(table)         按字符映射表批量替换（比循环快）
    """
    print("\n② 替换")

    s = "hello world, hello python"

    # replace：替换所有
    print("  replace all:", s.replace("hello", "hi"))

    # replace：只替换第一个
    print("  replace 1次:", s.replace("hello", "hi", 1))

    # translate：字符级别替换，适合批量字符映射
    # str.maketrans 创建映射表
    table = str.maketrans(
        "aeiou",   # 这些字符
        "AEIOU",   # 替换成这些
    )
    print("  translate 元音大写:", "hello world".translate(table))

    # translate 还可以删除字符（第三个参数）
    table2 = str.maketrans("", "", "aeiou")   # 删除所有元音
    print("  translate 删除元音:", "hello world".translate(table2))


def demo03_split():
    """③ 分割与合并

    split(sep)       按分隔符分割，返回列表
    split(sep, n)    最多分割 n 次
    rsplit           从右往左分割
    splitlines()     按换行符分割（\\n \\r\\n 都识别）
    join(iterable)   用字符串连接可迭代对象
    """
    print("\n③ 分割与合并")

    # split：最常用
    csv = "Alice,Bob,Charlie,Dave"
    print("  split(','):", csv.split(","))

    # split 不传参：按空白符分割，自动去掉多余空格
    s = "  hello   world   python  "
    print("  split():", s.split())             # ['hello', 'world', 'python']

    # 限制分割次数
    path = "2026/07/06/news"
    print("  split('/', 2):", path.split("/", 2))   # ['2026', '07', '06/news']

    # rsplit：从右往左分割
    print("  rsplit('/', 1):", path.rsplit("/", 1))  # ['2026/07/06', 'news']

    # splitlines：按换行分割
    text = "第一行\n第二行\r\n第三行"
    print("  splitlines:", text.splitlines())

    # join：合并列表
    words = ["hello", "world", "python"]
    print("  join(' '):", " ".join(words))
    print("  join(','):", ",".join(words))
    print("  join('\\n'):")
    print("   ", "\n  ".join(words))


def demo04_case():
    """④ 大小写转换

    upper()       全大写
    lower()       全小写
    title()       每个单词首字母大写
    capitalize()  只有整个字符串的第一个字母大写
    swapcase()    大小写互换
    casefold()    激进小写（处理德语ß等特殊字符，用于大小写不敏感比较）
    """
    print("\n④ 大小写")

    s = "hello World PYTHON"

    print("  upper():", s.upper())
    print("  lower():", s.lower())
    print("  title():", s.title())           # Hello World Python
    print("  capitalize():", s.capitalize()) # Hello world python
    print("  swapcase():", s.swapcase())     # HELLO wORLD python

    # casefold 用于大小写不敏感比较（比 lower 更彻底）
    print("  'ß'.lower():", "ß".lower())         # ß（德语字符）
    print("  'ß'.casefold():", "ß".casefold())   # ss（展开为 ss）


def demo05_strip():
    """⑤ 去空白（及指定字符）

    strip()    去除两端空白（空格、\\n、\\t、\\r）
    lstrip()   只去左端
    rstrip()   只去右端

    也可以传入字符集，去除两端出现在集合中的字符（不是子串！）
    """
    print("\n⑤ 去空白")

    s = "  \t hello world \n  "
    print("  原始:", repr(s))
    print("  strip():", repr(s.strip()))
    print("  lstrip():", repr(s.lstrip()))
    print("  rstrip():", repr(s.rstrip()))

    # 去除指定字符集（常见误解：是字符集，不是子串）
    s2 = "###hello###world###"
    print("  strip('#'):", s2.strip("#"))    # 'hello###world'（只去两端的#）

    s3 = "xyz_hello_xyz"
    print("  strip('xyz'):", s3.strip("xyz"))   # '_hello_'（去掉两端的x/y/z字符）


def demo06_check():
    """⑥ 判断方法（返回 bool）

    startswith(prefix)   是否以 prefix 开头（支持元组）
    endswith(suffix)     是否以 suffix 结尾（支持元组）
    isdigit()            是否全是数字字符
    isalpha()            是否全是字母
    isalnum()            是否全是字母或数字
    isspace()            是否全是空白字符
    isupper() / islower() 是否全大/小写
    """
    print("\n⑥ 判断")

    # startswith / endswith
    url = "https://www.example.com/page.html"
    print("  startswith('https'):", url.startswith("https"))
    print("  endswith('.html'):", url.endswith(".html"))

    # 支持元组：匹配任意一个即为 True
    filename = "photo.jpg"
    print("  是图片:", filename.endswith((".jpg", ".png", ".gif")))

    # 字符判断
    tests = ["123", "abc", "abc123", "   ", "Hello", "HELLO", "123abc!"]
    print(f"\n  {'字符串':12s} {'isdigit':8s} {'isalpha':8s} {'isalnum':8s} {'isspace':8s}")
    for t in tests:
        print(f"  {t!r:12s} {str(t.isdigit()):8s} {str(t.isalpha()):8s} "
              f"{str(t.isalnum()):8s} {str(t.isspace()):8s}")


def demo07_pad():
    """⑦ 填充对齐

    center(width, fillchar)  居中，默认空格填充
    ljust(width, fillchar)   左对齐（右边填充）
    rjust(width, fillchar)   右对齐（左边填充）
    zfill(width)             左边填 0（常用于序号、编号）
    """
    print("\n⑦ 填充对齐")

    s = "hello"
    print("  center(20):", s.center(20))
    print("  center(20,'*'):", s.center(20, "*"))
    print("  ljust(20,'-'):", s.ljust(20, "-"))
    print("  rjust(20,'-'):", s.rjust(20, "-"))

    # zfill：序号补零
    for i in [1, 10, 100]:
        print(f"  {str(i).zfill(4)}")    # 0001, 0010, 0100


def demo08_partition():
    """⑧ partition / rpartition：切三段

    partition(sep)   从左找第一个 sep，返回 (前, sep, 后) 三元组
    rpartition(sep)  从右找最后一个 sep，返回 (前, sep, 后) 三元组

    与 split 的区别：
      - 固定返回三元组，长度可预期，方便解包
      - 保留分隔符本身
      - 找不到时不报错：返回 (原串, '', '')，可用 sep 是否为空来判断

    适合场景：解析 key=value / host:port / 路径分割等固定格式
    """
    print("\n⑧ partition / rpartition")

    s = "hello:world:python"

    # partition：从左找第一个
    print("  partition(':'):", s.partition(":"))    # ('hello', ':', 'world:python')

    # rpartition：从右找最后一个
    print("  rpartition(':'):", s.rpartition(":"))  # ('hello:world', ':', 'python')

    # 找不到分隔符
    print("  找不到:", "hello".partition(":"))       # ('hello', '', '')

    # 用 sep 是否为空来判断是否找到
    for line in ["host=localhost", "no-equal-sign"]:
        before, sep, after = line.partition("=")
        if sep:
            print(f"  解析成功 → key={before!r}, value={after!r}")
        else:
            print(f"  不含 '=' → {before!r}")

    # 实际场景：解析 URL 里的协议
    url = "https://www.example.com/page"
    scheme, _, rest = url.partition("://")
    print(f"  协议={scheme!r}, 地址={rest!r}")


if __name__ == "__main__":
    demo01_find()
    demo02_replace()
    demo03_split()
    demo04_case()
    demo05_strip()
    demo06_check()
    demo07_pad()
    demo08_partition()
