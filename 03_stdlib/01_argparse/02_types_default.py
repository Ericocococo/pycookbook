"""argparse 参数细节:type 类型转换 / default 默认值 / required 必填

标准库。Python 3.12。运行: python 02_types_default.py
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="type / default / required")
    # type:自动把字符串转成指定类型,转换失败会打印错误并退出
    parser.add_argument("--count", type=int, default=1, help="次数(int,默认 1)")
    parser.add_argument("--ratio", type=float, default=0.5, help="比例(float)")
    # required=True 让"可选参数"变成必填(不给就报错)
    parser.add_argument("--name", required=True, help="必填的名字")
    return parser


def demo_all_given():
    """① 全给(count 会从字符串转成 int)"""
    parser = build_parser()
    args = parser.parse_args([
        "--name", "tom",
        "--count", "3",
        "--ratio", "0.8",
    ])
    print("① 全给:")
    print("  args.name:", args.name)
    print("  args.count:", args.count, "->", type(args.count).__name__)
    print("  args.ratio:", args.ratio)


def demo_defaults():
    """② 不传 --count / --ratio,用默认值"""
    parser = build_parser()
    args = parser.parse_args([
        "--name", "jerry",
    ])
    print("② 用默认值:")
    print("  args.name:", args.name)
    print("  args.count:", args.count)
    print("  args.ratio:", args.ratio)


def demo_missing_required():
    """③ 漏传必填 --name → argparse 打印 usage+error 并退出"""
    parser = build_parser()
    print("③ 缺少必填 --name:")
    try:
        parser.parse_args([])
    except SystemExit:
        print("  -> argparse 已报错并退出(符合预期)")


if __name__ == "__main__":
    demo_all_given()
    demo_defaults()
    demo_missing_required()
