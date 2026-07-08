"""@contextmanager —— 用生成器实现上下文管理器

Python 3.12。
运行: python 02_contextmanager.py

@contextmanager 把一个"yield 一次的生成器函数"转变为上下文管理器：
  yield 之前的代码 = __enter__
  yield 的值       = as 变量的值
  yield 之后的代码 = __exit__（在 finally 里保证执行）

演示：
  ① 最简 @contextmanager
  ② yield 之前/之后的执行顺序
  ③ 正确处理异常（try/finally vs try/except/yield）
  ④ @contextmanager 与 class 写法对比
  ⑤ 实际场景 A：临时改变工作目录
  ⑥ 实际场景 B：计时器（可重用）
  ⑦ 实际场景 C：临时 mock 补丁
"""

import os
import time
from contextlib import contextmanager


# ---------------------------------------------------------------------------
# ① 最简 @contextmanager
# ---------------------------------------------------------------------------

@contextmanager
def simple_cm():
    print("  [enter] 准备资源")
    yield "资源对象"                     # yield 的值绑定到 as 变量
    print("  [exit]  释放资源")


def demo01_basic():
    """① 最简 @contextmanager"""
    print("① 最简 @contextmanager")

    with simple_cm() as resource:
        print(f"  with 块内: resource = {resource!r}")

    print("  with 块后正常继续")


# ---------------------------------------------------------------------------
# ② 执行顺序
# ---------------------------------------------------------------------------

@contextmanager
def tracer(name: str):
    """用来演示执行顺序的上下文管理器"""
    print(f"  [{name}] __enter__ 开始")
    try:
        yield name
    finally:
        print(f"  [{name}] __exit__ 结束")


def demo02_order():
    """② 执行顺序：嵌套时从外到内进入，从内到外退出"""
    print("\n② 执行顺序")

    with tracer("外层") as outer:
        print(f"  外层 as 变量: {outer!r}")
        with tracer("内层") as inner:
            print(f"  内层 as 变量: {inner!r}")
            print("  with 块最深处")


# ---------------------------------------------------------------------------
# ③ 异常处理
# ---------------------------------------------------------------------------

@contextmanager
def safe_open(path: str):
    """带异常处理的文件管理器（正确写法）"""
    f = None
    try:
        f = open(path)
        yield f
    except FileNotFoundError:
        print(f"  [safe_open] 文件不存在: {path!r}")
        yield None                       # 让 with 块能运行（以 None 进入）
    finally:
        if f:
            f.close()
            print(f"  [safe_open] 已关闭")


@contextmanager
def suppress_cm(*exc_types):
    """抑制指定异常的 @contextmanager 版本"""
    try:
        yield
    except exc_types:
        pass                             # 吃掉异常，继续执行


def demo03_exception():
    """③ 异常处理"""
    print("\n③ 异常处理")

    # with 块内抛异常——finally 保证执行
    @contextmanager
    def risky():
        print("  [risky] 进入")
        try:
            yield
        finally:
            print("  [risky] 退出（finally 保证）")

    try:
        with risky():
            print("  [risky] 抛出异常")
            raise ValueError("演示")
    except ValueError:
        print("  ValueError 在外部被捕获")

    # 抑制异常
    print()
    with suppress_cm(ZeroDivisionError):
        result = 1 / 0                   # 被 suppress_cm 吃掉
    print("  ZeroDivisionError 被抑制，继续执行")


# ---------------------------------------------------------------------------
# ④ @contextmanager vs 类写法
# ---------------------------------------------------------------------------

def demo04_vs_class():
    """④ @contextmanager 与类写法对比"""
    print("\n④ @contextmanager vs 类写法")

    # 类写法（繁琐但功能完整）
    class Timer:
        def __enter__(self):
            self._start = time.perf_counter()
            return self
        def __exit__(self, *_):
            self.elapsed = time.perf_counter() - self._start
            return False

    # @contextmanager 写法（简洁）
    @contextmanager
    def timer():
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            print(f"  耗时: {elapsed * 1000:.3f} ms")

    with timer():
        _ = sum(range(1_000_000))

    # 类写法的优势：可以在 with 块后访问 .elapsed
    with Timer() as t:
        _ = sum(range(1_000_000))
    print(f"  类写法 elapsed: {t.elapsed * 1000:.3f} ms")


# ---------------------------------------------------------------------------
# ⑤ 实际场景：临时切换工作目录
# ---------------------------------------------------------------------------

@contextmanager
def chdir(path: str):
    """临时切换工作目录，退出后自动恢复"""
    old_dir = os.getcwd()
    try:
        os.chdir(path)
        print(f"  [chdir] 切换到: {os.getcwd()}")
        yield
    finally:
        os.chdir(old_dir)
        print(f"  [chdir] 恢复到: {os.getcwd()}")


def demo05_chdir():
    """⑤ 临时切换工作目录"""
    print("\n⑤ 临时切换工作目录")
    original = os.getcwd()
    print(f"  原始目录: {original}")

    with chdir(os.path.dirname(os.path.abspath(__file__))):
        print(f"  with 块内: {os.getcwd()}")

    print(f"  with 块后: {os.getcwd()}")
    assert os.getcwd() == original


# ---------------------------------------------------------------------------
# ⑥ 实际场景：可重用计时器（返回 dict 供 with 块后读取）
# ---------------------------------------------------------------------------

@contextmanager
def measure(label: str = ""):
    """计时器，with 块后可读取 result['elapsed_ms']"""
    result = {}
    start = time.perf_counter()
    try:
        yield result                     # 传入可变容器，让 with 块后也能访问
    finally:
        result["elapsed_ms"] = (time.perf_counter() - start) * 1000
        tag = f"[{label}] " if label else ""
        print(f"  {tag}耗时 {result['elapsed_ms']:.3f} ms")


def demo06_measure():
    """⑥ 可重用计时器"""
    print("\n⑥ 计时器")

    with measure("矩阵求和") as r:
        total = sum(i * i for i in range(500_000))

    print(f"  总和: {total}  (通过 result 对象访问耗时: {r['elapsed_ms']:.3f} ms)")


# ---------------------------------------------------------------------------
# ⑦ 实际场景：临时 mock 属性
# ---------------------------------------------------------------------------

@contextmanager
def patch_attr(obj, attr: str, new_value):
    """临时替换对象属性，退出后还原"""
    original = getattr(obj, attr)
    setattr(obj, attr, new_value)
    try:
        yield
    finally:
        setattr(obj, attr, original)


class Config:
    DEBUG = False
    DB_URL = "postgresql://prod/mydb"


def demo07_patch():
    """⑦ 临时 mock 属性（测试中常用）"""
    print("\n⑦ 临时 mock 属性")

    print(f"  原始 Config.DEBUG = {Config.DEBUG}")
    with patch_attr(Config, "DEBUG", True):
        print(f"  with 块内 Config.DEBUG = {Config.DEBUG}")
    print(f"  with 块后 Config.DEBUG = {Config.DEBUG}")


if __name__ == "__main__":
    demo01_basic()
    demo02_order()
    demo03_exception()
    demo04_vs_class()
    demo05_chdir()
    demo06_measure()
    demo07_patch()
