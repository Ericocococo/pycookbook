"""argparse 进阶:自定义 type 函数 / 自定义 action / parse_known_args

标准库。Python 3.12。运行: python 08_advanced.py
"""
import argparse


def even_int(s: str) -> int:
    """自定义 type：接收命令行字符串，返回想要的对象；
    校验失败抛 ArgumentTypeError，argparse 会转成友好的报错信息。
    """
    v = int(s)
    if v % 2 != 0:
        raise argparse.ArgumentTypeError(f"{v} 不是偶数")
    return v


class UpperAction(argparse.Action):
    """自定义 action：继承 argparse.Action 并重写 __call__，这里把传入值转成大写再存入 namespace。"""

    def __call__(self, parser, namespace, values, option_string=None):
        # namespace（命名空间）：存放所有解析结果的对象，等同于 args
        # option_string：触发此 action 的选项字符串，如 "--name" 或 "-n"
        # setattr：set attribute，动态给对象设属性，等效于 namespace.dest = values.upper()
        setattr(namespace, self.dest, values.upper())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="进阶用法")
    parser.add_argument("--num", type=even_int, help="必须是偶数")
    parser.add_argument("--name", action=UpperAction, help="自动转大写")
    return parser


def demo01_custom_type_action():
    """① 自定义 type(校验偶数)+ 自定义 action(转大写)"""
    parser = build_parser()
    args = parser.parse_args([
        "--num", "4",
        "--name", "tom",
    ])
    print("① 自定义 type + action:")
    print("  args.num:", args.num, type(args.num))
    print("  args.name:", args.name, type(args.name), "(已转大写)")


def demo02_type_fail():
    """② 自定义 type 校验失败 → 报错退出"""
    parser = build_parser()
    print("② --num 传奇数 3:")
    try:
        parser.parse_args([
            "--num", "3",
        ])
    except SystemExit:
        print("  -> 校验失败,argparse 已报错退出(符合预期)")


def demo03_parse_known():
    """③ parse_known_args：只解析认识的参数,其余原样返回（适合把未知参数转发给别的程序）"""
    parser = build_parser()
    known, unknown = parser.parse_known_args([
        "--num", "2",
        "--foo", "bar",   # --foo 不认识,会被收进 unknown 列表
    ])
    print("③ parse_known_args:")
    print("  known.num:", known.num, type(known.num))
    print("  known.name:", known.name, type(known.name))
    print("  unknown:", unknown, type(unknown))


if __name__ == "__main__":
    demo01_custom_type_action()
    demo02_type_fail()
    demo03_parse_known()