"""parquet 之 谓词下推过滤 与 增量追加写

依赖:pandas + pyarrow
安装:pip install pandas pyarrow
Python 3.12。运行: python 04_filters_append.py

- 谓词下推（predicate pushdown）：把过滤条件推到文件层执行，不必全读进内存再筛，
  数据量大时能省大量 IO / 内存（量化里按 symbol / 日期取子集常用）。
  predicate = 谓词（逻辑判断条件），pushdown = 下推（推到更底层执行）。
- 增量写（ParquetWriter）：分批把多个批次（batch）写进同一文件（如逐日追加行情）。
输出写到脚本旁的 data/ 目录(已被 .gitignore 忽略)。
"""
import pathlib

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA_DIR = pathlib.Path(__file__).parent / "data"

df = pd.DataFrame({
    "symbol": ["AAPL", "MSFT", "AAPL", "MSFT"],
    "date":   ["2026-07-01", "2026-07-01", "2026-07-02", "2026-07-02"],
    "close":  [210.5, 505.2, 212.0, 506.1],
})


def demo01_filters():
    """① 谓词下推：filters 在读取时就把不符合的行过滤掉"""
    path = DATA_DIR / "quotes_all.parquet"
    # index=False：不把 DataFrame 的行索引（0,1,2...）写入文件
    df.to_parquet(path, index=False)
    only_aapl = pd.read_parquet(path, filters=[("symbol", "==", "AAPL")])
    print("① 谓词下推 filters=[('symbol','==','AAPL')]:")
    print("  过滤后行数:", len(only_aapl))
    print(only_aapl.to_string(index=False))


def demo02_incremental():
    """② 增量追加写：ParquetWriter 分批把多个批次写进同一文件"""
    path = DATA_DIR / "stream.parquet"
    batch1 = pa.table({"symbol": ["AAPL"], "close": [210.5]})
    batch2 = pa.table({"symbol": ["MSFT"], "close": [505.2]})
    writer = pq.ParquetWriter(path, batch1.schema)
    writer.write_table(batch1)  # 第一批，产生一个 row group（行组，parquet 的内部分片单元）
    writer.write_table(batch2)  # 第二批，再产生一个 row group
    writer.close()

    back = pq.read_table(path)
    print("② 增量追加写(两批):")
    print("  最终行数:", back.num_rows)
    print("  行组数:", pq.ParquetFile(path).num_row_groups)


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    demo01_filters()
    demo02_incremental()