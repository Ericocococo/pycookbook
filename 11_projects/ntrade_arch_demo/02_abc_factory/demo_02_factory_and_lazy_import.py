# coding=utf-8
"""工厂方法 + 延迟导入 — 按配置自动创建正确的实现。

## 上一节的问题

策略启动时要自己创建 BacktestProvider 或 LiveProvider，
还要知道这些类在哪、怎么 import。

## 方案：工厂方法 + 延迟导入

1. 用 dataclass 定义配置（BacktestConfig / LiveConfig）
2. TradeContext 提供 classmethod 工厂：backtest(config) / live(config)
3. 工厂方法内部 import 具体实现 — 未安装的模块不会在 import 时报错

ntrade 中 NtTradeContext.backtest() / .live() 就是这个模式。
实盘依赖 QMT SDK，没安装时 import ntrade 不会报错，
只有真正调 NtTradeContext.live() 时才会触发 import。

## 学到什么

- 工厂方法：策略不 new 对象，让工厂按配置决定
- 延迟导入：解决可选依赖问题
- dataclass 配置对象
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


# ============================================================
# 配置 — ntrade 中的 BacktestConfig / LiveConfig
# ============================================================

@dataclass
class BacktestConfig:
    """回测配置。"""
    symbols: List[str] = field(default_factory=list)
    start: str = "2024-01-01"
    end: str = "2024-12-31"
    initial_cash: float = 1_000_000.0


@dataclass
class LiveConfig:
    """实盘配置。"""
    account_id: str = ""
    broker_url: str = "wss://broker.example.com"


# ============================================================
# 抽象基类（同 demo_01）
# ============================================================

class BaseProvider(ABC):
    @abstractmethod
    def get_data(self, symbol):
        ...

    @abstractmethod
    def place_order(self, symbol, volume):
        ...


# ============================================================
# 具体实现（模拟放在同文件，实际项目中放在不同模块）
# ============================================================

class BacktestProvider(BaseProvider):
    def __init__(self, config: BacktestConfig):
        self._config = config
        print(f"  [BacktestProvider] 加载 {len(config.symbols)} 只标的, "
              f"{config.start} ~ {config.end}")

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "本地CSV", "price": 10.5}

    def place_order(self, symbol, volume):
        return f"[模拟成交] {symbol} x {volume} 股"


class LiveProvider(BaseProvider):
    def __init__(self, config: LiveConfig):
        self._config = config
        print(f"  [LiveProvider] 连接 {config.broker_url}, 账号 {config.account_id}")

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "交易所实时", "price": 10.8}

    def place_order(self, symbol, volume):
        return f"[真实下单] {symbol} x {volume} 股"


# ============================================================
# TradeContext — 带工厂方法的统一入口
# ============================================================

class TradeContext:
    """统一上下文 — ntrade 中的 NtTradeContext。

    策略只通过 TradeContext.backtest(config) 或 TradeContext.live(config) 创建，
    不直接 new BacktestProvider / LiveProvider。
    """

    def __init__(self, mode: str, config, provider: BaseProvider):
        self._mode = mode
        self._config = config
        self._provider = provider

    @classmethod
    def backtest(cls, config: BacktestConfig) -> "TradeContext":
        """工厂方法 — 创建回测上下文。

        ntrade 中的真实代码：
            @classmethod
            def backtest(cls, config):
                from ntrade._impl.backtest._data import NtBacktestDataProvider  # 延迟导入
                from ntrade._impl.backtest._broker import NtBacktestBroker
                ...

        延迟导入的好处：没安装 C++ 引擎时 import ntrade 不报错。
        """
        # 实际项目中这里是延迟导入：
        # from myproject.backtest import BacktestProvider
        provider = BacktestProvider(config)
        return cls(mode="backtest", config=config, provider=provider)

    @classmethod
    def live(cls, config: LiveConfig) -> "TradeContext":
        """工厂方法 — 创建实盘上下文。"""
        provider = LiveProvider(config)
        return cls(mode="live", config=config, provider=provider)

    @property
    def provider(self) -> BaseProvider:
        return self._provider

    @property
    def mode(self) -> str:
        return self._mode


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    # ---- 回测：传 BacktestConfig，工厂自动创建 BacktestProvider ----
    print("=== 回测模式 ===")
    ctx = TradeContext.backtest(BacktestConfig(
        symbols=["600519.SH", "000001.SZ"],
        start="2024-01-01",
        end="2024-06-30",
    ))
    print(f"  模式: {ctx.mode}")
    print(f"  数据: {ctx.provider.get_data('600519.SH')}")

    # ---- 实盘：传 LiveConfig，工厂自动创建 LiveProvider ----
    print("\n=== 实盘模式 ===")
    ctx = TradeContext.live(LiveConfig(
        account_id="test_001",
        broker_url="wss://broker.example.com",
    ))
    print(f"  模式: {ctx.mode}")
    print(f"  数据: {ctx.provider.get_data('600519.SH')}")
