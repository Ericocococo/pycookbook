# vnpy —— Python 量化交易系统开发框架

> 学习笔记 / 二次开发记录。
> 官方仓库:<https://github.com/vnpy/vnpy>
> 重环境框架(依赖交易接口、数据库、行情源),以 `.md` 笔记为主,关键代码片段随文附上。
> 本机跑用 conda 环境 `quant312`。

---

## 1. 是什么 / 解决什么

vnpy(VeighNa)是国内最流行的开源量化交易框架,覆盖**行情接入 → 策略开发 → 回测 → 实盘交易**的全链路,适合在其之上搭建自己的量化交易平台。

## 2. 环境安装

```bash
# 建议独立环境
pip install vnpy
# 具体网关(如 CTP)、UI(VeighNa Station)、回测/数据模块按需额外安装
```
> 待补充:本机 quant312 实际装了哪些模块、版本、踩到的依赖问题。

## 3. 核心架构

vnpy 的核心是「**事件驱动 + 主引擎 + 网关 + 应用**」分层:

| 组件 | 作用 |
|------|------|
| `EventEngine` 事件引擎 | 事件注册/分发,整个系统的心脏 |
| `MainEngine` 主引擎 | 管理网关与应用,统一入口 |
| `Gateway` 网关 | 对接券商/交易所接口(CTP、IB…),收发行情与订单 |
| `App` 应用模块 | 上层功能:CTA 策略、算法交易、价差、回测等 |
| UI(VeighNa Station) | 图形界面 |

**数据流**:行情 → `Gateway` → `EventEngine` → 策略 `App` → 下单 → `Gateway` → 交易所

## 4. 快速上手

> 待补充:最小可跑示例(创建 `EventEngine` + `MainEngine` → 加载 `Gateway`/`App` → 启动)。

## 5. 策略开发(以 CTA 为例)

- 继承 `CtaTemplate`,实现 `on_tick` / `on_bar` / `on_trade` / `on_order` 等回调
- 信号 → 下单 → 持仓管理的基本骨架
> 待补充:一个完整的双均线策略示例。

## 6. 回测

- `BacktestingEngine`:加载历史数据 → 设参数 → `run_backtesting()` → 结果/绩效分析
> 待补充:回测示例 + 参数优化。

## 7. 二次开发要点

- 自定义 `Gateway` 接入新接口/交易所
- 自定义 `App` 模块扩展功能
- 数据服务(datafeed)/数据库(database)适配
> 待补充:实际二开记录。

## 8. 踩坑 / 笔记

> 随手记(依赖冲突、接口限流、时区、复权处理等)。
