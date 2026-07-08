# 迭代体系

Python 的迭代体系是一套基于协议的设计：任何实现了 `__iter__` / `__next__` 的对象都能被 `for` 消费。
生成器是迭代器的语法糖，`yield from` 进一步简化了委托，异步生成器将整套机制搬到 `async/await` 世界。

| 文件 | 内容 |
|------|------|
| [01_protocol.py](01_protocol.py) | Iterable / Iterator 协议，手写 `__iter__`/`__next__`，`for` 循环底层 |
| [02_generator_func.py](02_generator_func.py) | 生成器函数，`yield`，`send`，惰性求值的内存优势 |
| [03_generator_expr.py](03_generator_expr.py) | 生成器表达式 `(x for x in ...)`，与列表推导式对比 |
| [04_yield_from.py](04_yield_from.py) | `yield from`，委托子生成器，透传 `send`/`throw`/`return` |
| [05_async_generator.py](05_async_generator.py) | `async def + yield`，异步生成器，`async for`，`__aiter__`/`__anext__` |

## 核心概念

| 术语 | 含义 |
|------|------|
| **Iterable** | 实现了 `__iter__()` 的对象，每次调用返回一个新迭代器；可反复消费 |
| **Iterator** | 实现了 `__iter__()` + `__next__()` 的对象；一次性，消费完抛 `StopIteration` |
| **Generator** | 用 `yield` 实现的迭代器；暂停/恢复执行，天然惰性 |
| **yield from** | 把迭代委托给子迭代器，同时透传 `send`/`throw`/`return` 值 |
| **async generator** | `async def` + `yield` 组合；用 `async for` 消费，不能有 `return value` |

## 适用

- 数据量大或来源无穷时用生成器（惰性，按需计算，节省内存）
- 管道式数据处理（多个生成器串联，零中间列表）
- 实现自定义容器类，让它支持 `for` 循环
- 异步 I/O 场景下逐批拉取数据

## 不适用

- 需要随机下标访问（`seq[i]`）—— 用列表
- 需要多次遍历同一份数据 —— 用列表（生成器只能走一遍）
- 数据量小且已在内存中 —— 列表推导式更直观

## 核心速查

```python
# for 循环等价展开
it = iter(iterable)          # 调用 __iter__
while True:
    try:
        item = next(it)      # 调用 __next__
    except StopIteration:
        break

# 生成器函数
def countdown(n):
    while n > 0:
        yield n              # 暂停，返回值给调用方
        n -= 1               # 恢复时从这里继续

# 生成器表达式（惰性）
gen = (x * x for x in range(10**6))  # 不立即计算

# yield from（委托）
def chain(a, b):
    yield from a
    yield from b

# 检查类型（正式方式）
from collections.abc import Iterable, Iterator, Generator
isinstance([], Iterable)             # True
isinstance(iter([]), Iterator)       # True
```
