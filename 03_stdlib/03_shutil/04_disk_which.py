"""shutil —— 实用工具:磁盘用量 / 查可执行文件 / 终端尺寸

标准库。Python 3.12。运行: python 04_disk_which.py

这几个是 shutil 里与"复制/删除"无关、但很常用的独立工具函数。
"""
import shutil
from pathlib import Path


def demo01_disk_usage():
    """① disk_usage:查某路径所在磁盘的总量/已用/剩余(字节)"""
    usage = shutil.disk_usage(Path(__file__).parent)
    gb = 1024 ** 3
    print("① disk_usage(当前磁盘):")
    print("  total:", round(usage.total / gb, 1), "GB")
    print("  used :", round(usage.used / gb, 1), "GB")
    print("  free :", round(usage.free / gb, 1), "GB")
    print("  返回值是具名元组:", usage._fields)


def demo02_which():
    """② which:在 PATH 中定位可执行程序(相当于 shell 的 which/where)"""
    print("② which 查可执行文件:")
    for name in ("python", "pip", "definitely_not_exist_cmd"):
        found = shutil.which(name)
        print(f"  {name:24} -> {found}")   # 找不到返回 None


def demo03_terminal_size():
    """③ get_terminal_size:获取终端宽高(用于对齐输出/进度条)"""
    size = shutil.get_terminal_size()
    print("③ get_terminal_size:")
    print("  columns 列:", size.columns)
    print("  lines 行:", size.lines)
    # 可传 fallback:非终端环境(如管道、重定向)拿不到真实尺寸时用它
    size2 = shutil.get_terminal_size(fallback=(80, 24))
    print("  fallback 示例:", (size2.columns, size2.lines))


if __name__ == "__main__":
    demo01_disk_usage()
    print()
    demo02_which()
    print()
    demo03_terminal_size()
