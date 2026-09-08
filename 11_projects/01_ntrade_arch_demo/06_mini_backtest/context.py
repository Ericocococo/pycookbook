# coding=utf-8
"""全局上下文 + 抽象基类 + 工厂方法。

对应 ntrade 中的 ntrade/_impl/_runtime/nt_context.py。
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


# ============================================================
# 线程本地上下文（对齐真实 nt_context.py：threading.local 而非全局+Lock）
# ============================================================

_local = threading.local()


def set_current_context(ctx: TradeContext) -> None:
    """设置当前线程的上下文（只影响本线程）。"""
    _local.ctx = ctx


def get_current_context() -> TradeContext:
    """获取当前线程的上下文。未初始化抛 RuntimeError（fail-fast）。"""
    ctx = getattr(_local, "ctx", None)
    if ctx is None:
        raise RuntimeError("TradeContext 未初始化")
    return ctx


def clear_current_context() -> None:
    """清除当前线程的上下文（run() 的 finally 中调用）。"""
    if hasattr(_local, "ctx"):
        del _local.ctx


# ============================================================
# 配置
# ============================================================

@dataclass
class BacktestConfig:
    """回测配置。对应 ntrade 的 BacktestConfig。"""
    symbols: List[str] = field(default_factory=list)
    start: str = "2024-01-01"
    end: str = "2024-12-31"
    initial_cash: float = 1_000_000.0


# ============================================================
# 抽象基类
# ============================================================

class BaseDataProvider(ABC):
    """行情数据提供者抽象。对应 ntrade 的 BaseDataProvider。

    引擎通过 _bar_index 推进"当前 bar 位置"实现防未来函数：
    数据提供者只返回截至该位置的行情（数据只增不减，对齐真实 HisBarMgr）。
    """

    # 类属性默认值：引擎每日推进（provider._bar_index = i）
    _bar_index: int = 0

    @abstractmethod
    def get_market_data(self, symbol: str, start: str = "", end: str = "") -> List[Dict]:
        """获取历史行情（只含当前 bar 及之前）。"""
        ...

    @abstractmethod
    def get_trading_dates(self, start: str = "", end: str = "") -> List[str]:
        """获取交易日列表。"""
        ...


class BaseBroker(ABC):
    """交易代理抽象。对应 ntrade 的 BaseBroker。

    下单/查询为回测与实盘共用的抽象方法；挂单撮合与 T+1 登记是回测
    broker 的扩展能力（真实中 NtBacktestBroker 特有，此处声明占位让
    引擎按接口编程）。
    """

    @abstractmethod
    def order(self, symbol: str, volume: int, price_type: str = "market",
              price: float | None = None) -> int:
        """下单（挂单），返回订单号。price_type: market 市价 / limit 限价。"""
        ...

    @abstractmethod
    def get_cash(self) -> float:
        """查询可用资金。"""
        ...

    @abstractmethod
    def get_positions(self) -> Dict[str, int]:
        """查询持仓。"""
        ...

    # ---- 回测扩展能力（挂单撮合队列，实盘 broker 无）----

    def on_new_day(self) -> None:
        """新交易日开始：T+1 登记清空（昨日买入今日可卖）。"""
        pass

    def match_pending(self, open_prices: Dict[str, float]) -> None:
        """撮合挂单队列（本 bar 开盘价成交）。"""
        del open_prices  # 基类占位：实盘 broker 无撮合队列
        pass

    def get_trades(self) -> list:
        """成交记录列表。"""
        return []


# ============================================================
# TradeContext — 统一入口
# ============================================================

class TradeContext:
    """策略运行上下文。对应 ntrade 的 NtTradeContext。"""

    def __init__(self, config: BacktestConfig,
                 data_provider: BaseDataProvider, broker: BaseBroker):
        self._config = config
        self._data_provider = data_provider
        self._broker = broker

    @classmethod
    def backtest(cls, config: BacktestConfig) -> TradeContext:
        """工厂方法 — 创建回测上下文（延迟导入）。"""
        from backtest_impl import BacktestDataProvider, BacktestBroker
        provider = BacktestDataProvider(config)
        broker = BacktestBroker(config.initial_cash)
        return cls(config=config, data_provider=provider, broker=broker)

    @property
    def data_provider(self) -> BaseDataProvider:
        return self._data_provider

    @property
    def broker(self) -> BaseBroker:
        return self._broker

    @property
    def config(self) -> BacktestConfig:
        return self._config

    def run(self, strategy_fn) -> Dict[str, Any]:
        """运行回测。对应 ntrade 的 NtTradeContext.run()。"""
        set_current_context(self)
        try:
            from engine import BacktestEngine
            engine = BacktestEngine(self, strategy_fn)
            return engine.run()
        finally:
            clear_current_context()
