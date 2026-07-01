"""argparse 的 nargs(参数个数)与 choices(限定取值)

标准库。Python 3.12。运行: python 04_nargs_choices.py

nargs（number of arguments，参数个数）取值:
  N     固定 N 个,存成列表
  "+"   一个或多个
  "*"   零个或多个
  "?"   零个或一个(配合 const 有三态行为)
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="nargs / choices")
    # nargs=2：固定吃 2 个值,存成列表
    parser.add_argument("--point", nargs=2, type=int, help="两个整数,如 --point 3 4")
    # nargs="+"：一个或多个
    parser.add_argument("--files", nargs="+", help="一个或多个文件")
    # nargs="?" 的三态：
    #   完全不给 → default；给了但不带值 → const（常量）；给了带值 → 该值
    parser.add_argument(
        "--extra", nargs="?", default="none", const="given", help="三态参数"
    )
    # choices（选项集合）：限定只能从给定集合里选,否则报错
    parser.add_argument("--level", choices=["low", "mid", "high"], default="low")
    return parser


def demo01_full():
    """① 全给"""
    parser = build_parser()
    args = parser.parse_args([
        "--point", "3", "4",
        "--files", "a", "b", "c",
        "--level", "high",
        "--extra", "x",
    ])
    print("① 全给:")
    print("  args.point:", args.point, type(args.point))
    print("  args.files:", args.files, type(args.files))
    print("  args.level:", args.level, type(args.level))
    print("  args.extra:", args.extra, type(args.extra))


def demo02_nargs_optional():
    """② nargs="?" 的三态(简短,直接对照)"""
    parser = build_parser()
    no_extra = parser.parse_args([]).extra
    bare     = parser.parse_args(["--extra"]).extra
    with_val = parser.parse_args(["--extra", "x"]).extra
    print("② nargs='?' 三态:")
    print("  完全不给 --extra:", no_extra, type(no_extra))
    print("  给了但不带值:", bare, type(bare))
    print("  给了带值 x:", with_val, type(with_val))


def demo03_invalid_choice():
    """③ choices 不在集合内 → 报错退出"""
    parser = build_parser()
    print("③ --level 传非法值 unknown:")
    try:
        parser.parse_args([
            "--level", "unknown",
        ])
    except SystemExit:
        print("  -> argparse 已报错并退出(符合预期)")


if __name__ == "__main__":
    demo01_full()
    demo02_nargs_optional()
    demo03_invalid_choice()