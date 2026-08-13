#coding=utf-8
"""交易模块 — 接口声明。

只保留类/函数签名与文档，实现位于 ntrade._impl.nttrader。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from .nttype import (
        StockAccount, NtAsset, NtOrder, NtTrade, NtPosition,
        NtOrderError, NtCancelError, NtOrderResponse, NtCancelOrderResponse,
        NtAccountStatus,
    )
    from .ntresult import BacktestResult


class NtQuantTraderCallback(object):
    """交易回调基类。"""

    def on_connected(self) -> None:
        pass

    def on_disconnected(self) -> None:
        """连接断开推送。"""
        pass

    def on_stock_order(self, order: "NtOrder") -> None:
        """委托状态变化。"""
        pass

    def on_stock_trade(self, trade: "NtTrade") -> None:
        """成交推送。"""
        pass

    def on_stock_position(self, position: "NtPosition") -> None:
        """持仓变化。"""
        pass

    def on_stock_asset(self, asset: "NtAsset") -> None:
        """资产变化。"""
        pass

    def on_order_error(self, order_error: "NtOrderError") -> None:
        """委托错误。"""
        pass

    def on_cancel_error(self, cancel_error: "NtCancelError") -> None:
        """撤单错误。"""
        pass

    def on_order_stock_async_response(self, response: "NtOrderResponse") -> None:
        """异步下单请求响应。"""
        pass

    def on_cancel_order_stock_async_response(self, response: "NtCancelOrderResponse") -> None:
        """异步撤单请求响应。"""
        pass

    def on_account_status(self, status: "NtAccountStatus") -> None:
        """账户状态变化。"""
        pass


class NtQuantTrader(object):
    """
    牛股王量化交易接口。

    与 xtquant 兼容的回测使用方式:

        from ntrade._impl import ntdata, nttrader, nttype, ntconstant

        account = nttype.StockAccount("backtest")

        def strategy():
            df = ntdata.get_market_data_ex(field_list=[], stock_list=["600000.SH"], ...)
            nttrader.order_stock(account, "600000.SH",
                ntconstant.STOCK_BUY, 1000, ntconstant.FIX_PRICE, 0)

        trader = nttrader.NtQuantTrader(path, session)
        trader.set_backtest_config(symbols=["600000.SH"], ...)
        trader.start(); trader.connect(); trader.subscribe(account)
        result = trader.run_backtest(strategy)   # ← 直接传策略函数
    """

    def __init__(self, path: str, session: int,
                 callback: Optional["NtQuantTraderCallback"] = None):
        ...

    # ---- 回测配置 ----

    def set_backtest_config(self, **kwargs) -> None:
        """配置回测参数。

        Args:
            symbols: 标的列表，如 ["600000.SH", "000001.SZ"]
            start: 起始日期 "YYYY-MM-DD" 或 "YYYYMMDD"
            end: 结束日期
            initial_cash: 初始资金，默认 1_000_000.0
            commission_rate: 佣金费率，如 0.0003
            benchmark_symbol: 基准标的
            slippage_bps: 滑点（bps）
        """
        ...

    def set_live_config(self, **kwargs) -> None:
        """配置实盘参数。

        Args:
            account_id: 资金账号
            qmt_path: QMT mini 版 userdata 目录路径
            session: 会话 ID
            run_mode: "realtime"（行情驱动）或 "timer"（定时触发）
            timer_interval_seconds: 定时触发间隔（秒）
        """
        ...

    def register_callback(self, callback: "NtQuantTraderCallback") -> None:
        """注册回调对象。"""
        ...

    # ---- 生命周期（回测中占位保持兼容）----

    def start(self) -> None:
        """启动交易服务。回测中仅占位。"""
        ...

    def connect(self) -> int:
        """连接交易服务。返回 0 成功，回测中模拟成功。"""
        ...

    def stop(self) -> None:
        """停止交易服务。"""
        ...

    def subscribe(self, account: "StockAccount") -> int:
        """订阅账号信息。返回 0 成功，回测中仅记录账号引用。"""
        ...

    def unsubscribe(self, account: "StockAccount") -> int:
        """取消订阅。返回 0 成功。"""
        ...

    # ---- run_backtest ----

    def run_backtest(self, strategy_fn: Optional[Callable] = None,
                     handlebar: Optional[Callable] = None,
                     after_init: Optional[Callable] = None,
                     on_stop: Optional[Callable] = None) -> "BacktestResult":
        """运行回测（替代 run_forever）。

        支持两种模式：

        模式一 — 单函数模式（与 xtquant 兼容）:

            def strategy():
                df = ntdata.get_market_data_ex(...)
                nttrader.order_stock(account, ...)

            trader.run_backtest(strategy)

        模式二 — init/handlebar 模式（兼容 qmttools）:

            def init(C):
                C.stock_code = "600000.SH"
                C.period = "1d"
                C.asset = 1000000.0

            def handlebar(C):
                C.passorder(23, 1101, "", "600000.SH", 0, 7.23, 1000)

            trader.run_backtest(init, handlebar)

        Args:
            strategy_fn: 单策略函数（无参）。
            handlebar: 每 bar 回调，接收 NtBarContext 参数。
            after_init: 引擎就绪后回调，接收 NtBarContext。可选。
            on_stop: 回测结束后回调，接收 NtBarContext。可选。

        Returns:
            BacktestResult: 含 cash / equity / equity_curve / trades / paint_data 等
        """
        ...

    def run_forever(self) -> None:
        """阻塞运行（仅实盘模式）。"""
        ...

    def run(self, strategy_fn: Optional[Callable] = None,
            handlebar: Optional[Callable] = None,
            after_init: Optional[Callable] = None,
            on_stop: Optional[Callable] = None) -> Optional["BacktestResult"]:
        """统一入口 — 由调度框架按已配置的模式自动分派回测/实盘。

        同一份策略（单函数 strategy_fn 或 init/handlebar 上下文模式），
        调用方用 set_backtest_config() / set_live_config() 声明模式，
        run() 自动分派:

            回测: result = trader.run(init, handlebar)   # 返回 BacktestResult
            实盘: trader.run(init, handlebar)            # 阻塞运行，返回 None
        """
        ...

    # ---- 下单 ----

    def order_stock(self, account: "StockAccount", stock_code: str, order_type: int,
                    order_volume: int, price_type: int, price: float,
                    strategy_name: str = '', order_remark: str = '') -> int:
        """同步下单。返回订单编号或 -1（失败）。"""
        ...

    def order_stock_async(self, account: "StockAccount", stock_code: str, order_type: int,
                          order_volume: int, price_type: int, price: float,
                          strategy_name: str = '', order_remark: str = '') -> int:
        """异步下单，返回下单请求序号（回测同步模拟）。"""
        ...

    def cancel_order_stock(self, account: "StockAccount", order_id: int) -> int:
        """同步撤单。返回 0 成功或 -1 失败。"""
        ...

    def cancel_order_stock_sysid(self, account: "StockAccount", market: str, sysid: str) -> int:
        """按柜台编号撤单（桩）。"""
        ...

    def cancel_order_stock_sysid_async(self, account: "StockAccount", market: str, sysid: str) -> int:
        """异步按柜台编号撤单（桩）。"""
        ...

    def cancel_order_stock_async(self, account: "StockAccount", order_id: int) -> int:
        """异步撤单，返回撤单请求序号（回测同步模拟）。"""
        ...

    # ---- 查询 ----

    def query_stock_asset(self, account: "StockAccount") -> Optional["NtAsset"]:
        """查询股票资产。返回 NtAsset 或 None。"""
        ...

    def query_stock_order(self, account: "StockAccount", order_id: int) -> Optional["NtOrder"]:
        """查询指定委托。返回 NtOrder 或 None。"""
        ...

    def query_stock_orders(self, account: "StockAccount",
                           cancelable_only: bool = False) -> List["NtOrder"]:
        """查询当日所有委托。返回 list[NtOrder]。"""
        ...

    def query_stock_trades(self, account: "StockAccount") -> List["NtTrade"]:
        """查询当日所有成交。返回 list[NtTrade]。"""
        ...

    def query_stock_position(self, account: "StockAccount",
                             stock_code: str) -> Optional["NtPosition"]:
        """查询指定股票持仓。返回 NtPosition 或 None。"""
        ...

    def query_stock_positions(self, account: "StockAccount") -> List["NtPosition"]:
        """查询当日所有持仓。返回 list[NtPosition]。"""
        ...

    # ---- 账户管理 ----

    def query_account_infos(self) -> List[dict]:
        """查询已订阅的账户信息列表。返回 list[dict]。"""
        ...

    def query_account_status(self) -> List["NtAccountStatus"]:
        """查询已订阅的账户状态列表。返回 list[NtAccountStatus]。"""
        ...


# ==================================================================
# 模块级交易函数（委托到当前 NtTradeContext 的 broker）
# ==================================================================

def order_stock(account: "StockAccount", stock_code: str, order_type: int, order_volume: int,
                price_type: int, price: float,
                strategy_name: str = '', order_remark: str = '') -> int:
    """同步下单。返回订单编号或 -1（失败）。"""
    ...


def order_stock_async(account: "StockAccount", stock_code: str, order_type: int, order_volume: int,
                      price_type: int, price: float,
                      strategy_name: str = '', order_remark: str = '') -> int:
    """异步下单，返回下单请求序号（回测同步模拟）。"""
    ...


def cancel_order_stock(account: "StockAccount", order_id: int) -> int:
    """同步撤单。返回 0 成功或 -1 失败。"""
    ...


def cancel_order_stock_async(account: "StockAccount", order_id: int) -> int:
    """异步撤单，返回撤单请求序号（回测同步模拟）。"""
    ...


def cancel_order_stock_sysid(account: "StockAccount", market: str, sysid: str) -> int:
    """按柜台编号撤单。"""
    ...


def cancel_order_stock_sysid_async(account: "StockAccount", market: str, sysid: str) -> int:
    """异步按柜台编号撤单。"""
    ...


def query_stock_asset(account: "StockAccount") -> Optional["NtAsset"]:
    """查询股票资产。返回 NtAsset 或 None。"""
    ...


def query_stock_order(account: "StockAccount", order_id: int) -> Optional["NtOrder"]:
    """查询指定委托。返回 NtOrder 或 None。"""
    ...


def query_stock_orders(account: "StockAccount", cancelable_only: bool = False) -> List["NtOrder"]:
    """查询当日所有委托。返回 list[NtOrder]。"""
    ...


def query_stock_trades(account: "StockAccount") -> List["NtTrade"]:
    """查询当日所有成交。返回 list[NtTrade]。"""
    ...


def query_stock_position(account: "StockAccount", stock_code: str) -> Optional["NtPosition"]:
    """查询指定股票持仓。返回 NtPosition 或 None。"""
    ...


def query_stock_positions(account: "StockAccount") -> List["NtPosition"]:
    """查询当日所有持仓。返回 list[NtPosition]。"""
    ...


def query_account_infos() -> List[dict]:
    """查询已订阅的账户信息列表。返回 list[dict]。"""
    ...


def query_account_status() -> List["NtAccountStatus"]:
    """查询已订阅的账户状态列表。返回 list[NtAccountStatus]。"""
    ...
