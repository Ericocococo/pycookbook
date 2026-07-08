"""yield from —— 委托生成器与双向透传

Python 3.12。
运行: python 04_yield_from.py

yield from <expr> 做了三件事：
  1. 把 <expr> 的每个值原样 yield 给外层调用方（等同于 for x in expr: yield x）
  2. 透传 send() 进来的值到子生成器
  3. 子生成器 return 的值成为 yield from 表达式本身的值

演示：
  ① 替代 for-yield 循环
  ② 透传 send() 值
  ③ 透传 return 值（StopIteration.value）
  ④ 透传 throw()
  ⑤ 实际场景：树形结构扁平化
  ⑥ 实际场景：生成器协程链
"""


# ---------------------------------------------------------------------------
# ① 替代 for-yield
# ---------------------------------------------------------------------------

def chain_manual(iterables):
    """手动 for-yield：写起来繁琐，且不透传 send/throw"""
    for it in iterables:
        for item in it:
            yield item


def chain_yield_from(iterables):
    """yield from：等价且更简洁，并自动透传所有通信"""
    for it in iterables:
        yield from it


def demo01_replace_for_yield():
    """① yield from 替代 for-yield"""
    print("① yield from 替代 for-yield")

    data = [[1, 2], [3, 4], [5]]
    print("  chain_manual:     ", list(chain_manual(data)))
    print("  chain_yield_from: ", list(chain_yield_from(data)))

    # 字符串也可以
    print("  展开字符串:", list(chain_yield_from(["hello", "world"])))


# ---------------------------------------------------------------------------
# ② 透传 send()
# ---------------------------------------------------------------------------

def inner_gen():
    """子生成器：接收 send 进来的值并处理"""
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value
    return total                         # return 的值通过 StopIteration 传递


def outer_gen():
    """外层生成器：用 yield from 委托给 inner_gen"""
    result = yield from inner_gen()      # result = inner_gen 的 return 值
    yield f"内层生成器最终累计: {result}"


def demo02_send_passthrough():
    """② send() 透传：外层 send 直达内层"""
    print("\n② send() 透传")

    g = outer_gen()
    print("  next():", next(g))          # 推进到 inner_gen 的第一个 yield，total=0
    print("  send(10):", g.send(10))     # total=10
    print("  send(20):", g.send(20))     # total=30
    print("  send(None):", g.send(None)) # inner 退出，outer yield 结果


# ---------------------------------------------------------------------------
# ③ 子生成器 return 值
# ---------------------------------------------------------------------------

def accumulator(items):
    """子生成器：逐个消费列表，返回总和"""
    total = 0
    for item in items:
        total += item
        yield item                       # 逐个 yield 出去
    return total                         # ← 这个值会赋给 yield from 表达式


def report(items):
    """外层：用 yield from 拿到子生成器的 return 值"""
    total = yield from accumulator(items)
    yield f"合计: {total}"


def demo03_return_value():
    """③ 子生成器 return 值通过 yield from 捕获"""
    print("\n③ return 值透传")

    g = report([10, 20, 30])
    for val in g:
        print(f"  {val}")


# ---------------------------------------------------------------------------
# ④ throw() 透传
# ---------------------------------------------------------------------------

def resilient_inner():
    """子生成器：能处理外部注入的 ValueError"""
    try:
        while True:
            yield "ok"
    except ValueError as e:
        yield f"inner 捕获: {e}"


def resilient_outer():
    """外层：yield from 把 throw 透传给 inner"""
    yield from resilient_inner()


def demo04_throw_passthrough():
    """④ throw() 透传到子生成器"""
    print("\n④ throw() 透传")

    g = resilient_outer()
    print(" ", next(g))                          # ok
    print(" ", g.throw(ValueError, "外部注入"))  # inner 捕获: 外部注入


# ---------------------------------------------------------------------------
# ⑤ 实际场景：树形结构扁平化
# ---------------------------------------------------------------------------

def flatten(nested):
    """递归展开任意深度的嵌套可迭代对象（字符串除外）"""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)     # 递归委托
        else:
            yield item


def demo05_flatten_tree():
    """⑤ 实际场景：递归 yield from 展开嵌套结构"""
    print("\n⑤ 树形结构扁平化")

    tree = [1, [2, [3, 4], 5], [6, 7], 8]
    print("  原始:", tree)
    print("  展平:", list(flatten(tree)))

    # 混合元组和列表
    mixed = (1, [2, (3, [4, 5])], 6)
    print("  混合:", list(flatten(mixed)))


# ---------------------------------------------------------------------------
# ⑥ 实际场景：协程链（生产者 → 过滤 → 消费者）
# ---------------------------------------------------------------------------

def producer(items):
    """生产者：yield 原始数据"""
    for item in items:
        yield item


def even_filter(source):
    """中间件：只通过偶数"""
    for item in source:
        if item % 2 == 0:
            yield item


def squarer(source):
    """变换：平方"""
    yield from (x * x for x in source)


def demo06_pipeline():
    """⑥ 生成器协程链：各阶段用 yield from 串联"""
    print("\n⑥ 生成器协程链")

    data = range(1, 11)
    pipeline = squarer(even_filter(producer(data)))

    print("  偶数的平方:", list(pipeline))


if __name__ == "__main__":
    demo01_replace_for_yield()
    demo02_send_passthrough()
    demo03_return_value()
    demo04_throw_passthrough()
    demo05_flatten_tree()
    demo06_pipeline()
