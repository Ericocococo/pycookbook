# 反射与自省（Reflection & Introspection）

Python 的反射能力让程序在运行时动态读取、修改、检查自身结构。

| 文件 | 内容 |
|------|------|
| [01_getattr_family.py](01_getattr_family.py) | `getattr/setattr/delattr/hasattr`：动态属性读写，核心四件套 |
| [02_introspection.py](02_introspection.py) | `vars/dir/callable/type/isinstance/issubclass`：对象自省工具 |
| [03_magic_attrs.py](03_magic_attrs.py) | `__getattr__/__getattribute__/__setattr__/__delattr__`：自定义属性访问行为 |
| [04_inspect.py](04_inspect.py) | `inspect` 模块：函数签名 / 源码 / 成员列表 / 调用栈 |

## 核心概念

| 术语 | 含义 |
|------|------|
| **反射（Reflection）** | 运行时动态操作对象的属性和方法，属性名是字符串而非硬编码标识符 |
| **自省（Introspection）** | 查询对象自身的类型、属性列表、是否可调用等结构信息 |
| **`__dict__`** | 实例/类的属性字典，`vars()` 就是读它 |
| **`__getattr__`** | 属性查找失败时的兜底钩子（只在找不到时触发） |
| **`__getattribute__`** | 每次属性访问都触发（比 `__getattr__` 更底层，用错会无限递归） |

## 适用

- 根据字符串名称动态调用方法（命令分发、插件系统）
- 把字典/配置映射为对象属性访问风格
- 实现 `__getattr__` 做属性代理或懒加载
- 用 `inspect` 做调试工具、自动文档生成、框架钩子

## 不适用

- 能用普通属性访问就不要用 `getattr`——反射更慢、可读性更差
- `__getattribute__` 轻易不要重写（每次访问都触发，很容易递归崩溃）

## 核心速查

```python
# 动态读写属性
obj.name == getattr(obj, "name")
getattr(obj, "name", "默认值")   # 不存在时返回默认值而不是抛异常
setattr(obj, "name", value)
delattr(obj, "name")
hasattr(obj, "name")             # 内部调用 getattr，捕获 AttributeError

# 自省
vars(obj)                        # obj.__dict__，实例属性字典
dir(obj)                         # 所有属性名（含继承），用于探索
type(obj)                        # 精确类型
isinstance(obj, SomeClass)       # 推荐：支持继承和 Union
callable(obj)                    # 是否可以被调用

# inspect
import inspect
inspect.signature(func)          # 参数签名
inspect.getsource(func)          # 源代码字符串
inspect.getmembers(obj, inspect.ismethod)  # 所有方法
```
