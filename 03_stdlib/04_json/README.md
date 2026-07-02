# json —— JSON 数据的序列化与反序列化(JavaScript Object Notation)

| 文件 | 内容 |
|------|------|
| `01_basic.py` | 四核心:dumps/loads(字符串) 与 dump/load(文件)+ 类型映射 |
| `02_format.py` | 格式化输出:ensure_ascii / indent / sort_keys / separators |
| `03_custom_types.py` | 序列化 json 不认识的类型:default 函数 / 自定义 Encoder |
| `04_hooks.py` | 反序列化钩子:object_hook / parse_float / parse_int |
| `05_pitfalls.py` | 常见陷阱:单引号 / NaN / 尾逗号 / 中文落盘 / key 被转字符串 |


## 适用

- 与 Web API、配置文件、前端交换数据(JSON 是事实标准的文本交换格式)
- 把 dict/list 等结构存成人类可读的文本,或从文本还原
- 需要跨语言、跨平台传递结构化数据

## 不适用

- 存 Python 专有对象(函数、集合、自定义类实例)→ pickle(不跨语言、有安全风险)
- 超大数据 / 高性能场景 → orjson、ujson(三方库,更快)或列式存储 parquet
- 带注释、尾逗号的配置 → 用 toml / yaml,JSON 语法不支持

## 核心速查

```python
import json

json.dumps(obj)                        # 对象 -> JSON 字符串
json.loads(s)                          # JSON 字符串 -> 对象
json.dump(obj, f)                      # 对象 -> 写入文件对象 f
json.load(f)                           # 从文件对象 f 读 -> 对象

json.dumps(obj, ensure_ascii=False)    # 中文正常显示(默认会转成 \\uXXXX)
json.dumps(obj, indent=2)              # 缩进美化(默认紧凑单行)
json.dumps(obj, default=fn)            # 遇到不支持的类型时调 fn 转换
json.loads(s, parse_float=Decimal)     # 金额等用 Decimal 解析,避免精度丢失
```
