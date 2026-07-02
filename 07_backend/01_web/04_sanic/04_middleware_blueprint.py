"""
04_middleware_blueprint.py —— Sanic 特色:中间件 + 蓝图
================================================================================
所属: 三方库 Sanic 25.x | Python 3.12

运行:
  python 04_middleware_blueprint.py         # 自测:真实 curl 打一遍
  python 04_middleware_blueprint.py serve   # 起服务,手动 curl:
    curl -i http://127.0.0.1:9044/api/ping    # 看中间件加的 X-Process-Time 响应头
    curl http://127.0.0.1:9044/api/hello/world

要点:
  ① @app.on_request / @app.on_response —— 中间件(钩子):请求前、响应后统一处理
     常用于:鉴权、计时、加公共响应头、日志
     request.ctx —— 每个请求独立的上下文对象,用来在钩子间传数据
  ② Blueprint —— 把一组路由打包成模块,统一挂到某个 url_prefix 下
================================================================================
"""
import json
import sys
import time
from functools import partial

from sanic import Blueprint, Sanic
from sanic.response import json as sjson

PORT = 9044
app = Sanic("MiddlewareApp")
_dumps = partial(json.dumps, ensure_ascii=False)


def jresp(obj, status=200):
    return sjson(obj, status=status, dumps=_dumps)


# ① 中间件:请求进来时记开始时间,响应出去时算耗时并写进响应头
@app.on_request
async def start_timer(request):
    request.ctx.start = time.monotonic()      # request.ctx 存本次请求的临时数据


@app.on_response
async def add_process_time(request, response):
    cost = (time.monotonic() - getattr(request.ctx, "start", time.monotonic())) * 1000
    response.headers["X-Process-Time-Ms"] = f"{cost:.1f}"   # 每个响应都带上耗时


# ② 蓝图:一组 /api 下的路由打包成模块
api = Blueprint("api", url_prefix="/api")


@api.get("/ping")
async def ping(request):
    return jresp({"module": "api", "msg": "pong"})


@api.get("/hello/<name:str>")
async def hello(request, name):
    return jresp({"hello": name})


app.blueprint(api)                            # 把蓝图挂载到 app


CURL_CASES = [
    {"desc": "蓝图路由 /api/ping,响应头含中间件加的 X-Process-Time-Ms",
     "show_headers": True, "path": "/api/ping"},
    {"desc": "蓝图路由 + 路径参数", "path": "/api/hello/world"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        app.run(host="127.0.0.1", port=PORT,
                single_process=True, access_log=False, motd=False)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
