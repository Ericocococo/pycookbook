"""Feather 格式读写

依赖: pip install pandas pyarrow
Python 3.12。运行: python 05_feather.py

Arrow 内存格式直接落盘，读写速度最快（接近内存速度）。
适合进程间、脚本间临时数据交换；不保证跨 pyarrow 大版本兼容，不适合长期归档。
"""
import pathlib
import time

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


def demo01_basic():
    """① 写出 / 读回"""
    print("① 基本读写")
    path = DATA_DIR / "data.feather"

    df.to_feather(path)
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    back = pd.read_feather(path)
    print(f"  读回: {back.shape}  dtypes → close:{back['close'].dtype}")


def demo02_columns():
    """② 只读部分列"""
    print("\n② 列裁剪")
    path = DATA_DIR / "data.feather"

    part = pd.read_feather(path, columns=["date", "close", "volume"])
    print(f"  只读 3列: {part.shape}")


def demo03_vs_csv():
    """③ 与 CSV 读写速度对比（10 万行）"""
    print("\n③ 与 CSV 速度对比（10 万行）")

    big = pd.DataFrame({
        "symbol": rng.choice(["AAPL", "MSFT", "GOOG"], 100_000),
        "close":  rng.uniform(100, 500, 100_000).round(4),
        "volume": rng.integers(100_000, 10_000_000, 100_000),
    })

    csv_path     = DATA_DIR / "big.csv"
    feather_path = DATA_DIR / "big.feather"

    # CSV
    t0 = time.perf_counter(); big.to_csv(csv_path, index=False); csv_w = time.perf_counter() - t0
    t0 = time.perf_counter(); pd.read_csv(csv_path);              csv_r = time.perf_counter() - t0

    # Feather
    t0 = time.perf_counter(); big.to_feather(feather_path); fth_w = time.perf_counter() - t0
    t0 = time.perf_counter(); pd.read_feather(feather_path); fth_r = time.perf_counter() - t0

    print(f"  {'格式':<10} {'写(ms)':>9} {'读(ms)':>9} {'大小(KB)':>10}")
    print(f"  {'CSV':<10} {csv_w*1000:>9.1f} {csv_r*1000:>9.1f} {csv_path.stat().st_size/1024:>10.1f}")
    print(f"  {'Feather':<10} {fth_w*1000:>9.1f} {fth_r*1000:>9.1f} {feather_path.stat().st_size/1024:>10.1f}")
    print(f"\n  写速度提升: {csv_w/fth_w:.1f}x  读速度提升: {csv_r/fth_r:.1f}x")


def demo04_pipeline():
    """④ 典型用法：脚本 A 处理数据 → Feather → 脚本 B 接着用"""
    print("\n④ 进程间中转场景")
    path = DATA_DIR / "stage1_output.feather"

    # 模拟 脚本A：清洗数据后保存
    cleaned = df.dropna().copy()
    cleaned["close_norm"] = (cleaned["close"] - cleaned["close"].mean()) / cleaned["close"].std()
    cleaned.to_feather(path)
    print(f"  脚本A 写出中间结果: {path.name}  {path.stat().st_size:,} bytes")

    # 模拟 脚本B：直接读，零解析开销
    stage2 = pd.read_feather(path)
    result = stage2.groupby("symbol")["close_norm"].mean()
    print(f"  脚本B 读入并聚合:\n{result.to_string(dtype=False)}")


def demo05_vs_memory():
    """⑤ Feather vs 内存：差距只在 IO，格式本身零开销

    Feather 用 Arrow 列式内存格式直接落盘，读取时 mmap 映射，
    操作系统把文件页当内存页——几乎没有解析开销，差的只是磁盘带宽。
    """
    print("\n⑤ Feather vs 内存速度对比")
    import copy

    big = pd.DataFrame({
        "symbol": rng.choice(["AAPL", "MSFT", "GOOG"], 500_000),
        "close":  rng.uniform(100, 500, 500_000).astype("float32"),
        "volume": rng.integers(100_000, 10_000_000, 500_000),
    })
    path = DATA_DIR / "big.feather"
    big.to_feather(path)

    # 内存操作：deep copy 模拟"从另一个变量拿数据"
    t0 = time.perf_counter()
    _ = copy.copy(big)          # shallow copy，Arrow 零拷贝语义
    mem_t = time.perf_counter() - t0

    # Feather 读（mmap，接近内存速度）
    t0 = time.perf_counter()
    _ = pd.read_feather(path)
    fth_t = time.perf_counter() - t0

    print(f"  内存 copy:     {mem_t*1000:6.2f} ms")
    print(f"  Feather 读:    {fth_t*1000:6.2f} ms  ({path.stat().st_size/1024/1024:.1f} MB)")
    print(f"  差距: {fth_t/max(mem_t,1e-6):.1f}x")
    print("""
  定位对比：
    内存（DataFrame）   ~10 GB/s   容量受 RAM 限制，进程退出即消失
    Feather             ~1-3 GB/s  容量受磁盘限制，跨进程/重启可恢复
    Parquet             ~0.5 GB/s  体积最小，长期存储首选

  选型：
    同一进程反复用          → 留在内存
    跨进程传递 / 临时中转   → Feather（最接近内存速度的落盘方案）
    数据超过 RAM / 长期存储 → Parquet
    怕崩溃丢数据（长计算）  → Feather 定期 checkpoint
    "有保质期的高速缓存"   → Feather；"长期仓库" → Parquet
""")


if __name__ == "__main__":
    demo01_basic()
    demo02_columns()
    demo03_vs_csv()
    demo04_pipeline()
    demo05_vs_memory()
