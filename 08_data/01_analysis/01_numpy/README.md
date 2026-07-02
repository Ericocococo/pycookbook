# numpy —— 多维数组(ndarray)与向量化数值计算的基础库

| 文件 | 内容 |
|------|------|
| `01_create.py` | 创建数组、dtype、形状属性 |
| `02_index_slice.py` | 索引 / 切片 / 布尔索引 / 花式索引 / 视图 vs 拷贝 |
| `03_reshape_axis.py` | reshape / 转置 / 拼接 / 拆分,理解 axis(轴) |
| `04_ufunc_broadcast.py` | 逐元素运算(ufunc)与广播(broadcasting)规则 |
| `05_aggregation.py` | sum/mean/std/argmax/cumsum 等沿轴聚合 |
| `06_random.py` | 随机数:重点 np.random.default_rng(新式 Generator) |
| `07_linalg.py` | 线性代数:@ / inv / solve / det / eig / svd / norm |
| `08_advanced.py` | 进阶:einsum / newaxis / structured array / 滑窗 / where |


## 适用

- 大批量数值计算(比纯 Python list 快 10~100 倍,内存紧凑)
- 矩阵/线性代数、统计、信号、图像等一切"整块数据"运算
- pandas / scipy / sklearn / pytorch 的底层数据结构

## 不适用

- 需要频繁增删单个元素、异构对象 → 用 list / dict
- 带标签的表格数据(列名、索引对齐) → 用 pandas.DataFrame
- 超大规模超出内存 → 用 dask / 内存映射 np.memmap

## 核心速查

```python
import numpy as np
a = np.array([[1, 2, 3], [4, 5, 6]])   # 从 list 建二维数组
a.shape, a.dtype, a.ndim               # (2,3)  int64  2
a[a > 3]                               # 布尔索引 -> array([4,5,6])
a.sum(axis=0)                          # 沿"行方向"求和 -> [5,7,9]
a @ a.T                                # 矩阵乘法
rng = np.random.default_rng(42)        # 新式随机数生成器(可复现)
rng.normal(0, 1, size=(2, 3))          # 标准正态随机

```

## 常用命令

```bash
pip install "numpy>=2.0"
python -c "import numpy; print(numpy.__version__)"
```
