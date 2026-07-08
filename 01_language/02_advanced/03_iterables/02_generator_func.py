"""生成器函数 —— yield / send / throw / close

Python 3.12。
运行: python 02_generator_func.py

生成器函数：含有 yield 表达式的函数。
调用它不执行函数体，而是返回一个生成器对象（既是 Iterable 又是 Iterator）。
每次 next() 从上次 yield 处恢复执行，再次遇到 yield 时挂起并返回值。

演示：
  ① 最简生成器 + 执行流程对比
  ② 内存优势：生成器 vs 列表
  ③ send()：向生成器传值（双向通道）
  ④ throw()：向生成器注入异常
  ⑤ close()：提前终止生成器
  ⑥ 实际场景：惰性数据管道
"""

import sys


# ---------------------------------------------------------------------------
# ① 最简生成器 + 执行流程
# ---------------------------------------------------------------------------

def simple_gen():
    """最简生成器：三步走"""
    print("  [gen] 开始执行")
    yield 1
    print("  [gen] 第一个 yield 之后")
    yield 2
    print("  [gen] 第二个 yield 之后，函数结束")


def demo01_basic():
    """① 生成器执行流程：调用 next 才驱动"""
    print("① 最简生成器执行流程")

    g = simple_gen()
    print("  调用函数后，函数体还没执行，g =", g)

    print("  第一次 next:")
    v = next(g)
    print(f"  next() 返回: {v}")

    print("  第二次 next:")
    v = next(g)
    print(f"  next() 返回: {v}")

    print("  第三次 next（函数执行完毕后会 StopIteration）:")
    try:
        next(g)
    except StopIteration as e:
        print(f"  StopIteration，value={e.value}")   # 函数 return 的值在这里


# ---------------------------------------------------------------------------
# ② 内存优势
# ---------------------------------------------------------------------------

def range_list(n: int) -> list:
    """把所有值装入列表——一次性占用 O(n) 内存"""
    result = []
    for i in range(n):
        result.append(i * i)
    return result


def range_gen(n: int):
    """惰性生成——每次只持有一个值"""
    for i in range(n):
        yield i * i


def demo02_memory():
    """② 内存对比：生成器 vs 列表"""
    print("\n② 内存占用对比（n=1_000_000）")

    n = 1_000_000
    lst = range_list(n)
    gen = range_gen(n)

    # sys.getsizeof 只看对象自身大小（不含列表元素内存）
    # 但生成器对象极小；list 对象本身就很大
    print(f"  list  sys.getsizeof: {sys.getsizeof(lst):>10,} bytes")
    print(f"  gen   sys.getsizeof: {sys.getsizeof(gen):>10,} bytes")

    # 消费前 5 个
    print("  前 5 个平方数:", [next(gen) for _ in range(5)])


# ---------------------------------------------------------------------------
# ③ send()：双向通道
# ---------------------------------------------------------------------------

def echo_gen():
    """接收 send 进来的值，加工后 yield 出去。

    yield 表达式本身是双向的：
      - next(g) 等价于 g.send(None)，驱动到下一个 yield
      - g.send(value) 把 value 塞进 yield 表达式，作为其"返回值"
    """
    received = None
    while True:
        # yield 右侧的值发给调用方，左侧的值来自 send()
        received = yield f"echo: {received}"


def demo03_send():
    """③ send()：向生成器注入值"""
    print("\n③ send() 双向通道")

    g = echo_gen()
    # 第一次必须用 next() 或 send(None) 推进到第一个 yield
    print(" ", next(g))                  # echo: None
    print(" ", g.send("hello"))          # echo: hello
    print(" ", g.send("world"))          # echo: world
    g.close()


# ---------------------------------------------------------------------------
# ④ throw()：注入异常
# ---------------------------------------------------------------------------

def safe_gen():
    """能捕获外部注入异常的生成器"""
    try:
        while True:
            yield "running"
    except ValueError as e:
        yield f"捕获了异常: {e}"


def demo04_throw():
    """④ throw()：从外部向生成器注入异常"""
    print("\n④ throw() 注入异常")

    g = safe_gen()
    print(" ", next(g))                  # running
    print(" ", next(g))                  # running
    # 向生成器内部注入 ValueError
    print(" ", g.throw(ValueError, "出错了"))   # 捕获了异常: 出错了


# ---------------------------------------------------------------------------
# ⑤ close()：提前终止
# ---------------------------------------------------------------------------

def resource_gen():
    """模拟带资源的生成器，close 时触发 GeneratorExit"""
    print("  [gen] 资源打开")
    try:
        for i in range(100):
            yield i
    finally:
        # GeneratorExit 会传入 finally，确保清理代码运行
        print("  [gen] 资源释放（finally 保证执行）")


def demo05_close():
    """⑤ close()：提前终止，finally 保证清理"""
    print("\n⑤ close() 提前终止")

    g = resource_gen()
    print("  取前 3 个:")
    for i, val in enumerate(g):
        print(f"  {val}", end="  ")
        if i == 2:
            break
    print()
    g.close()                            # 触发 GeneratorExit → finally


# ---------------------------------------------------------------------------
# ⑥ 实际场景：惰性数据管道
# ---------------------------------------------------------------------------

def read_lines(text: str):
    """模拟逐行读取（实际可换成 open(file)）"""
    for line in text.splitlines():
        yield line


def strip_comments(lines):
    """过滤掉注释行（# 开头）和空行"""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield stripped


def parse_kv(lines):
    """把 key=value 行解析为 (key, value) 元组"""
    for line in lines:
        if "=" in line:
            key, _, val = line.partition("=")
            yield key.strip(), val.strip()


def demo06_pipeline():
    """⑥ 管道：多个生成器串联，零中间列表"""
    print("\n⑥ 惰性数据管道")

    config_text = """
# 数据库配置
host = localhost
port = 5432
# 认证
user = admin
password = secret

debug = true
"""

    # 三个生成器首尾相接——数据一行一行流过，不产生中间列表
    lines = read_lines(config_text)
    cleaned = strip_comments(lines)
    parsed = parse_kv(cleaned)

    for key, value in parsed:
        print(f"  {key!r:12s} = {value!r}")


if __name__ == "__main__":
    demo01_basic()
    demo02_memory()
    demo03_send()
    demo04_throw()
    demo05_close()
    demo06_pipeline()
