"""文件格式性能基准：写速度 / 读速度 / 文件大小横向对比

依赖:
  pip install pandas pyarrow openpyxl h5py
  # HDF5（pandas 方式）还需: pip install tables
Python 3.12。运行: python 02_benchmark.py

测试数据：10 万行 × 5 列（混合类型），接近真实业务数据。
结果因机器和磁盘不同而异，重点关注相对量级。
"""
import pathlib
import pickle
import time

import numpy as np
import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

N = 100_000
rng = np.random.default_rng(42)
df = pd.DataFrame({
    "date":     pd.date_range("2020-01-01", periods=N, freq="min"),
    "symbol":   rng.choice(["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"], N),
    "close":    rng.uniform(100, 500, N).round(4),
    "volume":   rng.integers(100_000, 10_000_000, N),
    "category": rng.choice(["A", "B", "C", "D"], N),
})


def _timeit(func, repeat=3):
    """多次执行取最小值（排除抖动）"""
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        func()
        times.append(time.perf_counter() - t0)
    return min(times)


def _size_kb(path):
    return path.stat().st_size / 1024


# ---------------------------------------------------------------------------
# 各格式的写 / 读 函数
# ---------------------------------------------------------------------------

def _bench_csv(path):
    write = _timeit(lambda: df.to_csv(path, index=False))
    read  = _timeit(lambda: pd.read_csv(path))
    return write, read, _size_kb(path)


def _bench_json(path):
    write = _timeit(lambda: df.to_json(path, orient="records", date_format="iso"))
    read  = _timeit(lambda: pd.read_json(path, orient="records"))
    return write, read, _size_kb(path)


def _bench_parquet_snappy(path):
    write = _timeit(lambda: df.to_parquet(path, compression="snappy", index=False))
    read  = _timeit(lambda: pd.read_parquet(path))
    return write, read, _size_kb(path)


def _bench_parquet_zstd(path):
    write = _timeit(lambda: df.to_parquet(path, compression="zstd", index=False))
    read  = _timeit(lambda: pd.read_parquet(path))
    return write, read, _size_kb(path)


def _bench_feather(path):
    write = _timeit(lambda: df.to_feather(path))
    read  = _timeit(lambda: pd.read_feather(path))
    return write, read, _size_kb(path)


def _bench_excel(path):
    # Excel 很慢，只跑 1 次
    write = _timeit(lambda: df.to_excel(path, index=False, engine="openpyxl"), repeat=1)
    read  = _timeit(lambda: pd.read_excel(path, engine="openpyxl"), repeat=1)
    return write, read, _size_kb(path)


def _bench_pickle(path):
    write = _timeit(lambda: path.write_bytes(pickle.dumps(df, protocol=pickle.HIGHEST_PROTOCOL)))
    read  = _timeit(lambda: pickle.loads(path.read_bytes()))
    return write, read, _size_kb(path)


def _bench_hdf5_h5py(path):
    """h5py 存纯数值数组（字符串列需先编码，典型用法是 ML 特征矩阵）"""
    try:
        import h5py
        # h5py 不支持 object dtype（字符串），只存数值列
        num_df = df[["close", "volume"]].copy()
        # 字符串列编码为整数
        sym_codes = pd.Categorical(df["symbol"]).codes.astype("int32")
        cat_codes = pd.Categorical(df["category"]).codes.astype("int32")
        arr_close  = num_df["close"].to_numpy(dtype="float32")
        arr_volume = num_df["volume"].to_numpy(dtype="int64")

        def write():
            with h5py.File(path, "w") as f:
                f.create_dataset("close",    data=arr_close,   compression="gzip")
                f.create_dataset("volume",   data=arr_volume,  compression="gzip")
                f.create_dataset("symbol",   data=sym_codes,   compression="gzip")
                f.create_dataset("category", data=cat_codes,   compression="gzip")

        def read():
            with h5py.File(path, "r") as f:
                return {k: f[k][:] for k in f.keys()}

        w = _timeit(write)
        r = _timeit(read)
        return w, r, _size_kb(path)
    except ImportError:
        return None, None, None


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

FORMATS = [
    ("CSV",             "data.csv",           _bench_csv),
    ("JSON",            "data.json",          _bench_json),
    ("Excel",           "data.xlsx",          _bench_excel),
    ("Parquet(snappy)", "data_snappy.parquet", _bench_parquet_snappy),
    ("Parquet(zstd)",   "data_zstd.parquet",  _bench_parquet_zstd),
    ("Feather",         "data.feather",       _bench_feather),
    ("Pickle",          "data.pkl",           _bench_pickle),
    ("HDF5(h5py+gzip)", "data.h5",            _bench_hdf5_h5py),
]


def run_benchmark():
    print(f"基准测试：{N:,} 行 × 5 列（date/str/float/int/str）\n")
    print(f"{'格式':<20} {'写(ms)':>9} {'读(ms)':>9} {'大小(KB)':>10} {'压缩率':>8}")
    print("-" * 62)

    results = []
    csv_size = None

    for name, filename, bench_fn in FORMATS:
        path = DATA_DIR / filename
        try:
            w, r, size = bench_fn(path)
        except Exception as e:
            print(f"  {name:<18} 跳过（{e}）")
            continue

        if w is None:
            print(f"  {name:<18} 跳过（未安装依赖）")
            continue

        if name == "CSV":
            csv_size = size

        ratio = f"{size / csv_size:.1%}" if csv_size else "-"
        print(f"  {name:<18} {w*1000:>9.1f} {r*1000:>9.1f} {size:>10.1f} {ratio:>8}")
        results.append((name, w, r, size))

    print()
    _print_summary(results)
    _print_column_read(DATA_DIR)


def _print_summary(results):
    if not results:
        return

    by_write = sorted(results, key=lambda x: x[1])
    by_read  = sorted(results, key=lambda x: x[2])
    by_size  = sorted(results, key=lambda x: x[3])

    print("排名（越小越好）")
    print(f"  写速度: {' > '.join(r[0] for r in by_write)}")
    print(f"  读速度: {' > '.join(r[0] for r in by_read)}")
    print(f"  文件大小: {' > '.join(r[0] for r in by_size)}")


def _print_column_read(data_dir):
    """列裁剪对比：Parquet vs CSV 只读 2 列"""
    print("\n列裁剪对比（只读 close + volume 2列）")
    parquet_path = data_dir / "data_zstd.parquet"
    csv_path     = data_dir / "data.csv"

    if parquet_path.exists():
        t = _timeit(lambda: pd.read_parquet(parquet_path, columns=["close", "volume"]))
        print(f"  Parquet(zstd) 列裁剪: {t*1000:.1f} ms")

    if csv_path.exists():
        t = _timeit(lambda: pd.read_csv(csv_path, usecols=["close", "volume"]))
        print(f"  CSV           列裁剪: {t*1000:.1f} ms")
        t2 = _timeit(lambda: pd.read_csv(csv_path))
        print(f"  CSV           全列读: {t2*1000:.1f} ms  （CSV 列裁剪几乎无收益，仍要扫全文件）")

    print("""
结论
  读写速度：  Feather ≈ Pickle > Parquet > HDF5 > CSV > JSON >> Excel
  文件大小：  Parquet(zstd) < HDF5 < Parquet(snappy) < Feather < Pickle < CSV < JSON < Excel
  列裁剪：    Parquet 优势显著（只扫需要的列）；CSV/JSON 无论读几列都要扫全文件

选型建议
  通用交换 / 给别人         → CSV / JSON
  报表 / 有样式 / 多 Sheet  → Excel
  大数据分析 / 数据湖        → Parquet + zstd（兼顾压缩率与速度）
  进程间临时中转             → Feather（最快，但版本兼容弱）
  科学计算 / 多维数组        → HDF5（h5py）/ NPZ
  Python 对象持久化         → Pickle（仅内部，不跨语言）
""")


if __name__ == "__main__":
    run_benchmark()
