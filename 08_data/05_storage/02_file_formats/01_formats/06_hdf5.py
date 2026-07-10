"""HDF5 格式读写

依赖: pip install h5py
      # pandas 方式还需: pip install tables
Python 3.12。运行: python 06_hdf5.py

层次化数据容器（Hierarchical Data Format）：一个文件内多个数据集 + 元数据。
擅长多维数组（图像/特征矩阵）和科学数据集；支持切片读，不必加载全部数据。
"""
import pathlib

import numpy as np

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)


def demo01_basic():
    """① h5py 基本读写：数据集 + 属性"""
    try:
        import h5py
    except ImportError:
        print("需要安装: pip install h5py")
        return

    print("① 基本读写（h5py）")
    path = DATA_DIR / "demo.h5"

    arr = rng.random((100, 50)).astype("float32")
    labels = rng.integers(0, 5, 100)

    with h5py.File(path, "w") as f:
        f.create_dataset("features", data=arr)
        f.create_dataset("labels",   data=labels)
        # 文件级属性（元数据）
        f.attrs["description"] = "示例数据集"
        f.attrs["version"]     = "1.0"
        f.attrs["n_samples"]   = 100

    with h5py.File(path, "r") as f:
        feats = f["features"][:]
        labs  = f["labels"][:]
        desc  = f.attrs["description"]
        print(f"  features: {feats.shape}  labels: {labs.shape}")
        print(f"  描述: {desc}  版本: {f.attrs['version']}")

    print(f"  文件大小: {path.stat().st_size:,} bytes")


def demo02_slice():
    """② 切片读：只加载需要的部分（大数据集核心用法）"""
    try:
        import h5py
    except ImportError:
        return

    print("\n② 切片读（不加载全部）")
    path = DATA_DIR / "images.h5"

    # 模拟 1000 张 64×64 RGB 图像
    images = rng.random((1000, 64, 64, 3)).astype("float32")
    with h5py.File(path, "w") as f:
        # chunks 决定每次 IO 的最小粒度，按 batch 大小设置更高效
        f.create_dataset("images", data=images,
                         compression="gzip", compression_opts=4,
                         chunks=(32, 64, 64, 3))

    with h5py.File(path, "r") as f:
        batch = f["images"][0:32]     # 只读第 0~31 张
        print(f"  全量 shape: {f['images'].shape}")
        print(f"  切片 batch[0:32]: {batch.shape}")
        print(f"  文件大小: {path.stat().st_size:,} bytes（gzip 压缩）")


def demo03_groups():
    """③ 组（Groups）：在一个文件内组织多个数据集，类似目录树"""
    try:
        import h5py
    except ImportError:
        return

    print("\n③ 层次化组（Groups）")
    path = DATA_DIR / "hierarchical.h5"

    with h5py.File(path, "w") as f:
        # 创建组（类似目录）
        train = f.create_group("train")
        val   = f.create_group("val")

        train.create_dataset("X", data=rng.random((800, 128)).astype("float32"))
        train.create_dataset("y", data=rng.integers(0, 10, 800))
        val.create_dataset("X",   data=rng.random((200, 128)).astype("float32"))
        val.create_dataset("y",   data=rng.integers(0, 10, 200))

        # 组级属性
        train.attrs["split"] = "train"
        val.attrs["split"]   = "val"

    with h5py.File(path, "r") as f:
        print(f"  顶级 keys: {list(f.keys())}")
        print(f"  train/X: {f['train/X'].shape}")
        print(f"  val/X:   {f['val/X'].shape}")
        print(f"  train split: {f['train'].attrs['split']}")

    print(f"  文件大小: {path.stat().st_size:,} bytes")


def demo04_pandas():
    """④ pandas HDF5（需要 tables 包）：表格数据 + 查询"""
    print("\n④ pandas HDF5（tables）")
    try:
        import pandas as pd
        import tables  # noqa：触发 ImportError 提示
        path = DATA_DIR / "df.h5"
        df = pd.DataFrame({
            "symbol": rng.choice(["AAPL", "MSFT", "GOOG"], 100),
            "close":  rng.uniform(100, 500, 100).round(2),
            "volume": rng.integers(100_000, 5_000_000, 100),
        })
        df.to_hdf(path, key="quotes", mode="w", complevel=5, format="table",
                  data_columns=["symbol", "close", "volume"])
        back = pd.read_hdf(path, key="quotes")
        print(f"  写读: {back.shape}  {path.stat().st_size:,} bytes")

        # format="table" + data_columns 支持 where 查询
        subset = pd.read_hdf(path, key="quotes", where="close > 300")
        print(f"  where close>300: {subset.shape}")
    except ImportError:
        print("  需要安装: pip install tables")
        print("  （h5py 不依赖 tables，pandas HDF5 才需要）")


if __name__ == "__main__":
    demo01_basic()
    demo02_slice()
    demo03_groups()
    demo04_pandas()
