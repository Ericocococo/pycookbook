"""
数据分析 —— 数值计算与表格分析库

  01_numpy/    多维数组 ndarray、向量化计算、随机数、线性代数(数据分析的基石)

适用
  · 数值/矩阵运算、统计、随机模拟
  · pandas / scipy / sklearn 的底层数据结构

不适用
  · 带标签的表格数据(列名、索引对齐) → pandas.DataFrame(后续 02_pandas)
  · 图形展示 → 见 08_data/02_visualization

核心速查
  import numpy as np
  a = np.array([[1, 2, 3], [4, 5, 6]])
  a.sum(axis=0)                       # 沿行方向求和
  rng = np.random.default_rng(42)     # 新式随机数生成器
  rng.normal(0, 1, size=(2, 3))
"""
