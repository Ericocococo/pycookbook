# coding=utf-8
"""全局上下文 + 模块级函数转发 — ntrade 的核心设计模式。

## 要解决的问题

策略代码希望这样写：
    import api
    api.get_data("AAPL")      # 不关心数据从哪来
    api.place_order("AAPL")   # 不关心是模拟还是真下单

但实际数据来源取决于运行模式（回测读本地文件，实盘连交易所）。
如何让策略代码不感知运行模式？

## 方案：全局上下文 + 模块级函数转发

1. 定义一个全局变量 _current_provider，用 set/get 管理
2. 模块级函数（api.get_data）内部只做一件事：get_provider().get_data(...)
3. 启动时 set 具体实现，结束时 clear

策略代码只 import api，不 import 任何具体实现。
这就是 ntrade 中 ntdata.py / nttrader.py 的做法。

## 学到什么

- 全局上下文模式（Service Locator 的简化版）
- 模块级函数做「薄转发层」
- threading.Lock 保证线程安全
"""

import threading

# ============================================================
# 第一步：定义两种数据提供者（模拟回测 vs 实盘）
# ============================================================

class BacktestProvider:
    """回测数据提供者 — 从本地文件读数据。"""

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "本地CSV", "price": 10.5}

    def place_order(self, symbol, volume):
        return f"[模拟成交] {symbol} x {volume} 股"


class LiveProvider:
    """实盘数据提供者 — 从交易所拉数据。"""

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "交易所实时", "price": 10.8}

    def place_order(self, symbol, volume):
        return f"[真实下单] {symbol} x {volume} 股"


# ============================================================
# 第二步：全局上下文管理（ntrade 中的 nt_context.py）
# ============================================================

_current_provider = None
_lock = threading.Lock()


def set_provider(provider):
    """设置当前数据提供者。ntrade 中对应 set_current_context()。"""
    global _current_provider
    with _lock:
        _current_provider = provider


def get_provider():
    """获取当前数据提供者。ntrade 中对应 get_current_context()。"""
    with _lock:
        if _current_provider is None:
            raise RuntimeError("未设置 provider，请先调用 set_provider()")
        return _current_provider


def clear_provider():
    """清除当前提供者。ntrade 中对应 clear_current_context()。"""
    global _current_provider
    with _lock:
        _current_provider = None


# ============================================================
# 第三步：模块级函数 — 策略的唯一入口（ntrade 中的 _impl/ntdata.py）
#
# 每个函数只做一件事：转发到 get_provider().xxx()
# 策略代码 import 这些函数就行，不关心谁在背后干活
# ============================================================

def get_data(symbol):
    """获取行情数据。"""
    return get_provider().get_data(symbol)


def place_order(symbol, volume):
    """下单。"""
    return get_provider().place_order(symbol, volume)


# ============================================================
# 第四步：策略函数 — 注意，它不 import 任何具体实现
# ============================================================

def my_strategy():
    """一个简单策略：获取数据，如果价格低于 11 就买入。"""
    data = get_data("600519.SH")
    print(f"  行情来源: {data['source']}, 价格: {data['price']}")
    if data["price"] < 11:
        result = place_order("600519.SH", 1000)
        print(f"  {result}")
    else:
        print("  价格太高，不买")


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    # ---- 回测模式 ----
    print("=== 回测模式 ===")
    set_provider(BacktestProvider())
    try:
        my_strategy()
    finally:
        clear_provider()

    # ---- 实盘模式 ----
    print("\n=== 实盘模式 ===")
    set_provider(LiveProvider())
    try:
        my_strategy()
    finally:
        clear_provider()

    # 同一个 my_strategy() 函数，零改动切换了运行模式
    # 这就是 ntrade 能做到「策略代码写一份」的原因
