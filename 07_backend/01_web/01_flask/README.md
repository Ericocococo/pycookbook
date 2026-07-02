# Flask —— 轻量同步 Web 微框架(三方库)

| 文件 | 内容 |
|------|------|
| `01_hello.py` | 最小应用:@app.route 路由、返回文本/JSON |
| `02_routing.py` | 路径参数 <int:uid>、查询参数、GET/POST/PUT/DELETE 方法 |
| `03_request_response.py` | 读 JSON body、状态码、请求头/响应头、make_response |
| `04_blueprint_error.py` | 蓝图(Blueprint)分模块 + 自定义 404/500 错误处理 |
| `_curl_selftest.py` | 【工具,非配方】各配方共用的「起服务 + 真实 curl 自测」助手 |

## 运行方式

```bash
python 01_hello.py            —— 自测:自动起服务 + 用真实 curl 打一遍 + 打印响应
python 01_hello.py --serve      —— 只起服务,自己另开终端 curl(命令见各文件头部)
说明:每个配方都是「双模式」,curl 用例写在文件顶部 docstring 和末尾 CURL_CASES 里。
```

## 适用

- 中小型 Web 站点、后台管理、快速原型
- 传统服务端渲染(配 Jinja2 模板)
- 团队熟悉、生态成熟(flask-sqlalchemy / flask-login 等扩展齐全)
- 入门学习 Web 开发

## 不适用

- 超高并发 I/O 密集(同步 WSGI 模型,异步不是强项)→ 看 FastAPI/Sanic
- WebSocket / 长连接为主 → 看 Tornado
- 需要开箱即用的数据校验 + 自动 API 文档 → 看 FastAPI

## 核心速查

```python
from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route("/user/<int:uid>", methods=["GET", "POST"])
def handler(uid):
    request.args.get("q")          # 查询参数 ?q=
    request.get_json()             # 请求体 JSON
    return jsonify(id=uid), 201    # 返回 JSON + 状态码
app.run(host="127.0.0.1", port=8000)

```

## 四框架横向对比

```text
维度        Flask          FastAPI          Tornado         Sanic
----------  -------------  ---------------  --------------  --------------
编程模型     WSGI 同步      ASGI 异步         自带/asyncio     ASGI 异步
                                            异步
路由风格     装饰器          装饰器+类型注解    类 + 正则        装饰器
数据校验     手写/扩展       内置(Pydantic)   手写            手写/扩展
自动文档     无             内置 /docs        无              有(较弱)
外部服务器   生产用 gunicorn 需 uvicorn        自带            自带
性能        中             高                高              很高
生态成熟度   最成熟          高且增长快         成熟(偏老)      中
最擅长      小站/原型       REST API/微服务    WebSocket/长连接  高吞吐 API

一句话选型:
  小项目/传统 Web/入门        → Flask
  REST API/微服务/要校验和文档 → FastAPI(当下最推荐)
  WebSocket/实时推送/长连接    → Tornado
  纯追求异步高吞吐 + Flask 式简洁 → Sanic
```
