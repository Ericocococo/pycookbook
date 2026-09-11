# coding=utf-8
"""最简逐 bar 引擎 — 回测的本质就是一个 for 循环。

Python 3.12。
运行: python 01_simplest_loop.py

演示：
  ① 逐bar回测：用均线策略跑最简引擎，打印逐日操作与最终净值

## 回测到底在干什么？

把历史行情按时间顺序一天一天"喂"给策略函数：
    for 每个交易日:
        截取「当天及之前」的行情（防止偷看未来数据）
        调用策略函数
        记录净值

就这么简单。ntrade 的 C++ BacktestEngine 做的也是同一件事，只是更快。
【注】两处教学简化，真实引擎不同（详见 03_matching_timing.py 与 00_design 红线 ②③）：
  1. 这里按"当日收盘价即时成交"；真实是挂单留到下一根 bar 开盘撮合
  2. 这里用 bars[:i+1] 切片截断防未来；真实是引擎先推进行情再回调策略（只增视图）

## 策略签名说明（衔接 01 与 06，别被绕晕）

本 demo 的策略签名是 `my_strategy(visible_bars, cash, position)`——
引擎把数据、资金、持仓"喂"给策略（push 方向，纯粹为了把"截断"演清楚）。

但 01 里教过：真实 single 策略是**无参函数**，自己调模块级函数取数
（pull 方向，策略主动拉）。真实引擎就是 pull——策略体内
`ntdata.get_market_data_ex(...)` 取到的数据天然被截断到当前 bar。
所以：本站的传参形态是教学简化，06_mini_backtest 会回到 01 的无参+api 形态。

## 什么是「防未来函数」？

回测时策略只能看到当前 bar 及之前的数据，不能偷看未来的价格。
否则你写个「明天涨就今天买」的策略，回测收益逆天但实盘必亏。

实现方式很朴素：每次只给策略 bars[:i+1]（截到当前位置）。

## 学到什么

- 逐 bar 驱动的核心循环
- 防未来函数的实现原理
- 回测引擎的最小骨架
"""

# ============================================================
# 模拟行情数据
# ============================================================

BARS = [
    {"date": "2024-01-02", "close": 9.7,  "volume": 500000},
    {"date": "2024-01-03", "close": 9.9,  "volume": 600000},
    {"date": "2024-01-04", "close": 10.0, "volume": 550000},
    {"date": "2024-01-05", "close": 10.1, "volume": 580000},
    {"date": "2024-01-08", "close": 10.2, "volume": 520000},
]


# ============================================================
# 策略函数 — 接收「截至当前」的行情
# ============================================================

def my_strategy(visible_bars, cash, position):
    """均线策略：3日均价以上买入，以下卖出。

    参数:
        visible_bars: 当前 bar 及之前的行情（已防未来函数）
        cash: 当前资金
        position: 当前持仓数量

    返回:
        action: "buy" / "sell" / None
    """
    if len(visible_bars) < 3:
        return None

    avg_3 = sum(b["close"] for b in visible_bars[-3:]) / 3
    latest = visible_bars[-1]["close"]

    if latest > avg_3 and position == 0:
        return "buy"
    elif latest < avg_3 and position > 0:
        return "sell"
    return None


# ============================================================
# 最简引擎 — 一个 for 循环
# ============================================================

def run_backtest(bars, strategy_fn, initial_cash=100_000):
    """逐 bar 驱动策略。

    这就是回测引擎的全部核心逻辑。
    ntrade 的 C++ 引擎做的事情完全一样，只是多了：
    - 多标的并行
    - 手续费/滑点计算
    - 订单撮合细节
    """
    cash = initial_cash
    position = 0
    buy_price = 0
    equity_curve = []

    print(f"回测开始, 初始资金 {cash:,.0f}\n")

    for i, bar in enumerate(bars):
        # ★ 关键：只给策略看 bars[:i+1]，不让它看到未来
        visible_bars = bars[:i + 1]

        action = strategy_fn(visible_bars, cash, position)

        if action == "buy" and position == 0:
            volume = int(cash / bar["close"] / 100) * 100  # 整百股
            cost = volume * bar["close"]
            cash -= cost
            position = volume
            buy_price = bar["close"]
            print(f"  {bar['date']} | 买入 {volume} 股 @ {bar['close']:.2f}")

        elif action == "sell" and position > 0:
            revenue = position * bar["close"]
            profit = (bar["close"] - buy_price) * position
            cash += revenue
            print(f"  {bar['date']} | 卖出 {position} 股 @ {bar['close']:.2f}, "
                  f"盈亏 {profit:+.0f}")
            position = 0

        else:
            print(f"  {bar['date']} | 持有 (持仓 {position} 股)")

        equity = cash + position * bar["close"]
        equity_curve.append({"date": bar["date"], "equity": equity})

    print(f"\n回测结束, 最终净值 {equity_curve[-1]['equity']:,.0f}")
    return equity_curve


# ============================================================
# 运行
# ============================================================

def demo01_run_backtest():
    """① 逐bar回测：用均线策略跑最简引擎，打印逐日操作与最终净值"""
    run_backtest(BARS, my_strategy)


if __name__ == "__main__":
    demo01_run_backtest()
