"""numpy —— reshape / 转置 / 拼接 / 拆分,理解 axis(轴)

第三方库。Python 3.12 / numpy 2.x。运行: python 03_reshape_axis.py

axis(轴)口诀:二维数组 axis=0 是"沿行往下"(压缩行,得每列结果),
             axis=1 是"沿列往右"(压缩列,得每行结果)。
"""
import numpy as np


def demo01_reshape():
    """① reshape 变形:元素总数不变,-1 表示自动推断该维"""
    a = np.arange(12)
    print("① reshape:")
    print("  原:", a)
    print("  reshape(3,4):\n", a.reshape(3, 4))
    print("  reshape(2,-1):\n", a.reshape(2, -1), "-1 自动算成 6")
    print("  reshape(2,2,3) 三维:\n", a.reshape(2, 2, 3))


def demo02_flatten():
    """② 拉平:ravel(视图,省内存) vs flatten(拷贝)"""
    a = np.arange(6).reshape(2, 3)
    print("② 拉平:")
    print("  ravel:", a.ravel(), "(尽量返回视图)")
    print("  flatten:", a.flatten(), "(总是拷贝)")
    print("  ravel(order='F'):", a.ravel(order="F"), "按列优先(Fortran 顺序)")


def demo03_transpose():
    """③ 转置与轴交换"""
    a = np.arange(6).reshape(2, 3)
    print("③ 转置:")
    print("  原 shape:", a.shape, "\n", a)
    print("  a.T shape:", a.T.shape, "\n", a.T)
    b = np.arange(24).reshape(2, 3, 4)
    # transpose 指定新的轴顺序:把 (0,1,2) 重排为 (1,0,2)
    print("  三维 transpose(1,0,2) shape:", b.transpose(1, 0, 2).shape)
    print("  swapaxes(0,2) shape:", b.swapaxes(0, 2).shape, "交换两个轴")


def demo04_concat_stack():
    """④ 拼接:concatenate / vstack / hstack / stack"""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    print("④ 拼接:")
    print("  concat axis=0(竖着接):\n", np.concatenate([a, b], axis=0))
    print("  concat axis=1(横着接):\n", np.concatenate([a, b], axis=1))
    print("  vstack:\n", np.vstack([a, b]), "等价 axis=0")
    print("  hstack:\n", np.hstack([a, b]), "等价 axis=1")
    print("  stack 新增轴 shape:", np.stack([a, b]).shape, "(2,2,2) 堆成三维")


def demo05_split():
    """⑤ 拆分:split / vsplit / hsplit"""
    a = np.arange(12).reshape(3, 4)
    print("⑤ 拆分:")
    parts = np.split(a, 3, axis=0)        # 沿 axis=0 均分 3 份
    print("  split 成 3 份,每份:\n", parts[0], "\n ...")
    left, right = np.hsplit(a, 2)          # 水平均分 2 份
    print("  hsplit 左半:\n", left)
    print("  hsplit 右半:\n", right)


def demo06_axis_meaning():
    """⑥ axis 到底压缩哪个方向(最易错点)"""
    a = np.array([[1, 2, 3], [4, 5, 6]])
    print("⑥ axis 语义(以 sum 为例):")
    print("  原:\n", a)
    print("  sum(axis=0):", a.sum(axis=0), "沿行往下,消掉行 -> 每列的和")
    print("  sum(axis=1):", a.sum(axis=1), "沿列往右,消掉列 -> 每行的和")
    print("  sum():", a.sum(), "不指定 -> 全部求和")


if __name__ == "__main__":
    demo01_reshape()
    print()
    demo02_flatten()
    print()
    demo03_transpose()
    print()
    demo04_concat_stack()
    print()
    demo05_split()
    print()
    demo06_axis_meaning()
