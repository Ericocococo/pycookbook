"""numpy —— 线性代数:@ / dot / inv / solve / det / eig / svd / norm

第三方库。Python 3.12 / numpy 2.x。运行: python 07_linalg.py

注意:* 是逐元素乘,矩阵乘法用 @ 运算符(或 np.matmul / np.dot)。
"""
import numpy as np


def demo01_matmul():
    """① 矩阵乘法:@ vs 逐元素 *"""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    print("① 矩阵乘法:")
    print("  a * b 逐元素:\n", a * b)
    print("  a @ b 矩阵乘:\n", a @ b)
    print("  np.dot(a,b):\n", np.dot(a, b), "(等价 @)")
    v = np.array([1, 1])
    print("  矩阵 @ 向量:", a @ v)


def demo02_basic():
    """② 转置 / 迹 / 行列式 / 秩"""
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    print("② 基础量:")
    print("  转置 a.T:\n", a.T)
    print("  trace 迹(对角线和):", np.trace(a))
    print("  det 行列式:", np.linalg.det(a))
    print("  rank 秩:", np.linalg.matrix_rank(a))


def demo03_solve_inv():
    """③ 解线性方程组 Ax=b:优先 solve,别显式求逆"""
    A = np.array([[3.0, 1.0], [1.0, 2.0]])
    b = np.array([9.0, 8.0])
    x = np.linalg.solve(A, b)             # 解 Ax=b,数值更稳、更快
    print("③ 解方程 Ax=b:")
    print("  solve 解 x:", x)
    print("  验证 A@x:", A @ x, "(应等于 b)")
    inv = np.linalg.inv(A)                # 逆矩阵(除非确实需要,否则别用它解方程)
    print("  inv 逆矩阵:\n", inv)
    print("  A@inv 应为单位阵:\n", np.round(A @ inv, 10))


def demo04_eig_svd():
    """④ 特征值分解 与 奇异值分解(SVD)"""
    a = np.array([[2.0, 0.0], [0.0, 3.0]])
    vals, vecs = np.linalg.eig(a)         # 特征值 + 特征向量
    print("④ 分解:")
    print("  eig 特征值:", vals)
    print("  eig 特征向量:\n", vecs)
    m = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    U, S, Vt = np.linalg.svd(m)           # SVD:降维/压缩/伪逆的基础
    print("  svd 奇异值:", S)
    print("  U shape:", U.shape, "Vt shape:", Vt.shape)


def demo05_norm():
    """⑤ 范数(norm):向量长度 / 矩阵范数"""
    v = np.array([3.0, 4.0])
    print("⑤ 范数:")
    print("  L2 范数(欧氏长度):", np.linalg.norm(v), "= sqrt(3^2+4^2)=5")
    print("  L1 范数(绝对值和):", np.linalg.norm(v, 1))
    print("  inf 范数(最大绝对值):", np.linalg.norm(v, np.inf))
    m = np.array([[1.0, 2.0], [3.0, 4.0]])
    print("  矩阵 Frobenius 范数:", round(float(np.linalg.norm(m)), 4))


if __name__ == "__main__":
    demo01_matmul()
    print()
    demo02_basic()
    print()
    demo03_solve_inv()
    print()
    demo04_eig_svd()
    print()
    demo05_norm()
