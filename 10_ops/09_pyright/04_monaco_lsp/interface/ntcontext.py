#coding=utf-8
"""策略上下文类型协议 — 仅供类型标注使用。

用法:

    from ntrade.interface.ntcontext import INTradeContext

    def init(context: INTradeContext):
        context.symbols = ["600000.SH"]
        context.initial_cash = 1_000_000.0

    def handlebar(context: INTradeContext):
        df = context.get_market_data_ex(stock_list=["600000.SH"])
        context.buy("600000.SH", 1000)
        print(context.cash)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    import pandas as pd
    from .nttype import NtAsset, NtOrder, NtTrade, NtPosition


@runtime_checkable
class INTradeContext(Protocol):
    """ntrade 策略上下文协议 — init/handlebar 模式下 context 参数的接口定义。

    实际实现为 NtBarContext (_impl/backtest/_context.py)，Protocol 仅用于类型提示，
    策略代码 import 时不会产生实际依赖。
    """

    # ---- 配置属性 (init 中写入) ----
    stock_code: str
    """单标的代码，兼容 qmttools。"""
    symbols: List[str]
    """多标的列表。"""
    period: str
    """K线周期，如 "1d"。"""
    start_time: str
    """开始时间，兼容 qmttools。"""
    end_time: str
    """结束时间，兼容 qmttools。"""
    start: str
    """开始日期。"""
    end: str
    """结束日期。"""
    asset: float
    """初始资金，兼容 qmttools（别名）。"""
    initial_cash: float
    """初始资金。"""
    commission_rate: Optional[float]
    """佣金费率。"""
    benchmark_symbol: str
    """基准标的。"""
    slippage_bps: float
    """滑点（bps）。"""
    dividend_type: str
    """除权类型。"""

    # ---- bar 帧信息 ----
    timelist: List[Any]
    """时间列表。"""
    barpos: int
    """当前 bar 位置索引。"""

    # ---- 生命周期钩子 ----
    def after_init(self) -> None:
        """引擎就绪后、第一根 bar 之前调用。可选重写。"""
        ...

    def on_stop(self) -> None:
        """回测结束后调用。可选重写。"""
        ...

    # ---- 资产与持仓 ----
    @property
    def cash(self) -> float:
        """当前可用资金。"""
        ...

    @property
    def total_asset(self) -> float:
        """当前总资产（现金+市值）。"""
        ...

    @property
    def positions(self) -> List["NtPosition"]:
        """当前持仓列表（list[NtPosition]）。"""
        ...

    def position_for(self, symbol: str) -> Optional["NtPosition"]:
        """查询指定股票的持仓。"""
        ...

    # ---- 行情 ----
    def get_market_data_ex(
        self,
        field_list: Optional[List[str]] = None,
        stock_list: Optional[List[str]] = None,
        period: str = "1d",
        start_time: str = "",
        end_time: str = "",
        count: int = -1,
        dividend_type: str = "none",
        fill_data: bool = True,
    ) -> Dict[str, "pd.DataFrame"]:
        """获取历史行情数据。返回 {stock_code: DataFrame}。"""
        ...

    def get_trading_dates(
        self, market: str, start_time: str = "", end_time: str = "",
        count: int = -1,
    ) -> List[str]:
        """获取交易日列表。"""
        ...

    def get_divid_factors(self, stock_code: str, start_time: str = "", end_time: str = "") -> "pd.DataFrame":
        """获取除权除息数据。"""
        ...

    def get_instrument_detail(self, stock_code: str, iscomplete: bool = False) -> dict:
        """获取合约详细信息。"""
        ...

    def get_instrument_type(self, stock_code: str,
                            variety_list: Optional[List[str]] = None) -> Dict[str, bool]:
        """判断证券类型。返回 {品种名: True}。"""
        ...

    def get_full_tick(self, code_list: List[str]) -> Dict[str, Any]:
        """获取盘口 tick 数据。返回 {stock_code: tick_dict}。"""
        ...

    @staticmethod
    def get_holidays() -> List[str]:
        """获取节假日列表。"""
        ...

    @staticmethod
    def get_sector_list() -> List[str]:
        """获取板块列表。"""
        ...

    @staticmethod
    def get_stock_list_in_sector(sector: str) -> List[str]:
        """获取板块成分股列表。"""
        ...

    # ---- 交易 ----
    def buy(self, symbol: str, volume: int, price: float = 0, price_type: Optional[int] = None) -> int:
        """买入。返回订单编号或 -1。"""
        ...

    def sell(self, symbol: str, volume: int, price: float = 0, price_type: Optional[int] = None) -> int:
        """卖出。返回订单编号或 -1。"""
        ...

    def order_stock(
        self, stock_code: str, order_type: int, order_volume: int,
        price_type: int = 0, price: float = 0,
        strategy_name: str = "", order_remark: str = "",
    ) -> int:
        """下单。返回订单编号或 -1。"""
        ...

    def passorder(
        self, opType: int, orderType: int = 1101, accountid: str = "",
        orderCode: str = "", prType: int = 0, modelprice: float = 0,
        volume: int = 0, strategyName: str = "", quickTrade: int = 0,
        userOrderId: int = 0,
    ) -> int:
        """兼容 qmttools 的 passorder 下单。"""
        ...

    # ---- 查询 ----
    def query_stock_asset(self) -> Optional["NtAsset"]:
        """查询资产。返回 NtAsset 或 None。"""
        ...

    def query_stock_positions(self) -> List["NtPosition"]:
        """查询所有持仓。返回 list[NtPosition]。"""
        ...

    def query_stock_position(self, stock_code: str) -> Optional["NtPosition"]:
        """查询指定股票持仓。返回 NtPosition 或 None。"""
        ...

    def query_stock_orders(self, cancelable_only: bool = False) -> List["NtOrder"]:
        """查询委托列表。返回 list[NtOrder]。"""
        ...

    def query_stock_trades(self) -> List["NtTrade"]:
        """查询成交列表。返回 list[NtTrade]。"""
        ...

    # ---- 指标记录 ----
    def paint(self, name: str, value: Any, index: int = -1, drawstyle: int = 0, color: str = "", limit: str = "") -> None:
        """记录指标值（可视化用）。"""
        ...

    def get_paint_data(self) -> dict:
        """返回 paint 收集的所有指标数据。"""
        ...
