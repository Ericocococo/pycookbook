# coding=utf-8
"""T+1 与挂单撮合 — 不跑引擎，直接操作 broker 看交易语义。

Python 3.12。
运行: cd 06_mini_backtest && python 02_t1_semantics.py

演示：
  ① T+1 四天场景：挂单买入 → 撮合成交 → T+1 拒卖 → 换日后卖出

## 演示什么

完整引擎（01_run_backtest）把时序藏在循环里，这里把 broker 单独拎出来，
用四天的场景逐步展示交易层语义（对齐真实 C++ CSimulateBroker + Python broker）：

day1 收盘  挂单买入 1000 股
day2 开盘  撮合：开盘价 10.0 成交（扣钱、持仓+1000、记当日买入）
day2 盘中  立刻想卖 → 被拒：当日买入不可卖（T+1）
day2 收盘  再挂卖单 → 仍被拒：登记要到下一个交易日才清
day3 开盘  换日登记：day2 买入今天可卖了
day3 收盘  挂卖单 1000 → 这次成功（可卖 1000）
day4 开盘  撮合：开盘价 11.0 成交，落袋 +1000

## 对齐真实代码

- 撮合 = C++ ManageActions（每根 bar 开头撮合上一轮挂单，当日有效单）
- T+1 可卖量 = 总持仓 − 当日买入登记（Python 侧维护，查询"看似透传实则算过"）
- 真实换日登记不做"清空"：`_day_buy_volume` 按 {交易日期} 键存，查询按当前日期
  键匹配，旧日期自然失效（详见 backtest_impl.py 的 on_new_day 注释）。
  mini 用"每日显式清空"做语义等价简化。

## 顺带体会

"当日买入当天收盘也卖不掉"不是引擎 bug——T+1 下真实柜台同样拒绝。
日线引擎下 T 日买入的股票最早 T+2 日开盘才能卖出（T+1 挂单 T+2 撮合）。
"""

from backtest_impl import BacktestBroker


def demo01_t1_four_day_scenario():
    """① T+1 四天场景：
    day1 挂单买入 → day2 撮合成交 → day2 T+1 拒卖 →
    day3 换日可卖 → day3 挂卖单 → day4 撮合卖出。
    """
    print("① T+1 四天场景")
    broker = BacktestBroker(initial_cash=100_000)
    print("初始资金 100,000\n")

    # ---- day1 收盘：决策 → 挂单（今天不再成交）----
    print("[day1 收盘] 策略决策 → 市价挂单买入 1000 股")
    broker.order("000001.SZ", 1000)

    # ---- day2 开盘：撮合昨日挂单 ----
    print("\n[day2 开盘] 撮合队列（开盘价 10.0）→ day1 挂单成交")
    broker.on_new_day()                       # 昨日无买入登记，无实际影响
    broker.match_pending({"000001.SZ": 10.0})  # day1 的单按 day2 开盘价成交
    print(f"  持仓: {broker.get_positions()}, 资金: {broker.get_cash():.0f}")

    # ---- day2 盘中：当天就想卖 → T+1 拒绝 ----
    print("\n[day2 盘中] 策略改主意想卖 1000 股（当日买入，可卖 0）")
    r1 = broker.order("000001.SZ", -1000)
    print(f"  下单结果: {'被拒（正确）' if r1 == -1 else '成交？！'}")

    # ---- day2 收盘：再挂卖单 → 仍被拒（登记还没清）----
    print("\n[day2 收盘] 想赶明早开盘卖 → 挂卖单")
    r2 = broker.order("000001.SZ", -1000)
    print(f"  下单结果: {'被拒（正确，T+1 登记未清）' if r2 == -1 else '成交？！'}")

    # ---- day3 开盘：换日登记清空 → day2 买的今天可卖了 ----
    print("\n[day3 开盘] 新交易日：on_new_day() → 当日买入登记清空")
    broker.on_new_day()
    print(f"  可卖 = 持仓 − 当日买入登记 = {broker.get_positions()['000001.SZ']}")

    # ---- day3 收盘：挂卖单 → 成功 ----
    print("\n[day3 收盘] 挂卖单 1000 股 → 通过 T+1 校验")
    broker.order("000001.SZ", -1000)

    # ---- day4 开盘：撮合卖单 ----
    print("\n[day4 开盘] 撮合队列（开盘价 11.0）→ day3 卖单成交")
    broker.on_new_day()
    broker.match_pending({"000001.SZ": 11.0})
    print(f"  持仓: {broker.get_positions()}, 资金: {broker.get_cash():.0f}")

    # ---- 汇总 ----
    print("\n成交记录:")
    for t in broker.get_trades():
        print(f"  {t['direction']} {t['symbol']} x {t['volume']} @ {t['price']:.2f}")
    profit = broker.get_cash() - 100_000
    print(f"\n总盈亏: {profit:+.0f}（买 10.0 卖 11.0 × 1000 股）")


if __name__ == "__main__":
    demo01_t1_four_day_scenario()
