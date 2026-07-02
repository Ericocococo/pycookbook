"""numpy —— 创建数组、dtype(数据类型)、形状属性

第三方库,需 pip install numpy。Python 3.12 / numpy 2.x。运行: python 01_create.py
"""
import numpy as np


def demo01_from_data():
    """① 从已有 Python 数据创建"""
    a = np.array([1, 2, 3])                 # 一维:从 list
    b = np.array([[1, 2], [3, 4]])          # 二维:从嵌套 list
    c = np.array((1.0, 2.0, 3.0))           # 从 tuple
    print("① 从数据创建:")
    print("  一维:", a, type(a))
    print("  二维:\n", b)
    print("  浮点:", c, c.dtype)            # dtype 由数据自动推断为 float64


def demo02_builtin():
    """② 内置构造函数:按形状快速生成"""
    print("② 构造函数(shape 参数决定形状):")
    print("  zeros:", np.zeros(3), "全 0")
    print("  ones:\n", np.ones((2, 3)), "全 1")
    print("  full:", np.full(4, 7), "填充指定值")
    print("  eye:\n", np.eye(3), "单位矩阵(对角为 1)")
    print("  arange:", np.arange(0, 10, 2), "类似 range,步长 2")
    print("  linspace:", np.linspace(0, 1, 5), "0~1 均匀取 5 个点(含端点)")
    print("  empty:", np.empty(3).shape, "只分配内存不初始化(值是垃圾数据)")


def demo03_dtype():
    """③ dtype:显式指定 / 转换类型"""
    a = np.array([1, 2, 3], dtype=np.float32)   # 创建时指定
    b = a.astype(np.int64)                       # astype 转换类型(返回新数组)
    c = np.array([1, 2, 3], dtype="uint8")       # 也可用字符串名
    print("③ dtype 数据类型:")
    print("  float32:", a, a.dtype, a.itemsize, "字节/元素")
    print("  astype->int64:", b, b.dtype)
    print("  uint8:", c, c.dtype, "(0~255)")
    # 溢出回绕:uint8 只能存 0~255。注意 numpy 2.x 里 np.array([256], dtype='uint8')
    # 会直接抛 OverflowError;要看回绕效果,须先建大 dtype 再 astype 转小类型。
    over = np.array([256, 257, 300], dtype="int64").astype("uint8")
    print("  uint8 溢出回绕:", over, "(256->0, 257->1, 300->44,即对 256 取模)")


def demo04_attributes():
    """④ 形状与内存属性"""
    a = np.arange(24).reshape(2, 3, 4)   # 三维数组
    print("④ 数组属性:")
    print("  .shape:", a.shape, type(a.shape), "各维长度")
    print("  .ndim:", a.ndim, "维度数(轴的个数)")
    print("  .size:", a.size, "元素总数 = 2*3*4")
    print("  .dtype:", a.dtype, "元素类型")
    print("  .itemsize:", a.itemsize, "单元素字节数")
    print("  .nbytes:", a.nbytes, "总字节数 = size*itemsize")
    print("  .T.shape:", a.T.shape, "转置后形状(轴逆序)")


if __name__ == "__main__":
    demo01_from_data()
    print()
    demo02_builtin()
    print()
    demo03_dtype()
    print()
    demo04_attributes()
