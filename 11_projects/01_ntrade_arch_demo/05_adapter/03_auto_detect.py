# coding=utf-8
"""自动探测策略模式 — 引擎零配置，按函数名认出两种写法。

Python 3.12。
运行: python 03_auto_detect.py

演示：
  ① 三种策略文件自动探测：single / lifecycle / lifecycle+bar_dict+别名
  ② 签名内省：handlebar 是否声明第二参 bar_dict

## 02_dual_mode 留下的问题

02_dual_mode 里选哪种模式靠**手动传参**（构造 StrategyWrapper 时指定
strategy_fn / handlebar）。真实 ntrade 不需要——策略文件加载后
引擎自己"看函数名"就能判断该按哪种方式驱动。

## 真实实现（ntrade/_impl/strategy_loader.py，已源码核实）

collect_strategy_functions() 的探测规则：
  模块里有 handlebar 或 handle_bar → lifecycle 模式
      （自动收集 init/initialize、after_init、on_stop，
        on_stop 兼容 qmttools 的 on_backtest_finished 别名）
  否则 → single 模式（strategy / macd_strategy / 第一个可调用函数）

还有个细节：handlebar 可以声明第二参 bar_dict（拿到当前 bar 快照）。
调用时用 inspect.signature 内省——声明了第二参才传，不声明就只传 context，
同一份引擎兼容两种签名。

## 学到什么

- 按函数名/签名探测：约定优于配置
- inspect.signature 内省：适配器读取函数声明，兼容不同签名
- 别名兼容：qmttools 的 on_backtest_finished → 同一钩子
"""

import inspect

# ============================================================
# 探测函数 — 从"策略模块"（用 dict 模拟）认出模式
# ============================================================

def collect_strategy_functions(module):
    """按函数名自动探测策略模式（对齐真实 strategy_loader）。

    module: 用 dict 模拟策略模块的命名空间（真实是动态加载的 .py 模块）
    返回: {"mode": "lifecycle"/"single", "strategy_fn"/"init"/"handlebar"...}
    """
    # 别名归一：qmttools 叫 handle_bar / on_backtest_finished，
    # ntrade 兼容收集（真实代码 getattr(mod, "handlebar") or getattr(mod, "handle_bar")）
    init_fn = module.get("init") or module.get("initialize")
    handlebar_fn = module.get("handlebar") or module.get("handle_bar")
    on_stop_fn = module.get("on_stop") or module.get("on_backtest_finished")

    if handlebar_fn is not None:
        # lifecycle 模式：有逐 bar 回调 → 按生命周期驱动
        return {"mode": "lifecycle", "init": init_fn, "handlebar": handlebar_fn,
                "after_init": module.get("after_init"), "on_stop": on_stop_fn}

    # single 模式：strategy / macd_strategy / 第一个可调用
    strategy_fn = module.get("strategy") or module.get("macd_strategy")
    if strategy_fn is None:
        for name, obj in module.items():
            if not name.startswith("_") and callable(obj):
                strategy_fn = obj
                break
    if strategy_fn is None:
        raise RuntimeError("策略模块需定义 handlebar 或 strategy/macd_strategy")
    return {"mode": "single", "strategy_fn": strategy_fn}


# ============================================================
# 适配器 — 把探测结果包装成引擎可驱动的形式
# ============================================================

class Engine:
    """引擎：不关心策略是什么形态，只按 desc 驱动。"""

    def __init__(self):
        self.ctx = {"symbol": "600519.SH"}           # 简化策略上下文
        self.bar_dict = {"600519.SH": {"close": 1715.0}}

    def run(self, desc):
        if desc["mode"] == "lifecycle":
            print("  [Engine] lifecycle 模式: init → handlebar × N")
            if desc["init"]:
                desc["init"]()
            for _ in range(2):
                # handlebar 签名不确定（一参或两参）→ 内省后调用
                call_handlebar(desc["handlebar"], self.ctx, self.bar_dict)
            if desc["on_stop"]:
                desc["on_stop"]()
        else:
            print("  [Engine] single 模式: 直接调策略函数")
            desc["strategy_fn"]()


def call_handlebar(handlebar, context, bar_dict):
    """按函数签名决定传不传 bar_dict（真实用 inspect.signature 判断）。

    为什么需要？qmttools 风格 handlebar(context) 只收一参，
    迅投风格 handlebar(context, bar_dict) 要两参——同一引擎两种都支持。
    """
    params = list(inspect.signature(handlebar).parameters.values())
    if len(params) >= 2:
        handlebar(context, bar_dict)     # 声明了第二参 → 传 bar_dict
    else:
        handlebar(context)               # 只声明一参 → 不传


# ============================================================
# 三种策略写法（模拟三个策略文件）
# ============================================================

# 文件 A：single 模式 — 无参函数（xtquant 风格）
def strategy_a():
    print("    [single] 检查行情 → 决策 → 下单...")


# 文件 B：lifecycle 模式 — init + handlebar（qmttools 风格）
def init_b():
    print("    [init] 设置标的与资金")


def handlebar_b(context):
    print(f"    [handlebar] bar={context} 决策...")


# 文件 C：lifecycle 模式 + 第二参 bar_dict + 别名钩子
def init_c():
    print("    [init] C 策略初始化")


def handlebar_c(context, bar_dict):
    bar = bar_dict.get("600519.SH", {})
    print(f"    [handlebar] bar={context} 当前bar close={bar.get('close')}...")


def on_backtest_finished_c():
    print("    [on_backtest_finished] qmttools 别名钩子触发（等同 on_stop）")


def demo01_auto_detect():
    """① 三种策略文件自动探测：
    文件A = single 模式，文件B = lifecycle 模式，
    文件C = lifecycle + bar_dict + 别名钩子。
    """
    print("① 三种策略文件自动探测")
    modules = {
        "文件A(single)": {"strategy": strategy_a},
        "文件B(lifecycle)": {"init": init_b, "handlebar": handlebar_b},
        "文件C(lifecycle+bar_dict+别名)": {
            "init": init_c, "handlebar": handlebar_c,
            "on_backtest_finished": on_backtest_finished_c,
        },
    }

    engine = Engine()
    for name, mod in modules.items():
        print(f"\n  --- {name} ---")
        desc = collect_strategy_functions(mod)          # 自动探测
        print(f"  探测结果: mode = {desc['mode']}")
        engine.run(desc)                                # 引擎统一驱动


def demo02_signature_inspect():
    """② 签名内省：handlebar 是否声明第二参 bar_dict，引擎按声明动态传参。"""
    print("\n② 签名内省：handlebar 收不收 bar_dict")
    ctx = {"symbol": "600519.SH"}
    bar_dict = {"600519.SH": {"close": 1715.0}}
    print("  调 handlebar_b（一参）:")
    call_handlebar(handlebar_b, ctx, bar_dict)
    print("  调 handlebar_c（两参）:")
    call_handlebar(handlebar_c, ctx, bar_dict)


if __name__ == "__main__":
    demo01_auto_detect()
    demo02_signature_inspect()
