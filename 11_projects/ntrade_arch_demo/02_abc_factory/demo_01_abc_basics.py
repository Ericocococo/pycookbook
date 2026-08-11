# coding=utf-8
"""抽象基类（ABC）— 用接口约束实现。

## 上一节的问题

BacktestProvider 和 LiveProvider 没有任何约束，
如果某个实现忘了写 get_data() 方法，直到运行时才会报错。

## 方案：用 ABC 定义接口

用 @abstractmethod 强制每个子类必须实现指定方法。
少写一个就无法实例化 — 错误在创建对象时暴露，而不是调用时。

ntrade 中的 BaseDataProvider / BaseBroker 就是这么做的。

## 学到什么

- ABC + @abstractmethod 的用法
- 抽象方法 vs 带默认实现的方法（ntrade 两种都用了）
- 何时用 abstract、何时给默认实现
"""

from abc import ABC, abstractmethod


# ============================================================
# 抽象基类 — 定义「数据提供者必须有哪些方法」
# ============================================================

class BaseProvider(ABC):
    """数据提供者抽象基类。

    ntrade 对应: BaseDataProvider（nt_context.py）
    """

    # ---- 必须实现的方法（@abstractmethod）----
    # 回测/实盘都要用，所以强制子类实现

    @abstractmethod
    def get_data(self, symbol):
        """获取行情数据。子类必须实现。"""
        ...

    @abstractmethod
    def place_order(self, symbol, volume):
        """下单。子类必须实现。"""
        ...

    # ---- 带默认实现的方法 ----
    # 不是所有模式都需要，给个默认行为
    # ntrade 中 subscribe_quote() 默认抛 NotSupportedInBacktestError
    # get_divid_factors() 默认抛 NotImplementedError

    def subscribe_realtime(self, symbol, callback):
        """订阅实时行情 — 仅实盘需要，回测子类不用覆盖。"""
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 subscribe_realtime")


# ============================================================
# 具体实现
# ============================================================

class BacktestProvider(BaseProvider):
    """回测实现 — 必须实现 get_data + place_order，不用管 subscribe_realtime。"""

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "本地CSV", "price": 10.5}

    def place_order(self, symbol, volume):
        return f"[模拟成交] {symbol} x {volume} 股"


class LiveProvider(BaseProvider):
    """实盘实现 — 除了必须方法，还覆盖了 subscribe_realtime。"""

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "交易所实时", "price": 10.8}

    def place_order(self, symbol, volume):
        return f"[真实下单] {symbol} x {volume} 股"

    def subscribe_realtime(self, symbol, callback):
        """实盘覆盖了默认实现，真正支持实时订阅。"""
        print(f"  已订阅 {symbol} 实时行情")
        return 1


# ============================================================
# 演示：少实现一个方法会怎样？
# ============================================================

class BrokenProvider(BaseProvider):
    """故意只实现 get_data，不实现 place_order。"""

    def get_data(self, symbol):
        return {"symbol": symbol, "price": 0}

    # place_order 没实现！


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    # 正常创建
    print("=== 正常创建 BacktestProvider ===")
    bt = BacktestProvider()
    print(f"  {bt.get_data('600519.SH')}")
    print(f"  {bt.place_order('600519.SH', 1000)}")

    # 实盘的 subscribe_realtime 正常工作
    print("\n=== LiveProvider 支持 subscribe_realtime ===")
    live = LiveProvider()
    live.subscribe_realtime("600519.SH", lambda: None)

    # 回测的 subscribe_realtime 抛异常（默认实现）
    print("\n=== BacktestProvider 不支持 subscribe_realtime ===")
    try:
        bt.subscribe_realtime("600519.SH", lambda: None)
    except NotImplementedError as e:
        print(f"  正确抛出: {e}")

    # 少实现方法 → 无法实例化（错误提前暴露）
    print("\n=== BrokenProvider 少实现了 place_order ===")
    try:
        broken = BrokenProvider()
    except TypeError as e:
        print(f"  无法实例化: {e}")
