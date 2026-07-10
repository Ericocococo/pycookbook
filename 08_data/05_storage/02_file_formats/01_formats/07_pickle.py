"""Pickle 格式读写

依赖: 内置模块，无需安装
Python 3.12。运行: python 07_pickle.py

Python 对象序列化：任意对象（模型、字典、自定义类）都能存取。
仅限 Python 内部使用，不跨语言；加载不可信来源的 pkl 有安全风险（可执行任意代码）。
"""
import io
import pathlib
import pickle
import time

import numpy as np
import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(42)


def demo01_basic():
    """① 写出 / 读回：任意 Python 对象"""
    print("① 基本读写")
    path = DATA_DIR / "obj.pkl"

    obj = {
        "config": {"lr": 0.001, "epochs": 100, "batch": 32},
        "history": {"loss": [0.9, 0.7, 0.5], "acc": [0.6, 0.8, 0.9]},
        "df_sample": pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]}),
        "arr": np.zeros((10, 10)),
    }

    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    with open(path, "rb") as f:
        loaded = pickle.load(f)
    print(f"  config: {loaded['config']}")
    print(f"  df_sample: {loaded['df_sample'].shape}")


def demo02_protocol():
    """② protocol 版本：影响兼容性与速度"""
    print("\n② protocol 版本对比")

    data = list(range(100_000))
    results = []
    for proto in range(pickle.HIGHEST_PROTOCOL + 1):
        buf = io.BytesIO()
        t0 = time.perf_counter()
        pickle.dump(data, buf, protocol=proto)
        w = time.perf_counter() - t0
        size = buf.tell()
        buf.seek(0)
        t0 = time.perf_counter()
        pickle.load(buf)
        r = time.perf_counter() - t0
        results.append((proto, size, w, r))

    print(f"  {'proto':<8} {'大小(B)':>10} {'写(ms)':>9} {'读(ms)':>9}")
    for proto, size, w, r in results:
        tag = " ← HIGHEST" if proto == pickle.HIGHEST_PROTOCOL else ""
        print(f"  {proto:<8} {size:>10,} {w*1000:>9.2f} {r*1000:>9.2f}{tag}")
    print("  建议：HIGHEST_PROTOCOL 速度最快，但旧版 Python 不兼容")


def demo03_bytes():
    """③ 内存中序列化（不经文件）：进程间传输 / 缓存"""
    print("\n③ 内存序列化（dumps/loads）")

    obj = {"key": "value", "arr": np.ones((100, 100))}

    data_bytes = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  dumps 大小: {len(data_bytes):,} bytes")

    back = pickle.loads(data_bytes)
    print(f"  loads 还原: arr shape = {back['arr'].shape}")


class _Model:
    """示例模型类（模块级定义，pickle 才能通过路径找到它）"""

    def __init__(self, weights, config):
        self.weights = weights
        self.config  = config
        self._cache  = {}   # 运行时状态，不需要持久化

    def __getstate__(self):
        """控制序列化内容：排除 _cache"""
        state = self.__dict__.copy()
        del state["_cache"]
        return state

    def __setstate__(self, state):
        """反序列化后恢复：重建 _cache"""
        self.__dict__.update(state)
        self._cache = {}

    def predict(self, x):
        return x @ self.weights


def demo04_custom_class():
    """④ 自定义类的序列化 / 反序列化（__getstate__ / __setstate__）"""
    print("\n④ 自定义类序列化")
    model = _Model(
        weights=np.random.rand(128, 10),
        config={"layers": [128, 64, 10], "activation": "relu"},
    )

    path = DATA_DIR / "model.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  写出模型: {path.stat().st_size:,} bytes")

    with open(path, "rb") as f:
        loaded_model = pickle.load(f)
    print(f"  weights shape: {loaded_model.weights.shape}")
    print(f"  config: {loaded_model.config}")
    print(f"  _cache 已重建: {loaded_model._cache}")


if __name__ == "__main__":
    demo01_basic()
    demo02_protocol()
    demo03_bytes()
    demo04_custom_class()
