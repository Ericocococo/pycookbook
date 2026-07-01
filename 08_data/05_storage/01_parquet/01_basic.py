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
    df.to_parquet(path, engine="pyarrow", compression="snappy")
    print("① 写出 parquet:")
    print("  文件:", path.name)
    print("  大小:", path.stat().st_size, "bytes")

    back = pd.read_parquet(path)
    print("② 读回来:")
    print("  形状:", back.shape)
    print("  close 的 dtype:", back["close"].dtype)    # dtype = data type，数据类型
    print("  volume 的 dtype:", back["volume"].dtype)


def demo02_columns():
    """② 只读部分列（列式存储核心优势：不加载整表）"""
    path = DATA_DIR / "quotes.parquet"
    part = pd.read_parquet(path, columns=["date", "close"])
    print("② 只读 date + close 两列:")
    print("  列:", list(part.columns))
    print("  行数:", len(part))


def demo03_compression():
    """③ 压缩算法对比（同一份数据不同 compression 的体积）"""
    print("③ 压缩对比(bytes):")
    for comp in [
        "snappy",   # Google 开发，速度优先
        "gzip",     # 通用压缩，压缩比高，速度慢
        "zstd",     # Facebook 开发（Zstandard），速度与压缩比均衡
    ]:
        path = DATA_DIR / f"q_{comp}.parquet"
        df.to_parquet(path, compression=comp)
        print(f"  {comp}: {path.stat().st_size}")


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