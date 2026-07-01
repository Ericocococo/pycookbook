"""argparse —— 命令行参数解析，运行此文件查看目录导航"""

print("""
argparse —— 命令行参数解析

  01_basic.py             位置参数与可选参数基础（src / output / verbose）
  02_types_default.py     type 类型转换、default 默认值、required 必填
  03_actions.py           action：store_true / store_false / append / count
  04_nargs_choices.py     nargs 参数个数（N / * / ? / +）与 choices 限定取值
  05_groups.py            argument_group（帮助分类）与 mutually_exclusive_group（互斥）
  06_subcommands.py       add_subparsers 实现多级子命令（git commit / push 模式）
  07_help_customization.py  prog / description / epilog / metavar / formatter_class 帮助定制
  08_advanced.py          自定义 type 函数、自定义 action、parse_known_args
""")
