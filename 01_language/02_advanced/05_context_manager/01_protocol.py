"""上下文管理器协议 —— __enter__ / __exit__

Python 3.12。
运行: python 01_protocol.py

with 语句保证"进入时初始化，离开时清理"——无论是否抛异常。
实现协议只需两个方法：
  __enter__(self)                   → 返回值绑定到 as 变量
  __exit__(self, exc_type, exc_val, tb) → 返回 True 抑制异常，False 让异常传播

演示：
  ① with 语句等价展开（手动调用 __enter__ / __exit__）
  ② 最简上下文管理器：文件包装器
  ③ __exit__ 的三个参数：处理异常
  ④ 抑制指定异常（return True）
  ⑤ 嵌套 with 与多变量 with
  ⑥ 实际场景：数据库事务管理器
"""


# ---------------------------------------------------------------------------
# ① with 等价展开
# ---------------------------------------------------------------------------

def demo01_equivalent():
    """① with 语句的等价 try/finally 展开"""
    print("① with 等价展开")

    # with open("README.md") as f: ... 等价于：
    # manager = open("README.md")
    # f = manager.__enter__()
    # try:
    #     ...
    # except:
    #     if not manager.__exit__(*sys.exc_info()):
    #         raise
    # else:
    #     manager.__exit__(None, None, None)

    # 用列表演示（list 没有上下文管理器协议，只是说明调用顺序）
    class TracedCM:
        def __enter__(self):
            print("  __enter__ 被调用")
            return "资源对象"

        def __exit__(self, exc_type, exc_val, tb):
            print(f"  __exit__ 被调用: exc_type={exc_type}")
            return False

    with TracedCM() as resource:
        print(f"  with 块内：resource = {resource!r}")
    print("  with 块后正常继续")


# ---------------------------------------------------------------------------
# ② 最简上下文管理器
# ---------------------------------------------------------------------------

class ManagedFile:
    """文件资源管理器：确保文件无论如何都会被关闭"""

    def __init__(self, path: str, mode: str = "r"):
        self._path = path
        self._mode = mode
        self._file = None

    def __enter__(self):
        self._file = open(self._path, self._mode)
        print(f"  [ManagedFile] 打开 {self._path!r}")
        return self._file                # 返回值绑定到 as 变量

    def __exit__(self, exc_type, exc_val, tb):
        if self._file:
            self._file.close()
            print(f"  [ManagedFile] 关闭 {self._path!r}")
        return False                     # 不抑制异常


def demo02_managed_file():
    """② 文件资源管理器"""
    print("\n② 最简上下文管理器")

    import tempfile, os

    # 创建临时文件用于演示
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("hello, context manager!\n")
        tmp_path = tmp.name

    try:
        with ManagedFile(tmp_path) as f:
            content = f.read()
            print(f"  读取内容: {content.strip()!r}")
        # 离开 with 块后，文件已关闭
        print(f"  文件已关闭: {f.closed}")
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# ③ __exit__ 三个参数
# ---------------------------------------------------------------------------

class ExceptionInspector:
    """展示 __exit__ 接收到的异常信息"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            print("  __exit__: 正常退出，无异常")
        else:
            print(f"  __exit__: 捕获到异常")
            print(f"    exc_type = {exc_type.__name__}")
            print(f"    exc_val  = {exc_val!r}")
            print(f"    tb       = {type(tb).__name__} 对象")
        return False                     # 不抑制，异常继续传播


def demo03_exit_params():
    """③ __exit__ 的三个参数"""
    print("\n③ __exit__ 参数")

    # 正常退出
    with ExceptionInspector():
        pass

    # 异常退出
    try:
        with ExceptionInspector():
            raise ValueError("测试异常")
    except ValueError:
        print("  ValueError 继续传播并在外部被捕获")


# ---------------------------------------------------------------------------
# ④ 抑制异常
# ---------------------------------------------------------------------------

class SuppressErrors:
    """抑制指定类型的异常（contextlib.suppress 的原理）"""

    def __init__(self, *exc_types):
        self._exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            return False
        suppressed = issubclass(exc_type, self._exc_types)
        if suppressed:
            print(f"  [suppress] 抑制了 {exc_type.__name__}: {exc_val}")
        return suppressed                # True = 抑制，False = 传播


def demo04_suppress():
    """④ 抑制指定异常（return True 的效果）"""
    print("\n④ 抑制异常")

    with SuppressErrors(FileNotFoundError, KeyError):
        raise FileNotFoundError("文件不存在")

    print("  FileNotFoundError 被抑制，程序继续")

    with SuppressErrors(FileNotFoundError):
        raise ValueError("值错误")      # ValueError 不在列表里，会传播

    print("  ← 这行不会打印")           # 不会执行到这里（上面 ValueError 已传播）


# ---------------------------------------------------------------------------
# ⑤ 嵌套 with 与多变量 with
# ---------------------------------------------------------------------------

def demo05_nesting():
    """⑤ 嵌套 with 与多变量 with（Python 3.1+ 支持）"""
    print("\n⑤ 嵌套 with")

    import tempfile, os

    # 两种等价写法：
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".a") as f1, \
         tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".b") as f2:
        f1.write("A")
        f2.write("B")
        p1, p2 = f1.name, f2.name

    print(f"  f1.closed={f1.closed}, f2.closed={f2.closed}")
    os.unlink(p1); os.unlink(p2)

    # Python 3.10+ 括号形式（更易读）
    # with (
    #     open("a.txt") as f1,
    #     open("b.txt") as f2,
    # ):
    #     ...


# ---------------------------------------------------------------------------
# ⑥ 实际场景：数据库事务
# ---------------------------------------------------------------------------

class FakeConnection:
    """模拟数据库连接"""
    def __init__(self, name: str):
        self.name = name
        self._committed = False

    def execute(self, sql: str):
        print(f"  [DB:{self.name}] EXEC: {sql}")

    def commit(self):
        self._committed = True
        print(f"  [DB:{self.name}] COMMIT")

    def rollback(self):
        print(f"  [DB:{self.name}] ROLLBACK")

    def close(self):
        print(f"  [DB:{self.name}] CLOSE")


class Transaction:
    """事务上下文管理器：成功则 commit，失败则 rollback"""

    def __init__(self, conn: FakeConnection):
        self._conn = conn

    def __enter__(self) -> FakeConnection:
        print(f"  [Tx] 开始事务")
        return self._conn

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
            print(f"  [Tx] 因 {exc_type.__name__} 回滚")
        self._conn.close()
        return False


def demo06_transaction():
    """⑥ 实际场景：数据库事务"""
    print("\n⑥ 数据库事务")

    print("  --- 成功路径 ---")
    conn = FakeConnection("main")
    with Transaction(conn) as c:
        c.execute("INSERT INTO orders VALUES (1, 100)")
        c.execute("UPDATE inventory SET qty = qty - 1")

    print("  --- 失败回滚 ---")
    conn2 = FakeConnection("main")
    try:
        with Transaction(conn2) as c:
            c.execute("INSERT INTO orders VALUES (2, 200)")
            raise RuntimeError("库存不足")     # 模拟业务异常
    except RuntimeError as e:
        print(f"  外部捕获: {e}")


if __name__ == "__main__":
    demo01_equivalent()
    demo02_managed_file()
    demo03_exit_params()
    try:
        demo04_suppress()
    except ValueError as e:
        print(f"  外部捕获 ValueError: {e}")
    demo05_nesting()
    demo06_transaction()
