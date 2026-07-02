"""
02_routing.py —— Flask 路由:路径参数 / 查询参数 / HTTP 方法
================================================================================
所属: 三方库 Flask 3.1 | Python 3.12

运行:
  python 02_routing.py            # 自测:真实 curl 打一遍
  python 02_routing.py serve      # 起服务,手动 curl:
    curl http://127.0.0.1:8012/user/1                 # 路径参数(int 转换)
    curl 'http://127.0.0.1:8012/users?limit=2'        # 查询参数
    curl -X POST http://127.0.0.1:8012/user           # POST 方法
    curl -X PUT  http://127.0.0.1:8012/user/1         # PUT 方法
    curl -X DELETE http://127.0.0.1:8012/user/1       # DELETE 方法

要点:
  ① <int:uid>  —— 路径参数带类型转换器(string/int/float/path/uuid)
  ② request.args.get —— 取 URL 查询参数(?limit=2)
  ③ methods=[...] —— 一个路径按 HTTP 方法(GET/POST/PUT/DELETE)分发
================================================================================
"""
import sys

from flask import Flask, jsonify, request

PORT = 8012
app = Flask(__name__)
app.json.ensure_ascii = False

# 内存假数据,仅供演示(重启即还原)
USERS = {1: {"id": 1, "name": "张三"}, 2: {"id": 2, "name": "李四"}}


@app.route("/user/<int:uid>")             # ① <int:uid>:把路径段转成 int 再传入
def get_user(uid):
    """路径参数:uid 已是 int 类型。"""
    user = USERS.get(uid)
    if user is None:
        return jsonify(error=f"用户 {uid} 不存在"), 404
    return jsonify(user)


@app.route("/users")
def list_users():
    """查询参数:?limit=N 控制返回条数,type=int 自动转换 + 默认值。"""
    limit = request.args.get("limit", default=10, type=int)   # ② 查询参数
    items = list(USERS.values())[:limit]
    return jsonify(count=len(items), limit=limit, items=items)


@app.route("/user", methods=["POST"])     # ③ 同一资源不同方法
def create_user():
    """POST 创建:这里只演示方法分发,JSON body 处理见 03。"""
    new_id = max(USERS) + 1 if USERS else 1
    USERS[new_id] = {"id": new_id, "name": f"用户{new_id}"}
    return jsonify(created=USERS[new_id]), 201


@app.route("/user/<int:uid>", methods=["PUT"])
def update_user(uid):
    """PUT 更新。"""
    if uid not in USERS:
        return jsonify(error=f"用户 {uid} 不存在"), 404
    USERS[uid]["name"] = "已更新"
    return jsonify(updated=USERS[uid])


@app.route("/user/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    """DELETE 删除。"""
    removed = USERS.pop(uid, None)
    if removed is None:
        return jsonify(error=f"用户 {uid} 不存在"), 404
    return jsonify(deleted=removed)


CURL_CASES = [
    {"desc": "路径参数:取 id=1 的用户", "path": "/user/1"},
    {"desc": "路径参数:不存在的 id → 404", "path": "/user/99"},
    {"desc": "查询参数:limit=1 只取 1 条", "path": "/users?limit=1"},
    {"desc": "POST 创建用户", "method": "POST", "path": "/user"},
    {"desc": "PUT 更新用户 1", "method": "PUT", "path": "/user/1"},
    {"desc": "DELETE 删除用户 2", "method": "DELETE", "path": "/user/2"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        app.run(host="127.0.0.1", port=PORT)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
