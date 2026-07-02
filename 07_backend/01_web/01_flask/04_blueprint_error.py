"""
04_blueprint_error.py —— Flask 蓝图分模块 + 自定义错误处理
================================================================================
所属: 三方库 Flask 3.1 | Python 3.12

运行:
  python 04_blueprint_error.py         # 自测:真实 curl 打一遍
  python 04_blueprint_error.py --serve   # 起服务,手动 curl:
    curl http://127.0.0.1:8014/api/ping          # 蓝图路由(带 /api 前缀)
    curl http://127.0.0.1:8014/api/boom          # 触发 500,看自定义错误 JSON
    curl http://127.0.0.1:8014/not-exist         # 404 自定义 JSON

要点:
  ① Blueprint —— 把一组相关路由拆成模块,注册时统一加 url_prefix
     蓝图 = Flask 里对路由分组/模块化的机制,便于大项目拆分
  ② @app.errorhandler(404/500) —— 全局错误处理,统一返回 JSON 而非 HTML
================================================================================
"""

from flask import Blueprint, Flask, jsonify

PORT = 8014

# ① 定义一个蓝图:名字 "api",后面统一挂到 /api 前缀下
api = Blueprint("api", __name__)


@api.route("/ping")
def ping():
    """蓝图内的路由;最终路径是 前缀 + 这里 = /api/ping。"""
    return jsonify(module="api", msg="pong")


@api.route("/boom")
def boom():
    """故意抛异常,演示 500 错误处理。"""
    raise RuntimeError("模拟服务器内部错误")


def create_app():
    """应用工厂:创建 app、注册蓝图和错误处理器。"""
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(api, url_prefix="/api")   # ① 挂载蓝图到 /api

    @app.errorhandler(404)                           # ② 404 统一返回 JSON
    def not_found(err):
        return jsonify(error="not found", path_hint="试试 /api/ping"), 404

    @app.errorhandler(500)                           # ② 500 统一返回 JSON
    def server_error(err):
        return jsonify(error="internal server error"), 500

    return app


app = create_app()


CURL_CASES = [
    {"desc": "蓝图路由 /api/ping", "path": "/api/ping"},
    {"desc": "触发 500 → 自定义错误 JSON", "path": "/api/boom"},
    {"desc": "访问不存在路径 → 404 自定义 JSON", "path": "/not-exist"},
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
