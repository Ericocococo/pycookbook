# coding=utf-8
"""全局上下文 + 模块级函数转发 — ntrade 的核心设计模式。

## 要解决的问题

策略代码希望这样写：
    import api
    api.get_data("AAPL")      # 不关心数据从哪来
    api.place_order("AAPL")   # 不关心是模拟还是真下单

但实际数据来源取决于运行模式（回测读本地文件，实盘连交易所）。
如何让策略代码不感知运行模式？

## 方案：线程本地全局上下文 + 模块级函数转发

1. 用 threading.local 存当前 provider（每线程一份，互不干扰）
2. 模块级函数（api.get_data）内部只做一件事：get_provider().get_data(...)
3. 启动时 set 具体实现，结束时 clear（demo_02 用 with 语句保证清理）

策略代码只 import api，不 import 任何具体实现。
这就是 ntrade 中 ntdata.py / nttrader.py 的做法。

## 为什么是 threading.local 而不是「全局变量 + Lock」？

- 全局变量 + Lock：只保证"同一时刻只有一个人能改"，不隔离线程——
  A 任务 set 了回测 provider，B 线程 get 到的是 A 的 → 上下文串了
- threading.local：每个线程有自己的副本，A 线程 set 只影响 A 线程

ntrade 的回测服务是多线程并发跑任务的，上下文必须按线程隔离，
所以真实代码（_impl/_runtime/nt_context.py）用的是 threading.local。

## 学到什么

- 全局上下文模式（Service Locator 的简化版）
- 模块级函数做「薄转发层」
- threading.local：线程级隔离 vs Lock 的互斥（两者解决不同问题）
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
# 第二步：线程本地上下文管理（ntrade 中的 nt_context.py）
# ============================================================

# threading.local：每个线程有独立的存储空间
# _local.provider = X 只影响"当前线程"，其他线程 get 不到也改不了
_local = threading.local()


def set_provider(provider):
    """设置当前线程的数据提供者。ntrade 对应 set_current_context()。"""
    _local.provider = provider


def get_provider():
    """获取当前线程的数据提供者。ntrade 对应 get_current_context()。"""
    provider = getattr(_local, "provider", None)
    if provider is None:
        raise RuntimeError("未设置 provider，请先调用 set_provider()")
    return provider


def clear_provider():
    """清除当前线程的提供者。ntrade 对应 clear_current_context()。"""
    if hasattr(_local, "provider"):
        del _local.provider


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

def _backtest_job():
    """回测线程任务：set 回测 provider → 跑两轮 → clear。"""
    set_provider(BacktestProvider())
    try:
        for _ in range(2):
            _run_and_print("回测线程")
    finally:
        clear_provider()


def _live_job():
    """实盘线程任务：set 实盘 provider → 跑两轮 → clear。"""
    set_provider(LiveProvider())
    try:
        for _ in range(2):
            _run_and_print("实盘线程")
    finally:
        clear_provider()


def _run_and_print(name):
    """取一次数据并打印来源（判断该线程拿到的是哪个 provider）。"""
    data = get_data("600519.SH")
    print(f"    [{name}] 行情来源: {data['source']}, 价格: {data['price']}")


if __name__ == "__main__":
    # ---- 单线程：回测模式 ----
    print("=== 回测模式 ===")
    set_provider(BacktestProvider())
    try:
        my_strategy()
    finally:
        clear_provider()

    # ---- 单线程：实盘模式 ----
    print("\n=== 实盘模式 ===")
    set_provider(LiveProvider())
    try:
        my_strategy()
    finally:
        clear_provider()

    # 同一个 my_strategy() 函数，零改动切换了运行模式
    # 这就是 ntrade 能做到「策略代码写一份」的原因

    # ---- 多线程并发：两个任务各跑各的模式 ----
    # 关键验证：若用"全局变量+Lock"，线程 B 可能 get 到线程 A set 的 provider；
    # threading.local 保证每线程独立——回测线程始终看到本地CSV、
    # 实盘线程始终看到交易所实时，互不串扰（真实回测服务正是多线程并发跑任务）
    print("\n=== 多线程并发：回测任务 + 实盘任务同时跑 ===")
    t1 = threading.Thread(target=_backtest_job)
    t2 = threading.Thread(target=_live_job)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
