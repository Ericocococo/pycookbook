# coding=utf-8
"""回测实现 — DataProvider + Broker。

对应 ntrade 中的:
- ntrade/_impl/backtest/_data/ 下的 Mixin 组装
- ntrade/_impl/backtest/_broker.py
"""

from typing import Dict, List
from context import BaseDataProvider, BaseBroker, BacktestConfig


# ============================================================
# 模拟行情数据（实际项目读 parquet / C++ CBarMgr）
# ============================================================

FAKE_MARKET_DATA = {
    "600519.SH": [
        {"date": "2024-01-02", "open": 1680, "high": 1700, "low": 1675, "close": 1695, "volume": 15000},
        {"date": "2024-01-03", "open": 1695, "high": 1710, "low": 1690, "close": 1705, "volume": 18000},
        {"date": "2024-01-04", "open": 1705, "high": 1720, "low": 1700, "close": 1715, "volume": 20000},
        {"date": "2024-01-05", "open": 1715, "high": 1730, "low": 1710, "close": 1725, "volume": 22000},
        {"date": "2024-01-08", "open": 1725, "high": 1735, "low": 1715, "close": 1720, "volume": 16000},
    ],
    "000001.SZ": [
        {"date": "2024-01-02", "open": 9.5, "high": 9.8, "low": 9.4, "close": 9.7, "volume": 500000},
        {"date": "2024-01-03", "open": 9.7, "high": 10.0, "low": 9.6, "close": 9.9, "volume": 600000},
        {"date": "2024-01-04", "open": 9.9, "high": 10.1, "low": 9.8, "close": 10.0, "volume": 550000},
        {"date": "2024-01-05", "open": 10.0, "high": 10.2, "low": 9.9, "close": 10.1, "volume": 580000},
        {"date": "2024-01-08", "open": 10.1, "high": 10.3, "low": 10.0, "close": 10.2, "volume": 520000},
    ],
}

TRADING_DATES = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-08"]


# ============================================================
# Mixin — 拆分数据维度（简化版，只演示两个）
# ============================================================

class MarketMixin:
    """行情 Mixin。对应 ntrade 的 MarketMixin。

    ntrade 中通过 self._cpp_ctx.get_his_df(sym) 从 C++ 获取截至当前 bar 的行情，
    这里用 self._bar_index 模拟「只能看到当前 bar 及之前的数据」（防未来函数）。
    """

    def get_market_data(self, symbol: str, start: str = '', end: str = '') -> List[Dict]:
        all_bars = FAKE_MARKET_DATA.get(symbol, [])
        # 只返回当前 bar 及之前的数据（防未来函数）
        cutoff = getattr(self, '_bar_index', len(all_bars))
        bars = all_bars[:cutoff + 1]

        if start:
            bars = [b for b in bars if b["date"] >= start]
        if end:
            bars = [b for b in bars if b["date"] <= end]
        return bars


class CalendarMixin:
    """日历 Mixin。对应 ntrade 的 CalendarMixin。"""

    def get_trading_dates(self, start: str = '', end: str = '') -> List[str]:
        dates = TRADING_DATES
        if start:
            dates = [d for d in dates if d >= start]
        if end:
            dates = [d for d in dates if d <= end]
        return dates


# ============================================================
# DataProvider — Mixin 组装
# ============================================================

class BacktestDataProvider(MarketMixin, CalendarMixin, BaseDataProvider):
    """回测数据提供者。对应 ntrade 的 NtBacktestDataProvider。

    通过多继承把 MarketMixin + CalendarMixin 组装在一起。
    """

    def __init__(self, config: BacktestConfig):
        self._config = config
        self._bar_index = 0


# ============================================================
# Broker — 模拟交易
# ============================================================

class BacktestBroker(BaseBroker):
    """回测交易代理。对应 ntrade 的 NtBacktestBroker。

    ntrade 中通过 C++ CSimulateBroker 撮合，这里纯 Python 模拟。
    """

    def __init__(self, initial_cash: float):
        self._cash = initial_cash
        self._positions: Dict[str, int] = {}
        self._order_id = 0
        self._trades: list = []

    def order(self, symbol: str, volume: int, price: float) -> int:
        cost = volume * price
        if volume > 0 and cost > self._cash:
            print(f"    [Broker] 资金不足: 需要 {cost:.0f}, 可用 {self._cash:.0f}")
            return -1

        self._order_id += 1
        if volume > 0:
            # 买入
            self._cash -= cost
            self._positions[symbol] = self._positions.get(symbol, 0) + volume
        else:
            # 卖出（volume 为负数）
            self._cash += abs(volume) * price
            self._positions[symbol] = self._positions.get(symbol, 0) + volume
            if self._positions[symbol] <= 0:
                del self._positions[symbol]

        direction = "买入" if volume > 0 else "卖出"
        self._trades.append({
            "order_id": self._order_id,
            "symbol": symbol,
            "direction": direction,
            "volume": abs(volume),
            "price": price,
        })
        print(f"    [Broker] {direction} {symbol} x {abs(volume)} @ {price:.2f}, "
              f"剩余资金 {self._cash:.0f}")
        return self._order_id

    def get_cash(self) -> float:
        return self._cash

    def get_positions(self) -> Dict[str, int]:
        return dict(self._positions)

    def get_trades(self) -> list:
        return list(self._trades)
