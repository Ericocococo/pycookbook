"""parquet 之 schema 与类型控制:显式指定列类型,读回精确还原

依赖:pyarrow
安装:pip install pyarrow
Python 3.12。运行: python 03_schema.py

parquet 自带 schema(列名 + 类型),写入时可显式指定;
读回时类型精确还原(int32 还是 int32、时间还是时间)——这是它比 CSV 强的关键。
输出写到脚本旁的 data/ 目录(已被 .gitignore 忽略)。
"""
import datetime
import pathlib

import pyarrow as pa
import pyarrow.parquet as pq

DATA_DIR = pathlib.Path(__file__).parent / "data"


def demo_explicit_schema():
    """① 显式指定 schema(string / int32 / float64 / timestamp),精确控制类型"""
    schema = pa.schema([
        ("symbol", pa.string()),
        ("volume", pa.int32()),
        ("close", pa.float64()),
        ("ts", pa.timestamp("us")),
    ])
    table = pa.table({
        "symbol": ["AAPL", "MSFT"],
        "volume": [1000, 800],
        "close": [210.5, 505.2],
        "ts": [datetime.datetime(2026, 7, 1), datetime.datetime(2026, 7, 2)],
    }, schema=schema)
    path = DATA_DIR / "typed.parquet"
    pq.write_table(table, path)
    print("① 显式 schema 写入:")
    print("  文件:", path.name)
    print("  写入 schema:\n", schema)


def demo_inspect_schema():
    """② 读回后 schema 精确还原"""
    path = DATA_DIR / "typed.parquet"
    back = pq.read_table(path)
    print("② 读回的 schema:")
    print(back.schema)
    print("  volume 列类型:", back.schema.field("volume").type)
    print("  ts 列类型:", back.schema.field("ts").type)


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    demo_explicit_schema()
    demo_inspect_schema()
