"""numpy —— 聚合与统计:sum/mean/std/argmax/cumsum 沿轴计算

第三方库。Python 3.12 / numpy 2.x。运行: python 05_aggregation.py
"""
import numpy as np


def demo01_basic_reduce():
    """① 基础聚合:整体 vs 沿轴"""
    a = np.array([[1, 2, 3], [4, 5, 6]])
    print("① 基础聚合:")
    print("  原:\n", a)
    print("  sum():", a.sum(), "全部")
    print("  sum(axis=0):", a.sum(axis=0), "每列(沿行往下)")
    print("  sum(axis=1):", a.sum(axis=1), "每行(沿列往右)")
    print("  min/max:", a.min(), a.max())
    print("  prod:", a.prod(), "全部连乘")


def demo02_stats():
    """② 统计量:均值/方差/标准差/中位数/分位数

    术语解释:
      方差 var         各数据与均值之差的平方的平均,衡量数据"离散程度"
      标准差 std       方差开根号,与原数据同量纲(单位),越大越分散
      中位数 median    排序后正中间的数,比均值更抗极端值干扰
      分位数 percentile  如 75 分位 = 有 75% 的数据 ≤ 该值
      极差 ptp         peak-to-peak,最大值减最小值
    """
    a = np.array([2, 4, 4, 4, 5, 5, 7, 9], dtype=float)
    print("② 统计量:")
    print("  mean 均值:", a.mean())
    print("  std 标准差:", a.std())
    print("  var 方差:", a.var())
    print("  median 中位数:", np.median(a))
    print("  percentile 75分位:", np.percentile(a, 75))
    print("  ptp 极差(max-min):", np.ptp(a), "(numpy 2.x 移除了 ndarray.ptp,用 np.ptp)")


def demo03_argfunc():
    """③ arg 系列:返回下标而非值"""
    a = np.array([[3, 1, 2], [9, 8, 7]])
    print("③ arg 系列(返回位置):")
    print("  argmax():", a.argmax(), "最大值的展平下标")
    print("  argmax(axis=1):", a.argmax(axis=1), "每行最大值列下标")
    print("  argmin(axis=0):", a.argmin(axis=0), "每列最小值行下标")
    print("  argsort:", np.array([3, 1, 2]).argsort(), "排序后的原下标")


def demo04_cumulative():
    """④ 累积运算:cumsum / cumprod(结果与输入等长)"""
    a = np.array([1, 2, 3, 4])
    print("④ 累积:")
    print("  cumsum 累加:", a.cumsum(), "[1,1+2,1+2+3,...]")
    print("  cumprod 累乘:", a.cumprod())
    m = np.array([[1, 2], [3, 4]])
    print("  cumsum(axis=0):\n", m.cumsum(axis=0), "沿行累加")


def demo05_keepdims_nan():
    """⑤ keepdims 保持维度(便于广播) + nan 安全聚合"""
    a = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
    s = a.sum(axis=1, keepdims=True)      # 保持二维 (2,1) 而非 (2,)
    print("⑤ keepdims 与 nan:")
    print("  sum(axis=1,keepdims):\n", s, "shape", s.shape)
    print("  归一化 a/s(靠广播):\n", np.round(a / s, 3))
    b = np.array([1, 2, np.nan, 4])
    print("  含 nan 的 sum:", b.sum(), "(nan 会传染)")
    print("  nansum(忽略 nan):", np.nansum(b))
    print("  nanmean:", np.nanmean(b))


if __name__ == "__main__":
    demo01_basic_reduce()
    print()
    demo02_stats()
    print()
    demo03_argfunc()
    print()
    demo04_cumulative()
    print()
    demo05_keepdims_nan()
