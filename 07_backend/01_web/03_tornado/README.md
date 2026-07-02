# Tornado —— 老牌异步 Web 框架 + 网络库(三方库)

| 文件 | 内容 |
|------|------|
| `01_hello.py` | 最小应用:RequestHandler 子类 + Application 路由表 |
| `02_routing.py` | 正则路由 + 捕获组作路径参数;查询参数;方法分发 |
| `03_request_response.py` | 解析 JSON body、读请求头、set_status/set_header |
| `04_coroutine.py` | 特色:async 协程 handler、await 异步 IO、gather 并发 |
| `_curl_selftest.py` | 【工具,非配方】起服务 + 真实 curl 自测助手 |

## 运行方式

```bash
python 01_hello.py            —— 自测:起服务 + 真实 curl 打一遍
python 01_hello.py --serve      —— 只起服务,自己 curl
```

## 适用

- WebSocket、长轮询、SSE 等长连接 / 实时推送(Tornado 最擅长)
- 高并发 I/O、需要对连接做精细控制
- 想要一个自带服务器 + 事件循环的异步框架

## 不适用

- 只是写普通 REST API → FastAPI 更省事(自带校验和文档)
- 传统同步 Web / 服务端渲染 → Flask 更简单
- 嫌类式 handler 样板多、想要装饰器风格 → Sanic/FastAPI

## 核心速查

```python
import asyncio, tornado.web
class H(tornado.web.RequestHandler):
    async def get(self, uid):        # 正则捕获组按位置传入; 方法即 HTTP 动词
        self.write({"uid": uid})     # write(dict) 自动 JSON(默认转义中文)
app = tornado.web.Application([(r"/user/(\\d+)", H)])
async def main():
    app.listen(8000); await asyncio.Event().wait()
asyncio.run(main())

```

> 四框架横向对比见 [01_flask/README.md](../01_flask/README.md)
