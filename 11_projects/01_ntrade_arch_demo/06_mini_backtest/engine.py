# coding=utf-8
"""回测引擎 — 逐 bar 驱动策略。

对应 ntrade 中的:
- ntrade/_impl/backtest/_adapter.py（NtBacktestAdapter）
- pycpp_quant 中的 C++ BacktestEngine

ntrade 的真实流程：
1. Adapter 加载行情数据 → 创建 C++ CDataProvider → 创建引擎
2. 引擎注册策略（CPyStrategy 接口）
3. 引擎逐 bar 驱动：on_start → [next × N bars] → on_stop
4. 策略的 next() 中调用 ntdata/nttrader 模块级函数

这里用纯 Python 模拟这个流程。
"""

from typing import Any, Callable, Dict
from context import TradeContext
from backtest_impl import TRADING_DATES


class BacktestEngine:
    """回测引擎。对应 ntrade 的 NtBacktestAdapter + C++ BacktestEngine。"""

    def __init__(self, ctx: TradeContext, strategy_fn: Callable):
        self._ctx = ctx
        self._strategy_fn = strategy_fn

    def run(self) -> Dict[str, Any]:
        """逐 bar 驱动策略。

        mini 每日顺序（与 C++ OnStrategyNext 语义等价，见下注）：
            1. 推进 bar（provider._bar_index，防未来函数——数据只增不减，
               策略只能看到截至当前推进位置的行）
            2. 新交易日: broker.on_new_day()（昨日买入登记清空 → 可卖）
            3. 撮合昨日挂单: broker.match_pending(本 bar 开盘价) ← 挂单次日撮合
            4. 调策略函数（其 api.order 只是挂单，今天不再成交）
            5. 收盘按最新价记录净值

        【顺序注】真实 C++ 顺序是"撮合在前、换日回调在后"：
        ManageActions（撮合昨日单）→ on_market_open（换日登记处理）→ …
        → next()。mini 把"清登记"挪到撮合之前——因为真实登记按日期键
        区分（换日回调在撮合后触发，清空会误清新撮合的当日买入，见
        backtest_impl.py on_new_day 注释与 00_design 红线⑤），而 mini
        是单键模型，先清后撮同样保证"当日撮合成交记入新登记（当日不可卖）"。
        两种顺序殊途同归：真实靠日期键、mini 靠先后次序。
        """
        config = self._ctx.config
        provider = self._ctx.data_provider
        broker = self._ctx.broker

        # 过滤配置范围内的交易日
        dates = [d for d in TRADING_DATES if config.start <= d <= config.end]

        print(f"[Engine] 回测开始: {dates[0]} ~ {dates[-1]}, "
              f"标的 {config.symbols}, 初始资金 {config.initial_cash:,.0f}")

        equity_curve = []

        for i, date in enumerate(dates):
            # ① 更新 bar 位置（让 DataProvider 只返回当前 bar 及之前的数据）
            provider._bar_index = i

            print(f"\n--- {date} (bar {i + 1}/{len(dates)}) ---")

            # ② 新交易日 → 昨日买入今日可卖（T+1 登记清空）
            broker.on_new_day()

            # ③ 撮合队列：昨日挂的单，按本 bar 开盘价成交
            #   （行情已推进到本 bar，市价单=开盘价——不是昨收！）
            open_prices = {}
            for sym in config.symbols:
                bars = provider.get_market_data(sym)
                if bars:
                    open_prices[sym] = bars[-1]["open"]
            broker.match_pending(open_prices)

            # ④ 调用策略函数（策略内部 api.xxx() → get_current_context() 取数/挂单）
            self._strategy_fn()

            # ⑤ 记录净值（收盘价估算持仓市值）
            cash = broker.get_cash()
            positions = broker.get_positions()
            market_value = 0
            for sym, vol in positions.items():
                bars = provider.get_market_data(sym)
                if bars:
                    market_value += bars[-1]["close"] * vol

            equity = cash + market_value
            equity_curve.append({"date": date, "equity": equity, "cash": cash})

        print(f"\n[Engine] 回测结束")

        return {
            "equity_curve": equity_curve,
            "trades": broker.get_trades(),
            "final_cash": broker.get_cash(),
            "final_positions": broker.get_positions(),
        }
