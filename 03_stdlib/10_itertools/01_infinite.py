"""itertools 无穷迭代器 —— count / cycle / repeat

Python 3.12。
运行: python 01_infinite.py

无穷迭代器永不 StopIteration——必须配合 islice / takewhile / break 截断。
它们全是惰性的，不占内存。

演示：
  ① count(start, step)：等差数列（无穷）
  ② cycle(iterable)：无限循环序列
  ③ repeat(object, times)：重复固定值
  ④ 配合 islice 截断
  ⑤ 实际场景：带序号的无穷 ID 生成器
  ⑥ 实际场景：轮询调度（Round-Robin）
"""

import itertools


# ---------------------------------------------------------------------------
# ① count
# ---------------------------------------------------------------------------

def demo01_count():
    """① count(start=0, step=1)：从 start 开始按 step 递增，无限"""
    print("① count")

    # 取前 5 个整数
    first5 = list(itertools.islice(itertools.count(), 5))
    print(f"  count()        前5个: {first5}")

    # 从 10 开始，步长 2
    evens = list(itertools.islice(itertools.count(10, 2), 6))
    print(f"  count(10, 2)   前6个: {evens}")

    # 步长可以是浮点数
    floats = list(itertools.islice(itertools.count(0.0, 0.5), 5))
    print(f"  count(0.0, 0.5) 前5个: {floats}")

    # 负步长（倒数）
    countdown = list(itertools.islice(itertools.count(10, -1), 6))
    print(f"  count(10, -1)  前6个: {countdown}")


# ---------------------------------------------------------------------------
# ② cycle
# ---------------------------------------------------------------------------

def demo02_cycle():
    """② cycle(iterable)：把序列无限循环"""
    print("\n② cycle")

    # 循环颜色
    colors = ["红", "绿", "蓝"]
    palette = list(itertools.islice(itertools.cycle(colors), 8))
    print(f"  cycle(['红','绿','蓝']) 前8个: {palette}")

    # 循环布尔值（奇偶标记）
    flags = list(itertools.islice(itertools.cycle([True, False]), 7))
    print(f"  cycle([T,F])           前7个: {flags}")

    # 实际应用：给列表中每行交替加背景色
    rows = ["行A", "行B", "行C", "行D"]
    bg_colors = itertools.cycle(["white", "#f0f0f0"])
    styled = [(row, bg) for row, bg in zip(rows, bg_colors)]
    print(f"  交替行颜色: {styled}")


# ---------------------------------------------------------------------------
# ③ repeat
# ---------------------------------------------------------------------------

def demo03_repeat():
    """③ repeat(object, times=None)：重复同一个对象"""
    print("\n③ repeat")

    # 有限重复（给定 times）
    fives = list(itertools.repeat(5, 4))
    print(f"  repeat(5, 4):          {fives}")

    # repeat 常与 map/starmap 搭配
    squares = list(map(pow, range(1, 6), itertools.repeat(2)))
    print(f"  map(pow, range(5), repeat(2)): {squares}")

    # 用 repeat 填充 zip_longest 的缺省值（备选方案）
    keys = ["a", "b", "c"]
    default_vals = list(zip(keys, itertools.repeat(None)))
    print(f"  zip(keys, repeat(None)): {default_vals}")

    # 无穷重复——必须配合 islice 或在 for 中 break
    gen = itertools.repeat("ping")
    first3 = [next(gen) for _ in range(3)]
    print(f"  repeat('ping') 前3个:  {first3}")


# ---------------------------------------------------------------------------
# ④ 配合 islice 截断
# ---------------------------------------------------------------------------

def demo04_islice():
    """④ islice 是截断无穷迭代器的标准工具"""
    print("\n④ islice 截断")

    # islice(it, stop)
    # islice(it, start, stop[, step])  —— 类似 slice，但不支持负索引

    it = itertools.count(1)
    print(f"  islice(count(1), 5):          {list(itertools.islice(it, 5))}")
    # it 的状态保留——继续取
    print(f"  再 islice(it, 5):             {list(itertools.islice(it, 5))}")

    # 带 start/stop/step
    print(f"  islice(count(0), 2, 10, 3):  {list(itertools.islice(itertools.count(0), 2, 10, 3))}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景：唯一 ID 生成器
# ---------------------------------------------------------------------------

def make_id_generator(prefix: str = ""):
    """生成带前缀的唯一自增 ID"""
    for n in itertools.count(1):
        yield f"{prefix}{n:06d}"


def demo05_id_generator():
    """⑤ 实际场景：无穷 ID 生成器"""
    print("\n⑤ 唯一 ID 生成器")

    order_id = make_id_generator("ORD-")
    user_id = make_id_generator("USR-")

    for _ in range(3):
        print(f"  {next(order_id)}  {next(user_id)}")


# ---------------------------------------------------------------------------
# ⑥ 实际场景：轮询调度
# ---------------------------------------------------------------------------

def round_robin(workers: list):
    """轮询调度：任务均匀分配给各 worker"""
    worker_cycle = itertools.cycle(workers)

    def assign(task: str) -> str:
        worker = next(worker_cycle)
        return f"任务 {task!r} → {worker}"

    return assign


def demo06_round_robin():
    """⑥ 实际场景：轮询调度"""
    print("\n⑥ 轮询调度")

    assign = round_robin(["Worker-1", "Worker-2", "Worker-3"])
    tasks = ["查询A", "写入B", "更新C", "删除D", "查询E", "写入F"]

    for task in tasks:
        print(f"  {assign(task)}")


if __name__ == "__main__":
    demo01_count()
    demo02_cycle()
    demo03_repeat()
    demo04_islice()
    demo05_id_generator()
    demo06_round_robin()
