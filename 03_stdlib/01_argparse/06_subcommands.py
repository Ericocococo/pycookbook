"""argparse 子命令:add_subparsers 实现 git commit / git push 那样的多级命令

标准库。Python 3.12。运行: python 06_subcommands.py

推荐配合 set_defaults(func=handler) 做命令分发:
解析完直接 args.func(args) 调用对应处理函数。
"""
import argparse


def cmd_add(args: argparse.Namespace) -> str:
    """add 子命令的处理函数"""
    return f"add {args.name}"


def cmd_remove(args: argparse.Namespace) -> str:
    """remove 子命令的处理函数"""
    return f"remove {args.name} force={args.force}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="子命令演示:类似 git <command>")
    # dest="cmd" 记录用户选了哪个子命令;required=True 强制必须选一个
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # 子命令 1: add
    p_add = subparsers.add_parser("add", help="添加一项")
    p_add.add_argument("name")
    p_add.set_defaults(func=cmd_add)   # 绑定处理函数

    # 子命令 2: remove
    p_rm = subparsers.add_parser("remove", help="删除一项")
    p_rm.add_argument("name")
    p_rm.add_argument("--force", action="store_true")
    p_rm.set_defaults(func=cmd_remove)
    return parser


def demo_add():
    """① add 子命令"""
    parser = build_parser()
    args = parser.parse_args([
        "add",
        "tom",
    ])
    result = args.func(args)
    print("① add 子命令:")
    print("  args.cmd:", args.cmd, type(args.cmd))
    print("  args.name:", args.name, type(args.name))
    print("  分发调用 args.func(args):", result, type(result))


def demo_remove():
    """② remove 子命令(带 --force)"""
    parser = build_parser()
    args = parser.parse_args([
        "remove",
        "jerry",
        "--force",
    ])
    result = args.func(args)
    print("② remove 子命令:")
    print("  args.cmd:", args.cmd, type(args.cmd))
    print("  args.name:", args.name, type(args.name))
    print("  args.force:", args.force, type(args.force))
    print("  分发调用 args.func(args):", result, type(result))


if __name__ == "__main__":
    demo_add()
    demo_remove()
