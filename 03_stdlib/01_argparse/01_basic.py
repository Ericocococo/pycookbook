"""argparse 基础:位置参数 与 可选参数

标准库,无需安装。Python 3.12。
运行: python 01_basic.py

说明:为便于演示,demo 里用 parser.parse_args([...]) 传入模拟参数;
真实使用时省略参数,parse_args() 默认读取 sys.argv(命令行)。
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="演示 argparse 最基础的两类参数")
    # 位置参数:必填,按顺序传,不带 - 前缀
    parser.add_argument("src", help="源文件路径")
    # 可选参数:带 - / -- 前缀,可省略;-o 是短选项,--output 是长选项
    parser.add_argument("-o", "--output", help="输出文件路径")
    # 布尔开关:出现即 True,不出现即 False
    parser.add_argument("-v", "--verbose", action="store_true", help="是否详细输出")
    return parser


def demo_all_given():
    """① 位置参数 + 可选参数全给"""
    parser = build_parser()
    args = parser.parse_args([
        "input.txt",        # 位置参数 src
        "-o", "out.txt",    # 可选参数 output
        "-v",               # 布尔开关 verbose
    ])
    print("① 全给:")
    print("  args.src:", args.src, type(args.src))
    print("  args.output:", args.output, type(args.output))
    print("  args.verbose:", args.verbose, type(args.verbose))


def demo_positional_only():
    """② 只给位置参数,可选参数取默认(None / False)"""
    parser = build_parser()
    args = parser.parse_args([
        "only_src.txt",
    ])
    print("② 只给位置参数:")
    print("  args.src:", args.src, type(args.src))
    print("  args.output:", args.output, type(args.output))
    print("  args.verbose:", args.verbose, type(args.verbose))


def demo_long_short():
    """③ 长短选项等价:--output 和 -o 都存进 args.output"""
    parser = build_parser()
    args = parser.parse_args([
        "a.txt",
        "--output", "b.txt",
    ])
    print("③ 长选项 --output 与 -o 等价:")
    print("  args.output:", args.output, type(args.output))


if __name__ == "__main__":
    demo_all_given()
    demo_positional_only()
    demo_long_short()
