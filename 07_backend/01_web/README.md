# Web 框架

Python 主流 Web 框架横向对比配方。每个子目录覆盖相同的四个切面：最小应用、路由、请求/响应、框架特色功能。

| 目录 | 框架 | 模型 | 一句话定位 |
|------|------|------|-----------|
| [01_flask/](01_flask/) | Flask | WSGI 同步 | 最成熟的微框架，入门/小站/原型首选 |
| [02_fastapi/](02_fastapi/) | FastAPI | ASGI 异步 | 自带 Pydantic 校验 + 自动文档，当下 REST API 最推荐 |
| [03_tornado/](03_tornado/) | Tornado | 异步 + 自带事件循环 | WebSocket / 长连接 / 实时推送最擅长 |
| [04_sanic/](04_sanic/) | Sanic | ASGI 异步 | Flask 式写法 + 自带高性能服务器，追求吞吐量 |

## 各框架配方文件

| | Flask | FastAPI | Tornado | Sanic |
|---|---|---|---|---|
| 最小应用 | `01_hello.py` | `01_hello.py` | `01_hello.py` | `01_hello.py` |
| 路由 | `02_routing.py` | `02_routing.py` | `02_routing.py` | `02_routing.py` |
| 请求/响应 | `03_request_response.py` | `03_request_response.py` | `03_request_response.py` | `03_request_response.py` |
| 框架特色 | `04_blueprint_error.py` 蓝图+错误处理 | `04_pydantic_depends.py` 校验+依赖注入 | `04_coroutine.py` 异步协程+gather | `04_middleware_blueprint.py` 中间件+蓝图 |

## 横向对比

### 基础特性

```text
维度            Flask           FastAPI           Tornado           Sanic
-------------   -------------   ----------------  ----------------  --------------
编程模型         WSGI 同步        ASGI 异步          自带事件循环异步    ASGI 异步
路由风格         装饰器           装饰器 + 类型注解    类 + 正则           装饰器
数据校验         手写 / 扩展      内置（Pydantic）    手写               手写 / 扩展
自动 API 文档    无               内置 /docs          无                 有（较弱）
外部服务器       生产用 gunicorn  需 uvicorn           自带               自带
生态成熟度       最成熟           高且增长快            成熟（偏老）         中
学习曲线         低（最易上手）    中（需懂类型注解）     中（类式 Handler）   低（接近 Flask）
```

### 性能 / QPS

```text
场景                  Flask      FastAPI    Tornado    Sanic
-------------------   --------   --------   --------   --------
单进程简单 JSON 接口    ~3k        ~15k       ~12k       ~20k+
多 worker（4 核）      ~12k       ~55k       ~45k       ~80k+
CPU 密集（含计算）      受 GIL     受 GIL     受 GIL     受 GIL
I/O 密集（模拟 DB）     低         高         高         最高

注：数字为量级参考（req/s），实际受硬件/负载/序列化方式影响较大。
    Flask 用同步模型，高并发下线程/进程开销是瓶颈；其余三者 async 无此问题。
    CPU 密集场景四者均受 GIL 限制，应配合 multiprocessing 或 C 扩展。
```

### 长连接 / 实时通信

```text
能力              Flask         FastAPI       Tornado       Sanic
---------------   -----------   -----------   -----------   -----------
WebSocket         需扩展         内置支持       原生最成熟     原生支持
SSE               手写           手写           手动实现       有扩展
长轮询            可用            可用           专门优化       可用
并发连接数         受线程数限制     高（async）    高（async）   高（async）
推荐程度           ★☆☆☆☆        ★★★★☆        ★★★★★       ★★★☆☆

性能：FastAPI（uvicorn + uvloop）WebSocket 吞吐 ≥ Tornado，两者相当甚至略高。
成熟度：Tornado 生命周期钩子更完整（内置 Ping/Pong 心跳、压缩、子协议协商），生产案例更多。
选择：已有 FastAPI 项目追加 WebSocket → 直接用，性能够；核心业务是大规模实时连接 → 优先 Tornado。
```

### 功能扩展 / 生态

```text
方向              Flask                  FastAPI               Tornado              Sanic
---------------   --------------------   -------------------   ------------------   ------------------
ORM 集成          Flask-SQLAlchemy        SQLAlchemy(async)      SQLAlchemy 手接       SQLAlchemy 手接
认证              Flask-Login/JWT         fastapi-users          手写                  手写 / 扩展
表单校验          WTForms                 Pydantic（内置）        手写                  手写
后台任务          Celery / RQ             BackgroundTasks        异步任务               Sanic 扩展
中间件            before/after_request   Starlette 中间件        复写 prepare/finish    @app.middleware
测试              Flask test client       TestClient(httpx)      AsyncHTTPTestCase     sanic-testing
Admin 后台        Flask-Admin             无官方                  无                    无
插件数量           最多（数百个）           中（增长快）              较少                   少
```

### 部署

```text
方式              Flask              FastAPI           Tornado           Sanic
---------------   ----------------   ---------------   ---------------   ---------------
开发              flask run          uvicorn --reload  python app.py     python app.py
生产单机           gunicorn + gevent  uvicorn + gunicorn 自带 HTTPServer   自带 + workers=N
容器化            标准               标准               标准              标准
多进程            gunicorn -w N      gunicorn -w N      IOLoop fork       app.run(workers=N)
ASGI 兼容         否（WSGI）         是                 否（自有）          是
```

## 选型

```text
小项目 / 传统 Web / 入门             → Flask
REST API / 微服务 / 需要校验和文档    → FastAPI（当下最推荐）
WebSocket / 实时推送 / 长连接        → Tornado
纯追求异步高吞吐 + Flask 式简洁       → Sanic
```

## 运行方式（通用）

每个配方文件均支持双模式：

```bash
python 01_hello.py           # 自测：自动起服务 + curl 打一遍 + 打印响应
python 01_hello.py --serve   # 只起服务，自己另开终端 curl
```
