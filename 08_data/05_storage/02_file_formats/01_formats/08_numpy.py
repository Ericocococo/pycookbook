"""NumPy 数组格式读写（NPY / NPZ）

依赖: pip install numpy
Python 3.12。运行: python 08_numpy.py

NPY：单个 NumPy 数组的二进制格式，无依赖，精确还原 dtype 和 shape。
NPZ：多个数组打包 + 可选压缩，本质是 ZIP 包。
适合：纯数组存取、ML 特征/标签、数值计算中间结果。不适合 DataFrame（用 Parquet）。
"""
import pathlib
import time

import numpy as np

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)


def demo01_npy():
    """① NPY：单数组读写，精确保留 dtype / shape / 字节序"""
    print("① NPY（单数组）")
    path = DATA_DIR / "arr.npy"

    arr = rng.random((1000, 128)).astype("float32")
    np.save(path, arr)
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    loaded = np.load(path)
    print(f"  读回: shape={loaded.shape}  dtype={loaded.dtype}")
    print(f"  数值一致: {np.allclose(arr, loaded)}")


def demo02_npz():
    """② NPZ：多数组打包，savez_compressed 额外压缩"""
    print("\n② NPZ（多数组打包）")

    X_train = rng.random((5000, 128)).astype("float32")
    y_train = rng.integers(0, 10, 5000)
    X_val   = rng.random((1000, 128)).astype("float32")
    y_val   = rng.integers(0, 10, 1000)

    # 不压缩（更快）
    path_raw = DATA_DIR / "dataset.npz"
    np.savez(path_raw, X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val)

    # 压缩（更小，稍慢）
    path_cmp = DATA_DIR / "dataset_compressed.npz"
    np.savez_compressed(path_cmp, X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val)

    print(f"  savez:            {path_raw.stat().st_size/1024:,.1f} KB")
    print(f"  savez_compressed: {path_cmp.stat().st_size/1024:,.1f} KB")

    # 读：惰性加载，访问 key 时才真正读取
    data = np.load(path_cmp)
    print(f"  keys: {list(data.keys())}")
    print(f"  X_train: {data['X_train'].shape}  y_train: {data['y_train'].shape}")


def demo03_memmap():
    """③ memmap：内存映射，按需从磁盘加载，处理超大数组不 OOM"""
    print("\n③ memmap（内存映射）")
    path = DATA_DIR / "big.npy"

    # 创建一个 "大" 数组并写到磁盘（memmap 模式直接写，不占内存）
    shape = (10_000, 256)
    fp = np.memmap(path, dtype="float32", mode="w+", shape=shape)
    fp[:] = rng.random(shape).astype("float32")
    fp.flush()
    print(f"  写出（memmap）: {path.stat().st_size/1024:,.1f} KB  shape={shape}")

    # 读：只映射不加载，访问 fp[i] 时才 IO
    fp_read = np.memmap(path, dtype="float32", mode="r", shape=shape)
    batch = fp_read[0:32]           # 只读前 32 行，其余不 IO
    print(f"  读 batch[0:32]: {batch.shape}  mean={batch.mean():.4f}")
    print(f"  适合：数组大于内存 / 只访问局部切片 / 多进程共享只读数组")


def demo04_dtype():
    """④ dtype 精度：选对 dtype 显著减小体积"""
    print("\n④ dtype 与体积")
    arr = rng.random((100_000,))

    configs = [
        ("float64", arr.astype("float64")),
        ("float32", arr.astype("float32")),
        ("float16", arr.astype("float16")),
        ("int32",   (arr * 1000).astype("int32")),
        ("int16",   (arr * 1000).astype("int16")),
    ]

    print(f"  {'dtype':<10} {'大小(KB)':>10} {'精度损失'}")
    for name, a in configs:
        path = DATA_DIR / f"arr_{name}.npy"
        np.save(path, a)
        loss = "" if "float64" in name else f"max diff={abs(a.astype('float64') - arr).max():.2e}"
        print(f"  {name:<10} {path.stat().st_size/1024:>10.1f}  {loss}")


def demo05_vs_csv():
    """⑤ NPZ vs CSV 速度对比（纯数组场景）"""
    print("\n⑤ NPZ vs CSV 速度对比")
    import pandas as pd

    arr = rng.random((50_000, 10)).astype("float32")
    df  = pd.DataFrame(arr, columns=[f"c{i}" for i in range(10)])

    csv_path = DATA_DIR / "arr.csv"
    npz_path = DATA_DIR / "arr_cmp.npz"

    t0 = time.perf_counter(); df.to_csv(csv_path, index=False); csv_w = time.perf_counter() - t0
    t0 = time.perf_counter(); pd.read_csv(csv_path);             csv_r = time.perf_counter() - t0

    t0 = time.perf_counter(); np.savez_compressed(npz_path, data=arr); npz_w = time.perf_counter() - t0
    t0 = time.perf_counter(); np.load(npz_path)["data"];                npz_r = time.perf_counter() - t0

    print(f"  {'格式':<10} {'写(ms)':>9} {'读(ms)':>9} {'大小(KB)':>10}")
    print(f"  {'CSV':<10} {csv_w*1000:>9.1f} {csv_r*1000:>9.1f} {csv_path.stat().st_size/1024:>10.1f}")
    print(f"  {'NPZ':<10} {npz_w*1000:>9.1f} {npz_r*1000:>9.1f} {npz_path.stat().st_size/1024:>10.1f}")


if __name__ == "__main__":
    demo01_npy()
    demo02_npz()
    demo03_memmap()
    demo04_dtype()
    demo05_vs_csv()
