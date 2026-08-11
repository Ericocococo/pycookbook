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

        对应 C++ BacktestEngine.run_multi() 的流程：
        1. 遍历每个交易日
        2. 更新当前 bar 位置（防未来函数）
        3. 调用策略函数
        4. 收集结果
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
            # 更新 bar 位置（让 DataProvider 只返回当前 bar 及之前的数据）
            provider._bar_index = i

            print(f"\n--- {date} (bar {i + 1}/{len(dates)}) ---")

            # 调用策略函数（策略内部通过 api.xxx() → get_current_context() 取数据/下单）
            self._strategy_fn()

            # 记录净值
            cash = broker.get_cash()
            positions = broker.get_positions()
            # 简化：用最后一根 bar 的收盘价估算持仓市值
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
