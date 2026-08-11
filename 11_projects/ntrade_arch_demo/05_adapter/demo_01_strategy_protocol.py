# coding=utf-8
"""适配器模式 — 把策略函数包装成引擎能识别的接口。

## 上一节的问题

策略函数直接接收 engine 引用：strategy(engine)。
但真实引擎（尤其是 C++ 引擎）不认识 Python 函数，
它需要一个固定协议的对象：

    class CPyStrategy:
        def on_start(self): ...
        def next(self): ...
        def on_stop(self): ...

引擎按生命周期调用这些方法，不关心策略具体怎么写。

## 方案：适配器（Adapter / Wrapper）

写一个 StrategyWrapper，把用户的策略函数包装成引擎要求的协议：

    class StrategyWrapper(CPyStrategy):
        def __init__(self, user_fn):
            self._fn = user_fn
        def next(self):
            self._fn()      # 引擎调 next() → 实际执行用户策略

ntrade 中 _BacktestStrategyWrapper 就是这个角色。

## 学到什么

- 适配器模式：接口不兼容时用 Wrapper 转换
- 引擎的生命周期协议（on_start / next / on_stop）
- 策略函数如何被引擎「逐 bar 调用」
"""

from abc import ABC, abstractmethod


# ============================================================
# 引擎的策略协议（C++ 引擎要求的接口）
# ============================================================

class IStrategy(ABC):
    """策略协议 — 引擎通过这些方法驱动策略。

    ntrade 对应: CPyStrategy（C++ 端定义的接口）
    - on_start():  回测开始时调用一次
    - next():      每个 bar 调用一次（策略决策点）
    - on_stop():   回测结束时调用一次
    """

    @abstractmethod
    def on_start(self):
        ...

    @abstractmethod
    def next(self):
        ...

    @abstractmethod
    def on_stop(self):
        ...


# ============================================================
# 引擎 — 只认识 IStrategy 协议
# ============================================================

class Engine:
    """回测引擎 — 按协议驱动策略。

    引擎不知道策略的具体逻辑，只按生命周期调用接口。
    """

    def __init__(self, dates, strategy: IStrategy):
        self._dates = dates
        self._strategy = strategy

    def run(self):
        print("[Engine] 调用 on_start()")
        self._strategy.on_start()

        for i, date in enumerate(self._dates):
            print(f"[Engine] bar {i+1}/{len(self._dates)} ({date}) → 调用 next()")
            self._strategy.next()

        print("[Engine] 调用 on_stop()")
        self._strategy.on_stop()


# ============================================================
# 用户写的策略函数 — 只是一个普通函数，不懂什么协议
# ============================================================

def user_strategy():
    """用户的策略函数 — 简单打印。

    用户不想（也不该）去实现 IStrategy，
    他只想写一个函数就完事。
    """
    print("    → 策略执行中: 检查行情, 决定是否下单...")


# ============================================================
# 适配器 — 把普通函数包装成 IStrategy
# ============================================================

class StrategyWrapper(IStrategy):
    """策略适配器 — 把用户函数包装成引擎要求的 IStrategy。

    ntrade 对应: _BacktestStrategyWrapper（_adapter.py 中的内部类）

    ntrade 的真实代码：
        class _BacktestStrategyWrapper:
            def __init__(self, strategy_fn, ctx):
                self._fn = strategy_fn
                self._ctx = ctx

            def init_cppctx(self, cpp_ctx):
                # C++ 引擎注入上下文（注入 broker + data_provider 的 C++ 引用）
                ...

            def on_start(self):
                self._ctx.after_init()

            def next(self):
                self._fn()          # ← 用户策略在这里执行

            def on_stop(self):
                self._ctx.on_stop()
    """

    def __init__(self, user_fn, on_start_fn=None, on_stop_fn=None):
        self._fn = user_fn
        self._on_start = on_start_fn
        self._on_stop = on_stop_fn

    def on_start(self):
        if self._on_start:
            self._on_start()
        print("  [Wrapper] 策略已就绪")

    def next(self):
        self._fn()

    def on_stop(self):
        if self._on_stop:
            self._on_stop()
        print("  [Wrapper] 策略已结束")


# ============================================================
# 运行演示
# ============================================================

if __name__ == "__main__":
    dates = ["2024-01-02", "2024-01-03", "2024-01-04"]

    # 用户只写了一个函数
    # 适配器把它包装成引擎要求的 IStrategy
    wrapper = StrategyWrapper(user_strategy)

    # 引擎只认识 IStrategy，不知道里面是个普通函数
    engine = Engine(dates, wrapper)
    engine.run()
