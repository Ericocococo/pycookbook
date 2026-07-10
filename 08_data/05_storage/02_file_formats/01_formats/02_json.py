"""JSON 格式读写

依赖: pip install pandas
Python 3.12。运行: python 02_json.py

API 数据 / 嵌套结构首选。纯文本，跨语言，但体积大、无类型（数值/字符串不区分）。
"""
import json
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


def demo01_stdlib():
    """① 标准库 json：嵌套对象 / 任意结构"""
    print("① 标准库 json（嵌套对象）")
    path = DATA_DIR / "obj.json"

    obj = {
        "name": "Alice",
        "scores": [95, 87, 92],
        "meta": {"level": "vip", "tags": ["python", "data"]},
    }

    # 写：ensure_ascii=False 保留中文，indent=2 格式化
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    with open(path, encoding="utf-8") as f:
        loaded = json.load(f)
    print(f"  读回: {loaded}")

    # 字符串互转（不经文件）
    s = json.dumps(obj, ensure_ascii=False)
    back = json.loads(s)
    print(f"  dumps/loads: {back['name']}")


def demo02_dataframe():
    """② Pandas DataFrame → JSON（多种 orient）"""
    print("\n② DataFrame JSON")

    # orient="records"：[{col:val,...}, ...]，最常用，行级，易与前端/API 互通
    path = DATA_DIR / "data_records.json"
    df.to_json(path, orient="records", date_format="iso", force_ascii=False)
    back = pd.read_json(path, orient="records", convert_dates=["date"])
    print(f"  records: {back.shape}  {path.stat().st_size:,} bytes")

    # orient="split"：{columns:[], index:[], data:[[]]}，体积较小，保留列名和索引
    path_split = DATA_DIR / "data_split.json"
    df.to_json(path_split, orient="split", date_format="iso")
    back_split = pd.read_json(path_split, orient="split", convert_dates=["date"])
    print(f"  split:   {back_split.shape}  {path_split.stat().st_size:,} bytes")

    # orient 速查：
    # records  → [{col:val}, ...]         行级，最常用
    # split    → {columns,index,data}     保留结构，体积较小
    # index    → {idx:{col:val}}          带行索引
    # columns  → {col:{idx:val}}          列导向
    # values   → [[val,...]]              纯数据，最紧凑，无列名


def demo03_lines():
    """③ JSON Lines（JSONL）：每行一个 JSON 对象，适合流式读写 / 大文件"""
    print("\n③ JSON Lines（JSONL）")
    path = DATA_DIR / "data.jsonl"

    # 写：lines=True
    df.to_json(path, orient="records", lines=True, date_format="iso")
    print(f"  写出: {path.name}  {path.stat().st_size:,} bytes")

    # 读：lines=True
    back = pd.read_json(path, orient="records", lines=True, convert_dates=["date"])
    print(f"  读回: {back.shape}")

    # 标准库流式读（一行一行处理，不全量加载）
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            _ = json.loads(line)
            count += 1
    print(f"  流式读行数: {count}")


def demo04_custom_encoder():
    """④ 自定义序列化：处理 datetime / numpy / Decimal 等不可序列化类型"""
    print("\n④ 自定义 encoder")
    import datetime
    import decimal

    class SmartEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    data = {
        "dt": datetime.datetime(2026, 1, 1, 12, 0),
        "price": decimal.Decimal("123.456"),
        "arr": np.array([1, 2, 3]),
        "np_int": np.int64(42),
    }

    s = json.dumps(data, cls=SmartEncoder, ensure_ascii=False, indent=2)
    print(f"  序列化结果:\n{s}")


if __name__ == "__main__":
    demo01_stdlib()
    demo02_dataframe()
    demo03_lines()
    demo04_custom_encoder()
