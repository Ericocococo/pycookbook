# 常见文件格式

CSV / JSON / Excel / Parquet / Feather / HDF5 / Pickle / NPY 的读写用法与性能横向对比。

| 文件 | 内容 |
|------|------|
| [01_formats.py](01_formats.py) | 各格式读写 API：写出、读回、常用参数说明 |
| [02_benchmark.py](02_benchmark.py) | 10 万行数据的写速度 / 读速度 / 文件大小基准测试 |

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

## 性能基准（10 万行 × 5 列，本机实测量级）

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

## 列裁剪对比

```text
Parquet(zstd) 只读 2 列：  ~3 ms    ← 只扫需要的列
CSV           只读 2 列：  ~24 ms   ← 仍需扫全文件
CSV           全列读：     ~44 ms
```

列式格式（Parquet）在"宽表只取少量列"场景下优势显著。

## 选型

```text
通用交换 / 给别人          → CSV / JSON
报表 / 有样式 / 多 Sheet   → Excel
大数据分析 / 数据湖         → Parquet + zstd（兼顾压缩率与速度）
进程间临时中转              → Feather（最快，但版本兼容弱）
科学计算 / 多维数组         → HDF5（h5py）/ NPZ
Python 对象持久化          → Pickle（仅内部，不跨语言）
```

## 适用

- 需要跨语言、跨工具交换数据用 CSV / JSON / Parquet
- 纯 Python 内部缓存用 Feather 或 Pickle
- ML 训练数据集（图像/特征矩阵）用 HDF5 或 NPZ

## 不适用

- Excel 不适合程序间批量读写（慢 100x）
- Pickle 不适合跨语言或长期存储（版本/安全问题）
- Feather 不适合长期归档（大版本兼容性弱）

## 核心速查

```python
import pandas as pd

# CSV
df.to_csv("f.csv", index=False, encoding="utf-8-sig")
df = pd.read_csv("f.csv")

# Parquet（推荐日常用）
df.to_parquet("f.parquet", compression="zstd", index=False)
df = pd.read_parquet("f.parquet", columns=["col1", "col2"])  # 列裁剪

# Feather（临时中转）
df.to_feather("f.feather")
df = pd.read_feather("f.feather")

# Excel 多 Sheet
with pd.ExcelWriter("f.xlsx", engine="openpyxl") as w:
    df1.to_excel(w, sheet_name="Sheet1", index=False)
    df2.to_excel(w, sheet_name="Sheet2", index=False)

# HDF5 多维数组（h5py）
import h5py, numpy as np
with h5py.File("f.h5", "w") as f:
    f.create_dataset("X", data=np.zeros((1000, 128)), compression="gzip")
with h5py.File("f.h5", "r") as f:
    batch = f["X"][0:32]   # 切片读，不加载全部
```
