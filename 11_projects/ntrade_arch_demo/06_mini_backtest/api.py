# coding=utf-8
"""模块级 API — 策略代码的唯一入口。

对应 ntrade 中的 ntrade/_impl/ntdata.py + ntrade/_impl/nttrader.py。
每个函数只做一件事：转发到 get_current_context().xxx()。
"""

from context import get_current_context


# ---- 行情 API（对应 ntdata.py）----

def get_market_data(symbol, start='', end=''):
    """获取历史行情数据。"""
    return get_current_context().data_provider.get_market_data(symbol, start, end)


def get_trading_dates(start='', end=''):
    """获取交易日列表。"""
    return get_current_context().data_provider.get_trading_dates(start, end)


# ---- 交易 API（对应 nttrader.py 的模块级函数）----

def order(symbol, volume, price):
    """下单。"""
    return get_current_context().broker.order(symbol, volume, price)


def get_cash():
    """查询可用资金。"""
    return get_current_context().broker.get_cash()


def get_positions():
    """查询持仓。"""
    return get_current_context().broker.get_positions()
