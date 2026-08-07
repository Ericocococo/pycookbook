"""
05_response_model.py —— 响应模型：控制返回字段、自动文档
================================================================================
所属: 三方库 FastAPI + Pydantic 2 | Python 3.12

运行:
  python 05_response_model.py         # 自测
  python 05_response_model.py --serve  # 起服务，手动 curl:
    curl http://127.0.0.1:8025/user/1
    curl http://127.0.0.1:8025/users

要点:
  ① response_model —— 控制返回哪些字段（过滤掉密码等敏感信息）
  ② 输入模型 vs 输出模型 —— 同一个实体，创建时要密码，返回时不要
  ③ response_model_exclude_unset —— 只返回实际设置过的字段
================================================================================
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PORT = 8025
app = FastAPI()


# ── 输入模型：创建用户时需要密码 ──
class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0, le=150)
    password: str


# ── 输出模型：返回时过滤掉密码 ──
class UserOut(BaseModel):
    id: int
    name: str
    age: int


USERS_DB: dict[int, dict] = {
    1: {"id": 1, "name": "张三", "age": 25, "password": "secret123"},
    2: {"id": 2, "name": "李四", "age": 30, "password": "pass456"},
}


@app.get("/user/{uid}", response_model=UserOut)
async def get_user(uid: int):
    """① response_model=UserOut → 即使内部数据有 password，返回时自动过滤掉。"""
    if uid not in USERS_DB:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    return USERS_DB[uid]


@app.get("/users", response_model=list[UserOut])
async def list_users():
    """② response_model=list[UserOut] → 列表里每项都过滤。"""
    return list(USERS_DB.values())


@app.post("/user", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate):
    """③ 输入用 UserCreate（含密码），输出用 UserOut（不含密码）。"""
    new_id = max(USERS_DB) + 1 if USERS_DB else 1
    record = {"id": new_id, **user.model_dump()}
    USERS_DB[new_id] = record
    return record


CURL_CASES = [
    {"desc": "取用户 → 有 id/name/age，无 password", "path": "/user/1"},
    {"desc": "用户列表 → 每项都无 password", "path": "/users"},
    {"desc": "创建用户 → 输入带密码，输出不带", "method": "POST", "path": "/user",
     "json": {"name": "王五", "age": 20, "password": "mypass"}},
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
