# 常见文件格式

CSV / JSON / Excel / Parquet / Feather / HDF5 / Pickle / NPY 的读写、性能对比与编码修复。

| 目录 | 内容 |
|------|------|
| [01_formats/](01_formats/) | 各格式读写配方（8 个文件，每格式一个） |
| [02_benchmark/](02_benchmark/) | 10 万行性能基准：写速 / 读速 / 文件大小 / 列裁剪 |
| [03_encoding/](03_encoding/) | CSV 编码修复工具（解决 Windows Excel 乱码） |

## 格式速览

| 格式 | 可读性 | 压缩 | 多表 | 适合场景 |
|------|--------|------|------|---------|
| CSV | ✅ 文本 | ❌ | ❌ | 通用交换、Excel 互通 |
| JSON | ✅ 文本 | ❌ | ❌ | API 数据、嵌套结构 |
| Excel | ❌ 二进制 | ❌ | ✅ | 报表、有公式/样式需求 |
| Parquet | ❌ 二进制 | ✅ | ❌ | 大数据分析、数据湖 |
| Feather | ❌ 二进制 | 弱 | ❌ | 进程间临时中转 |
| HDF5 | ❌ 二进制 | ✅ | ✅ | 科学计算、多维数组 |
| Pickle | ❌ 二进制 | ❌ | ❌ | Python 对象持久化 |
| NPY/NPZ | ❌ 二进制 | NPZ有 | ❌ | NumPy 数组 |

## 性能基准（10 万行 × 5 列，量级参考）

```text
格式                  写(ms)    读(ms)    大小(KB)   相对CSV
-------------------   -------   -------   --------   ------
CSV                    ~160       ~46      4374       100%
JSON                    ~66      ~153      9745       223%    ← 体积最大
Excel                  ~4800    ~4300      3362        77%    ← 读写最慢
Parquet(snappy)         ~38        ~8      2469        56%
Parquet(zstd)           ~40        ~8      2322        53%    ← 体积最小（DataFrame）
Feather                 ~11        ~6      2836        65%    ← 读写最快
Pickle                  ~11        ~8      3444        79%
HDF5(h5py+gzip)         ~25        ~6       833        19%    ← 纯数值列，压缩率最高
```

## 选型

```text
通用交换 / 给别人          → CSV / JSON
报表 / 有样式 / 多 Sheet   → Excel
大数据分析 / 数据湖         → Parquet + zstd
进程间临时中转              → Feather
科学计算 / 多维数组         → HDF5 / NPZ
Python 对象持久化          → Pickle（仅内部）
```
