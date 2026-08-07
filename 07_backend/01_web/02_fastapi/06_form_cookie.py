"""
06_form_cookie.py —— 表单提交 + Cookie 读写
================================================================================
所属: 三方库 FastAPI | Python 3.12 | 额外: pip install python-multipart

运行:
  python 06_form_cookie.py         # 自测
  python 06_form_cookie.py --serve  # 起服务，手动 curl:
    curl -X POST http://127.0.0.1:8026/login -d 'username=admin&password=123'
    curl http://127.0.0.1:8026/me -b 'session_id=abc123'

要点:
  ① Form(...) —— 接收表单字段（application/x-www-form-urlencoded）
  ② Cookie(...) —— 读取请求中的 Cookie
  ③ response.set_cookie() —— 写 Cookie 到响应（浏览器会自动保存）
================================================================================
"""

import uvicorn
from fastapi import Cookie, FastAPI, Form
from fastapi.responses import JSONResponse

PORT = 8026
app = FastAPI()

SESSIONS: dict[str, str] = {}


@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    """① Form() 接收表单字段（不是 JSON，是 key=value 格式）。"""
    if username == "admin" and password == "123":
        session_id = "abc123"
        SESSIONS[session_id] = username
        response = JSONResponse({"msg": "登录成功", "user": username})
        # ③ set_cookie：写 Cookie 到响应
        response.set_cookie(key="session_id", value=session_id)
        return response
    return JSONResponse({"msg": "用户名或密码错误"}, status_code=401)


@app.get("/me")
async def me(session_id: str = Cookie(default=None)):
    """② Cookie() 读取请求中的 Cookie。"""
    if session_id and session_id in SESSIONS:
        return {"user": SESSIONS[session_id], "session_id": session_id}
    return JSONResponse({"msg": "未登录"}, status_code=401)


CURL_CASES = [
    {"desc": "表单登录（Form 字段，非 JSON）", "method": "POST", "path": "/login",
     "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "raw_data": "username=admin&password=123"},
    {"desc": "带 Cookie 访问（模拟已登录）", "path": "/me",
     "headers": {"Cookie": "session_id=abc123"}},
    {"desc": "无 Cookie → 401", "path": "/me"},
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
