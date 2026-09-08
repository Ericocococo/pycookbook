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
# Broker — 挂单次日撮合 + T+1 可卖限制
# ============================================================

class BacktestBroker(BaseBroker):
    """回测交易代理。对应 ntrade 的 NtBacktestBroker。

    真实撮合在 C++ CSimulateBroker（ManageActions），语义：
    - 下单 ≠ 成交：order_stock 只把委托送进队列，下一根 bar 开盘才撮合
    - T+1：当日买入不可卖（C++ 盘中不结算、换日清算，Python 侧登记当日买入量）
    mini 版本用纯 Python 复刻这两个语义：order() 挂单 → engine 每日
    on_new_day() + match_pending(开盘价) 撮合。
    """

    def __init__(self, initial_cash: float):
        self._cash = initial_cash
        self._positions: Dict[str, int] = {}   # 总持仓（已含今日买入）
        self._today_bought: Dict[str, int] = {}  # 当日买入量登记（T+1 扣减用）
        self._pending: list = []               # 挂单队列 [dict]
        self._order_id = 0
        self._trades: list = []

    def on_new_day(self) -> None:
        """新交易日开始：昨日买入登记清空 → 昨日买的今天可卖。

        【真实机制的等价简化】真实 NtBacktestBroker 不在换日清空登记：
        `_day_buy_volume` 按 {symbol: {交易日期: 当日买入量}} 键存，查询按
        "当前日期键"匹配，旧日期条目自然失效（且 C++ 换日回调在当日撮合
        之后触发，换日清空会误清新撮合的当日买入）。mini 是单标的单日键
        模型，用"每日开头显式清空"实现同样的效果——引擎顺序保证先清后撮，
        当天撮合成交仍记入新登记（当天不可卖）。
        """
        self._today_bought.clear()

    def order(self, symbol: str, volume: int, price_type: str = "market",
              price: float | None = None) -> int:
        """挂单（入队，不立即成交）。volume 正=买、负=卖。

        对齐真实 order_stock：把委托送进柜台/撮合队列，成交等下一根 bar。
        卖出先做 T+1 校验：可卖 = 总持仓 - 当日买入量。
        """
        qty = abs(volume)
        if volume < 0:
            # T+1 校验：今天刚买的不能卖（真实 C++ 盘中不结算，Python broker
            # 用当日买入登记表还原可卖量——"查询看似透传，实则 Python 侧维护语义"）
            available = self._positions.get(symbol, 0) \
                - self._today_bought.get(symbol, 0)
            if qty > available:
                print(f"    [Broker] 拒绝卖出: 可卖 {available} < {qty}"
                      f"（T+1：当日买入不可卖）")
                return -1

        self._order_id += 1
        self._pending.append({
            "order_id": self._order_id, "symbol": symbol, "volume": volume,
            "price_type": price_type, "price": price,
        })
        side = "买" if volume > 0 else "卖"
        print(f"    [Broker] 挂单 {side} {symbol} x {qty}"
              f"（等待下一根 bar 撮合）")
        return self._order_id

    def match_pending(self, open_prices: Dict[str, float]) -> None:
        """撮合挂单队列：用本 bar 开盘价成交（对应 C++ ManageActions）。

        真实撮合发生在每根 bar 开头、策略决策之前——队列里是"昨天"挂的单，
        行情已推进到今天，市价单按今天开盘价成交。
        """
        for o in self._pending:
            sym, vol = o["symbol"], o["volume"]
            if sym not in open_prices:
                continue
            px: float = open_prices[sym]

            if vol > 0:  # 买入
                cost = vol * px
                if cost > self._cash:
                    print(f"    [Broker] 资金不足，买单作废: 需 {cost:.0f} 可用 {self._cash:.0f}")
                    continue
                self._cash -= cost
                self._positions[sym] = self._positions.get(sym, 0) + vol
                # 记入当日买入登记：今天买的今天不可卖（T+1）
                self._today_bought[sym] = self._today_bought.get(sym, 0) + vol
                side = "买入"
            else:        # 卖出
                self._cash += abs(vol) * px
                self._positions[sym] = self._positions.get(sym, 0) + vol
                if self._positions[sym] <= 0:
                    del self._positions[sym]
                side = "卖出"

            self._trades.append({
                "order_id": o["order_id"], "symbol": sym, "direction": side,
                "volume": abs(vol), "price": px,
            })
            print(f"    [Broker] 成交 {side} {sym} x {abs(vol)}"
                  f" @ {px:.2f}（本 bar 开盘价），剩余资金 {self._cash:.0f}")
        self._pending.clear()   # 当日有效单：本 bar 没成交就作废（不跨日保留）

    def get_cash(self) -> float:
        return self._cash

    def get_positions(self) -> Dict[str, int]:
        return dict(self._positions)

    def get_trades(self) -> list:
        return list(self._trades)
