# coding=utf-8
"""把引擎提取成类 — 分离数据加载、驱动、结果收集。

## 上一节的问题

所有逻辑都在一个函数里：加载数据、驱动策略、撮合交易、记录净值...
实际项目中这些职责要分开。

## 方案：Engine 类

把引擎拆成三个阶段：
1. __init__: 加载数据、初始化状态
2. run():    逐 bar 驱动
3. result(): 收集结果

ntrade 中 NtBacktestAdapter.run() 的三段式：
    def run(self):
        self._load_data()         # 加载行情
        self._init_engine()       # 创建 C++ 引擎
        return self._run_bars()   # 逐 bar 驱动 + 收集结果

## 学到什么

- 引擎的职责拆分
- 数据 vs 引擎 vs 策略的边界
- Broker（交易撮合）独立出来
"""


# ============================================================
# Broker — 交易撮合（从引擎中独立出来）
# ============================================================

class SimpleBroker:
    """交易撮合器。ntrade 对应 NtBacktestBroker → C++ CSimulateBroker。

    职责：管理资金、持仓、订单，不关心行情和策略。
    """

    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.positions = {}   # {symbol: volume}
        self.trades = []

    def buy(self, symbol, volume, price):
        cost = volume * price
        if cost > self.cash:
            return -1
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + volume
        self.trades.append({"symbol": symbol, "side": "买", "volume": volume, "price": price})
        return len(self.trades)

    def sell(self, symbol, volume, price):
        held = self.positions.get(symbol, 0)
        if volume > held:
            volume = held
        self.cash += volume * price
        self.positions[symbol] = held - volume
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        self.trades.append({"symbol": symbol, "side": "卖", "volume": volume, "price": price})
        return len(self.trades)

    def equity(self, prices):
        """计算总资产 = 现金 + 持仓市值。"""
        market_value = sum(prices.get(s, 0) * v for s, v in self.positions.items())
        return self.cash + market_value


# ============================================================
# Engine — 逐 bar 驱动
# ============================================================

class BacktestEngine:
    """回测引擎。ntrade 对应 NtBacktestAdapter + C++ BacktestEngine。

    职责：加载数据、按时间顺序驱动策略、收集结果。
    不关心策略的具体逻辑，不关心交易撮合细节。
    """

    def __init__(self, bars_dict, broker, strategy_fn):
        """
        参数:
            bars_dict: {symbol: [bar, bar, ...]}，每个 bar 是 dict
            broker: 交易撮合器
            strategy_fn: 策略函数，签名 fn(engine_ctx)
        """
        self._bars = bars_dict
        self._broker = broker
        self._strategy_fn = strategy_fn

        # 所有标的的交易日取并集
        all_dates = set()
        for bars in bars_dict.values():
            all_dates.update(b["date"] for b in bars)
        self._dates = sorted(all_dates)

        self._bar_index = 0

    def get_visible_bars(self, symbol):
        """获取当前 bar 及之前的行情（防未来函数）。"""
        all_bars = self._bars.get(symbol, [])
        return [b for b in all_bars if b["date"] <= self._dates[self._bar_index]]

    def get_current_date(self):
        return self._dates[self._bar_index]

    def run(self):
        """逐 bar 驱动策略。"""
        equity_curve = []

        print(f"[Engine] {self._dates[0]} ~ {self._dates[-1]}, "
              f"共 {len(self._dates)} 个 bar\n")

        for i in range(len(self._dates)):
            self._bar_index = i
            date = self._dates[i]

            # 调用策略（策略通过 engine 引用来获取数据和下单）
            self._strategy_fn(self)

            # 收集当前价格，计算净值
            prices = {}
            for sym, bars in self._bars.items():
                visible = [b for b in bars if b["date"] <= date]
                if visible:
                    prices[sym] = visible[-1]["close"]

            equity = self._broker.equity(prices)
            equity_curve.append({"date": date, "equity": equity})

        return {
            "equity_curve": equity_curve,
            "trades": self._broker.trades,
            "final_cash": self._broker.cash,
            "final_positions": dict(self._broker.positions),
        }


# ============================================================
# 策略函数 — 通过 engine 获取数据和下单
# ============================================================

def dual_ma_strategy(engine: BacktestEngine):
    """双标的轮动策略：哪个涨得快买哪个。"""
    symbols = ["000001.SZ", "600519.SH"]
    date = engine.get_current_date()

    best_symbol = None
    best_return = -999

    for sym in symbols:
        bars = engine.get_visible_bars(sym)
        if len(bars) < 3:
            continue
        # 近3日涨幅
        ret = (bars[-1]["close"] - bars[-3]["close"]) / bars[-3]["close"]
        if ret > best_return:
            best_return = ret
            best_symbol = sym

    if best_symbol is None:
        return

    # 如果持有其他标的则先卖
    for sym in list(engine._broker.positions.keys()):
        if sym != best_symbol:
            held = engine._broker.positions[sym]
            bars = engine.get_visible_bars(sym)
            price = bars[-1]["close"]
            engine._broker.sell(sym, held, price)
            print(f"  {date} | 卖出 {sym} x {held} @ {price:.2f}")

    # 买入最强标的
    if best_symbol not in engine._broker.positions:
        bars = engine.get_visible_bars(best_symbol)
        price = bars[-1]["close"]
        volume = int(engine._broker.cash / price / 100) * 100
        if volume > 0:
            engine._broker.buy(best_symbol, volume, price)
            print(f"  {date} | 买入 {best_symbol} x {volume} @ {price:.2f}")


# ============================================================
# 运行
# ============================================================

if __name__ == "__main__":
    bars_dict = {
        "000001.SZ": [
            {"date": "2024-01-02", "close": 9.7},
            {"date": "2024-01-03", "close": 9.9},
            {"date": "2024-01-04", "close": 10.0},
            {"date": "2024-01-05", "close": 10.1},
            {"date": "2024-01-08", "close": 10.2},
        ],
        "600519.SH": [
            {"date": "2024-01-02", "close": 1695},
            {"date": "2024-01-03", "close": 1705},
            {"date": "2024-01-04", "close": 1715},
            {"date": "2024-01-05", "close": 1710},
            {"date": "2024-01-08", "close": 1720},
        ],
    }

    broker = SimpleBroker(initial_cash=500_000)
    engine = BacktestEngine(bars_dict, broker, dual_ma_strategy)
    result = engine.run()

    print(f"\n最终资金: {result['final_cash']:,.0f}")
    print(f"最终持仓: {result['final_positions']}")
    print(f"\n净值曲线:")
    for e in result['equity_curve']:
        print(f"  {e['date']}: {e['equity']:>12,.0f}")
