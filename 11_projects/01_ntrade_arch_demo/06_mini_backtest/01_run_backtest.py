# coding=utf-8
"""最小可运行回测 — 所有概念的完整组合。

Python 3.12。
运行: cd 06_mini_backtest && python 01_run_backtest.py

演示：
  ① 完整回测流程：创建配置 → 工厂创建上下文 → 运行策略 → 查看结果

## 本 demo 组合了各阶段的概念

1. 全局上下文 + 模块级转发（01_global_context）
   → context.py 的 set/get/clear + api.py 的薄转发函数

2. ABC + 工厂方法 + 延迟导入（02_abc_factory）
   → context.py 的 BaseDataProvider/BaseBroker + TradeContext.backtest()

3. Mixin 组装（03_mixin_assembly）
   → backtest_impl.py 的 MarketMixin + CalendarMixin → BacktestDataProvider

4. 逐 bar 引擎 + 撮合时序（04_bar_engine，含 03_matching_timing 的撮合队列）
   → engine.py 每日：推进 → 换日登记 → 撮合昨日挂单 → 调策略

## 文件对应关系

    本 demo                    ntrade 真实代码
    ─────────────────────────────────────────────────
    context.py                 _impl/_runtime/nt_context.py
    api.py                     _impl/ntdata.py + _impl/nttrader.py
    backtest_impl.py           _impl/backtest/_data/ + _impl/backtest/_broker.py
    engine.py                  _impl/backtest/_adapter.py + C++ BacktestEngine

## 运行方式

    cd 06_mini_backtest && python 01_run_backtest.py

## 学到什么

- 一个策略函数如何通过 5 层间接调用最终执行到具体实现
- 策略 → api.get_data() → get_current_context().data_provider → MarketMixin.get_data()
- 引擎如何逐 bar 驱动策略，以及如何防止未来函数
- 下单 ≠ 成交：api.order() 只挂单，次日开盘才撮合（对齐真实撮合时序）
"""

import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import api
from context import TradeContext, BacktestConfig


# ============================================================
# 策略函数 — 只用 api 模块，不 import 任何实现细节
# ============================================================

def simple_strategy():
    """简单均价策略：
    - 获取标的所有可见行情（引擎已截断到当前 bar，防未来函数）
    - 最新收盘价 > 均价 1% → 市价挂单买入
    - 最新收盘价 < 均价 1% → 市价挂单卖出

    注意：api.order() 只挂单——引擎下一根 bar 开盘才撮合成交
    （真实 ntrade 同样如此，见 04_bar_engine/03_matching_timing.py）
    """
    symbol = "000001.SZ"
    bars = api.get_market_data(symbol)

    if len(bars) < 2:
        return

    avg_price = sum(b["close"] for b in bars) / len(bars)
    latest = bars[-1]

    positions = api.get_positions()
    holding = positions.get(symbol, 0)

    if latest["close"] > avg_price * 1.01 and holding == 0:
        # 市价挂单买入 10000 股（不指定价格，成交价 = 次 bar 开盘价）
        api.order(symbol, 10000)
    elif latest["close"] < avg_price * 0.99 and holding > 0:
        # 市价挂单全卖（卖单受 T+1 限制：当日买入部分不可卖）
        api.order(symbol, -holding)


# ============================================================
# 启动回测
# ============================================================

def demo01_run_backtest():
    """① 完整回测流程：
    创建配置 → 工厂创建上下文 → 运行策略 → 打印成交记录和净值曲线。
    """
    print("① 完整回测流程")

    # 1. 创建配置
    config = BacktestConfig(
        symbols=["000001.SZ"],
        start="2024-01-02",
        end="2024-01-08",
        initial_cash=500_000.0,
    )

    # 2. 工厂方法创建上下文（自动创建 DataProvider + Broker）
    ctx = TradeContext.backtest(config)

    # 3. 运行（set_context → 逐 bar 驱动 → clear_context，异常也清理）
    result = ctx.run(simple_strategy)

    # 4. 查看结果
    print(f"\n最终资金: {result['final_cash']:,.0f}")
    print(f"最终持仓: {result['final_positions']}")

    print(f"\n成交记录:")
    for t in result['trades']:
        print(f"  {t['direction']} {t['symbol']} x {t['volume']} @ {t['price']:.2f}")

    print(f"\n净值曲线:")
    for e in result['equity_curve']:
        print(f"  {e['date']}: 净值 {e['equity']:>12,.0f}  现金 {e['cash']:>12,.0f}")


if __name__ == "__main__":
    demo01_run_backtest()
