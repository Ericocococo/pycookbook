"""
03_request_response.py —— Tornado 请求与响应:JSON body / 状态码 / 响应头
================================================================================
所属: 三方库 Tornado 6.x | Python 3.12

运行:
  python 03_request_response.py         # 自测:真实 curl 打一遍
  python 03_request_response.py serve   # 起服务,手动 curl:
    curl -X POST http://127.0.0.1:9033/echo \
         -H 'Content-Type: application/json' -d '{"name":"王五","age":18}'
    curl -i http://127.0.0.1:9033/headers

要点:
  ① self.request.body —— 原始请求体(bytes),用 json.loads 解析
  ② self.request.headers.get —— 读请求头
  ③ self.set_status / self.set_header —— 自定义状态码和响应头
================================================================================
"""
import asyncio
import json
import sys

import tornado.web

PORT = 9033


def write_json(handler, obj, status=200):
    handler.set_status(status)
    handler.set_header("Content-Type", "application/json; charset=utf-8")
    handler.write(json.dumps(obj, ensure_ascii=False))


class EchoHandler(tornado.web.RequestHandler):
    def post(self):
        """① 解析 JSON 请求体并回显。"""
        try:
            data = json.loads(self.request.body or b"{}")
        except json.JSONDecodeError:
            return write_json(self, {"error": "非法 JSON"}, 400)
        if not isinstance(data, dict):
            return write_json(self, {"error": "请发送 JSON 对象"}, 400)
        write_json(self, {"received": data, "field_count": len(data)})


class HeadersHandler(tornado.web.RequestHandler):
    def get(self):
        """② 读请求头;③ 设自定义响应头。"""
        ua = self.request.headers.get("User-Agent", "unknown")
        self.set_header("X-Powered-By", "tornado-demo")
        write_json(self, {"your_user_agent": ua})


class CreatedHandler(tornado.web.RequestHandler):
    def post(self):
        """③ 自定义状态码 201 + Location 头。"""
        self.set_header("Location", "/resource/1")
        write_json(self, {"msg": "资源已创建"}, 201)


def make_app():
    return tornado.web.Application([
        (r"/echo", EchoHandler),
        (r"/headers", HeadersHandler),
        (r"/created", CreatedHandler),
    ])


async def main():
    make_app().listen(PORT, address="127.0.0.1")
    await asyncio.Event().wait()


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
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        asyncio.run(main())
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
