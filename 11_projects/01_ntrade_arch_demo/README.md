# ntrade 架构学习 Demo（arch = architecture，架构）

从真实量化框架 [quant.ntrade.codestrategy.frame](https://gitlab.niuguwang.com/quanti/quant.ntrade.codestrategy.frame)
提炼核心设计模式，由浅入深做成可运行微缩 demo。先读 [00_design/](00_design/) 了解全局设计，再按 01→06 逐步验证每个设计点。

## 学习路线

| 目录 | 主题 | 学到什么 |
|------|------|----------|
| [00_design/](00_design/) | 架构拆解 + 重构方案 | 真实代码长什么样、每阶段 demo 与真实机制的对应与偏差 |
| `01_global_context/` | 全局上下文 + 模块级函数转发 | ntrade API 能无缝切换的核心秘密 |
| `02_abc_factory/` | 抽象基类 + 工厂方法 + 延迟导入 | 为什么 import ntrade 不会因为没装 C++ 引擎而报错 |
| `03_mixin_assembly/` | Mixin 多继承组装 | DataProvider 怎么按数据维度拆分成 6 个小模块 |
| `04_bar_engine/` | 逐 bar 引擎 | 回测的本质：一个 for 循环 + 防未来函数 |
| `05_adapter/` | 适配器 + 双模式兼容 | 策略函数如何被引擎驱动，两种写法如何统一 |
| `06_mini_backtest/` | 最小可运行回测框架 | 以上全部概念组合成一个能跑策略的完整引擎 |

每个目录都是独立可运行的 demo，直接 `python demo_xxx.py` 即可。

## 架构全景

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

> 真实仓库：`ntrade/interface/`（协议与纯类型）、`ntrade/_impl/`（实现层）、
> `ntrade/backtest_server/`（在线回测服务，与架构核心无关）。
> 注意：**backtest 与 livetrade 不各存一份 ntdata/nttrader**——两处只是 re-export
> `_impl` 的同一份实现，真正的分支点是工厂选择的 provider/broker（详见 00_design §4）。
