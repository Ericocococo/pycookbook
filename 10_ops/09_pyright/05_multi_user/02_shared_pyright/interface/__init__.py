#coding=utf-8
"""ntquant interface — API 参考文档与数据类型。

ntrade.interface 仅展示支持的接口签名与类型定义。
实际使用时统一从 ntrade._impl 导入共享实现（由 NtTradeContext 区分回测/实盘）:

    from ntrade._impl import ntdata, nttrader, nttype, ntconstant

兼容旧路径:
    回测: from ntrade._impl.backtest import ntdata, nttrader, nttype, ntconstant
    实盘: from ntrade._impl.livetrade import ntdata, nttrader, nttype, ntconstant
"""

from .nttype import (
    StockAccount,
    NtAsset,
    NtOrder,
    NtTrade,
    NtPosition,
    NtOrderError,
    NtCancelError,
    NtOrderResponse,
    NtCancelOrderResponse,
    NtAccountStatus,
    NtCreditOrder,
    NtCreditDeal,
)
from .ntconstant import (
    STOCK_BUY, STOCK_SELL,
    FIX_PRICE, LATEST_PRICE,
    SECURITY_ACCOUNT,
    SH_MARKET, SZ_MARKET,
    MARKET_SHANGHAI, MARKET_SHENZHEN, MARKET_BEIJING,
    ORDER_UNREPORTED, ORDER_WAIT_REPORTING, ORDER_REPORTED,
    ORDER_REPORTED_CANCEL, ORDER_PARTSUCC_CANCEL, ORDER_PART_CANCEL,
    ORDER_CANCELED, ORDER_PART_SUCC, ORDER_SUCCEEDED, ORDER_JUNK, ORDER_UNKNOWN,
    ACCOUNT_STATUS_INVALID, ACCOUNT_STATUS_OK, ACCOUNT_STATUS_WAITING_LOGIN,
    ACCOUNT_STATUSING, ACCOUNT_STATUS_FAIL, ACCOUNT_STATUS_INITING,
    ACCOUNT_STATUS_CORRECTING, ACCOUNT_STATUS_CLOSED,
)

__all__ = [
    # 数据类型
    'StockAccount', 'NtAsset', 'NtOrder', 'NtTrade', 'NtPosition',
    'NtOrderError', 'NtCancelError', 'NtOrderResponse',
    'NtCancelOrderResponse', 'NtAccountStatus',
    'NtCreditOrder', 'NtCreditDeal',
    # 常量
    'STOCK_BUY', 'STOCK_SELL',
    'FIX_PRICE', 'LATEST_PRICE',
    'SECURITY_ACCOUNT',
    'SH_MARKET', 'SZ_MARKET',
    'MARKET_SHANGHAI', 'MARKET_SHENZHEN', 'MARKET_BEIJING',
    # 委托状态
    'ORDER_UNREPORTED', 'ORDER_WAIT_REPORTING', 'ORDER_REPORTED',
    'ORDER_REPORTED_CANCEL', 'ORDER_PARTSUCC_CANCEL', 'ORDER_PART_CANCEL',
    'ORDER_CANCELED', 'ORDER_PART_SUCC', 'ORDER_SUCCEEDED', 'ORDER_JUNK', 'ORDER_UNKNOWN',
    # 账号状态
    'ACCOUNT_STATUS_INVALID', 'ACCOUNT_STATUS_OK', 'ACCOUNT_STATUS_WAITING_LOGIN',
    'ACCOUNT_STATUSING', 'ACCOUNT_STATUS_FAIL', 'ACCOUNT_STATUS_INITING',
    'ACCOUNT_STATUS_CORRECTING', 'ACCOUNT_STATUS_CLOSED',
]
