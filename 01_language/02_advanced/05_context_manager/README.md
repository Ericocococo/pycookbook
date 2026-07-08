# 上下文管理器

`with` 语句保证资源在离开代码块时被释放——无论正常退出还是抛异常。
实现协议只需两个魔术方法；`@contextmanager` 让生成器函数直接充当上下文管理器。

| 文件 | 内容 |
|------|------|
| [01_protocol.py](01_protocol.py) | `__enter__`/`__exit__` 协议，异常参数，抑制异常 |
| [02_contextmanager.py](02_contextmanager.py) | `@contextmanager`，`yield` 分界点，异常处理 |
| [03_contextlib_tools.py](03_contextlib_tools.py) | `suppress`/`ExitStack`/`nullcontext`，`async with`/`@asynccontextmanager` |

## 核心概念

| 术语 | 含义 |
|------|------|
| **`__enter__`** | 进入 `with` 块时调用，返回值绑定到 `as` 变量 |
| **`__exit__(exc_type, exc_val, tb)`** | 离开时调用；返回 `True` 可抑制异常 |
| **`@contextmanager`** | `yield` 之前是 `__enter__`，之后是 `__exit__`；只能 `yield` 一次 |
| **`ExitStack`** | 动态注册任意数量的上下文管理器，统一在 `__exit__` 时清理 |

## 适用

- 文件、网络连接、锁、数据库事务等需要配对"打开/关闭"的资源
- 临时改变全局状态（改目录、改精度、mock）然后自动还原
- 动态数量的资源需要统一清理（用 `ExitStack`）

## 不适用

- 简单的 `try/finally` 逻辑不必封装成上下文管理器（过度抽象）

## 核心速查

```python
# 协议写法
class ManagedFile:
    def __init__(self, path): self.path = path
    def __enter__(self):
        self.f = open(self.path)
        return self.f
    def __exit__(self, exc_type, exc_val, tb):
        self.f.close()
        return False       # False = 不抑制异常

# @contextmanager 写法
from contextlib import contextmanager
@contextmanager
def managed_file(path):
    f = open(path)
    try:
        yield f            # yield 值绑定到 as 变量
    finally:
        f.close()          # 无论如何都会执行

with managed_file("data.txt") as f:
    data = f.read()

# suppress：静默指定异常
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("tmp.txt")

# ExitStack：动态注册
from contextlib import ExitStack
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
```
