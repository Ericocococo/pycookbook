# coding=utf-8
"""C++ 优先 / Python 兜底的双路径模式。

## 实际问题

ntrade 的 Mixin 不是简单返回固定数据，而是：
1. 优先调 C++ 引擎（速度快）
2. C++ 出错或没初始化时，回退到 Python 实现

这个模式在每个 Mixin 中重复出现。

## 学到什么

- try/except 实现「优先路径 + 兜底路径」
- 怎样在 Mixin 中引用共享状态（如 self._engine）
- ntrade 每个 Mixin 的真实模式
"""

from abc import ABC, abstractmethod


# ============================================================
# 模拟外部引擎（对应 ntrade 中的 C++ CDataProvider）
# ============================================================

class FastEngine:
    """模拟 C++ 引擎 — 速度快但可能不可用。"""

    def __init__(self, available=True):
        self._available = available

    def get_trading_dates(self, start, end):
        if not self._available:
            raise RuntimeError("C++ 引擎未初始化")
        return ["2024-01-02", "2024-01-03"]

    def get_sector_list(self):
        if not self._available:
            raise RuntimeError("C++ 引擎未初始化")
        return ["沪深300", "中证500"]


# ============================================================
# Mixin — 双路径模式
# ============================================================

class BaseProvider(ABC):
    @abstractmethod
    def get_trading_dates(self, start, end):
        ...

    @abstractmethod
    def get_sector_list(self):
        ...


class CalendarMixin:
    """日历 Mixin — C++ 优先，Python 兜底。

    ntrade 中 CalendarMixin.get_trading_dates 的真实逻辑：
        try:
            return self._cpp_data_provider.get_trading_dates(start_ns, end_ns)
        except Exception:
            return self._python_fallback_trading_dates(start, end)
    """

    def get_trading_dates(self, start, end):
        # 路径1：尝试走快速引擎
        try:
            result = self._engine.get_trading_dates(start, end)
            print(f"    [CalendarMixin] 走 C++ 快速路径")
            return result
        except Exception:
            pass

        # 路径2：Python 兜底（读本地文件等）
        print(f"    [CalendarMixin] C++ 不可用，走 Python 兜底")
        return ["2024-01-02", "2024-01-03", "2024-01-04"]


class SectorMixin:
    """板块 Mixin — 同样的双路径模式。"""

    def get_sector_list(self):
        try:
            result = self._engine.get_sector_list()
            print(f"    [SectorMixin] 走 C++ 快速路径")
            return result
        except Exception:
            pass

        print(f"    [SectorMixin] C++ 不可用，走 Python 兜底")
        return ["沪深300(py)", "中证500(py)", "科创50(py)"]


# ============================================================
# 组装
# ============================================================

class BacktestProvider(CalendarMixin, SectorMixin, BaseProvider):
    """回测数据提供者 — Mixin 引用 self._engine。

    ntrade 中 _engine 对应 self._cpp_data_provider，
    由 NtBacktestAdapter 在引擎启动时注入。
    """

    def __init__(self, engine=None):
        self._engine = engine


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    # 场景1：C++ 引擎可用 → 走快速路径
    print("=== 场景1：C++ 引擎可用 ===")
    engine = FastEngine(available=True)
    provider = BacktestProvider(engine=engine)
    print(f"  交易日: {provider.get_trading_dates('2024-01-01', '2024-01-05')}")
    print(f"  板块:   {provider.get_sector_list()}")

    # 场景2：C++ 引擎不可用 → 自动回退 Python
    print("\n=== 场景2：C++ 引擎不可用 ===")
    engine = FastEngine(available=False)
    provider = BacktestProvider(engine=engine)
    print(f"  交易日: {provider.get_trading_dates('2024-01-01', '2024-01-05')}")
    print(f"  板块:   {provider.get_sector_list()}")

    # 场景3：没有引擎 → 也能回退
    print("\n=== 场景3：引擎为 None ===")
    provider = BacktestProvider(engine=None)
    print(f"  交易日: {provider.get_trading_dates('2024-01-01', '2024-01-05')}")
