"""argparse 分组:argument_group(仅帮助分类) 与 mutually_exclusive_group(互斥)

标准库。Python 3.12。运行: python 05_groups.py

区别:
  argument_group          只影响 -h 帮助的分组展示,不改变解析逻辑
  mutually_exclusive_group 组内参数最多只能出现一个,否则报错
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="参数分组与互斥")

    # 1) argument_group:把相关参数在帮助里归到一起,纯展示用
    io_group = parser.add_argument_group("输入输出")
    io_group.add_argument("--src", help="源")
    io_group.add_argument("--dst", help="目标")

    # 2) mutually_exclusive_group:--json 和 --yaml 只能选一个
    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="以 JSON 输出")
    fmt.add_argument("--yaml", action="store_true", help="以 YAML 输出")
    return parser


def demo_normal():
    """① 正常(只给一个格式)"""
    parser = build_parser()
    args = parser.parse_args([
        "--src", "a",
        "--json",
    ])
    print("① 正常(只给一个格式):")
    print("  args.src:", args.src, type(args.src))
    print("  args.dst:", args.dst, type(args.dst))
    print("  args.json:", args.json, type(args.json))
    print("  args.yaml:", args.yaml, type(args.yaml))


def demo_group_help():
    """② argument_group 只影响帮助展示,不改变解析逻辑"""
    parser = build_parser()
    has_title = "输入输出" in parser.format_help()
    print("② 帮助文本是否含分组标题 '输入输出':")
    print("  ", has_title, type(has_title))


def demo_mutual_exclusive():
    """③ 同时给互斥的两个 → 报错退出"""
    parser = build_parser()
    print("③ 同时给互斥的 --json --yaml:")
    try:
        parser.parse_args([
            "--json",
            "--yaml",
        ])
    except SystemExit:
        print("  -> argparse 已报错并退出(符合预期)")


if __name__ == "__main__":
    demo_normal()
    demo_group_help()
    demo_mutual_exclusive()
