# coding=utf-8
"""全局上下文 + 抽象基类 + 工厂方法。

对应 ntrade 中的 ntrade/_impl/_runtime/nt_context.py。
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# 全局上下文
# ============================================================

_current_context: Optional[TradeContext] = None
_lock = threading.Lock()


def set_current_context(ctx: TradeContext) -> None:
    global _current_context
    with _lock:
        _current_context = ctx


def get_current_context() -> TradeContext:
    with _lock:
        if _current_context is None:
            raise RuntimeError("TradeContext 未初始化")
        return _current_context


def clear_current_context() -> None:
    global _current_context
    with _lock:
        _current_context = None


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
    """行情数据提供者抽象。对应 ntrade 的 BaseDataProvider。"""

    @abstractmethod
    def get_market_data(self, symbol: str, start: str, end: str) -> List[Dict]:
        """获取历史行情。"""
        ...

    @abstractmethod
    def get_trading_dates(self, start: str, end: str) -> List[str]:
        """获取交易日列表。"""
        ...


class BaseBroker(ABC):
    """交易代理抽象。对应 ntrade 的 BaseBroker。"""

    @abstractmethod
    def order(self, symbol: str, volume: int, price: float) -> int:
        """下单，返回订单号。"""
        ...

    @abstractmethod
    def get_cash(self) -> float:
        """查询可用资金。"""
        ...

    @abstractmethod
    def get_positions(self) -> Dict[str, int]:
        """查询持仓。"""
        ...


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
