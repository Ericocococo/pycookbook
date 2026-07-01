"""argparse 的 action:决定"遇到这个参数时做什么动作"

标准库。Python 3.12。运行: python 03_actions.py

常见 action:
  store_true / store_false —— 布尔开关（出现即存 True/False）
  store_const              —— 出现即存一个预设常量（const）
  append                   —— 同一参数可重复,每次值追加进列表
  count                    —— 统计参数出现次数（如 -vvv → 3）
  version                  —— 打印版本号后退出
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="常见 action 演示")
    parser.add_argument("--flag-on", action="store_true", help="出现即 True")
    parser.add_argument("--flag-off", action="store_false", help="出现即 False")
    # store_const：出现即把 const（常量）存进属性，不出现则为 None
    parser.add_argument("--mode", action="store_const", const="fast", help="出现即存常量 fast")
    # append：同一参数出现多次,值收集成列表
    parser.add_argument("--tag", action="append", help="可重复,收集成列表")
    # count：出现几次值就是几,常用于 -v/-vv/-vvv 递增日志级别
    parser.add_argument("-v", action="count", default=0, help="详细级别(-vvv=3)")
    return parser


def demo01_actions():
    """① 各 action 的结果(--flag-on 的连字符转成下划线属性名 args.flag_on)"""
    parser = build_parser()
    args = parser.parse_args([
        "--flag-on",
        "--flag-off",
        "--mode",
        "--tag", "a",
        "--tag", "b",
        "-vvv",
    ])
    print("① 各 action 的结果:")
    print("  args.flag_on:", args.flag_on, type(args.flag_on))
    print("  args.flag_off:", args.flag_off, type(args.flag_off))
    print("  args.mode:", args.mode, type(args.mode))
    print("  args.tag:", args.tag, type(args.tag))
    print("  args.v:", args.v, type(args.v))


def demo02_defaults():
    """② 都不传的默认(注意 store_false 默认为 True)"""
    parser = build_parser()
    args = parser.parse_args([])
    print("② 都不传的默认:")
    print("  args.flag_on:", args.flag_on, type(args.flag_on))
    print("  args.flag_off:", args.flag_off, type(args.flag_off))
    print("  args.mode:", args.mode, type(args.mode))
    print("  args.tag:", args.tag, type(args.tag))
    print("  args.v:", args.v, type(args.v))


def demo03_version():
    """③ version action:打印版本号后直接退出"""
    print("③ --version 的效果(下一行是它打印的版本):")
    vp = argparse.ArgumentParser()
    vp.add_argument("--version", action="version", version="myapp 1.0")
    try:
        vp.parse_args([
            "--version",
        ])
    except SystemExit:
        pass  # version 打印后即以 SystemExit 退出


if __name__ == "__main__":
    demo01_actions()
    demo02_defaults()
    demo03_version()