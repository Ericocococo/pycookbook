"""
03_request_response.py —— FastAPI 请求与响应:JSON body / 状态码 / 响应头
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 03_request_response.py         # 自测:真实 curl 打一遍
  python 03_request_response.py serve   # 起服务,手动 curl:
    curl -X POST http://127.0.0.1:8023/echo \
         -H 'Content-Type: application/json' -d '{"name":"王五","age":18}'
    curl -i http://127.0.0.1:8023/headers

要点:
  ① 参数注解成 dict / Body → 自动解析 JSON 请求体
  ② Header(...) / Request → 读请求头
  ③ Response 形参上设 headers/status_code,或直接返回 JSONResponse → 自定义头和状态码
================================================================================
"""
import sys

import uvicorn
from fastapi import FastAPI, Header, Response
from fastapi.responses import JSONResponse

PORT = 8023
app = FastAPI()


@app.post("/echo")
async def echo(payload: dict):
    """① 参数注解成 dict → FastAPI 自动把请求体 JSON 解析进来。"""
    return {"received": payload, "field_count": len(payload)}


@app.get("/headers")
async def show_headers(response: Response, user_agent: str = Header(default="unknown")):
    """② Header(...) 取请求头 User-Agent;③ 往 response.headers 写自定义响应头。"""
    response.headers["X-Powered-By"] = "fastapi-demo"
    return {"your_user_agent": user_agent}


@app.post("/created")
async def created():
    """③ 直接返回 JSONResponse,自定义状态码 201 + Location 头。"""
    return JSONResponse(
        content={"msg": "资源已创建"},
        status_code=201,
        headers={"Location": "/resource/1"},
    )


CURL_CASES = [
    {"desc": "POST JSON 回显", "method": "POST", "path": "/echo",
     "json": {"name": "王五", "age": 18}},
    {"desc": "读请求头 + 自定义响应头(X-Powered-By)", "show_headers": True,
     "path": "/headers", "headers": {"User-Agent": "curl-demo/1.0"}},
    {"desc": "创建资源:201 + Location 头", "show_headers": True,
     "method": "POST", "path": "/created"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
