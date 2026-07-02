"""numpy —— 索引 / 切片 / 布尔索引 / 花式索引 / 视图 vs 拷贝

第三方库。Python 3.12 / numpy 2.x。运行: python 02_index_slice.py

关键区别:切片得到的是"视图"(共享内存),布尔/花式索引得到的是"拷贝"(独立内存)。
"""
import numpy as np


def demo01_basic_index():
    """① 基础索引:多维用逗号分隔各轴"""
    a = np.arange(1, 13).reshape(3, 4)   # 3 行 4 列
    print("① 原数组:\n", a)
    print("  a[0, 0]:", a[0, 0], "第 0 行第 0 列")
    print("  a[1, 2]:", a[1, 2], "第 1 行第 2 列")
    print("  a[-1, -1]:", a[-1, -1], "最后一行最后一列")
    print("  a[1]:", a[1], "取整行(第 1 行)")


def demo02_slice():
    """② 切片:start:stop:step,可跨轴组合"""
    a = np.arange(1, 13).reshape(3, 4)
    print("② 切片:")
    print("  a[0:2]:\n", a[0:2], "前两行")
    print("  a[:, 1]:", a[:, 1], "第 1 列(所有行)")
    print("  a[:, 1:3]:\n", a[:, 1:3], "第 1~2 列")
    print("  a[::2, ::2]:\n", a[::2, ::2], "行列都隔一个取")


def demo03_bool_index():
    """③ 布尔索引:用条件掩码(mask)筛选,返回一维拷贝"""
    a = np.arange(1, 13).reshape(3, 4)
    mask = a % 2 == 0                     # 生成布尔数组
    print("③ 布尔索引:")
    print("  mask 偶数掩码:\n", mask)
    print("  a[mask]:", a[mask], "取出所有偶数(拉平成一维)")
    print("  a[a > 6]:", a[a > 6], "大于 6 的元素")
    a2 = a.copy()
    a2[a2 > 6] = 0                        # 布尔索引赋值:批量修改
    print("  >6 置 0:\n", a2)


def demo04_fancy_index():
    """④ 花式索引:用整数数组指定要取的下标(可乱序、可重复)"""
    a = np.arange(10, 20)
    idx = [0, 3, 3, 5]
    print("④ 花式索引:")
    print("  a:", a)
    print("  a[[0,3,3,5]]:", a[idx], "按下标取,可重复")
    b = np.arange(1, 13).reshape(3, 4)
    # 二维花式:行下标与列下标配对 -> 取 (0,0) 和 (2,3)
    print("  b[[0,2],[0,3]]:", b[[0, 2], [0, 3]], "取(0,0)与(2,3)两点")


def demo05_view_vs_copy():
    """⑤ 视图 vs 拷贝:切片共享内存,改视图会改原数组"""
    a = np.arange(6)
    view = a[1:4]        # 切片 -> 视图(共享底层内存)
    copy = a[1:4].copy() # 显式拷贝 -> 独立内存
    view[0] = 999        # 改视图
    print("⑤ 视图 vs 拷贝:")
    print("  改 view 后原数组:", a, "(原数组被改!)")
    print("  view.base is a:", view.base is a, "视图的 base 指向原数组")
    print("  copy.base is None:", copy.base is None, "拷贝独立")
    print("  提示: 布尔/花式索引返回拷贝,切片返回视图")


if __name__ == "__main__":
    demo01_basic_index()
    print()
    demo02_slice()
    print()
    demo03_bool_index()
    print()
    demo04_fancy_index()
    print()
    demo05_view_vs_copy()
