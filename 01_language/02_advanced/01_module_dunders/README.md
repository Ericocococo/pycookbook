# dunder 属性 —— 双下划线特殊方法

dunder = double underscore，Python 约定的特殊名称前后各两个下划线。

| 文件 | 内容 |
|------|------|
| `01_module.py` | 模块级：`__file__` / `__name__` / `__doc__` / `__package__` / `__dict__` / `__cached__` / `__all__` / `__version__` |
| `02_class.py` | 类级：`__init__` / `__repr__` / `__eq__` / `__hash__` / `__slots__` / `__getitem__` / `__call__` / `__enter__` |
| `03_function.py` | 函数级：`__name__` / `__qualname__` / `__defaults__` / `__annotations__` / `__code__` / `__closure__` |

## 核心概念

### 模块级

| 属性 | 一句话 |
|------|--------|
| `__file__` | 当前文件绝对路径，配合 pathlib 定位资源 |
| `__name__` | 直接运行为 `'__main__'`，import 时为模块全限定名 |
| `__doc__` | 模块/函数/类的 docstring，`help()` 读取它 |
| `__package__` | 所属包名，顶层脚本为 `None` |
| `__all__` | 控制 `from module import *` 的导出列表 |
| `__version__` | 约定俗成的版本号，setuptools 读取 |

### 类级

| 属性 | 一句话 |
|------|--------|
| `__init__` | 初始化实例，最常用 |
| `__repr__` | 给开发者看的字符串，`eval(repr(obj))` 应能重建 |
| `__str__` | 给用户看的字符串，`print(obj)` 调用 |
| `__eq__` | `==` 运算符 |
| `__hash__` | `hash(obj)`，放到 set/dict key 的前提 |
| `__bool__` | `if obj:` 判断，优先于 `__len__` |
| `__getitem__` | `obj[i]` 取值 |
| `__call__` | 让实例像函数一样调用 |
| `__enter__` / `__exit__` | `with obj:` 上下文管理器 |

### 函数级

| 属性 | 一句话 |
|------|--------|
| `__qualname__` | 含类路径的限定名，如 `Outer.inner` |
| `__defaults__` | 位置默认参数的元组 |
| `__annotations__` | 参数和返回值的类型注解字典 |
| `__code__` | 字节码对象，含 `co_varnames` / `co_argcount` / `co_filename` |
| `__closure__` | 闭包捕获的自由变量，普通函数为 `None` |

## 核心速查

```python
# 模块
from pathlib import Path
BASE = Path(__file__).resolve().parent
if __name__ == "__main__":
    main()

# 类：让自定义类像内置类型
class Shelf:
    def __init__(self, items): self._items = items
    def __repr__(self): return f"Shelf({self._items})"
    def __len__(self): return len(self._items)
    def __getitem__(self, i): return self._items[i]
    def __contains__(self, x): return x in self._items

# 函数调试
func.__code__.co_varnames       # 参数名
func.__defaults__               # 默认值
double.__closure__[0].cell_contents  # 闭包捕获的值
```
