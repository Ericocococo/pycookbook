"""parquet —— 列式存储格式，运行此文件查看目录导航"""

print("""
parquet —— 列式存储格式

  01_basic.py          pandas 读写、列裁剪、压缩对比、按列分区
  02_pyarrow_api.py    pyarrow 原生 API 直接读写、查看文件元数据
  03_schema.py         显式指定 schema 与列类型，读回精确还原
  04_filters_append.py 谓词下推过滤（减少 IO）与增量追加写
""")
