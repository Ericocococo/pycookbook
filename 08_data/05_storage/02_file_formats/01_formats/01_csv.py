"""CSV 格式读写

依赖: pip install pandas
Python 3.12。运行: python 01_csv.py

最通用的文本格式，与任何工具（Excel、数据库、其他语言）互通。
代价：无类型信息（读回全是字符串，需手动 parse_dates 等）、体积大、无法存多表。

编码修复（Windows Excel 乱码）见 fix_csv_encoding.py。
"""
import pathlib

import numpy as np
import pandas as pd

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


# ---------------------------------------------------------------------------
# ① 基本读写
# ---------------------------------------------------------------------------

def demo01_basic():
    """① 写出 / 读回"""
    print("① 写出 / 读回")
    path = DATA_DIR / "data.csv"

    # utf-8-sig 带 BOM，Windows Excel 双击打开中文不乱码
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    back = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["date"])
    print(f"  读回: {back.shape}  dtypes → close:{back['close'].dtype}  date:{back['date'].dtype}")


# ---------------------------------------------------------------------------
# ② 常用参数
# ---------------------------------------------------------------------------

def demo02_options():
    """② 常用参数：分隔符 / 指定列 / 跳过行"""
    print("\n② 常用参数")
    path = DATA_DIR / "data.csv"

    # 只读部分列
    part = pd.read_csv(path, usecols=["date", "close", "volume"])
    print(f"  usecols 3列: {part.shape}")

    # TSV（制表符分隔）
    tsv_path = DATA_DIR / "data.tsv"
    df.to_csv(tsv_path, sep="\t", index=False)
    back_tsv = pd.read_csv(tsv_path, sep="\t")
    print(f"  TSV 写读: {back_tsv.shape}  {tsv_path.stat().st_size:,} bytes")

    # skiprows + nrows：只读中间片段
    mid = pd.read_csv(path, skiprows=range(1, 51), nrows=20)
    print(f"  skiprows+nrows: {mid.shape}")


# ---------------------------------------------------------------------------
# ③ 大文件分块读
# ---------------------------------------------------------------------------

def demo03_chunk():
    """③ 大文件分块读（不一次性加载到内存）"""
    print("\n③ 分块读")
    path = DATA_DIR / "data.csv"

    total_rows = 0
    close_sum  = 0.0
    for chunk in pd.read_csv(path, chunksize=30, parse_dates=["date"]):
        total_rows += len(chunk)
        close_sum  += chunk["close"].sum()

    print(f"  分块（chunksize=30）总行数: {total_rows}")
    print(f"  close 累计均值: {close_sum / total_rows:.2f}")


# ---------------------------------------------------------------------------
# ④ 编码说明
# ---------------------------------------------------------------------------

def demo04_encoding():
    """④ 编码：写出时指定 utf-8-sig，避免 Windows 乱码"""
    print("\n④ 编码")
    src = DATA_DIR / "data_utf8.csv"
    dst = DATA_DIR / "data_utf8sig.csv"

    df.to_csv(src, index=False, encoding="utf-8")      # 无 BOM，Excel 可能乱码
    df.to_csv(dst, index=False, encoding="utf-8-sig")  # 带 BOM，Excel 正常

    print(f"  utf-8:     {src.stat().st_size:,} bytes（无 BOM）")
    print(f"  utf-8-sig: {dst.stat().st_size:,} bytes（带 BOM，Excel 可打开）")
    print("  已有乱码文件的批量修复：python fix_csv_encoding.py *.csv")


if __name__ == "__main__":
    demo01_basic()
    demo02_options()
    demo03_chunk()
    demo04_encoding()
