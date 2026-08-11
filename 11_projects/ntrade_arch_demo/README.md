# ntrade 架构学习 Demo

从 `quant.core.frame/ntrade` 中提炼的核心设计模式，由浅入深分 6 个阶段。

## 架构全景

ntrade 用三层架构实现「策略代码写一份，回测/实盘随意切换」：

```
策略代码
  │  import ntdata / nttrader（模块级函数）
  │
  ▼
共享实现层（_impl/ntdata.py, _impl/nttrader.py）
  │  所有函数都只做一件事：get_current_context().data_provider.xxx()
  │
  ▼
全局上下文（NtTradeContext）
  │  持有 data_provider + broker，由工厂方法 backtest()/live() 创建
  │
  ├──► 回测实现（BacktestDataProvider + BacktestBroker + C++引擎）
  └──► 实盘实现（LiveDataProvider + LiveBroker + QMT SDK）
```

## 学习路线

| 目录 | 主题 | 学到什么 |
|------|------|----------|
| `01_global_context/` | 全局上下文 + 模块级函数转发 | ntrade API 能无缝切换的核心秘密 |
| `02_abc_factory/` | 抽象基类 + 工厂方法 + 延迟导入 | 为什么 import ntrade 不会因为没装 C++ 引擎而报错 |
| `03_mixin_assembly/` | Mixin 多继承组装 | DataProvider 怎么按数据维度拆分成 6 个小模块 |
| `04_bar_engine/` | 逐 bar 引擎 | 回测的本质：一个 for 循环 + 防未来函数 |
| `05_adapter/` | 适配器 + 双模式兼容 | 策略函数如何被引擎驱动，两种写法如何统一 |
| `06_mini_backtest/` | 最小可运行回测框架 | 以上全部概念组合成一个能跑策略的完整引擎 |

每个目录都是独立可运行的 demo，直接 `python demo_xxx.py` 即可。
