"""sys —— 解释器版本与平台信息

标准库。Python 3.12。运行: python 01_info.py
"""
import sys


def demo01_version():
    """① sys.version / sys.version_info / sys.hexversion"""
    print("① Python 版本信息")
    print("  sys.version:", sys.version)              # 完整版本字符串（含编译器信息）
    vi = sys.version_info
    print("  sys.version_info:", vi)
    print("    major:", vi.major, type(vi.major))      # 主版本号，如 3
    print("    minor:", vi.minor, type(vi.minor))      # 次版本号，如 12
    print("    micro:", vi.micro, type(vi.micro))      # 修订号，如 0
    print("    releaselevel:", vi.releaselevel)         # 'alpha'/'beta'/'rc'/'final'
    print("    serial:", vi.serial)                     # 预发布序号（final 时为 0）
    print("  版本比较（推荐写法）:", vi >= (3, 10))      # 比字符串比较更可靠
    print("  sys.hexversion:", hex(sys.hexversion))    # 0x030c00f0 格式，便于一次性比较


def demo02_platform():
    """② sys.platform / sys.implementation / sys.api_version"""
    print("② 平台与实现信息")
    print("  sys.platform:", sys.platform)              # 'win32' / 'linux' / 'darwin'
    impl = sys.implementation
    print("  sys.implementation.name:", impl.name)      # 'cpython' / 'pypy' 等
    print("  sys.implementation.version:", impl.version)
    print("  sys.api_version:", sys.api_version)        # Python C API 版本号（整数）


def demo03_paths():
    """③ sys.executable / sys.prefix / sys.base_prefix / sys.exec_prefix"""
    print("③ 解释器路径与安装目录")
    print("  sys.executable:", sys.executable)           # 当前 Python 解释器可执行文件完整路径
    print("  sys.prefix:", sys.prefix)                   # 安装目录（虚拟环境/Conda env 的根）
    print("  sys.base_prefix:", sys.base_prefix)         # 原始基础安装目录（激活虚拟环境前不变）
    print("  sys.exec_prefix:", sys.exec_prefix)         # 平台相关扩展模块（.pyd/.so）的安装目录
    in_venv = sys.prefix != sys.base_prefix
    print("  是否在虚拟环境 / Conda env 中:", in_venv)   # prefix != base_prefix 即说明在隔离环境


def demo04_limits():
    """④ sys.maxsize / sys.maxunicode / sys.byteorder"""
    print("④ 平台数值限制与字节序")
    print("  sys.maxsize:", sys.maxsize)                 # C long 最大值（64 位机：2^63-1）
    print("  sys.maxunicode:", sys.maxunicode)           # 最大 Unicode 码点 0x10FFFF = 1114111
    print("  sys.byteorder:", sys.byteorder)             # 'little'（x86/ARM）/ 'big'（SPARC 等）


def demo05_numeric_info():
    """⑤ sys.float_info / sys.int_info / sys.hash_info 关键字段"""
    print("⑤ 数值类型内部信息")

    fi = sys.float_info
    print("  sys.float_info:")
    print("    max:", fi.max)                            # float 最大值（约 1.8e308）
    print("    min:", fi.min)                            # float 最小正规化值（约 2.2e-308）
    print("    dig:", fi.dig)                            # float 十进制有效位数（约 15-17 位）
    print("    epsilon:", fi.epsilon)                    # 机器精度：1.0 + epsilon != 1.0 的最小值

    ii = sys.int_info
    print("  sys.int_info:")
    print("    bits_per_digit:", ii.bits_per_digit)      # 大整数每个内部 digit 的位数（30 或 15）
    print("    sizeof_digit:", ii.sizeof_digit)          # 每个 digit 占用字节数

    hi = sys.hash_info
    print("  sys.hash_info:")
    print("    width:", hi.width)                        # hash 值使用的有效位数
    print("    modulus:", hi.modulus)                    # SipHash 使用的 Mersenne 素数模数


if __name__ == "__main__":
    demo01_version()
    print()
    demo02_platform()
    print()
    demo03_paths()
    print()
    demo04_limits()
    print()
    demo05_numeric_info()
