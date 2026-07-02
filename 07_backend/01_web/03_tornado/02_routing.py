"""
02_routing.py —— Tornado 路由:正则路径 / 查询参数 / HTTP 方法
================================================================================
所属: 三方库 Tornado 6.x | Python 3.12

运行:
  python 02_routing.py            # 自测:真实 curl 打一遍
  python 02_routing.py --serve      # 起服务,手动 curl:
    curl http://127.0.0.1:9032/user/1
    curl 'http://127.0.0.1:9032/users?limit=1'
    curl -X POST http://127.0.0.1:9032/user
    curl -X PUT  http://127.0.0.1:9032/user/1
    curl -X DELETE http://127.0.0.1:9032/user/2

要点:
  ① 路由用正则,捕获组 (\d+) 按位置传给 get/post 等方法
  ② get_query_argument 取查询参数(?limit=1)
  ③ 同一 Handler 类里定义 get/post/put/delete,天然按方法分发
================================================================================
"""
import asyncio
import json

import tornado.web

PORT = 9032

USERS = {1: {"id": 1, "name": "张三"}, 2: {"id": 2, "name": "李四"}}


def write_json(handler, obj, status=200):
    """统一写 JSON:设状态码、类型,中文不转义。"""
    handler.set_status(status)
    handler.set_header("Content-Type", "application/json; charset=utf-8")
    handler.write(json.dumps(obj, ensure_ascii=False))


class UserHandler(tornado.web.RequestHandler):
    """对应 /user/(\\d+):捕获组作为 uid 传进来。"""

    def get(self, uid):                       # ① uid 来自正则捕获组,是字符串
        uid = int(uid)
        if uid not in USERS:
            return write_json(self, {"error": f"用户 {uid} 不存在"}, 404)
        write_json(self, USERS[uid])

    def put(self, uid):                       # ③ 按 HTTP 方法分发
        uid = int(uid)
        if uid not in USERS:
            return write_json(self, {"error": f"用户 {uid} 不存在"}, 404)
        USERS[uid]["name"] = "已更新"
        write_json(self, {"updated": USERS[uid]})

    def delete(self, uid):
        removed = USERS.pop(int(uid), None)
        if removed is None:
            return write_json(self, {"error": f"用户 {uid} 不存在"}, 404)
        write_json(self, {"deleted": removed})


class UserCollectionHandler(tornado.web.RequestHandler):
    """对应 /user(无 id):POST 创建。"""

    def post(self):
        new_id = max(USERS) + 1 if USERS else 1
        USERS[new_id] = {"id": new_id, "name": f"用户{new_id}"}
        write_json(self, {"created": USERS[new_id]}, 201)


class UserListHandler(tornado.web.RequestHandler):
    """对应 /users:查询参数 limit。"""

    def get(self):
        limit = int(self.get_query_argument("limit", default="10"))  # ② 查询参数
        items = list(USERS.values())[:limit]
        write_json(self, {"count": len(items), "limit": limit, "items": items})


def make_app():
    return tornado.web.Application([
        (r"/user/(\d+)", UserHandler),        # 捕获组 → 方法参数
        (r"/user", UserCollectionHandler),
        (r"/users", UserListHandler),
    ])


async def main():
    make_app().listen(PORT, address="127.0.0.1")
    await asyncio.Event().wait()


CURL_CASES = [
    {"desc": "路径参数:取 id=1", "path": "/user/1"},
    {"desc": "路径参数:不存在 → 404", "path": "/user/99"},
    {"desc": "查询参数:limit=1", "path": "/users?limit=1"},
    {"desc": "POST 创建", "method": "POST", "path": "/user"},
    {"desc": "PUT 更新", "method": "PUT", "path": "/user/1"},
    {"desc": "DELETE 删除", "method": "DELETE", "path": "/user/2"},
]


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        asyncio.run(main())
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
