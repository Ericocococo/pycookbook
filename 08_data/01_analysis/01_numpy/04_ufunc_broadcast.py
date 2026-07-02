"""numpy —— 逐元素运算(ufunc)与广播(broadcasting)规则

第三方库。Python 3.12 / numpy 2.x。运行: python 04_ufunc_broadcast.py

ufunc = universal function,对数组每个元素逐一运算,底层 C 循环,无需写 for。
广播 = 形状不同的数组按规则自动"扩展"到相同形状再运算。
"""
import numpy as np


def demo01_elementwise():
    """① 逐元素算术:整块运算,不用写循环"""
    a = np.array([1, 2, 3, 4])
    b = np.array([10, 20, 30, 40])
    print("① 逐元素运算:")
    print("  a + b:", a + b)
    print("  a * b:", a * b, "(对应元素相乘,不是矩阵乘)")
    print("  b / a:", b / a)
    print("  a ** 2:", a ** 2)
    print("  a > 2:", a > 2, "(逐元素比较得布尔数组)")


def demo02_ufunc():
    """② 常用数学 ufunc"""
    a = np.array([1.0, 4.0, 9.0])
    print("② 数学函数(逐元素):")
    print("  sqrt:", np.sqrt(a))
    print("  exp:", np.exp(np.array([0, 1])))
    print("  log:", np.log(np.array([1, np.e])))
    print("  sin:", np.round(np.sin(np.array([0, np.pi / 2])), 4))
    print("  clip(裁剪到[2,8]):", np.clip(np.array([1, 5, 10]), 2, 8))


def demo03_scalar_broadcast():
    """③ 标量广播:标量自动扩展到整个数组"""
    a = np.arange(6).reshape(2, 3)
    print("③ 标量广播:")
    print("  a:\n", a)
    print("  a + 100:\n", a + 100, "(100 广播到每个元素)")
    print("  a * 2:\n", a * 2)


def demo04_broadcast_rule():
    """④ 广播规则:从末轴对齐,维度相等或其一为 1 才能广播"""
    a = np.arange(6).reshape(2, 3)      # shape (2,3)
    row = np.array([10, 20, 30])         # shape (3,)   -> 广播成每一行都加
    col = np.array([[100], [200]])       # shape (2,1)  -> 广播成每一列都加
    print("④ 广播规则:")
    print("  (2,3) + (3,):\n", a + row, "行向量加到每一行")
    print("  (2,3) + (2,1):\n", a + col, "列向量加到每一列")
    # (3,1) + (1,4) -> (3,4):外积式广播
    x = np.array([[1], [2], [3]])        # (3,1)
    y = np.array([[10, 20, 30, 40]])     # (1,4)
    print("  (3,1)+(1,4) -> (3,4):\n", x + y)


def demo05_broadcast_fail():
    """⑤ 广播失败示例:末轴既不相等也不为 1"""
    a = np.ones((2, 3))
    b = np.ones((2, 2))
    print("⑤ 广播失败:")
    try:
        _ = a + b                         # (2,3) 与 (2,2) 末轴 3≠2 且都不为 1
    except ValueError as e:
        print("  (2,3)+(2,2) 报错:", e)


if __name__ == "__main__":
    demo01_elementwise()
    print()
    demo02_ufunc()
    print()
    demo03_scalar_broadcast()
    print()
    demo04_broadcast_rule()
    print()
    demo05_broadcast_fail()
