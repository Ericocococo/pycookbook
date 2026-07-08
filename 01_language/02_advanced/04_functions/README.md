# 函数高阶语法

Python 函数是一等对象：可以赋值给变量、作为参数传递、作为返回值返回。
这一特性衍生出闭包和装饰器两大模式，是 Python 元编程的入门台阶。

| 文件 | 内容 |
|------|------|
| [01_higher_order.py](01_higher_order.py) | 高阶函数：`map`/`filter`/`sorted` + 自定义，函数作为一等对象 |
| [02_lambda.py](02_lambda.py) | `lambda` 匿名函数，适用场景与限制 |
| [03_closure.py](03_closure.py) | 闭包，自由变量捕获，`nonlocal`，经典陷阱 |
| [04_decorator.py](04_decorator.py) | 无参装饰器，`@wraps`，计时 / 日志 / 重试 demo |
| [05_decorator_args.py](05_decorator_args.py) | 带参装饰器（三层嵌套），可选参数装饰器 |
| [06_class_decorator.py](06_class_decorator.py) | 类实现装饰器（`__call__`），用装饰器修改类 |

## 核心概念

| 术语 | 含义 |
|------|------|
| **高阶函数** | 接收函数作为参数，或返回函数作为结果 |
| **闭包** | 内层函数捕获了外层作用域的自由变量，外层函数返回后变量仍存活 |
| **装饰器** | 接收函数并返回新函数的高阶函数；`@deco` 是语法糖 |
| **`nonlocal`** | 在闭包内声明变量来自外层作用域，允许赋值（不声明只能读） |

## 适用

- 行为参数化（把策略作为函数传入，避免大量 `if/elif`）
- 横切关注点（日志、计时、鉴权、重试）用装饰器集中处理
- 工厂模式：用闭包生成"预设了某些参数"的函数

## 不适用

- 逻辑复杂时用普通函数而非 `lambda`（可读性优先）
- 装饰器不要处理业务逻辑，只做"围绕"目标函数的横切工作

## 核心速查

```python
# 高阶函数
sorted(data, key=lambda x: x.age)
list(map(str, [1, 2, 3]))
list(filter(None, [0, 1, "", "a"]))

# 闭包
def make_adder(n):
    def adder(x):
        return x + n      # n 是自由变量
    return adder
add5 = make_adder(5)

# 无参装饰器
from functools import wraps
def log(func):
    @wraps(func)          # 保留 __name__/__doc__ 等
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def greet(name): ...

# 带参装饰器
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def hello(): print("hi")
```
