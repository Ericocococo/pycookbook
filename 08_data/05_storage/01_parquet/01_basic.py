"""parquet 列式存储基础:pandas 读写 / 列裁剪 / 压缩对比 / 分区

依赖:pandas + pyarrow 引擎
安装:pip install pandas pyarrow
Python 3.12。运行: python 01_basic.py

输出写到脚本旁的 data/ 目录(已被 .gitignore 忽略)。
parquet 相比 CSV（Comma-Separated Values，逗号分隔值格式）:
按列存二进制 + 自带 schema（数据结构定义：列名 + 类型）+ 压缩,
读部分列不用扫全表,特别适合大数据分析 / 量化行情落盘。
"""
import pathlib

import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "data"

# 示例行情数据（symbol = 股票代码）
df = pd.DataFrame({
    "date":   ["2026-07-01", "2026-07-01", "2026-07-02"],
    "symbol": ["AAPL", "MSFT", "AAPL"],
    "close":  [210.5, 505.2, 212.0],
    "volume": [1_000_000, 800_000, 1_200_000],
})


def demo01_write_read():
    """① 写出 parquet；读回来（类型自动还原，不像 CSV 全是字符串）"""
    path = DATA_DIR / "quotes.parquet"
    # engine="pyarrow"：指定底层引擎为 PyArrow（Apache Arrow 的 Python 绑定）
    # compression="snappy"：snappy 是 Google 开发的压缩算法，追求速度而非极限压缩比
    print(df)
    df.to_parquet(path, engine="pyarrow", compression="snappy")
    print("① 写出 parquet:")
    print("  文件:", path.name)
    print("  大小:", path.stat().st_size, "bytes")

    back = pd.read_parquet(path)
    print("② 读回来:")
    print(back)
    print("  形状:", back.shape)
    print("  close 的 dtype:", back["close"].dtype)    # dtype = data type，数据类型
    print("  volume 的 dtype:", back["volume"].dtype)


def demo02_columns():
    """② 只读部分列（列式存储核心优势：不加载整表）"""
    path = DATA_DIR / "quotes.parquet"
    part = pd.read_parquet(path, columns=["date", "close"])
    print("② 只读 date + close 两列:")
    print(part)
    print("  列:", list(part.columns))
    print("  行数:", len(part))


def demo03_compression():
    """③ 压缩算法对比：体积 / 写速度 / 读速度（用 10 万行数据让差异可见）"""
    import time
    import numpy as np

    # 10 万行行情数据，让压缩效果和速度差异肉眼可见
    rng = np.random.default_rng(42)
    n = 100_000
    big = pd.DataFrame({
        "date":   pd.date_range("2020-01-01", periods=n, freq="min"),
        "symbol": rng.choice(["AAPL", "MSFT", "GOOG", "AMZN"], n),
        "close":  rng.uniform(100, 500, n).round(2),
        "volume": rng.integers(100_000, 5_000_000, n),
    })

    algos = [
        ("snappy", None),    # Google，速度优先，压缩比适中
        ("gzip",   None),    # 通用，压缩比高，速度慢
        ("zstd",   1),       # Facebook Zstandard level-1，极快
        ("zstd",   9),       # Zstandard level-9，接近 gzip 压缩比但更快
        (None,     None),    # 不压缩，作为基准
    ]

    results = []
    for comp, level in algos:
        label = "none" if comp is None else (f"zstd-{level}" if comp == "zstd" and level else comp)
        path = DATA_DIR / f"big_{label}.parquet"
        kwargs = {"compression": comp or "none"}
        if comp == "zstd" and level:
            kwargs["compression_level"] = level

        t0 = time.perf_counter()
        big.to_parquet(path, **kwargs)
        write_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        pd.read_parquet(path)
        read_ms = (time.perf_counter() - t0) * 1000

        size_kb = path.stat().st_size / 1024
        results.append((label, size_kb, write_ms, read_ms))

    none_size = results[-1][1]
    print("③ 压缩对比（10 万行，约 {:.0f} KB 无压缩）\n".format(none_size))
    print(f"  {'算法':<10} {'大小(KB)':>10} {'压缩率':>8} {'写(ms)':>9} {'读(ms)':>9}")
    print("  " + "-" * 52)
    for label, size_kb, write_ms, read_ms in results:
        ratio = size_kb / none_size
        print(f"  {label:<10} {size_kb:>10.1f} {ratio:>7.1%} {write_ms:>9.1f} {read_ms:>9.1f}")

    print("""
  选型建议
    snappy   读写最快，压缩比中等；实时落盘 / 频繁读写首选
    zstd-1   速度接近 snappy，体积更小；日常推荐
    zstd-9   压缩比接近 gzip，速度比 gzip 快数倍；归档冷数据
    gzip     兼容性最好（Spark/Hive 默认支持），但速度最慢
    none     下游工具自行压缩，或磁盘 IO 不是瓶颈时用
""")


def demo04_partition():
    """④ 分区存储：按 symbol 拆成子目录 symbol=AAPL / symbol=MSFT"""
    ds = DATA_DIR / "dataset"
    # partition_cols（分区列）：按该列的不同取值拆分成子目录，查询时只扫对应分区
    df.to_parquet(ds, partition_cols=["symbol"])
    print("④ 分区存储(partition_cols=['symbol']):")
    for sub in sorted(ds.glob("symbol=*")):
        print("  分区目录:", sub.name)
    only_aapl = pd.read_parquet(ds / "symbol=AAPL")
    print("  只读 AAPL 分区形状:", only_aapl.shape)


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    demo01_write_read()
    demo02_columns()
    demo03_compression()
    demo04_partition()