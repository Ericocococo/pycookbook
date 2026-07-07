# 对象表示与标识

| 文件 | 内容 |
|------|------|
| [01_repr_str.py](01_repr_str.py) | `repr` vs `str` / `ascii` / `__repr__` / `__str__` / f-string `!r` |
| [02_print.py](02_print.py) | `print` 完整参数：`sep` / `end` / `file` / `flush` / 进度条 |
| [03_pprint.py](03_pprint.py) | `pprint`：嵌套结构漂亮打印 / `width` / `depth` / `pformat` |
| [04_id_hash.py](04_id_hash.py) | `id` / `is` vs `==` / `hash` / `__hash__` / 小整数缓存陷阱 |

## 核心概念

| 术语 | 含义 |
|------|------|
| `str(obj)` | 给人看的字符串，友好可读 |
| `repr(obj)` | 给开发者看的字符串，精确，通常可 `eval` 还原 |
| `id(obj)` | 对象唯一标识（CPython 里是内存地址） |
| `is` | 比较身份（id 是否相同），只用于 `None` / 单例 |
| `==` | 比较值（调用 `__eq__`），日常比较用这个 |
| `hash(obj)` | 哈希值，决定对象能否放进 `set` / `dict` |

## 核心速查

```python
# repr vs str
repr("hello\nworld")   # "'hello\\nworld'"  — 换行显示为 \n
str("hello\nworld")    # 'hello\nworld'     — 换行真的换行

# f-string 调试利器
x = "hello\nworld"
f"{x!r}"    # "'hello\\nworld'"  — 等价于 repr(x)

# print 参数
print("a", "b", "c", sep=",")    # a,b,c
print("进度", end="\r")           # 不换行，回到行首（进度条）
print("错误", file=sys.stderr)    # 打印到 stderr

# is vs ==
x is None       # ✓ 判断 None 用 is
x == "hello"    # ✓ 判断值用 ==

# hash
hash("hello")   # 可哈希，能放进 set/dict
hash([1,2,3])   # TypeError：list 不可哈希
```
