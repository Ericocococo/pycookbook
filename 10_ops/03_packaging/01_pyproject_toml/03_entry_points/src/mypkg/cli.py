import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="mypkg")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.parse_args()


def init_cmd() -> None:
    print("初始化项目...")
