# typing —— Python 类型注解模块

`typing` 提供类型标注语法，配合 Pyright/mypy 做静态检查，运行时零开销。

| 文件 | 内容 |
|------|------|
| `01_basic.py` | 类型推断、显式注解、类型收窄、Optional、Any 传染性 |
| `02_advanced.py` | Union、Literal、TypedDict、Final、assert_type |
| `03_generics_protocol.py` | 泛型函数/类（TypeVar/Generic）、Bound、Protocol 结构子类型 |
| `04_guards_overload.py` | TypeGuard 自定义守卫、Overload 函数重载、递归类型别名 |

## 适用

- 任何 Python 项目，给函数签名加类型，让 IDE 和类型检查器帮忙找 bug
- 公共 API / 库：必须加注解，`pyright --verifytypes` 检查覆盖率

## 不适用

- 纯脚本 / 一次性代码 → 加了反而啰嗦
- 运行时类型验证 → 用 `pydantic`，typing 的注解运行时被忽略

## 核心速查

```python
from typing import TypeVar, Generic, Protocol, TypeAlias, assert_type, Final

# 联合类型
def parse(value: str | int) -> int: ...

# 可空
name: str | None = None

# 泛型函数
T = TypeVar("T")
def first(items: list[T]) -> T | None: ...

# 泛型类
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...

# 鸭子类型（不需要继承）
class Drawable(Protocol):
    def draw(self) -> str: ...
```
