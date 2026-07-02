"""
03_request_response.py —— Flask 请求与响应:JSON body / 状态码 / 响应头
================================================================================
所属: 三方库 Flask 3.1 | Python 3.12

运行:
  python 03_request_response.py         # 自测:真实 curl 打一遍
  python 03_request_response.py --serve   # 起服务,手动 curl:
    curl -X POST http://127.0.0.1:8013/echo \
         -H 'Content-Type: application/json' -d '{"name":"王五","age":18}'
    curl -i http://127.0.0.1:8013/headers      # -i 连响应头一起看

要点:
  ① request.get_json() —— 解析请求体 JSON 成 dict
  ② request.headers    —— 读请求头
  ③ 返回 (body, 状态码, 头字典) 三元组 —— 自定义状态码和响应头
  ④ make_response      —— 需要更精细地构造响应对象时用
================================================================================
"""

from flask import Flask, jsonify, make_response, request

PORT = 8013
app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/echo", methods=["POST"])
def echo():
    """① 读 JSON body 原样回显,并回报收到的字段数。"""
    data = request.get_json(silent=True)          # silent=True:非法 JSON 返回 None 不报错
    if not isinstance(data, dict):
        return jsonify(error="请发送 JSON 对象"), 400
    return jsonify(received=data, field_count=len(data))


@app.route("/headers")
def show_headers():
    """② 读请求头:取 User-Agent(客户端标识)。"""
    ua = request.headers.get("User-Agent", "unknown")
    # ③ 返回三元组:body + 状态码 + 自定义响应头
    return jsonify(your_user_agent=ua), 200, {"X-Powered-By": "flask-demo"}


@app.route("/created", methods=["POST"])
def created():
    """④ make_response 构造响应,再设状态码和头。"""
    resp = make_response(jsonify(msg="资源已创建"))
    resp.status_code = 201
    resp.headers["Location"] = "/resource/1"      # 常见:创建后告知新资源地址
    return resp


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
        app.run(host="127.0.0.1", port=PORT)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
