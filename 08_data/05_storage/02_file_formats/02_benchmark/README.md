# 性能基准

| 文件 | 内容 |
|------|------|
| [01_benchmark.py](01_benchmark.py) | 10 万行 × 5 列，各格式写速 / 读速 / 文件大小 / 列裁剪横向对比 |

运行：`python 01_benchmark.py`

## 依赖安装

```bash
pip install pandas pyarrow openpyxl   # 基础（CSV/JSON/Excel/Parquet/Feather）
pip install h5py                      # HDF5 支持（缺少则该行显示"跳过"）
```

缺少某个依赖时，对应格式会跳过并提示安装命令，不影响其他格式的测试：

```text
HDF5(h5py+gzip)    跳过（未安装依赖：pip install h5py）
```
