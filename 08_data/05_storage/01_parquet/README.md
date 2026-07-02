# parquet —— 列式存储格式

| 文件 | 内容 |
|------|------|
| `01_basic.py` | pandas 读写、列裁剪、压缩对比（snappy/gzip/zstd）、按列分区 |
| `02_pyarrow_api.py` | pyarrow 原生 API 直接读写、查看文件元数据 |
| `03_schema.py` | 显式指定 schema 与列类型，读回精确还原 |
| `04_filters_append.py` | 谓词下推过滤（减少 IO）与增量追加写 |


## 适用

- GB 级批量数据离线存储与分析
- 只读部分列（列裁剪大幅减少 IO）
- 跨语言数据交换（Python / Spark / DuckDB / Hive 均原生支持）

## 不适用

- 逐行追加写入 → SQLite / CSV
- 需要人眼直接查看 → CSV
- 实时流数据 → Avro / Kafka

## 核心速查

```python
import pandas as pd

df.to_parquet('data.parquet', compression='snappy', index=False)
df = pd.read_parquet('data.parquet', columns=['id', 'value'])
df = pd.read_parquet('data.parquet', filters=[('year', '==', 2024)])

import pyarrow.parquet as pq
meta = pq.read_metadata('data.parquet')
print(meta.num_rows, meta.num_row_groups)
```
