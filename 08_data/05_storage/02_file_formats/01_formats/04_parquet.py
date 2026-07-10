"""Parquet 格式读写

依赖: pip install pandas pyarrow
Python 3.12。运行: python 04_parquet.py

列式二进制格式：只读用到的列、自带 schema、压缩比高。大数据分析 / 数据湖首选。
"""
import pathlib

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
N = 100
df = pd.DataFrame({
    "date":     pd.date_range("2026-01-01", periods=N, freq="D"),
    "symbol":   rng.choice(["AAPL", "MSFT", "GOOG", "AMZN"], N),
    "close":    rng.uniform(100, 500, N).round(2),
    "volume":   rng.integers(100_000, 5_000_000, N),
    "category": rng.choice(["A", "B", "C"], N),
})


def demo01_basic():
    """① 写出 / 读回：schema 自动保留，类型精确还原"""
    print("① 基本读写")
    path = DATA_DIR / "data.parquet"

    df.to_parquet(path, compression="zstd", index=False)
    print(f"  写出（zstd）: {path.stat().st_size:,} bytes")

    back = pd.read_parquet(path)
    print(f"  读回: {back.shape}")
    print(f"  dtypes: {dict(back.dtypes)}")


def demo02_column_prune():
    """② 列裁剪：只读需要的列，不扫整个文件（列式格式核心优势）"""
    print("\n② 列裁剪")
    path = DATA_DIR / "data.parquet"

    part = pd.read_parquet(path, columns=["date", "symbol", "close"])
    print(f"  只读 3列: {part.shape}")
    print(f"  未读入的列不占内存，也不从磁盘加载")


def demo03_filter():
    """③ 谓词下推：读取时过滤 row group，减少 IO"""
    print("\n③ 谓词下推（pyarrow filters）")
    path = DATA_DIR / "data.parquet"

    # filters 在读取阶段就过滤，不是读完再 filter
    table = pq.read_table(path, filters=[("symbol", "==", "AAPL")])
    print(f"  过滤 AAPL: {table.num_rows} 行")

    # 复合条件
    table2 = pq.read_table(path, filters=[
        ("symbol", "in", ["AAPL", "MSFT"]),
        ("close", ">", 200),
    ])
    print(f"  AAPL|MSFT 且 close>200: {table2.num_rows} 行")


def demo04_compression():
    """④ 压缩算法对比（snappy / zstd / gzip / none）"""
    print("\n④ 压缩对比")
    import time

    algos = [
        ("snappy", None),
        ("zstd",   1),
        ("zstd",   9),
        ("gzip",   None),
        ("none",   None),
    ]

    big_df = pd.DataFrame({
        "symbol": rng.choice(["AAPL", "MSFT", "GOOG"], 50_000),
        "close":  rng.uniform(100, 500, 50_000).round(4),
        "volume": rng.integers(100_000, 10_000_000, 50_000),
    })

    print(f"  {'算法':<12} {'大小(KB)':>10} {'写(ms)':>9} {'读(ms)':>9}")
    print("  " + "-" * 45)
    for comp, level in algos:
        label = comp if not level else f"{comp}-{level}"
        path = DATA_DIR / f"cmp_{label}.parquet"
        kw = {"compression": comp, "index": False}
        if level:
            kw["compression_level"] = level

        t0 = time.perf_counter()
        big_df.to_parquet(path, **kw)
        w = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        pd.read_parquet(path)
        r = (time.perf_counter() - t0) * 1000

        print(f"  {label:<12} {path.stat().st_size/1024:>10.1f} {w:>9.1f} {r:>9.1f}")


def demo05_partition():
    """⑤ 分区写出：按列值拆成子目录，查询时只扫对应分区"""
    print("\n⑤ 分区存储")
    ds_path = DATA_DIR / "dataset"

    df.to_parquet(ds_path, partition_cols=["symbol"], index=False)
    print(f"  分区目录（symbol=*）:")
    for sub in sorted(ds_path.glob("symbol=*")):
        files = list(sub.glob("*.parquet"))
        print(f"    {sub.name}  {len(files)} 文件")

    # 只读某个分区
    aapl = pd.read_parquet(ds_path / "symbol=AAPL")
    print(f"  只读 AAPL 分区: {aapl.shape}")


if __name__ == "__main__":
    demo01_basic()
    demo02_column_prune()
    demo03_filter()
    demo04_compression()
    demo05_partition()
