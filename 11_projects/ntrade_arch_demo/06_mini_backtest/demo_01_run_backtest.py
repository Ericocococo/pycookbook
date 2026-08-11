# coding=utf-8
"""最小可运行回测 — 所有概念的完整组合。

## 本 demo 组合了前三层的所有概念

1. 全局上下文 + 模块级转发（01_global_context）
   → context.py 的 set/get/clear + api.py 的薄转发函数

2. ABC + 工厂方法 + 延迟导入（02_abc_factory）
   → context.py 的 BaseDataProvider/BaseBroker + TradeContext.backtest()

3. Mixin 组装（03_mixin_assembly）
   → backtest_impl.py 的 MarketMixin + CalendarMixin → BacktestDataProvider

4. 引擎适配器（本层新增）
   → engine.py 的 BacktestEngine 逐 bar 驱动策略

## 文件对应关系

    本 demo                    ntrade 真实代码
    ─────────────────────────────────────────────────
    context.py                 _impl/_runtime/nt_context.py
    api.py                     _impl/ntdata.py + _impl/nttrader.py
    backtest_impl.py           _impl/backtest/_data/ + _impl/backtest/_broker.py
    engine.py                  _impl/backtest/_adapter.py + C++ BacktestEngine

## 运行方式

    cd 04_mini_backtest
    python demo_01_run_backtest.py

## 学到什么

- 一个策略函数如何通过 5 层间接调用最终执行到具体实现
- 策略 → api.get_data() → get_current_context().data_provider → MarketMixin.get_data()
- 引擎如何逐 bar 驱动策略，以及如何防止未来函数
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
    - 获取标的所有可见行情
    - 如果最新收盘价 > 均价的 1.01 倍，买入
    - 如果最新收盘价 < 均价的 0.99 倍，卖出
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
        # 买入 10000 股
        api.order(symbol, 10000, latest["close"])
    elif latest["close"] < avg_price * 0.99 and holding > 0:
        # 全部卖出
        api.order(symbol, -holding, latest["close"])


# ============================================================
# 启动回测
# ============================================================

if __name__ == "__main__":
    # 1. 创建配置
    config = BacktestConfig(
        symbols=["000001.SZ"],
        start="2024-01-02",
        end="2024-01-08",
        initial_cash=500_000.0,
    )

    # 2. 工厂方法创建上下文（自动创建 DataProvider + Broker）
    ctx = TradeContext.backtest(config)

    # 3. 运行（set_context → 逐 bar 驱动 → clear_context）
    result = ctx.run(simple_strategy)

    # 4. 查看结果
    print("\n" + "=" * 50)
    print("回测结果")
    print("=" * 50)

    print(f"\n最终资金: {result['final_cash']:,.0f}")
    print(f"最终持仓: {result['final_positions']}")

    print(f"\n成交记录:")
    for t in result['trades']:
        print(f"  {t['direction']} {t['symbol']} x {t['volume']} @ {t['price']:.2f}")

    print(f"\n净值曲线:")
    for e in result['equity_curve']:
        print(f"  {e['date']}: 净值 {e['equity']:>12,.0f}  现金 {e['cash']:>12,.0f}")
