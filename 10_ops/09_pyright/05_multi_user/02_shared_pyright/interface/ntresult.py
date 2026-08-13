#coding=utf-8
"""回测结果类型定义 — 供 NtQuantTrader.run_backtest 返回值的类型标注。

用法:

    from ntrade.interface.ntresult import BacktestResult

    result: BacktestResult = trader.run_backtest(strategy)
    print(f"净值: {result['equity']:.2f}")
    print(f"交易次数: {len(result['trades'])}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional


class BacktestResult(TypedDict, total=False):
    """NtQuantTrader.run_backtest() 的返回值结构。"""
    cash: float
    """回测结束时的可用资金。"""
    equity: float
    """回测结束时的总资产（现金+市值）。"""
    equity_curve: Any
    """净值曲线，DataFrame 或 list。"""
    trades: List[Dict[str, Any]]
    """交易记录列表。"""
    paint_data: Optional[Dict[str, Dict[str, float]]]
    """paint 指标数据。"""
