"""numpy —— 进阶技巧:where/select、newaxis、einsum、structured array、滑窗、向量化

第三方库。Python 3.12 / numpy 2.x。运行: python 08_advanced.py

这些是"写出快又短的 numpy 代码"的常用高级手法。
"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def demo01_where_select():
    """① 条件选择:where(三元) / select(多分支) / 条件赋值"""
    a = np.array([-2, -1, 0, 1, 2])
    print("① where / select:")
    # where(cond, x, y):cond 为真取 x,否则取 y(逐元素)
    print("  where(a>0, a, 0) 负数归零:", np.where(a > 0, a, 0))
    print("  where 只传 cond 返回下标:", np.where(a > 0)[0])
    # select:多条件分支,类似 if/elif/else
    cond = [a < 0, a == 0, a > 0]
    choice = [-1, 0, 1]
    print("  select 符号函数:", np.select(cond, choice))


def demo02_newaxis():
    """② np.newaxis:增加一个长度为 1 的轴,专为广播服务"""
    a = np.array([1, 2, 3])               # shape (3,)
    col = a[:, np.newaxis]                 # (3,1) 列向量
    row = a[np.newaxis, :]                 # (1,3) 行向量
    print("② newaxis 造广播:")
    print("  列向量 shape:", col.shape)
    print("  行向量 shape:", row.shape)
    # (3,1) + (1,3) -> (3,3) 外积式相加/相乘
    print("  外积表(col*row):\n", col * row)


def demo03_einsum():
    """③ einsum:爱因斯坦求和,一行表达复杂的乘加(点积/矩阵乘/迹/转置)"""
    a = np.arange(1, 5)                    # [1,2,3,4]
    b = np.arange(5, 9)                    # [5,6,7,8]
    M = np.arange(1, 7).reshape(2, 3)
    N = np.arange(1, 7).reshape(3, 2)
    print("③ einsum:")
    print("  向量点积 'i,i->':", np.einsum("i,i->", a, b))
    print("  矩阵乘 'ij,jk->ik':\n", np.einsum("ij,jk->ik", M, N))
    print("  转置 'ij->ji':\n", np.einsum("ij->ji", M))
    sq = np.arange(1, 5).reshape(2, 2)
    print("  取迹 'ii->':", np.einsum("ii->", sq), "(对角线和)")


def demo04_structured():
    """④ 结构化数组(structured array):一个数组存多字段(类似表的一行)"""
    dt = np.dtype([("name", "U10"), ("age", "i4"), ("score", "f4")])
    people = np.array([("Tom", 20, 88.5), ("Amy", 22, 95.0)], dtype=dt)
    print("④ 结构化数组:")
    print("  全部:", people)
    print("  按字段取 name:", people["name"])
    print("  按字段取 age:", people["age"])
    print("  按 score 排序后 name:", np.sort(people, order="score")["name"])


def demo05_sliding_window():
    """⑤ 滑动窗口:sliding_window_view 零拷贝造滑窗(求移动平均等)"""
    a = np.arange(1, 8)                    # [1..7]
    w = sliding_window_view(a, 3)          # 窗口大小 3 -> shape (5,3)
    print("⑤ 滑动窗口:")
    print("  原:", a)
    print("  窗口视图:\n", w)
    print("  移动平均(窗口3):", w.mean(axis=1))


def demo06_vectorize_apply():
    """⑥ 向量化替代循环:直接对整块运算(演示为何别用 Python for)"""
    x = np.linspace(0, 1, 5)
    print("⑥ 向量化:")
    # 一次算完,无需 for。np.vectorize 只是语法糖(不加速),真正提速靠原生 ufunc
    print("  整块运算 x^2+1:", x ** 2 + 1)
    f = np.vectorize(lambda v: v * 10 if v > 0.5 else v)  # 仅当逻辑难向量化时用
    print("  vectorize 分段:", np.round(f(x), 3))


if __name__ == "__main__":
    demo01_where_select()
    print()
    demo02_newaxis()
    print()
    demo03_einsum()
    print()
    demo04_structured()
    print()
    demo05_sliding_window()
    print()
    demo06_vectorize_apply()
