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


# ---- 交易 API（对应 nttrader.py 的模块级函数；真实签名 order_stock(...)）----

def order(symbol, volume, price_type="market", price=None):
    """下单（挂单，非即时成交）。

    price_type="market" 市价单：下一根 bar 开盘价成交（不需要传 price）；
    price_type="limit"  限价单：price 为限价，次 bar 触及才成交。
    对应真实 nttrader.order_stock()——只把委托送进队列，成交等撮合。

    【真实 API 形状差异】mini 用 volume 正/负号表示买/卖（教学简化）；
    真实 order_stock 用 order_type 常量区分（23=STOCK_BUY、24=STOCK_SELL），
    volume 恒为正；NtBarContext.buy/sell/passorder 快捷方法内部填好
    order_type 再委托 broker（下单后还失效资产缓存，见 _context.py）。
    """
    return get_current_context().broker.order(symbol, volume, price_type, price)


def get_cash():
    """查询可用资金。"""
    return get_current_context().broker.get_cash()


def get_positions():
    """查询持仓。"""
    return get_current_context().broker.get_positions()
