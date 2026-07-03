"""sys —— 解释器内部机制

标准库。Python 3.12。运行: python 05_internals.py
"""
import sys


def demo01_refcount():
    """① sys.getrefcount：引用计数（注意：调用时额外 +1）"""
    print("① sys.getrefcount —— 引用计数")
    print("  注意：getrefcount(obj) 调用本身会持有一个临时引用，")
    print("  所以返回值总比你实际能数到的引用多 1。")
    print()

    a = [1, 2, 3]
    rc1 = sys.getrefcount(a)
    print("  只有 a 一个引用时 refcount:", rc1,
          "（预期 2 = 变量 a + getrefcount 调用的临时引用）")

    b = a                              # b 也指向同一个列表
    rc2 = sys.getrefcount(a)
    print("  b = a 后          refcount:", rc2, "（预期 3 = a + b + 临时引用）")

    del b                              # 删除 b 引用
    rc3 = sys.getrefcount(a)
    print("  del b 后          refcount:", rc3, "（回到", rc1, "）")

    container = []
    container.append(a)               # 列表内部持有一个引用
    rc4 = sys.getrefcount(a)
    print("  a 进列表后        refcount:", rc4, "（再 +1 = 列表内引用）")


def demo02_getsizeof():
    """② sys.getsizeof：各类型对象大小（浅层，不递归子对象）"""
    print("② sys.getsizeof —— 对象字节大小（浅层）")
    objects = [
        ("int 0",          0),
        ("int 1000",       1000),
        ("int 10**100",    10**100),         # 大整数（任意精度）
        ("str ''",         ""),
        ("str 'hello'",    "hello"),
        ("str '中文'",     "中文"),
        ("bytes b''",      b""),
        ("bytes b'hello'", b"hello"),
        ("list []",        []),
        ("list [1,2,3]",   [1, 2, 3]),
        ("dict {}",        {}),
        ("dict {'a':1}",   {"a": 1}),
        ("tuple ()",       ()),
        ("tuple (1,2,3)",  (1, 2, 3)),
        ("set()",          set()),
        ("bool True",      True),
        ("None",           None),
    ]
    for label, obj in objects:
        print(f"  {label:<20}: {sys.getsizeof(obj):>6} 字节")

    print()
    print("  注意: list/dict/set 返回的是容器壳本身的大小（指针数组+元数据），")
    print("  内部每个元素对象的大小不计入其中（浅层计算）。")
    print("  若要深层统计，需递归调用或使用 pympler / objgraph 等三方工具。")


def demo03_recursion():
    """③ sys.getrecursionlimit / sys.setrecursionlimit：递归深度限制"""
    print("③ 递归深度限制")
    original_limit = sys.getrecursionlimit()
    print("  默认递归深度限制:", original_limit)  # 通常 1000

    # 临时降低限制，方便演示 RecursionError（避免真正打爆调用栈）
    sys.setrecursionlimit(60)
    print("  临时设为 60")

    def recurse(n: int) -> int:
        """无穷递归，用于触发 RecursionError"""
        return recurse(n + 1)

    try:
        recurse(0)
    except RecursionError as e:
        print("  捕获 RecursionError:", type(e).__name__)

    # 必须恢复，否则后续代码受影响
    sys.setrecursionlimit(original_limit)
    print("  已恢复默认限制:", sys.getrecursionlimit())
    print()
    print("  实践建议:")
    print("    不要轻易大幅提高递归限制（会增大栈溢出风险）")
    print("    深递归场景改用迭代（循环 + 显式栈）或 sys.setrecursionlimit 适度调大")


def demo04_intern():
    """④ sys.intern：字符串驻留，is 比较 vs == 比较"""
    print("④ sys.intern —— 字符串驻留")

    # CPython 会自动驻留：纯字母/数字/下划线的短字符串、编译期确定的常量
    a = "hello"
    b = "hello"
    print("  'hello' is 'hello':", a is b,
          "（CPython 编译期常量折叠，通常自动驻留，但不保证）")

    # 含空格的字符串不会被自动驻留
    s1 = "hello world"
    s2 = "hello world"
    print("  'hello world' 自动 is:", s1 is s2,
          "（含空格，CPython 可能不自动驻留）")

    # 手动驻留，保证 is 为 True
    i1 = sys.intern("hello world")
    i2 = sys.intern("hello world")
    print("  手动 intern 后 is:", i1 is i2, "（保证 True）")
    print("  手动 intern 后 ==:", i1 == i2, "（值相同）")

    print()
    print("  适用场景:")
    print("    大量重复字符串（CSV 列名、状态码字符串）驻留后节省内存")
    print("    dict/set 查找时，驻留字符串的 is 比较（O(1)）比 == 更快")
    print("    注意: Python 3.12+ 的 dict key 查找已高度优化，普通代码无需手动 intern")


def demo05_is_finalizing():
    """⑤ sys.is_finalizing：解释器是否正在关闭"""
    print("⑤ sys.is_finalizing —— 检测解释器关闭阶段")
    print("  当前调用结果:", sys.is_finalizing(), "（正常运行中，预期 False）")
    print()

    class ResourceWatcher:
        """演示在 __del__ 里安全使用 sys 的方式"""

        def __del__(self):
            # 解释器关闭时，全局变量可能已被置为 None
            # 必须先判断 sys 是否还存在
            if sys is None:
                return
            if sys.is_finalizing():
                # 正在关闭：不要访问其他模块（可能已被回收）
                return
            # 正常析构：可以安全访问其他资源
            pass  # 此处可放清理代码

    w = ResourceWatcher()
    del w   # 触发 __del__，此时 is_finalizing() 为 False，安全
    print("  ResourceWatcher 正常析构完毕")
    print()
    print("  注意事项:")
    print("    解释器退出时（atexit 之后），全局变量逐一被设为 None")
    print("    此时 __del__ 可能被调用，sys 本身也可能为 None")
    print("    安全写法: if sys and not sys.is_finalizing(): ...")


def demo06_exc_info():
    """⑥ sys.exc_info：在 except 块里获取当前异常三元组"""
    print("⑥ sys.exc_info —— 当前异常信息")

    # except 块外调用返回三个 None
    outside = sys.exc_info()
    print("  except 块外调用:", outside)

    print()
    try:
        result = 1 / 0
    except ZeroDivisionError:
        exc_type, exc_value, exc_tb = sys.exc_info()
        print("  在 except ZeroDivisionError 内:")
        print("    exc_type:", exc_type)
        print("    exc_value:", exc_value)
        print("    exc_tb:", exc_tb, type(exc_tb))

    # 离开 except 块后，exc_info 重置
    after = sys.exc_info()
    print("  离开 except 后:", after)

    print()
    # 嵌套异常时 exc_info 的变化
    try:
        try:
            raise ValueError("内层错误")
        except ValueError:
            inner_info = sys.exc_info()
            print("  内层 except 中 exc_info:", inner_info[0], inner_info[1])
            raise RuntimeError("外层错误")
    except RuntimeError:
        outer_info = sys.exc_info()
        print("  外层 except 中 exc_info:", outer_info[0], outer_info[1])

    print()
    print("  Python 3.11+ 推荐: except Exception as e: 直接使用 e")
    print("  sys.exc_info() 主要用于需要三元组参数的旧式 API，如 logging.exception()")


if __name__ == "__main__":
    demo01_refcount()
    print()
    demo02_getsizeof()
    print()
    demo03_recursion()
    print()
    demo04_intern()
    print()
    demo05_is_finalizing()
    print()
    demo06_exc_info()
