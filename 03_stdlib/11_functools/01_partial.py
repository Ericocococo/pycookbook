"""functools.partial —— 偏函数，固定部分参数

Python 3.12。
运行: python 01_partial.py

partial(func, *args, **kwargs) 返回一个新的可调用对象，
调用时会把预先绑定的参数与新传入的参数合并。

演示：
  ① 基本用法：固定位置参数 / 关键字参数
  ② partial 对象的属性：func / args / keywords
  ③ partial vs lambda vs def 三种等价写法
  ④ 固定关键字参数（常见场景）
  ⑤ 实际场景 A：预配置请求函数
  ⑥ 实际场景 B：批量生成专用函数
  ⑦ partialmethod：用于类方法
"""

import functools


# ---------------------------------------------------------------------------
# ① 基本用法
# ---------------------------------------------------------------------------

def power(base: float, exp: float) -> float:
    return base ** exp


def demo01_basic():
    """① 固定位置参数 / 关键字参数"""
    print("① 基本用法")

    # 固定第一个位置参数 base=2
    square = functools.partial(power, exp=2)       # 固定关键字参数
    cube = functools.partial(power, exp=3)

    print(f"  square(4) = {square(4)}")   # power(4, exp=2)
    print(f"  cube(3)   = {cube(3)}")     # power(3, exp=3)

    # 也可以固定位置参数
    two_to = functools.partial(power, 2)  # 固定 base=2（位置参数）
    print(f"  two_to(10) = {two_to(10)}") # power(2, 10) = 1024


# ---------------------------------------------------------------------------
# ② partial 对象的属性
# ---------------------------------------------------------------------------

def demo02_attributes():
    """② partial 对象有 .func / .args / .keywords"""
    print("\n② partial 对象属性")

    def greet(prefix: str, name: str, punctuation: str = "!") -> str:
        return f"{prefix} {name}{punctuation}"

    hello = functools.partial(greet, "Hello", punctuation=".")

    print(f"  hello.func:     {hello.func}")
    print(f"  hello.args:     {hello.args}")
    print(f"  hello.keywords: {hello.keywords}")
    print(f"  hello('Alice')  = {hello('Alice')}")

    # partial 对象是 callable
    import callable as _
    print(f"  callable(hello): {callable(hello)}")


# ---------------------------------------------------------------------------
# ③ partial vs lambda vs def
# ---------------------------------------------------------------------------

def demo03_equivalents():
    """③ 三种等价写法：partial / lambda / def"""
    print("\n③ partial vs lambda vs def")

    import math

    # 目标：创建"以 10 为底的对数"函数

    # lambda（最简洁，但不能 pickle，无 __name__）
    log10_lambda = lambda x: math.log(x, 10)

    # partial（可 pickle，有 func/args 属性，无自定义 __name__）
    log10_partial = functools.partial(math.log, base=10)

    # def（最明确，有 __doc__，有 __name__）
    def log10_def(x: float) -> float:
        return math.log(x, 10)

    for fn, name in [(log10_lambda, "lambda"), (log10_partial, "partial"), (log10_def, "def")]:
        print(f"  {name:8s} log10(1000) = {fn(1000)}")

    # partial 的优势：可序列化（用于 multiprocessing）
    import pickle
    pickled = pickle.dumps(log10_partial)
    restored = pickle.loads(pickled)
    print(f"  pickle 往返 log10(100) = {restored(100)}")


# ---------------------------------------------------------------------------
# ④ 固定关键字参数
# ---------------------------------------------------------------------------

def demo04_keyword_args():
    """④ 最常用的场景：固定常用关键字参数"""
    print("\n④ 固定关键字参数")

    # sorted 的专用版本
    reverse_sorted = functools.partial(sorted, reverse=True)
    print(f"  reverse_sorted([3,1,4,1,5]): {reverse_sorted([3,1,4,1,5])}")

    # print 预设分隔符和结尾符
    print_csv = functools.partial(print, sep=", ", end="\n")
    print("  print_csv:", end=" ")
    print_csv("Alice", 30, "工程师")

    # open 预设编码
    open_utf8 = functools.partial(open, encoding="utf-8", errors="replace")
    # 调用时只需传路径和模式
    # with open_utf8("data.txt", "r") as f: ...

    # int 预设进制（字符串转整数）
    from_hex = functools.partial(int, base=16)
    from_bin = functools.partial(int, base=2)
    print(f"  from_hex('FF') = {from_hex('FF')}")
    print(f"  from_bin('1010') = {from_bin('1010')}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景 A：预配置请求
# ---------------------------------------------------------------------------

def http_request(url: str, method: str = "GET", timeout: int = 30,
                 headers: dict | None = None) -> dict:
    """模拟 HTTP 请求（真实场景用 requests / httpx）"""
    headers = headers or {}
    return {
        "url": url,
        "method": method,
        "timeout": timeout,
        "headers": headers,
    }


def demo05_preconfigured_request():
    """⑤ 预配置 HTTP 客户端"""
    print("\n⑤ 预配置请求函数")

    BASE = "https://api.example.com"
    AUTH_HEADERS = {"Authorization": "Bearer token123"}

    # 预绑定公共参数
    api_get = functools.partial(
        http_request,
        method="GET",
        timeout=10,
        headers=AUTH_HEADERS,
    )
    api_post = functools.partial(
        http_request,
        method="POST",
        timeout=30,
        headers=AUTH_HEADERS,
    )

    r1 = api_get(f"{BASE}/users")
    r2 = api_post(f"{BASE}/orders")

    print(f"  GET  {r1['url']}  timeout={r1['timeout']}s")
    print(f"  POST {r2['url']}  timeout={r2['timeout']}s")


# ---------------------------------------------------------------------------
# ⑥ 实际场景 B：批量生成专用函数
# ---------------------------------------------------------------------------

def validate(value, min_val, max_val, name: str = "值") -> str:
    if min_val <= value <= max_val:
        return f"{name}={value} ✓"
    return f"{name}={value} ✗ (范围 [{min_val}, {max_val}])"


def demo06_batch_generate():
    """⑥ 用 partial 批量生成专用函数"""
    print("\n⑥ 批量生成专用校验函数")

    validators = {
        "age":      functools.partial(validate, min_val=0,   max_val=120, name="年龄"),
        "score":    functools.partial(validate, min_val=0,   max_val=100, name="分数"),
        "tax_rate": functools.partial(validate, min_val=0.0, max_val=1.0, name="税率"),
    }

    test_data = {
        "age":      [25, -1, 150],
        "score":    [85, 101],
        "tax_rate": [0.13, 1.5],
    }

    for field, fn in validators.items():
        for val in test_data[field]:
            print(f"  {fn(val)}")


# ---------------------------------------------------------------------------
# ⑦ partialmethod
# ---------------------------------------------------------------------------

def demo07_partialmethod():
    """⑦ partialmethod：绑定类方法的默认参数"""
    print("\n⑦ partialmethod")

    class Cell:
        def __init__(self):
            self._alive = False

        def set_state(self, state: bool):
            self._alive = state

        # partialmethod 创建专用方法
        set_alive = functools.partialmethod(set_state, True)
        set_dead  = functools.partialmethod(set_state, False)

        @property
        def alive(self):
            return self._alive

    c = Cell()
    c.set_alive()
    print(f"  set_alive() → {c.alive}")
    c.set_dead()
    print(f"  set_dead()  → {c.alive}")


if __name__ == "__main__":
    demo01_basic()
    demo02_attributes()
    demo03_equivalents()
    demo04_keyword_args()
    demo05_preconfigured_request()
    demo06_batch_generate()
    demo07_partialmethod()
