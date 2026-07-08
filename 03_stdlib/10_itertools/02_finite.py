"""itertools 有限迭代器 —— chain / takewhile / dropwhile / zip_longest / accumulate 等

Python 3.12。
运行: python 02_finite.py

有限迭代器：以输入数据为界，总会终止。

演示：
  ① chain：串联多个迭代器
  ② chain.from_iterable：从可迭代对象的可迭代对象串联
  ③ takewhile / dropwhile：按谓词截取/跳过前缀
  ④ zip_longest：以最长者为准
  ⑤ compress：按掩码过滤
  ⑥ starmap：解包参数的 map
  ⑦ accumulate：累积中间值
  ⑧ groupby：按键分组（需先排序）
  ⑨ pairwise：相邻元素对（Python 3.10+）
  ⑩ 实际场景：日志分析管道
"""

import itertools
import operator


# ---------------------------------------------------------------------------
# ① chain
# ---------------------------------------------------------------------------

def demo01_chain():
    """① chain(*iterables)：依次串联，零拷贝"""
    print("① chain")

    a, b, c = [1, 2], [3, 4], [5]
    print(f"  chain([1,2],[3,4],[5]): {list(itertools.chain(a, b, c))}")

    # 扁平化一层嵌套
    nested = [[1, 2], [3, 4], [5]]
    flat = list(itertools.chain(*nested))
    print(f"  chain(*nested):         {flat}")

    # 拼接不同类型的迭代器
    mixed = list(itertools.chain("ABC", range(3), (10, 20)))
    print(f"  chain str+range+tuple:  {mixed}")


# ---------------------------------------------------------------------------
# ② chain.from_iterable
# ---------------------------------------------------------------------------

def demo02_chain_from_iterable():
    """② chain.from_iterable：惰性展开可迭代的可迭代对象"""
    print("\n② chain.from_iterable")

    # 等价于 chain(*iterables)，但惰性：不会先把外层展开成 list
    nested = [[1, 2], [3, 4], [5, 6]]
    flat = list(itertools.chain.from_iterable(nested))
    print(f"  from_iterable: {flat}")

    # 实际场景：把字典列表的 values 全部展开
    records = [{"tags": ["python", "iter"]}, {"tags": ["functools"]}, {"tags": []}]
    all_tags = list(itertools.chain.from_iterable(r["tags"] for r in records))
    print(f"  所有 tags: {all_tags}")


# ---------------------------------------------------------------------------
# ③ takewhile / dropwhile
# ---------------------------------------------------------------------------

def demo03_take_drop():
    """③ takewhile / dropwhile：按谓词处理前缀"""
    print("\n③ takewhile / dropwhile")

    data = [2, 4, 6, 7, 8, 10, 12]

    # takewhile：满足条件就取，首次不满足立刻停（后面的不再检查）
    taken = list(itertools.takewhile(lambda x: x % 2 == 0, data))
    print(f"  takewhile(偶数): {taken}")   # [2, 4, 6]（遇到 7 停）

    # dropwhile：满足条件就跳过，首次不满足后全部保留
    dropped = list(itertools.dropwhile(lambda x: x % 2 == 0, data))
    print(f"  dropwhile(偶数): {dropped}")  # [7, 8, 10, 12]

    # 实际场景：解析有头部注释的配置文件
    lines = [
        "# 注释1",
        "# 注释2",
        "",
        "key = value",
        "# 内联注释（不跳过）",
        "other = data",
    ]
    content = list(itertools.dropwhile(lambda l: l.startswith("#"), lines))
    print(f"  跳过头部注释: {content}")


# ---------------------------------------------------------------------------
# ④ zip_longest
# ---------------------------------------------------------------------------

def demo04_zip_longest():
    """④ zip_longest：以最长者为准，短的补 fillvalue"""
    print("\n④ zip_longest")

    names = ["Alice", "Bob", "Carol"]
    scores = [95, 87]                    # 少一个

    # 内置 zip 按最短截断
    zipped = list(zip(names, scores))
    print(f"  zip（截断）:           {zipped}")

    # zip_longest 补 None
    zipped_long = list(itertools.zip_longest(names, scores))
    print(f"  zip_longest(默认 None): {zipped_long}")

    # 自定义 fillvalue
    zipped_fill = list(itertools.zip_longest(names, scores, fillvalue=0))
    print(f"  zip_longest(fill=0):    {zipped_fill}")

    # 多个序列
    a = [1, 2, 3, 4]
    b = ["a", "b"]
    c = [True]
    print(f"  三列 zip_longest: {list(itertools.zip_longest(a, b, c, fillvalue='-'))}")


# ---------------------------------------------------------------------------
# ⑤ compress
# ---------------------------------------------------------------------------

def demo05_compress():
    """⑤ compress(data, selectors)：按掩码过滤"""
    print("\n⑤ compress")

    data = ["A", "B", "C", "D", "E"]
    mask = [1, 0, 1, 0, 1]

    selected = list(itertools.compress(data, mask))
    print(f"  compress 按掩码: {selected}")

    # 实际场景：根据权限过滤菜单
    menu = ["首页", "用户管理", "商品", "报表", "系统设置"]
    perms = [True, False, True, True, False]
    visible = list(itertools.compress(menu, perms))
    print(f"  可见菜单: {visible}")


# ---------------------------------------------------------------------------
# ⑥ starmap
# ---------------------------------------------------------------------------

def demo06_starmap():
    """⑥ starmap(func, iterable)：自动解包每个元素作为参数"""
    print("\n⑥ starmap")

    # map 版本（需要手动传两个序列）
    pairs = [(2, 3), (4, 2), (10, 3)]

    # starmap 自动解包 (2, 3) → pow(2, 3)
    results = list(itertools.starmap(pow, pairs))
    print(f"  starmap(pow, pairs):  {results}")

    # 等价于 map(lambda p: pow(*p), pairs)
    results2 = list(map(lambda p: pow(*p), pairs))
    print(f"  map(lambda p: pow(*p)): {results2}")

    # 字符串格式化
    data = [("Alice", 30), ("Bob", 25), ("Carol", 35)]
    formatted = list(itertools.starmap(lambda n, a: f"{n}({a}岁)", data))
    print(f"  starmap 格式化: {formatted}")


# ---------------------------------------------------------------------------
# ⑦ accumulate
# ---------------------------------------------------------------------------

def demo07_accumulate():
    """⑦ accumulate：累积中间值序列（vs reduce 只返回最终值）"""
    print("\n⑦ accumulate")

    nums = [1, 2, 3, 4, 5]

    # 默认：累加（前缀和）
    prefix_sum = list(itertools.accumulate(nums))
    print(f"  前缀和:        {prefix_sum}")

    # 自定义：前缀积
    prefix_prod = list(itertools.accumulate(nums, operator.mul))
    print(f"  前缀积:        {prefix_prod}")

    # 初始值（Python 3.8+）
    with_init = list(itertools.accumulate(nums, operator.add, initial=100))
    print(f"  initial=100:  {with_init}")

    # 实际场景：股票历史最高价（running max）
    prices = [10, 8, 12, 11, 15, 9, 14]
    running_max = list(itertools.accumulate(prices, max))
    print(f"  股价:           {prices}")
    print(f"  历史最高:       {running_max}")


# ---------------------------------------------------------------------------
# ⑧ groupby
# ---------------------------------------------------------------------------

def demo08_groupby():
    """⑧ groupby：连续相同 key 的分组（必须先排序！）"""
    print("\n⑧ groupby")

    words = ["apple", "ant", "bear", "bee", "cat", "cherry"]

    # groupby 只合并连续相同 key 的元素——必须先按同一 key 排序
    words_sorted = sorted(words, key=lambda w: w[0])
    for letter, group in itertools.groupby(words_sorted, key=lambda w: w[0]):
        print(f"  {letter}: {list(group)}")

    # 实际场景：按日期汇总交易
    transactions = [
        {"date": "2024-01-01", "amount": 100},
        {"date": "2024-01-01", "amount": 200},
        {"date": "2024-01-02", "amount": 50},
        {"date": "2024-01-02", "amount": 150},
        {"date": "2024-01-03", "amount": 300},
    ]
    transactions.sort(key=lambda t: t["date"])
    print()
    for date, group in itertools.groupby(transactions, key=lambda t: t["date"]):
        daily = list(group)
        total = sum(t["amount"] for t in daily)
        print(f"  {date}: {len(daily)} 笔, 合计 ¥{total}")


# ---------------------------------------------------------------------------
# ⑨ pairwise（Python 3.10+）
# ---------------------------------------------------------------------------

def demo09_pairwise():
    """⑨ pairwise：相邻元素对"""
    print("\n⑨ pairwise（Python 3.10+）")

    data = [1, 3, 6, 10, 15]
    pairs = list(itertools.pairwise(data))
    print(f"  pairwise: {pairs}")

    # 计算相邻差分（等价 numpy.diff）
    diffs = [b - a for a, b in itertools.pairwise(data)]
    print(f"  差分:     {diffs}")


# ---------------------------------------------------------------------------
# ⑩ 实际场景：日志分析管道
# ---------------------------------------------------------------------------

def demo10_pipeline():
    """⑩ 实际场景：用 itertools 组合构建日志分析管道"""
    print("\n⑩ 日志分析管道")

    raw_logs = [
        "INFO  2024-01-01 10:00:01 用户登录 alice",
        "DEBUG 2024-01-01 10:00:02 会话建立",
        "ERROR 2024-01-01 10:00:03 数据库超时",
        "INFO  2024-01-01 10:00:04 用户登录 bob",
        "ERROR 2024-01-01 10:00:05 权限拒绝",
        "INFO  2024-01-01 10:00:06 用户退出 alice",
    ]

    # 只取 ERROR 日志（compress 按掩码）
    is_error = [line.startswith("ERROR") for line in raw_logs]
    errors = list(itertools.compress(raw_logs, is_error))
    print(f"  ERROR 日志:")
    for e in errors:
        print(f"    {e}")

    # 给错误编号（count + zip）
    numbered = list(zip(itertools.count(1), errors))
    print(f"  编号:")
    for n, e in numbered:
        print(f"    {n}. {e}")


if __name__ == "__main__":
    demo01_chain()
    demo02_chain_from_iterable()
    demo03_take_drop()
    demo04_zip_longest()
    demo05_compress()
    demo06_starmap()
    demo07_accumulate()
    demo08_groupby()
    demo09_pairwise()
    demo10_pipeline()
