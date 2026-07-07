"""字符串 —— 编码与解码

Python 3.12。
运行: python 05_encode.py

Python 3 中：
  str   = Unicode 文本（人类可读）
  bytes = 字节序列（二进制，存储/传输用）

两者通过编码互转：
  str  --encode(编码名)-->  bytes
  bytes --decode(编码名)-->  str

演示：
  ① encode / decode 基础
  ② 常见编码：utf-8 / gbk / ascii
  ③ 编码错误处理：errors 参数
  ④ 乱码的原因与排查
  ⑤ 实际场景：文件读写编码 / 网络数据处理
"""


def demo01_basic():
    """① encode / decode 基础

    str.encode(encoding)    str → bytes
    bytes.decode(encoding)  bytes → str

    不指定编码时，默认 utf-8。
    """
    print("① encode / decode 基础")

    s = "hello, 世界"

    # str → bytes
    b_utf8 = s.encode("utf-8")
    print("  原始 str:", s)
    print("  utf-8 编码:", b_utf8)
    print("  字节数:", len(b_utf8))       # 13（hello,=7，每个汉字3字节）
    print("  字符数:", len(s))            # 9

    # bytes → str
    s2 = b_utf8.decode("utf-8")
    print("  解码回 str:", s2)
    print("  还原成功:", s == s2)

    # 默认编码是 utf-8
    b_default = s.encode()              # 等价于 s.encode("utf-8")
    print("  默认编码:", b_default == b_utf8)


def demo02_encodings():
    """② 常见编码对比

    utf-8   国际通用，变长（ASCII 1字节，汉字 3字节），推荐
    gbk     Windows 中文系统默认，汉字 2字节，兼容 GB2312
    ascii   只能编码英文和标点（0-127），编码汉字会报错
    latin-1 西欧语言，单字节，0-255 全部有效（不会报错）
    """
    print("\n② 常见编码对比")

    s = "hello 中文"

    for enc in ["utf-8", "gbk"]:
        b = s.encode(enc)
        print(f"  {enc:8s}: {b}  ({len(b)} 字节)")

    # ascii 不能编码中文
    try:
        s.encode("ascii")
    except UnicodeEncodeError as e:
        print(f"  ascii:   编码失败 → {e}")

    # 各编码的汉字字节数
    char = "中"
    print(f"\n  '中' 字在各编码中的字节数:")
    for enc in ["utf-8", "gbk", "utf-16"]:
        b = char.encode(enc)
        print(f"    {enc:8s}: {len(b)} 字节  {b.hex()}")


def demo03_errors():
    """③ 编码错误处理：errors 参数

    encode 和 decode 都支持 errors 参数：
      'strict'  （默认）遇到无法处理的字符抛 UnicodeError
      'ignore'  忽略无法处理的字符
      'replace' 用 ? 或 \\ufffd 替换
      'xmlcharrefreplace'  encode 时替换为 XML 字符引用（&amp;#xxx;）
      'backslashreplace'   encode 时替换为 \\uXXXX 形式
    """
    print("\n③ errors 参数")

    s = "hello 中文 world"

    # encode 时处理不支持的字符
    for err in ["ignore", "replace", "xmlcharrefreplace", "backslashreplace"]:
        b = s.encode("ascii", errors=err)
        print(f"  encode ascii errors={err!r:20s}: {b}")

    print()

    # decode 时处理坏字节
    bad_bytes = b"hello \xff\xfe world"   # 包含无效 utf-8 字节
    for err in ["ignore", "replace"]:
        s2 = bad_bytes.decode("utf-8", errors=err)
        print(f"  decode utf-8 errors={err!r:10s}: {s2!r}")


def demo04_garbled():
    """④ 乱码的原因与排查

    乱码 = 用错误的编码解码。
    最常见：用 gbk 编码的文件，用 utf-8 解码（或反之）。
    """
    print("\n④ 乱码原因")

    s = "你好世界"

    # 用 gbk 编码
    b_gbk = s.encode("gbk")
    print("  gbk 编码:", b_gbk)

    # 误用 utf-8 解码 → 乱码（或报错）
    try:
        garbled = b_gbk.decode("utf-8")
        print("  误用 utf-8 解码:", garbled)
    except UnicodeDecodeError as e:
        print("  误用 utf-8 解码 → 报错:", e)

    # 用 latin-1 解码（不会报错，但是乱码）
    garbled2 = b_gbk.decode("latin-1")
    print("  误用 latin-1 解码:", repr(garbled2))   # 乱码字符

    # 排查步骤：找到原始编码，用正确编码解码
    s_correct = b_gbk.decode("gbk")
    print("  正确 gbk 解码:", s_correct)

    # 实用：chardet 库自动检测编码（需安装）
    print("\n  排查乱码流程:")
    print("    1. 确认数据来源（文件/接口/数据库）的编码")
    print("    2. 用正确编码 decode")
    print("    3. 实在不知道：pip install chardet，用 chardet.detect(bytes) 检测")


def demo05_practical():
    """⑤ 实际场景

    场景一：读写文件指定编码
    场景二：处理网络请求返回的字节数据
    场景三：十六进制字节串与 bytes 互转
    """
    print("\n⑤ 实际场景")

    # 场景一：文件读写指定编码
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                     suffix=".txt", delete=False) as f:
        f.write("你好，世界\n")
        tmp_path = f.name

    with open(tmp_path, encoding="utf-8") as f:
        content = f.read()
    print("  文件读写:", repr(content.strip()))
    os.unlink(tmp_path)

    # 场景二：网络数据（bytes）→ str
    raw_response = b'{"name": "\xe4\xb8\xad\xe6\x96\x87"}'  # utf-8 编码的 JSON
    text = raw_response.decode("utf-8")
    import json
    data = json.loads(text)
    print("  网络数据解码:", data)

    # 场景三：hex 字符串 ↔ bytes
    b = b"\xde\xad\xbe\xef"
    hex_str = b.hex()                      # 'deadbeef'
    print("  bytes → hex:", hex_str)
    b2 = bytes.fromhex(hex_str)            # bytes.fromhex('deadbeef')
    print("  hex → bytes:", b2)
    print("  还原一致:", b == b2)


if __name__ == "__main__":
    demo01_basic()
    demo02_encodings()
    demo03_errors()
    demo04_garbled()
    demo05_practical()
