#coding=utf-8
"""行情模块 — 接口声明。

只保留函数签名与文档，实现位于 ntrade._impl.ntdata。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional
    import pandas as pd


__all__ = [
    'subscribe_quote', 'subscribe_whole_quote', 'unsubscribe_quote', 'run',
    'get_market_data_ex', 'get_full_tick', 'get_divid_factors',
    'get_l2_quote', 'get_l2_order', 'get_l2_transaction', 'get_l2thousand_queue',
    'get_financial_data', 'get_instrument_detail', 'get_instrument_type',
    'get_trading_dates', 'get_holidays', 'get_sector_list', 'get_stock_list_in_sector',
]


def subscribe_quote(stock_code: str, period: str = '1d', start_time: str = '',
                    end_time: str = '', count: int = 0,
                    callback: Optional[Callable] = None) -> int:
    """
    订阅股票行情数据（仅实盘）。

    :param stock_code: 股票代码，e.g. "000001.SZ"
    :param period: 周期，分笔"tick" 分钟线"1m"/"5m" 日线"1d"等周期
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param count: 数量，-1 全部 / n: 从结束时间向前数 n 个
    :param callback: 订阅回调
    :return: 订阅序号
    """
    ...


def subscribe_whole_quote(code_list: List[str],
                          callback: Optional[Callable] = None) -> int:
    """订阅全推数据（仅实盘）。返回订阅序号。"""
    ...


def unsubscribe_quote(seq: int) -> None:
    """取消行情订阅（仅实盘）。"""
    ...


def run() -> None:
    """阻塞当前线程接收行情回调（仅实盘）。"""
    ...


def get_market_data_ex(field_list: List[str] = [], stock_list: List[str] = [],
                       period: str = '1d', start_time: str = '', end_time: str = '',
                       count: int = -1, dividend_type: str = 'none',
                       fill_data: bool = True) -> Dict[str, "pd.DataFrame"]:
    """获取历史行情数据。回测/实盘共用。

    :return: {stock_code: DataFrame}，单标的也返回 dict（与 xtquant 兼容）
    """
    ...


def get_full_tick(code_list: List[str]) -> Dict[str, Any]:
    """获取盘口 tick 数据（仅实盘）。返回 {stock_code: tick_dict}。"""
    ...


def get_divid_factors(stock_code: str, start_time: str = '',
                      end_time: str = '') -> "pd.DataFrame":
    """获取除权除息日及对应的权息。"""
    ...


def get_l2_quote(field_list: List[str] = [], stock_code: str = '',
                 start_time: str = '', end_time: str = '', count: int = -1) -> "pd.DataFrame":
    """获取 Level-2 实时行情快照。"""
    ...


def get_l2_order(field_list: List[str] = [], stock_code: str = '',
                 start_time: str = '', end_time: str = '', count: int = -1) -> "pd.DataFrame":
    """获取 Level-2 逐笔委托。"""
    ...


def get_l2_transaction(field_list: List[str] = [], stock_code: str = '',
                       start_time: str = '', end_time: str = '', count: int = -1) -> "pd.DataFrame":
    """获取 Level-2 逐笔成交。"""
    ...


def get_l2thousand_queue(stock_code: str, gear_num: Optional[int] = None,
                         price: Optional[float] = None) -> "pd.DataFrame":
    """获取 Level-2 千档委托队列。"""
    ...


def get_financial_data(stock_list: List[str], table_list: Optional[List[str]] = None,
                       start_time: str = '', end_time: str = '',
                       report_type: str = 'report_time') -> Dict[str, Any]:
    """获取财务数据。返回 {stock_code: {table: DataFrame}}。"""
    ...


def get_instrument_detail(stock_code: str, iscomplete: bool = False) -> dict:
    """获取合约详细信息。"""
    ...


def get_instrument_type(stock_code: str,
                        variety_list: Optional[List[str]] = None) -> Dict[str, bool]:
    """判断证券类型。返回 {品种名: True}，variety_list 非空时仅返回命中的品种。"""
    ...


def get_trading_dates(market: str, start_time: str = '', end_time: str = '',
                      count: int = -1) -> List[str]:
    """根据市场获取交易日列表。返回 YYYYMMDD 字符串列表。"""
    ...


def get_holidays() -> List[str]:
    """获取节假日列表。"""
    ...


def get_sector_list() -> List[str]:
    """获取板块列表。"""
    ...


def get_stock_list_in_sector(sector_name: str, real_timetag: int = -1) -> List[str]:
    """获取板块成份股。"""
    ...
