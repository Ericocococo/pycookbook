"""
02_routing.py —— FastAPI 路由:路径参数 / 查询参数 / HTTP 方法
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 02_routing.py            # 自测:真实 curl 打一遍
  python 02_routing.py serve      # 起服务,手动 curl:
    curl http://127.0.0.1:8022/user/1
    curl 'http://127.0.0.1:8022/users?limit=1'
    curl -X POST http://127.0.0.1:8022/user
    curl -X PUT  http://127.0.0.1:8022/user/1
    curl -X DELETE http://127.0.0.1:8022/user/2

要点(FastAPI 靠**类型注解**决定参数来源和转换):
  ① 函数参数名出现在路径 {uid} 里 + 注解 int  → 路径参数,自动转 int
  ② 函数参数不在路径里 + 有默认值             → 查询参数(?limit=1)
  ③ @app.get/post/put/delete                → 按 HTTP 方法分发
================================================================================
"""
import sys

import uvicorn
from fastapi import FastAPI, HTTPException

PORT = 8022
app = FastAPI()

USERS = {1: {"id": 1, "name": "张三"}, 2: {"id": 2, "name": "李四"}}


@app.get("/user/{uid}")                # ① {uid} + 注解 int → 路径参数
async def get_user(uid: int):
    if uid not in USERS:
        # HTTPException 会被 FastAPI 转成对应状态码的 JSON
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    return USERS[uid]


@app.get("/users")
async def list_users(limit: int = 10):  # ② limit 不在路径 + 有默认值 → 查询参数
    items = list(USERS.values())[:limit]
    return {"count": len(items), "limit": limit, "items": items}


@app.post("/user", status_code=201)     # ③ POST,并指定成功状态码 201
async def create_user():
    new_id = max(USERS) + 1 if USERS else 1
    USERS[new_id] = {"id": new_id, "name": f"用户{new_id}"}
    return {"created": USERS[new_id]}


@app.put("/user/{uid}")
async def update_user(uid: int):
    if uid not in USERS:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    USERS[uid]["name"] = "已更新"
    return {"updated": USERS[uid]}


@app.delete("/user/{uid}")
async def delete_user(uid: int):
    removed = USERS.pop(uid, None)
    if removed is None:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    return {"deleted": removed}


CURL_CASES = [
    {"desc": "路径参数:取 id=1", "path": "/user/1"},
    {"desc": "路径参数:不存在 → 404", "path": "/user/99"},
    {"desc": "查询参数:limit=1", "path": "/users?limit=1"},
    {"desc": "路径参数类型错误(abc 非 int)→ 422 自动校验", "path": "/user/abc"},
    {"desc": "POST 创建", "method": "POST", "path": "/user"},
    {"desc": "PUT 更新", "method": "PUT", "path": "/user/1"},
    {"desc": "DELETE 删除", "method": "DELETE", "path": "/user/2"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
