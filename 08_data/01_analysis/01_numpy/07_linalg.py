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
    """② 转置 / 迹 / 行列式 / 秩

    术语解释:
      迹 trace      方阵主对角线元素之和
      行列式 det    方阵对应的一个标量,几何上是线性变换的"体积缩放因子";
                    det=0 表示矩阵不可逆(奇异矩阵)
      秩 rank       矩阵中线性无关的行(或列)的最大数目,反映"有效维度"
    """
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
    """④ 特征值分解 与 奇异值分解(SVD)

    术语解释:
      特征值 λ / 特征向量 v   满足 A·v = λ·v 的方向 v 与倍数 λ:
                             矩阵作用在 v 上只把它拉伸 λ 倍而不改变方向
      奇异值分解 SVD          把任意矩阵拆成 U·S·V^T 三部分(奇异值在 S 对角线);
                             是降维(PCA)、数据压缩、求伪逆的数学基础
    """
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
    """⑤ 范数(norm):衡量向量/矩阵"大小"的标量

    常见范数:
      L2 范数    各元素平方和再开根号 = 欧氏几何长度(最常用,默认)
      L1 范数    各元素绝对值之和(又叫曼哈顿/出租车距离)
      inf 范数   所有元素绝对值里的最大值
      Frobenius  矩阵版的 L2:全部元素平方和再开根号
    """
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
