"""
pathlib —— 读写文件
标准库，无需安装，Python 3.4+
运行：python 04_read_write.py
产出写入脚本旁 data/ 目录（已被 .gitignore 忽略）
"""
from pathlib import Path

DATA = Path(__file__).parent / "data"


def demo_text():
    """① write_text / read_text"""
    DATA.mkdir(exist_ok=True)
    p = DATA / "hello.txt"
    p.write_text("第一行\n第二行\n", encoding="utf-8")
    content = p.read_text(encoding="utf-8")
    lines   = content.splitlines()
    print("① 文本读写:")
    print("  write_text -> 路径:", p, type(p))
    print("  read_text:", repr(content), type(content))
    print("  splitlines:", lines, type(lines))


def demo_bytes():
    """② write_bytes / read_bytes"""
    DATA.mkdir(exist_ok=True)
    p = DATA / "data.bin"
    p.write_bytes(b"\x00\x01\x02\x03")
    raw = p.read_bytes()
    print("② 二进制读写:")
    print("  write_bytes -> 4 字节")
    print("  read_bytes:", raw, type(raw))
    print("  len:", len(raw), type(len(raw)))


def demo_open():
    """③ open() 逐行读，大文件友好"""
    DATA.mkdir(exist_ok=True)
    p = DATA / "hello.txt"
    if not p.exists():
        p.write_text("第一行\n第二行\n", encoding="utf-8")
    print("③ open() 逐行读:")
    with p.open(encoding="utf-8") as f:
        for line in f:
            print("  行:", repr(line), type(line))


if __name__ == "__main__":
    demo_text()
    print()
    demo_bytes()
    print()
    demo_open()
