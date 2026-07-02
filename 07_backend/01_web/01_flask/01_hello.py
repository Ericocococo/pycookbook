"""
01_hello.py —— Flask 最小应用
================================================================================
所属: 三方库 Flask 3.1 | Python 3.12 | 安装: pip install flask

两种运行方式:
  ① 自测(推荐先跑这个,一条命令看全过程):
        python 01_hello.py
     会自动起服务、用真实 curl 打一遍、打印响应、再关掉服务。
  ② 手动:先起服务,再另开终端 curl:
        python 01_hello.py serve
        curl http://127.0.0.1:8011/            # 根路由,返回纯文本
        curl http://127.0.0.1:8011/json        # 返回 JSON

Flask 是同步 WSGI 微框架:@app.route 装饰器注册路由,视图函数返回值即响应。
WSGI = Web 服务器网关接口,Python 同步 Web 应用与服务器之间的标准接口。
================================================================================
"""
import sys

from flask import Flask, jsonify

PORT = 8011
app = Flask(__name__)
app.json.ensure_ascii = False         # 让 JSON 里的中文直接输出,不转成 \uXXXX


@app.route("/")                       # 装饰器把 URL 路径绑定到视图函数
def index():
    """返回纯文本:视图直接 return 字符串,Flask 包成 200 响应。"""
    return "Hello Flask"


@app.route("/json")
def hello_json():
    """返回 JSON:jsonify 把 dict 序列化并设好 Content-Type。"""
    return jsonify(framework="flask", msg="你好")


# curl 自测用例:(说明 + 请求方法/路径),交给 _curl_selftest 逐条真实调用
CURL_CASES = [
    {"desc": "根路由,返回纯文本", "path": "/"},
    {"desc": "返回 JSON", "path": "/json"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # 阻塞启动真实服务(供手动 curl)
        app.run(host="127.0.0.1", port=PORT)
    else:
        # 自测:起服务子进程 + 真实 curl 调用
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
