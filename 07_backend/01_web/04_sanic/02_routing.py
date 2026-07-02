"""
02_routing.py —— Sanic 路由:路径参数 / 查询参数 / HTTP 方法
================================================================================
所属: 三方库 Sanic 25.x | Python 3.12

运行:
  python 02_routing.py            # 自测:真实 curl 打一遍
  python 02_routing.py serve      # 起服务,手动 curl:
    curl http://127.0.0.1:9042/user/1
    curl 'http://127.0.0.1:9042/users?limit=1'
    curl -X POST http://127.0.0.1:9042/user
    curl -X PUT  http://127.0.0.1:9042/user/1
    curl -X DELETE http://127.0.0.1:9042/user/2

要点(写法接近 Flask,但全异步):
  ① <uid:int> —— 路径参数带类型(str/int/float/uuid/path...)
  ② request.args.get —— 取查询参数(?limit=1)
  ③ @app.get/post/put/delete —— 按 HTTP 方法分发;handler 首参固定是 request
================================================================================
"""
import json
import sys
from functools import partial

from sanic import Sanic
from sanic.response import json as sjson

PORT = 9042
app = Sanic("RoutingApp")
_dumps = partial(json.dumps, ensure_ascii=False)

USERS = {1: {"id": 1, "name": "张三"}, 2: {"id": 2, "name": "李四"}}


def jresp(obj, status=200):
    """统一 JSON 响应,中文不转义。"""
    return sjson(obj, status=status, dumps=_dumps)


@app.get("/user/<uid:int>")              # ① 路径参数带类型 int
async def get_user(request, uid):
    if uid not in USERS:
        return jresp({"error": f"用户 {uid} 不存在"}, 404)
    return jresp(USERS[uid])


@app.get("/users")
async def list_users(request):
    limit = int(request.args.get("limit", "10"))   # ② 查询参数(取到是字符串)
    items = list(USERS.values())[:limit]
    return jresp({"count": len(items), "limit": limit, "items": items})


@app.post("/user")                       # ③ 按方法分发
async def create_user(request):
    new_id = max(USERS) + 1 if USERS else 1
    USERS[new_id] = {"id": new_id, "name": f"用户{new_id}"}
    return jresp({"created": USERS[new_id]}, 201)


@app.put("/user/<uid:int>")
async def update_user(request, uid):
    if uid not in USERS:
        return jresp({"error": f"用户 {uid} 不存在"}, 404)
    USERS[uid]["name"] = "已更新"
    return jresp({"updated": USERS[uid]})


@app.delete("/user/<uid:int>")
async def delete_user(request, uid):
    removed = USERS.pop(uid, None)
    if removed is None:
        return jresp({"error": f"用户 {uid} 不存在"}, 404)
    return jresp({"deleted": removed})


CURL_CASES = [
    {"desc": "路径参数:取 id=1", "path": "/user/1"},
    {"desc": "路径参数:不存在 → 404", "path": "/user/99"},
    {"desc": "查询参数:limit=1", "path": "/users?limit=1"},
    {"desc": "POST 创建", "method": "POST", "path": "/user"},
    {"desc": "PUT 更新", "method": "PUT", "path": "/user/1"},
    {"desc": "DELETE 删除", "method": "DELETE", "path": "/user/2"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        app.run(host="127.0.0.1", port=PORT,
                single_process=True, access_log=False, motd=False)
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
