# functools — 高阶函数工具

`functools` 提供操作函数本身的工具：缓存、偏应用、包装、泛化分发。
与 `itertools` 关注"如何迭代"不同，`functools` 关注"如何变换函数"。

| 文件 | 内容 |
|------|------|
| [01_partial.py](01_partial.py) | `partial`：固定部分参数，生成专用函数 |
| [02_wraps.py](02_wraps.py) | `wraps`/`update_wrapper`：装饰器中保留函数元信息 |
| [03_lru_cache.py](03_lru_cache.py) | `lru_cache`/`cache`：缓存纯函数结果，`cache_info`/`cache_clear` |
| [04_reduce.py](04_reduce.py) | `reduce`：累积归约，与 `accumulate` 对比，配合 `operator` |
| [05_singledispatch.py](05_singledispatch.py) | `singledispatch`：按第一个参数类型分发的泛函数 |

## 核心概念

| 工具 | 一句话 |
|------|--------|
| `partial(func, *args, **kwargs)` | 预设部分参数，返回新的可调用对象 |
| `@wraps(func)` | 把 `func` 的 `__name__`/`__doc__`/`__wrapped__` 复制给包装函数 |
| `@lru_cache(maxsize=128)` | LRU 缓存：相同参数不重复计算，maxsize=None 则无上限 |
| `@cache` | Python 3.9+，等价于 `@lru_cache(maxsize=None)` |
| `reduce(func, it, init)` | 从左到右归约为单个值 |
| `@singledispatch` | 根据第一个参数的类型选择不同实现 |

## 核心速查

```python
from functools import partial, wraps, lru_cache, cache, reduce, singledispatch

# partial
from urllib.request import urlopen
get_json = partial(urlopen, timeout=5)

# wraps（装饰器标配）
def my_deco(func):
    @wraps(func)
    def wrapper(*a, **kw): return func(*a, **kw)
    return wrapper

# lru_cache
@lru_cache(maxsize=256)
def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)
fib.cache_info()      # CacheInfo(hits=..., misses=..., maxsize=256, currsize=...)

# reduce
reduce(lambda a, b: a * b, [1, 2, 3, 4])   # 24

# singledispatch
@singledispatch
def process(arg): raise NotImplementedError
@process.register(int)
def _(arg): return arg * 2
@process.register(str)
def _(arg): return arg.upper()
```
