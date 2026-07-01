"""argparse 帮助定制:prog / description / epilog / metavar / formatter_class

标准库。Python 3.12。运行: python 07_help_customization.py

用 parser.format_help() 可以拿到帮助文本字符串;
真实使用时用户敲 -h 会自动打印它并退出。
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mytool",                       # prog（program）：程序名，默认取脚本文件名
        description="工具说明,显示在参数列表上方",
        epilog="示例: mytool --count 3",     # epilog（尾声）：显示在帮助最末尾的补充说明
        # formatter_class（格式化类）：控制帮助文本的排版风格
        # ArgumentDefaultsHelpFormatter：在每个参数的 help 后自动追加 (default: ...)
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",    # metavar（meta variable，元变量）：帮助文本里参数值的占位名，不影响解析
        help="重复次数",
    )
    return parser


def demo01_show_help():
    """① 打印帮助文本,观察各项定制:prog / description / epilog / metavar / (default: 1)"""
    parser = build_parser()
    print("=== parser.format_help() 输出 ===")
    print(parser.format_help())


if __name__ == "__main__":
    demo01_show_help()