# argparse —— 命令行参数解析

| 文件 | 内容 |
|------|------|
| `01_basic.py` | 位置参数与可选参数基础（src / output / verbose） |
| `02_types_default.py` | type 类型转换、default 默认值、required 必填 |
| `03_actions.py` | action：store_true / store_false / append / count |
| `04_nargs_choices.py` | nargs 参数个数（N / * / ? / +）与 choices 限定取值 |
| `05_groups.py` | argument_group（帮助分类）与 mutually_exclusive_group（互斥） |
| `06_subcommands.py` | add_subparsers 实现多级子命令（git commit / push 模式） |
| `07_help_customization.py` | prog / description / epilog / metavar / formatter_class 帮助定制 |
| `08_advanced.py` | 自定义 type 函数、自定义 action、parse_known_args |


## 适用

- 脚本需要 --flag / 位置参数，且想自动生成 --help
- 零依赖（标准库）

## 不适用

- 命令繁多、偏好装饰器风格 → click / typer
- 交互式 TUI              → rich / prompt_toolkit
- 配置文件驱动             → pydantic-settings / dynaconf

## 核心速查

```python
import argparse
parser = argparse.ArgumentParser(description='...')
parser.add_argument('src')                            # 位置参数
parser.add_argument('--output', '-o', default='.')    # 可选参数
parser.add_argument('--verbose', action='store_true') # 布尔开关
parser.add_argument('--n', type=int, default=5)       # 类型转换
args = parser.parse_args()
# args.src / args.output / args.verbose / args.n
```
