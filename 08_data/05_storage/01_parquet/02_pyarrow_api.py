"""parquet 之 pyarrow 原生 API:不经过 pandas 直接读写 + 查看元数据

依赖:pyarrow
安装:pip install pyarrow
Python 3.12。运行: python 02_pyarrow_api.py

pandas 的 to_parquet/read_parquet 底层就是调 pyarrow；
直接用 pyarrow 能更细地控制 schema（数据结构定义）、逐行组读写、查看文件元数据。
输出写到脚本旁的 data/ 目录(已被 .gitignore 忽略)。
"""
import pathlib

import pyarrow as pa          # pa：pyarrow 的惯用别名
import pyarrow.parquet as pq  # pq：pyarrow.parquet 的惯用别名

DATA_DIR = pathlib.Path(__file__).parent / "data"


def demo01_build_table():
    """① 用 pyarrow 直接构造 Table（不经过 pandas）"""
    table = pa.table({
        "symbol": ["AAPL", "MSFT", "AAPL"],
        "close": [210.5, 505.2, 212.0],
    })
    print("① 构造 Table:")
    print("  行数:", table.num_rows)
    print("  列数:", table.num_columns)
    print("  列名:", table.column_names)
    print("  schema（列名+类型定义）:\n", table.schema)


def demo02_write_read():
    """② pq.write_table / pq.read_table 直接读写"""
    table = pa.table({
        "symbol": ["AAPL", "MSFT"],
        "close": [210.5, 505.2],
    })
    path = DATA_DIR / "native.parquet"
    pq.write_table(table, path, compression="snappy")
    back = pq.read_table(path)
    print("② 原生读写:")
    print("  写出文件:", path.name)
    print("  读回行数:", back.num_rows)
    # to_pydict：转成 Python 原生字典，键为列名，值为列表
    print("  转成 python dict:", back.to_pydict())


def demo03_metadata():
    """③ 查看 parquet 文件元数据（不读数据，只读文件头，极快）"""
    path = DATA_DIR / "native.parquet"
    pf   = pq.ParquetFile(path)
    meta = pf.metadata
    print("③ 文件元数据:")
    print("  行数:", meta.num_rows)
    print("  列数:", meta.num_columns)
    # row group（行组）：parquet 文件内部的分片单元，每个 write_table 产生一个行组
    print("  行组数:", meta.num_row_groups)
    print("  创建者:", meta.created_by)


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    demo01_build_table()
    demo02_write_read()
    demo03_metadata()