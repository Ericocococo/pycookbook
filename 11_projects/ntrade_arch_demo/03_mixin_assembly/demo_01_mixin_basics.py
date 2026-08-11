# coding=utf-8
"""Mixin 多继承组装 — 把大类拆成小模块。

## 上一节的问题

BacktestProvider 要实现很多方法（行情、日历、板块、财务、除权除息...），
全写在一个类里会变成几千行的巨型类。

## 方案：Mixin 组装

把每个数据维度拆成独立的 Mixin 类，最终通过多继承组合：

    class BacktestProvider(
        MarketMixin,       # 行情
        CalendarMixin,     # 日历
        SectorMixin,       # 板块
        BaseProvider,      # 抽象基类
    ): pass

ntrade 中 NtBacktestDataProvider 就是这样组装的，6 个 Mixin：
MarketMixin / CalendarMixin / StockInfoMixin / SectorMixin / FinancialMixin / L2Mixin

## 学到什么

- Mixin 模式：每个 Mixin 只负责一个维度
- 多继承的 MRO（方法解析顺序）
- 为什么 BaseProvider 要放在继承列表最后
"""

from abc import ABC, abstractmethod


# ============================================================
# 抽象基类 — 声明所有需要的方法
# ============================================================

class BaseProvider(ABC):
    """数据提供者抽象基类 — 声明全部接口。"""

    @abstractmethod
    def get_data(self, symbol):
        """获取行情数据。"""
        ...

    @abstractmethod
    def get_trading_dates(self, start, end):
        """获取交易日列表。"""
        ...

    @abstractmethod
    def get_sector_list(self):
        """获取板块列表。"""
        ...

    @abstractmethod
    def get_stock_list_in_sector(self, sector):
        """获取板块成份股。"""
        ...


# ============================================================
# Mixin — 每个负责一个数据维度
# ============================================================

class MarketMixin:
    """行情 Mixin — 负责 get_data。

    ntrade 对应: MarketMixin（_data/_market.py）
    """

    def get_data(self, symbol):
        return {"symbol": symbol, "source": "本地CSV", "price": 10.5}


class CalendarMixin:
    """日历 Mixin — 负责 get_trading_dates。

    ntrade 对应: CalendarMixin（_data/_calendar.py）
    """

    def get_trading_dates(self, start, end):
        return ["2024-01-02", "2024-01-03", "2024-01-04"]


class SectorMixin:
    """板块 Mixin — 负责 get_sector_list / get_stock_list_in_sector。

    ntrade 对应: SectorMixin（_data/_sector.py）
    """

    def get_sector_list(self):
        return ["沪深300", "中证500", "科创50"]

    def get_stock_list_in_sector(self, sector):
        if sector == "沪深300":
            return ["600519.SH", "000001.SZ", "601318.SH"]
        return []


# ============================================================
# 组装 — 多继承把 Mixin 拼成完整类
# ============================================================

class BacktestProvider(
    MarketMixin,       # 行情
    CalendarMixin,     # 日历
    SectorMixin,       # 板块
    BaseProvider,      # 抽象基类放最后（MRO 约定）
):
    """回测数据提供者 — Mixin 组装。

    ntrade 中的 NtBacktestDataProvider：
        class NtBacktestDataProvider(
            MarketMixin,
            CalendarMixin,
            StockInfoMixin,
            SectorMixin,
            FinancialMixin,
            L2Mixin,
            BaseDataProvider,
        ): pass

    为什么 BaseProvider 放最后？
    → Python MRO（C3 线性化）从左到右搜索方法。
    → Mixin 的具体实现会覆盖 BaseProvider 的 @abstractmethod。
    → 如果 BaseProvider 放前面，抽象方法会先被找到。
    """
    pass  # 不用写任何代码，全靠 Mixin 提供实现！


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    provider = BacktestProvider()

    print("=== Mixin 组装后的 BacktestProvider ===")
    print(f"  行情(MarketMixin):    {provider.get_data('600519.SH')}")
    print(f"  日历(CalendarMixin):  {provider.get_trading_dates('2024-01-01', '2024-01-05')}")
    print(f"  板块(SectorMixin):    {provider.get_sector_list()}")
    print(f"  成份股(SectorMixin):  {provider.get_stock_list_in_sector('沪深300')}")

    # 查看 MRO（方法解析顺序）
    print("\n=== MRO（方法搜索顺序）===")
    for i, cls in enumerate(BacktestProvider.__mro__):
        print(f"  {i}. {cls.__name__}")
    # 输出: BacktestProvider → MarketMixin → CalendarMixin → SectorMixin → BaseProvider → ABC → object
    # 搜索 get_data 时：先找 MarketMixin → 找到了，用它的实现

    # isinstance 检查正常工作
    print(f"\n  isinstance(provider, BaseProvider) = {isinstance(provider, BaseProvider)}")
