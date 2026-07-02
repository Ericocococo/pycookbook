"""
01_hello.py —— Sanic 最小应用
================================================================================
所属: 三方库 Sanic 25.x | Python 3.12 | 安装: pip install sanic

两种运行方式:
  ① 自测(推荐):python 01_hello.py
  ② 手动:python 01_hello.py --serve,再另开终端:
        curl http://127.0.0.1:9041/            # 纯文本
        curl http://127.0.0.1:9041/json        # JSON

Sanic 是高性能异步框架,写法接近 Flask(装饰器路由),但全异步、自带服务器:
  - @app.get 装饰器注册路由;handler 首参固定是 request 且是 async
  - app.run 内置服务器直接跑,无需额外的 uvicorn/gunicorn
(演示用 single_process=True 单进程启动,便于自测;生产可多 worker)
================================================================================
"""
import json
from functools import partial

from sanic import Sanic
from sanic.response import json as sjson
from sanic.response import text

PORT = 9041
app = Sanic("HelloApp")

# Sanic 的 JSON 默认会转义中文,自定义 dumps 让中文直接输出
_dumps = partial(json.dumps, ensure_ascii=False)


@app.get("/")
async def index(request):
    """纯文本响应。"""
    return text("Hello Sanic")


@app.get("/json")
async def hello_json(request):
    """JSON 响应:用自定义 dumps 保留中文。"""
    return sjson({"framework": "sanic", "msg": "你好"}, dumps=_dumps)


CURL_CASES = [
    {"desc": "根路由,返回纯文本", "path": "/"},
    {"desc": "返回 JSON", "path": "/json"},
]


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        # single_process 避免 Windows 下多进程 worker 重复导入;关掉访问日志和启动横幅
        app.run(host="127.0.0.1", port=PORT,
                single_process=True, access_log=False, motd=False)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
