"""
03_request_response.py —— Sanic 请求与响应:JSON body / 状态码 / 响应头
================================================================================
所属: 三方库 Sanic 25.x | Python 3.12

运行:
  python 03_request_response.py         # 自测:真实 curl 打一遍
  python 03_request_response.py --serve   # 起服务,手动 curl:
    curl -X POST http://127.0.0.1:9043/echo \
         -H 'Content-Type: application/json' -d '{"name":"王五","age":18}'
    curl -i http://127.0.0.1:9043/headers

要点:
  ① request.json —— 直接拿到解析好的 JSON 请求体(dict)
  ② request.headers.get —— 读请求头
  ③ 响应对象的 status / headers —— 自定义状态码和响应头
================================================================================
"""
import json
from functools import partial

from sanic import Sanic
from sanic.response import json as sjson

PORT = 9043
app = Sanic("ReqRespApp")
_dumps = partial(json.dumps, ensure_ascii=False)


def jresp(obj, status=200, headers=None):
    return sjson(obj, status=status, headers=headers, dumps=_dumps)


@app.post("/echo")
async def echo(request):
    """① request.json 直接是解析好的 dict(非法/空则为 None)。"""
    data = request.json
    if not isinstance(data, dict):
        return jresp({"error": "请发送 JSON 对象"}, 400)
    return jresp({"received": data, "field_count": len(data)})


@app.get("/headers")
async def show_headers(request):
    """② 读请求头;③ 通过 headers 参数设自定义响应头。"""
    ua = request.headers.get("User-Agent", "unknown")
    return jresp({"your_user_agent": ua}, headers={"X-Powered-By": "sanic-demo"})


@app.post("/created")
async def created(request):
    """③ 自定义状态码 201 + Location 头。"""
    return jresp({"msg": "资源已创建"}, status=201, headers={"Location": "/resource/1"})


CURL_CASES = [
    {"desc": "POST JSON 回显", "method": "POST", "path": "/echo",
     "json": {"name": "王五", "age": 18}},
    {"desc": "POST 非对象 JSON → 400", "method": "POST", "path": "/echo",
     "json": [1, 2, 3]},
    {"desc": "读请求头 + 自定义响应头(X-Powered-By)", "show_headers": True,
     "path": "/headers", "headers": {"User-Agent": "curl-demo/1.0"}},
    {"desc": "创建资源:201 + Location 头", "show_headers": True,
     "method": "POST", "path": "/created"},
]


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        app.run(host="127.0.0.1", port=PORT,
                single_process=True, access_log=False, motd=False)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
