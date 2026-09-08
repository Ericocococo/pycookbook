# coding=utf-8
"""撮合时序 — 下单价 ≠ 成交价，挂单到下一根 bar 才撮合。

## 前面 demo 的问题（为什么单独开一节）

demo_01/02 都是「信号出现当天按收盘价成交」——这是教学简化，
真实引擎不是这样：策略挂的单要等**下一根 bar** 才撮合。
简化的坏处：写「今日金叉今日买」的策略，回测按当日成交能赚，
实盘按次日开盘成交可能亏——收益口径全错。

## 真实时序（engine_impl.cpp OnStrategyNext，已源码核实）

引擎每个 bar 的处理顺序（C++ BacktestEngine）：
    while 还有行情切片:
        1. 推进行情到当前 bar（先于一切回调，防未来函数）
        2. ManageActions(): 撮合上一轮挂的单  ← 用"当前 bar"的行情
        3. 若换交易日: on_market_open + 换日清算（未成交单作废）
        4. 调策略 next() 决策 → 新挂的单留到下一根 bar 才撮合

所以：
- 市价单：bar T 决策挂单 → bar T+1 开盘价成交（不是 T 的收盘价）
- 限价单：bar T+1 的 low/high 有没有碰到限价，碰到才成交
- 挂单只有一次撮合机会，T+1 没成交就作废（当日有效单）

## 学到什么

- 撮合队列：订单先入队，随行情推进再结算
- 市价 vs 限价的成交价规则
- 为什么「次日开盘成交」比「当日收盘成交」更接近实盘
"""

# ============================================================
# 行情数据（制造跳空高开，让两种口径差异明显）
# ============================================================

BARS = [
    {"date": "01-02", "open": 10.0, "high": 10.3, "low": 9.9,  "close": 10.1},
    {"date": "01-03", "open": 10.2, "high": 10.6, "low": 10.1, "close": 10.5},  # 收盘新高
    {"date": "01-05", "open": 10.8, "high": 11.2, "low": 10.7, "close": 11.0},  # ★跳空高开
    {"date": "01-06", "open": 11.0, "high": 11.1, "low": 10.4, "close": 10.5},  # 回落
]


def decide(i, position):
    """决策函数：看截至 bar i 的行情，决定买/卖（只看 close）。

    - 空仓且 close 连涨两天 → 想买入
    - 持仓且 close 转跌 → 想卖出
    返回 "buy" / "sell" / None。注意：只做决策，不负责成交——成交归引擎。
    """
    if i < 1:
        return None
    rising = BARS[i]["close"] > BARS[i - 1]["close"]
    if position == 0 and rising and BARS[i]["close"] > 10.0:
        return "buy"
    if position > 0 and not rising:
        return "sell"
    return None


# ============================================================
# 口径 A：当日收盘成交（demo_01/02 的简化，教学对照用）
# ============================================================

def run_same_day_close(initial_cash=100_000):
    """简化口径：信号出现当天按收盘价成交。"""
    cash = initial_cash
    position = 0
    trades = []

    for i, bar in enumerate(BARS):
        action = decide(i, position)
        if action == "buy" and position == 0:
            position = int(cash / bar["close"] / 100) * 100
            cash -= position * bar["close"]
            trades.append(("买入", bar["date"], bar["close"]))
        elif action == "sell" and position > 0:
            cash += position * bar["close"]
            trades.append(("卖出", bar["date"], bar["close"]))
            position = 0

    equity = cash + position * BARS[-1]["close"]
    return trades, equity


# ============================================================
# 口径 B：挂单队列，次 bar 撮合（真实引擎口径）
# ============================================================

def run_pending_queue(initial_cash=100_000):
    """真实口径：决策当天只挂单，下一根 bar 开盘撮合。"""
    cash = initial_cash
    position = 0
    pending = None        # 挂单队列（演示单标的单笔足够）："buy"/"sell"
    trades = []

    for i, bar in enumerate(BARS):
        # ① 撮合上一轮挂单：市价单按"当前 bar"的开盘价成交
        if pending == "buy" and position == 0:
            position = int(cash / bar["open"] / 100) * 100
            cash -= position * bar["open"]
            trades.append(("买入", bar["date"], bar["open"]))  # 开盘价不是昨天收盘价
        elif pending == "sell" and position > 0:
            cash += position * bar["open"]
            trades.append(("卖出", bar["date"], bar["open"]))
            position = 0
        pending = None

        # ② 策略决策（收盘后）→ 只挂单，今天不再成交
        action = decide(i, position)
        if action in ("buy", "sell"):
            pending = action

    # 演示到尾：挂单没有下一根 bar 撮合了 → 作废（真实引擎换日清算同样作废）
    if position > 0:
        equity = cash + position * BARS[-1]["close"]
    else:
        equity = cash
    return trades, equity


# ============================================================
# 限价单：按次 bar 的 low/high 判定能否成交
# ============================================================

def demo_limit_order():
    """市价单无脑按开盘价成交；限价单要等价格"碰到"限价。

    C++ try_match 的真实判定（已源码核实）：
    - 一字板（high==low）：涨停拒买、跌停拒卖（退市股跌停仍可卖，清仓用）
    - 市价单：成交价 = 次 bar 开盘价 open
    - 限价买单：限价 lp ≥ 次 bar low → 成交，**成交价 = 限价 lp**
      （注意：C++ 不做"更好价"优化——开盘 10.8 ≤ 限价 10.9 也按 10.9 成交；
      真实柜台会按开盘价成交，引擎这里简化成"触及即按限价"）
    - 限价卖单：lp ≤ high → 成交，价 = lp
    - 当日没成交的挂单：换日清算时作废（当日有效单）
    """
    print("限价单判定（C++ try_match 规则）:")
    cases = [
        ("买单限价 10.9, 开盘 10.8", 10.9, 10.8, 10.7),  # 开盘即触及 → 按限价 10.9 成交
        ("买单限价 10.6, 开盘 10.8", 10.6, 10.8, 10.7),  # low > 限价 → 不成交作废
        ("买单限价 10.7, 开盘 10.8", 10.7, 10.8, 10.7),  # low == 限价 → 盘中触及成交
    ]
    for name, limit, open_, low_ in cases:
        if open_ <= limit:
            # 注意成交价按限价（C++ 简化，不做更好价优化）
            msg = f"成交 @ {limit}（开盘 {open_} ≤ 限价；引擎按限价成交，不做更好价优化）"
        elif low_ <= limit:
            msg = f"成交 @ {limit}（盘中 low {low_} 触及限价）"
        else:
            msg = f"不成交作废（low {low_} 未触及限价 {limit}）"
        print(f"  {name}: {msg}")


if __name__ == "__main__":
    trades_a, equity_a = run_same_day_close()
    trades_b, equity_b = run_pending_queue()

    print("=== 口径 A：当日收盘价成交（教学简化）===")
    for t in trades_a:
        print(f"  {t[0]} {t[1]} @ {t[2]:.2f}")
    print(f"  期末净值: {equity_a:,.0f}")

    print("\n=== 口径 B：挂单次日开盘成交（真实引擎）===")
    for t in trades_b:
        print(f"  {t[0]} {t[1]} @ {t[2]:.2f}")
    print(f"  期末净值: {equity_b:,.0f}")

    print(f"""
结论: 两口径差 {equity_a - equity_b:,.0f}
  口径 A 在 01-03 收盘(10.5)就买到 → 看似占了便宜（结果不亏不赚）；
  口径 B 等 01-05 开盘(10.8)才成交 → 真实买贵 0.3，净值亏 2,760。
  真实引擎是 B：信号出现当晚挂单，第二天开盘才成交——回测别按 A 算。
  信号当日收盘价成交 = 把"收盘后才知道的信息"当成了当天可用 → 未来函数。
  你写的策略若在回测里"今日信号今日成交"，实盘必然对不上收益。""")

    demo_limit_order()
