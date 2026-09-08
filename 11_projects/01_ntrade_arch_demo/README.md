# ntrade 架构学习 Demo（arch = architecture，架构）

从真实量化框架 [quant.ntrade.codestrategy.frame](https://gitlab.niuguwang.com/quanti/quant.ntrade.codestrategy.frame)
提炼核心设计模式，由浅入深做成可运行微缩 demo。

## 架构全景（先看这个，10 秒建立全局印象）

ntrade 用三层架构实现「策略代码写一份，回测/实盘随意切换」：

```
策略代码（demo/ 下两种形态：single 函数 / init+handlebar 生命周期）
  │  import ntdata / nttrader（扁平模块级函数）
  ▼
共享实现层（ntrade/_impl/ntdata.py, nttrader.py）
  │  所有函数都只做一件事：get_current_context().data_provider.xxx()
  ▼
线程本地全局上下文（ntrade/_impl/_runtime/nt_context.py）
  │  NtTradeContext.backtest()/live() 工厂创建，run() 内注入 + 分派
  ├──► 回测实现（BacktestDataProvider + BacktestBroker + C++ 引擎）
  └──► 实盘实现（LiveDataProvider + LiveBroker + QMT SDK）
```

> 看懂这三点即可往下走：① 策略只 import 扁平模块级函数；
> ② 函数内部经全局上下文转发；③ 上下文由工厂按模式创建，切回测/实盘只换
> provider/broker（**两路径不各存一份 ntdata/nttrader**，只是 re-export 同一份
> 实现——详见 00_design §3 红线①）。细节不用记，后面 01→06 逐个学。

## 怎么读（总分总三步）

| 步骤 | 读什么 | 目标 |
|------|--------|------|
| **总** | ① 先跑一次 [06_mini_backtest/demo_01_run_backtest.py](06_mini_backtest/demo_01_run_backtest.py) 看回测输出长啥样（30 秒，不求懂）② 看上面的"架构全景" | 建立全局印象：知道我们要造的最终产品长什么样、三层各是什么——学零件时心里有"装在哪"的锚点 |
| **分** | `01_global_context/` → `06_mini_backtest/` 逐个学 | 每阶段只引入一个新概念；docstring 已标注"教学简化 vs 真实机制"注脚，不会被带偏 |
| **总** | 全部学完，再读 [00_design/](00_design/) 复盘 | 此时 00_design 是"验证"不是"预习"：对照真实代码映射表、5 条红线，检查自己学到的是否与真实一致 |

> 00_design 的内容是"答案与地图"，学完再看才有效果；
> 学到某处想提前对照真实源码，docstring 里都写了对应文件路径。

## 学习路线

| 目录 | 主题 | 学到什么 |
|------|------|----------|
| `01_global_context/` | 全局上下文 + 模块级函数转发 | ntrade API 能无缝切换的核心秘密 |
| `02_abc_factory/` | 抽象基类 + 工厂方法 + 延迟导入 | 为什么 import ntrade 不会因为没装 C++ 引擎而报错 |
| `03_mixin_assembly/` | Mixin 多继承组装 | DataProvider 怎么按数据维度拆分成 6 个小模块 |
| `04_bar_engine/` | 逐 bar 引擎 | 回测的本质：一个 for 循环 + 防未来函数 |
| `05_adapter/` | 适配器 + 双模式兼容 | 策略函数如何被引擎驱动，两种写法如何统一 |
| `06_mini_backtest/` | 最小可运行回测框架 | 以上全部概念组合成一个能跑策略的完整引擎 |
| [00_design/](00_design/) | 架构拆解 + 重构方案（复盘用） | 真实代码映射、教学红线、逐条验证记录 |

## 各文件一览（学的时候对照，按顺序）

| 文件 | 讲什么 | 备注 |
|------|--------|------|
| [01/demo_01](01_global_context/demo_01_context_switch.py) | 全局上下文 + 模块级转发，threading.local + 多线程并发隔离 | 起点，先理解"为什么不能传参" |
| [01/demo_02](01_global_context/demo_02_context_manager.py) | 用 `with` 上下文管理器自动 set/clear | 防忘记清理、异常也清 |
| [02/demo_01](02_abc_factory/demo_01_abc_basics.py) | 抽象基类约束接口；默认实现分级（能力分级） | 02 开始"做 provider" |
| [02/demo_02](02_abc_factory/demo_02_factory_and_lazy_import.py) | 工厂方法按配置创建实现 + 延迟导入 + dataclass 配置 | ⚠️ 实盘是桩（docstring 有声明） |
| [03/demo_01](03_mixin_assembly/demo_01_mixin_basics.py) | Mixin 按数据维度拆小类再多继承组装 + MRO | provider 从"几个方法"变"完整服务" |
| [03/demo_02](03_mixin_assembly/demo_02_dual_path.py) | Mixin 内部真实模式：C++ 优先、异常回退 Python | 真实代码的 try/except 双路径 |
| [04/demo_01](04_bar_engine/demo_01_simplest_loop.py) | 回测本质：一个 for 循环 + 防未来函数 | ⚠️ 入门简化（push 传参 + 当日成交） |
| [04/demo_02](04_bar_engine/demo_02_engine_class.py) | 引擎类化：Broker/Engine 职责拆分 | ⚠️ 当日成交；pull 方向接近真实 |
| [04/demo_03](04_bar_engine/demo_03_matching_timing.py) | **撮合时序真实口径**：挂单次日开盘撮合、限价判定 | ★ 学 04 以它为准 |
| [05/demo_01](05_adapter/demo_01_strategy_protocol.py) | 适配器：把任意函数包装成引擎认得的协议对象 | 解释"为什么需要 adapter" |
| [05/demo_02](05_adapter/demo_02_dual_mode.py) | 双模式策略：single / init+handlebar 手动适配 | ⚠️ 真实靠自动探测（见 demo_03） |
| [05/demo_03](05_adapter/demo_03_auto_detect.py) | ★ 真实机制：按函数名自动探测模式 + 内省 handlebar 参数 | 对齐 strategy_loader |
| [06/](06_mini_backtest/) | 完整小框架：api/context/backtest_impl/engine 四件套 | 前面全部概念的组合 |
| [06/demo_01](06_mini_backtest/demo_01_run_backtest.py) | 跑一次完整回测（体验入口，30 秒不求懂） | 第一步先跑这个 |
| [06/demo_02](06_mini_backtest/demo_02_t1_semantics.py) | T+1 与挂单撮合语义单独演示（四天场景） | 交易层细节 |

> 符号：★ = 真实口径　⚠️ = 教学简化（docstring 内有说明）
> 04 内部注意：demo_01/02 用**当日收盘成交**（简化），**demo_03 才是真实口径**（次日开盘撮合）。

每个 demo 都可独立运行：`python <目录>/demo_xxx.py`。
06 的多文件框架在目录内跑：`cd 06_mini_backtest && python demo_01_run_backtest.py`。
