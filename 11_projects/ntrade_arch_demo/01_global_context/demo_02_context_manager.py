# coding=utf-8
"""用上下文管理器让 set/clear 更安全。

## 上一节的问题

手动 set_provider / clear_provider 容易忘记 clear，
尤其是策略抛异常时 clear 可能被跳过。

## 方案：上下文管理器

用 with 语句自动管理生命周期：
    with use_provider(BacktestProvider()):
        my_strategy()    # 退出 with 自动 clear

ntrade 中 NtTradeContext.run() 的 try/finally 就是这个思路。

## 学到什么

- 上下文管理器保证资源清理
- ntrade 中 set_current_context / clear_current_context 的最佳实践
"""

import threading
from contextlib import contextmanager


# ---- 全局上下文（同 demo_01） ----

_current_provider = None
_lock = threading.Lock()


def set_provider(provider):
    global _current_provider
    with _lock:
        _current_provider = provider


def get_provider():
    with _lock:
        if _current_provider is None:
            raise RuntimeError("未设置 provider")
        return _current_provider


def clear_provider():
    global _current_provider
    with _lock:
        _current_provider = None


@contextmanager
def use_provider(provider):
    """上下文管理器 — 自动 set/clear。

    ntrade 中 NtTradeContext.run() 用的是 try/finally 实现同样效果：
        set_current_context(self)
        try:
            adapter.run()
        finally:
            clear_current_context()

    这里用 @contextmanager 更 Pythonic。
    """
    set_provider(provider)
    try:
        yield provider
    finally:
        clear_provider()


# ---- 两种 Provider（同 demo_01） ----

class BacktestProvider:
    def get_data(self, symbol):
        return {"symbol": symbol, "source": "本地CSV", "price": 10.5}

    def place_order(self, symbol, volume):
        return f"[模拟成交] {symbol} x {volume} 股"


class LiveProvider:
    def get_data(self, symbol):
        return {"symbol": symbol, "source": "交易所实时", "price": 10.8}

    def place_order(self, symbol, volume):
        return f"[真实下单] {symbol} x {volume} 股"


# ---- 模块级函数（同 demo_01） ----

def get_data(symbol):
    return get_provider().get_data(symbol)


def place_order(symbol, volume):
    return get_provider().place_order(symbol, volume)


# ---- 策略（同 demo_01） ----

def my_strategy():
    data = get_data("600519.SH")
    print(f"  行情来源: {data['source']}, 价格: {data['price']}")
    if data["price"] < 11:
        result = place_order("600519.SH", 1000)
        print(f"  {result}")


# ============================================================
# 运行演示 — 对比手动 set/clear vs 上下文管理器
# ============================================================

if __name__ == "__main__":
    # 用 with 语句，即使 my_strategy 抛异常也能正确 clear
    print("=== 回测模式（with 语句）===")
    with use_provider(BacktestProvider()):
        my_strategy()

    print("\n=== 实盘模式（with 语句）===")
    with use_provider(LiveProvider()):
        my_strategy()

    # 验证：退出 with 后上下文已清除
    print("\n=== 验证上下文已清除 ===")
    try:
        get_data("600519.SH")
    except RuntimeError as e:
        print(f"  正确抛出异常: {e}")
