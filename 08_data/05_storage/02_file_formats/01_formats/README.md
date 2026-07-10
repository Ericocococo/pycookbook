# 各格式读写配方

每个文件对应一种格式，独立可运行：`python <文件名>.py`

| 文件 | 格式 | 内容 |
|------|------|------|
| [01_csv.py](01_csv.py) | CSV | 写出/读回、分隔符、分块读、编码说明 |
| [02_json.py](02_json.py) | JSON | 标准库嵌套对象、DataFrame 多种 orient、JSON Lines、自定义 encoder |
| [03_excel.py](03_excel.py) | Excel | 单表、多 Sheet、读取参数、openpyxl 样式（加粗/背景色/列宽） |
| [04_parquet.py](04_parquet.py) | Parquet | 基本读写、列裁剪、谓词下推、压缩算法对比、分区存储 |
| [05_feather.py](05_feather.py) | Feather | 基本读写、列裁剪、与 CSV 速度对比、进程间中转场景、与内存速度对比 |
| [06_hdf5.py](06_hdf5.py) | HDF5 | h5py 数组 + 属性、切片读、层次化 Groups、pandas HDF5 |
| [07_pickle.py](07_pickle.py) | Pickle | 任意对象、protocol 对比、内存序列化、自定义类 `__getstate__` |
| [08_numpy.py](08_numpy.py) | NPY/NPZ | NPY/NPZ、memmap 内存映射、dtype 精度与体积、与 CSV 对比 |

## Feather vs 内存 vs Parquet

Feather 使用 Arrow 列式内存格式直接落盘，读取时 mmap 映射，操作系统把文件页当内存页，几乎没有解析开销，差的只是磁盘 IO 带宽。

```text
存储层          速度          容量         持久性        适合场景
-----------     ----------    ---------    ----------    ---------------------------
内存            ~10 GB/s      受 RAM 限制   进程退出消失   同一进程内反复使用
Feather         ~1-3 GB/s     受磁盘限制    跨进程/重启    临时中转、进程间传递、checkpoint
Parquet         ~0.5 GB/s     受磁盘限制    长期稳定       数据湖、长期存储、跨语言共享
```

**选型：**

```text
同一进程反复用              → 留在内存
跨进程传递 / 临时中转        → Feather（最接近内存速度的落盘方案）
数据超过 RAM / 长期存储      → Parquet
长时间计算怕中途崩溃         → Feather 定期 checkpoint
```

> Feather 是"有保质期的高速缓存"，Parquet 是"长期仓库"。
