# coding=utf-8
"""双模式策略兼容 — 一个适配器支持两种写法。

Python 3.12。
运行: python 02_dual_mode.py

演示：
  ① 单函数模式：xtquant 风格，策略是一个无参函数
  ② 生命周期模式：qmttools 风格，init + handlebar 双回调

## 实际问题

ntrade 要兼容两种策略写法：

模式一 — 单函数（xtquant 风格）:
    def strategy():
        data = ntdata.get_market_data_ex(...)
        nttrader.order_stock(...)

模式二 — init/handlebar（qmttools 风格）:
    def init(context):
        context.stock_code = "600519.SH"

    def handlebar(context):
        context.buy("600519.SH", 1000)

两种写法都要能跑。引擎不改，靠适配器搞定。

## 方案

StrategyWrapper 根据传入参数判断模式：
- 只传 strategy_fn → 单函数模式（next 直接调 fn）
- 传 init_fn + handlebar → 生命周期模式（on_start 调 init，next 调 handlebar）

【真实做法对比】ntrade 不是手动传参选模式——策略文件加载后由
strategy_loader 按函数名自动探测（有 handlebar/handle_bar → lifecycle，
否则找 strategy/macd_strategy → single），再用 inspect.signature 内省
handlebar 是否声明第二参。自动探测见 03_auto_detect.py。

## 学到什么

- 同一个适配器支持多种策略接口
- ntrade 如何实现 xtquant/qmttools 双兼容
- （自动探测版见 03_auto_detect.py）
"""

from abc import ABC, abstractmethod


# ============================================================
# 策略协议（同 01_strategy_protocol）
# ============================================================

class IStrategy(ABC):
    @abstractmethod
    def on_start(self):
        ...

    @abstractmethod
    def next(self):
        ...

    @abstractmethod
    def on_stop(self):
        ...


# ============================================================
# 简化的策略上下文 — init/handlebar 模式用
# ============================================================

class BarContext:
    """策略上下文 — 传入 init/handlebar 的参数。

    ntrade 对应: NtBarContext（_context.py）

    用户在 init(ctx) 中设置 ctx.symbol / ctx.cash 等参数，
    在 handlebar(ctx) 中通过 ctx.buy() / ctx.sell() 下单。
    """

    def __init__(self):
        self.symbol = ""
        self.cash = 100_000
        self.position = 0
        self.bar_index = 0

    def buy(self, symbol, volume):
        print(f"    [Context] 买入 {symbol} x {volume}")
        self.position += volume

    def sell(self, symbol, volume):
        print(f"    [Context] 卖出 {symbol} x {volume}")
        self.position -= volume


# ============================================================
# 适配器 — 自动识别模式
# ============================================================

class StrategyWrapper(IStrategy):
    """双模式策略适配器。

    ntrade 中的实现分布在两处：
    - NtQuantTrader.run_backtest(): 判断模式，构造 _wrapped_strategy
    - _BacktestStrategyWrapper: 实际包装

    单函数模式:
        def next(self):
            self._fn()

    生命周期模式:
        def on_start(self):
            self._init_fn(self._ctx)      # 用户的 init(context)
        def next(self):
            self._handlebar(self._ctx)     # 用户的 handlebar(context)
    """

    def __init__(self, strategy_fn=None, init_fn=None, handlebar=None):
        if handlebar is not None:
            # 生命周期模式
            self._mode = "lifecycle"
            self._init_fn = strategy_fn or init_fn  # 第一个参数当 init
            self._handlebar = handlebar
            self._ctx = BarContext()
        elif strategy_fn is not None:
            # 单函数模式
            self._mode = "single"
            self._fn = strategy_fn
        else:
            raise ValueError("至少传入 strategy_fn 或 handlebar")

    def on_start(self):
        if self._mode == "lifecycle" and self._init_fn:
            print("  [Wrapper] 生命周期模式 → 调用 init(context)")
            self._init_fn(self._ctx)
        else:
            print("  [Wrapper] 单函数模式 → 无 init")

    def next(self):
        if self._mode == "lifecycle":
            self._ctx.bar_index += 1
            self._handlebar(self._ctx)
        else:
            self._fn()

    def on_stop(self):
        print(f"  [Wrapper] 策略结束 (模式={self._mode})")


# ============================================================
# 引擎（同 01_strategy_protocol）
# ============================================================

class Engine:
    def __init__(self, dates, strategy: IStrategy):
        self._dates = dates
        self._strategy = strategy

    def run(self):
        self._strategy.on_start()
        for i, date in enumerate(self._dates):
            print(f"\n  --- {date} ---")
            self._strategy.next()
        print()
        self._strategy.on_stop()


# ============================================================
# 两种策略写法
# ============================================================

# 写法一：单函数（xtquant 风格）
def simple_strategy():
    """策略不需要 context，直接用模块级函数。"""
    print("    → [单函数策略] 检查行情, 决策...")


# 写法二：init + handlebar（qmttools 风格）
def init(context: BarContext):
    """初始化：设置参数。"""
    context.symbol = "600519.SH"
    context.cash = 200_000
    print(f"    → [init] 设置标的={context.symbol}, 资金={context.cash}")


def handlebar(context: BarContext):
    """每 bar 调用：策略决策。"""
    print(f"    → [handlebar] bar={context.bar_index}, "
          f"持仓={context.position}, 决策中...")
    if context.bar_index == 2 and context.position == 0:
        context.buy(context.symbol, 100)


# ============================================================
# 运行演示
# ============================================================

def demo01_single_fn():
    """① 单函数模式：xtquant 风格，策略是一个无参函数，next() 直接调用。"""
    print("① 单函数模式（xtquant 风格）")
    dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
    wrapper = StrategyWrapper(strategy_fn=simple_strategy)
    Engine(dates, wrapper).run()


def demo02_lifecycle():
    """② 生命周期模式：qmttools 风格，init + handlebar 双回调。"""
    print("\n② 生命周期模式（init + handlebar，qmttools 风格）")
    dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
    wrapper = StrategyWrapper(strategy_fn=init, handlebar=handlebar)
    Engine(dates, wrapper).run()
    # 同一个引擎，同一个 Engine.run()，两种策略都能跑
    # ntrade 的 NtQuantTrader.run() 也是这样分派的


if __name__ == "__main__":
    demo01_single_fn()
    demo02_lifecycle()
