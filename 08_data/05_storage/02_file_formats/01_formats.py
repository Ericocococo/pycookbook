"""常见文件格式读写：CSV / JSON / Excel / Parquet / Feather / HDF5 / Pickle / NPY

依赖:
  pip install pandas pyarrow openpyxl h5py
  # HDF5（pandas 方式）还需: pip install tables
Python 3.12。运行: python 01_formats.py

输出写到脚本旁的 data/ 目录（已被 .gitignore 忽略）。
"""
import json
import pathlib
import pickle

import numpy as np
import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 通用示例数据（100 行）
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
# ① CSV
# ---------------------------------------------------------------------------

def demo01_csv():
    """① CSV：最通用的文本格式，与任何工具互通"""
    print("① CSV")
    path = DATA_DIR / "data.csv"

    # 写：utf-8-sig 带 BOM，Excel 双击打开中文不乱码
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    # 读
    back = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["date"])
    print(f"  读回: {back.shape}  dtypes: close={back['close'].dtype}")

    # 大文件分块读（不一次性加载到内存）
    total = sum(len(chunk) for chunk in pd.read_csv(path, chunksize=30))
    print(f"  分块读（chunksize=30）共 {total} 行")


# ---------------------------------------------------------------------------
# ② JSON
# ---------------------------------------------------------------------------

def demo02_json():
    """② JSON：API 数据 / 嵌套结构首选"""
    print("\n② JSON")

    # 标准库 —— 嵌套对象
    obj = {"name": "Alice", "scores": [95, 87, 92], "meta": {"level": "vip"}}
    path_obj = DATA_DIR / "obj.json"
    with open(path_obj, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    with open(path_obj, encoding="utf-8") as f:
        loaded = json.load(f)
    print(f"  标准库 obj: {loaded}")

    # Pandas —— 表格型 JSON（orient="records" 最常用）
    path_df = DATA_DIR / "data.json"
    df.to_json(path_df, orient="records", date_format="iso", force_ascii=False)
    back = pd.read_json(path_df, orient="records", convert_dates=["date"])
    print(f"  DataFrame JSON: {back.shape}  {path_df.stat().st_size:,} bytes")

    # orient 选项速查
    # records  → [{col:val,...}, ...]   最常用，行级
    # split    → {columns:[], data:[]} 保留列名，体积小
    # index    → {idx:{col:val}}       带行索引
    # columns  → {col:{idx:val}}       列导向
    # values   → [[val,...]]           纯数据，最紧凑


# ---------------------------------------------------------------------------
# ③ Excel
# ---------------------------------------------------------------------------

def demo03_excel():
    """③ Excel：报表 / 多 Sheet / 有样式需求时用"""
    print("\n③ Excel")
    path = DATA_DIR / "data.xlsx"

    # 读单表
    df.to_excel(path, sheet_name="行情", index=False)
    back = pd.read_excel(path, sheet_name="行情")
    print(f"  单表写读: {back.shape}  {path.stat().st_size:,} bytes")

    # 写多 Sheet
    path_multi = DATA_DIR / "multi.xlsx"
    with pd.ExcelWriter(path_multi, engine="openpyxl") as writer:
        df[df["symbol"] == "AAPL"].to_excel(writer, sheet_name="AAPL", index=False)
        df[df["symbol"] == "MSFT"].to_excel(writer, sheet_name="MSFT", index=False)
        df.describe().to_excel(writer, sheet_name="统计")
    print(f"  多 Sheet 写出: {path_multi.name}  {path_multi.stat().st_size:,} bytes")

    # 读指定 Sheet
    aapl = pd.read_excel(path_multi, sheet_name="AAPL")
    print(f"  读 AAPL sheet: {aapl.shape}")


# ---------------------------------------------------------------------------
# ④ Parquet
# ---------------------------------------------------------------------------

def demo04_parquet():
    """④ Parquet：列式二进制，大数据分析 / 数据湖首选"""
    print("\n④ Parquet")
    path = DATA_DIR / "data.parquet"

    df.to_parquet(path, compression="zstd", index=False)
    print(f"  写出（zstd）: {path.stat().st_size:,} bytes")

    # 列裁剪：只读需要的列，不扫整个文件
    part = pd.read_parquet(path, columns=["date", "symbol", "close"])
    print(f"  列裁剪读（3列）: {part.shape}  dtypes: {dict(part.dtypes)}")

    # 谓词下推（pyarrow filters）：只加载满足条件的 row group
    import pyarrow.parquet as pq
    table = pq.read_table(path, filters=[("symbol", "==", "AAPL")])
    print(f"  过滤读（AAPL）: {table.num_rows} 行")


# ---------------------------------------------------------------------------
# ⑤ Feather
# ---------------------------------------------------------------------------

def demo05_feather():
    """⑤ Feather：进程间临时中转，读写速度最快，不适合长期存储"""
    print("\n⑤ Feather")
    path = DATA_DIR / "data.feather"

    df.to_feather(path)
    back = pd.read_feather(path)
    print(f"  写读: {back.shape}  {path.stat().st_size:,} bytes")
    print(f"  特点：Arrow 内存格式直接落盘，读写接近内存速度")
    print(f"  注意：不保证跨 pyarrow 大版本兼容，仅用于短期中转")


# ---------------------------------------------------------------------------
# ⑥ HDF5
# ---------------------------------------------------------------------------

def demo06_hdf5():
    """⑥ HDF5：层次化容器，适合多维数组 / 科学数据 / 机器学习数据集"""
    print("\n⑥ HDF5")

    # h5py 方式 —— 多维数组（ML 数据集典型用法）
    try:
        import h5py
        path = DATA_DIR / "arrays.h5"
        images = rng.random((50, 32, 32, 3)).astype("float32")   # 50 张 32×32 RGB 图
        labels = rng.integers(0, 10, 50)

        with h5py.File(path, "w") as f:
            f.create_dataset("images", data=images, compression="gzip", chunks=(10, 32, 32, 3))
            f.create_dataset("labels", data=labels)
            f.attrs["description"] = "示例图像数据集"   # 文件级元数据

        with h5py.File(path, "r") as f:
            batch = f["images"][0:8]    # 切片读，不加载全部
            desc  = f.attrs["description"]
        print(f"  h5py 写出: {path.stat().st_size:,} bytes")
        print(f"  切片读 batch: {batch.shape}  描述: {desc}")

    except ImportError:
        print("  h5py 未安装，跳过：pip install h5py")

    # pandas 方式 —— 表格数据（需要 tables 包）
    try:
        path_pd = DATA_DIR / "df.h5"
        df.to_hdf(path_pd, key="quotes", mode="w", complevel=5)
        back = pd.read_hdf(path_pd, key="quotes")
        print(f"  pandas HDF5: {back.shape}  {path_pd.stat().st_size:,} bytes")
    except ImportError:
        print("  pandas HDF5 需要 tables 包，跳过：pip install tables")


# ---------------------------------------------------------------------------
# ⑦ Pickle
# ---------------------------------------------------------------------------

def demo07_pickle():
    """⑦ Pickle：任意 Python 对象序列化，仅内部使用"""
    print("\n⑦ Pickle")
    path = DATA_DIR / "obj.pkl"

    # 任意对象（模型、字典、自定义类实例）
    obj = {
        "config": {"lr": 0.001, "epochs": 100},
        "history": [0.9, 0.92, 0.95],
        "df_head": df.head(5),
    }
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(path, "rb") as f:
        loaded = pickle.load(f)

    print(f"  写读: {path.stat().st_size:,} bytes")
    print(f"  config: {loaded['config']}")
    print(f"  df_head shape: {loaded['df_head'].shape}")
    print(f"  警告：只 load 可信来源的 pkl，恶意 pkl 可执行任意代码")


# ---------------------------------------------------------------------------
# ⑧ NPY / NPZ
# ---------------------------------------------------------------------------

def demo08_numpy():
    """⑧ NPY / NPZ：NumPy 数组专用格式"""
    print("\n⑧ NPY / NPZ")

    arr = rng.random((1000, 100))

    # 单数组
    path_npy = DATA_DIR / "arr.npy"
    np.save(path_npy, arr)
    loaded = np.load(path_npy)
    print(f"  npy 写读: {arr.shape} → {loaded.shape}  {path_npy.stat().st_size:,} bytes")

    # 多数组打包（压缩）
    X = rng.random((500, 128)).astype("float32")
    y = rng.integers(0, 10, 500)
    path_npz = DATA_DIR / "dataset.npz"
    np.savez_compressed(path_npz, X=X, y=y)

    data = np.load(path_npz)
    print(f"  npz 写读: X={data['X'].shape}  y={data['y'].shape}  {path_npz.stat().st_size:,} bytes")
    print(f"  特点：纯 NumPy 无依赖，适合数组存取；不适合 DataFrame")


if __name__ == "__main__":
    demo01_csv()
    demo02_json()
    demo03_excel()
    demo04_parquet()
    demo05_feather()
    demo06_hdf5()
    demo07_pickle()
    demo08_numpy()
