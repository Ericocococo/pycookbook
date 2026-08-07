"""
08_router_structure.py —— APIRouter：多文件拆分路由
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 08_router_structure.py         # 自测
  python 08_router_structure.py --serve  # 起服务

要点:
  ① APIRouter —— 子路由器，和 app 用法一样，但可以在单独文件里定义
  ② prefix —— 给一组路由加统一前缀（如 /api/users）
  ③ tags —— 给一组路由加标签，/docs 文档里分组显示
  ④ app.include_router() —— 把子路由器挂载到主 app

  实际项目结构（本文件把多文件浓缩在一个文件里演示）：
    app/
    ├── main.py          # app = FastAPI() + include_router
    ├── routers/
    │   ├── users.py     # user_router = APIRouter(prefix="/api/users")
    │   └── items.py     # item_router = APIRouter(prefix="/api/items")
================================================================================
"""

import uvicorn
from fastapi import APIRouter, FastAPI

PORT = 8028
app = FastAPI()

# ── ① 用户子路由器（实际项目放在 routers/users.py） ──
user_router = APIRouter(
    prefix="/api/users",  # ② 统一前缀
    tags=["用户管理"],      # ③ /docs 里的分组名
)

USERS = {1: {"id": 1, "name": "张三"}, 2: {"id": 2, "name": "李四"}}


@user_router.get("/")
async def list_users():
    """实际路径: GET /api/users/"""
    return list(USERS.values())


@user_router.get("/{uid}")
async def get_user(uid: int):
    """实际路径: GET /api/users/1"""
    return USERS.get(uid, {"error": "not found"})


# ── 商品子路由器（实际项目放在 routers/items.py） ──
item_router = APIRouter(prefix="/api/items", tags=["商品管理"])

ITEMS = [{"id": 1, "name": "手机", "price": 999}, {"id": 2, "name": "耳机", "price": 99}]


@item_router.get("/")
async def list_items():
    return ITEMS


# ── ④ 挂载到主 app ──
app.include_router(user_router)
app.include_router(item_router)


@app.get("/")
async def root():
    """主 app 的根路由，不受任何 prefix 影响。"""
    return {"msg": "首页", "api_docs": "/docs"}


CURL_CASES = [
    {"desc": "首页", "path": "/"},
    {"desc": "用户列表（prefix=/api/users）", "path": "/api/users/"},
    {"desc": "单个用户", "path": "/api/users/1"},
    {"desc": "商品列表（prefix=/api/items）", "path": "/api/items/"},
]

if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest

        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
