"""argparse 帮助定制:prog / description / epilog / metavar / formatter_class

标准库。Python 3.12。运行: python 07_help_customization.py

用 parser.format_help() 可以拿到帮助文本字符串;
真实使用时用户敲 -h 会自动打印它并退出。
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mytool",                       # 程序名(默认取脚本文件名)
        description="工具说明,显示在参数列表上方",
        epilog="示例: mytool --count 3       (结尾补充说明)",
        # 默认帮助不显示默认值;换成这个 formatter 会自动追加 (default: ...)
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",                         # 帮助里参数值的占位显示名
        help="重复次数",
    )
    return parser


def demo_show_help():
    """直接打印帮助文本,观察各项定制:prog / description / epilog / metavar / (default: 1)"""
    parser = build_parser()
    print("=== parser.format_help() 输出 ===")
    print(parser.format_help())


if __name__ == "__main__":
    demo_show_help()
