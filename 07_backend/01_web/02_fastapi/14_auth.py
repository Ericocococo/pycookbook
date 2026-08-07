"""
14_auth.py —— JWT 鉴权：登录获取 token，接口验证 token
================================================================================
所属: 三方库 FastAPI | Python 3.12 | 额外: pip install pyjwt passlib[bcrypt]

运行:
  python 14_auth.py         # 自测
  python 14_auth.py --serve  # 起服务

要点:
  ① OAuth2PasswordBearer —— 声明 token 从哪来（Authorization: Bearer xxx）
  ② jwt.encode / decode —— 生成和验证 JWT token
  ③ Depends(get_current_user) —— 受保护接口自动校验 token
  ④ 完整流程：注册 → 登录拿 token → 带 token 访问接口
================================================================================
"""

import uvicorn
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

PORT = 8034
app = FastAPI()

SECRET_KEY = "demo-secret-key-not-for-production"
USERS_DB: dict[str, dict] = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class UserRegister(BaseModel):
    username: str
    password: str


# ── 注册 ──
@app.post("/register", status_code=201)
async def register(user: UserRegister):
    if user.username in USERS_DB:
        raise HTTPException(status_code=400, detail="用户已存在")
    USERS_DB[user.username] = {"username": user.username, "password": user.password}
    return {"msg": f"{user.username} 注册成功"}


# ── 登录 → 返回 JWT token ──
@app.post("/login")
async def login(user: UserRegister):
    db_user = USERS_DB.get(user.username)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    # ② 生成 JWT token
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# ── ③ 依赖：从 token 里解出当前用户 ──
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """① OAuth2PasswordBearer 自动从 Authorization: Bearer xxx 里取 token。"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None or username not in USERS_DB:
            raise HTTPException(status_code=401, detail="token 无效")
        return USERS_DB[username]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="token 解析失败")


# ── ④ 受保护接口 ──
@app.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """需要 Authorization: Bearer <token> 才能访问。"""
    return {"msg": "已鉴权", "user": user["username"]}


CURL_CASES = [
    {"desc": "注册", "method": "POST", "path": "/register",
     "json": {"username": "admin", "password": "123"}},
    {"desc": "登录 → 拿 token", "method": "POST", "path": "/login",
     "json": {"username": "admin", "password": "123"}},
    {"desc": "无 token → 401", "path": "/me"},
    {"desc": "带 token → 成功", "path": "/me",
     "headers": {"Authorization": "Bearer placeholder"}},
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
