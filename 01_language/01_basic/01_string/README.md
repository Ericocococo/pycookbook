# 字符串（str）

| 文件 | 内容 |
|------|------|
| [01_create.py](01_create.py) | 创建方式：引号 / 三引号 / raw / 转义字符 / bytes |
| [02_format.py](02_format.py) | 格式化：f-string / format / 对齐 / 数字格式 / 日期 |
| [03_methods.py](03_methods.py) | 常用方法：查找 / 替换 / 分割 / 大小写 / 去空白 / 判断 |
| [04_slice.py](04_slice.py) | 索引与切片：正负索引 / 切片 / 步长 / 反转 |
| [05_encode.py](05_encode.py) | 编码：str/bytes 互转 / encode / decode / 乱码原因 |

## 核心概念

| 术语 | 含义 |
|------|------|
| **不可变（immutable）** | 字符串创建后不能原地修改，所有"修改"操作都返回新字符串 |
| **Unicode** | Python 3 的 str 是 Unicode 字符串，一个汉字 = 一个字符 |
| **bytes** | 字节串，存储二进制数据，与 str 通过 encode/decode 互转 |
| **f-string** | `f"..."` 格式，花括号内可写任意 Python 表达式，Python 3.6+ |

## 核心速查

```python
s = "hello, 世界"

# 长度（字符数，不是字节数）
len(s)                      # 9

# f-string 格式化
name, score = "Alice", 99.5
f"{name} 得了 {score:.1f} 分"  # 'Alice 得了 99.5 分'

# 常用方法
s.upper()                   # 'HELLO, 世界'
s.replace("hello", "hi")    # 'hi, 世界'
"a,b,c".split(",")          # ['a', 'b', 'c']
"  hi  ".strip()            # 'hi'
s.startswith("hello")       # True

# 切片
s[0]      # 'h'
s[-1]     # '界'
s[0:5]    # 'hello'
s[::-1]   # 反转

# 编码
s.encode("utf-8")           # bytes
b'\xe4\xb8\x96'.decode("utf-8")  # str
```
