"""
01_hello.py —— FastAPI 最小应用
================================================================================
所属: 三方库 FastAPI 0.1xx | Python 3.12 | 安装: pip install fastapi "uvicorn[standard]"

两种运行方式:
  ① 自测(推荐):python 01_hello.py
     自动起 uvicorn 服务、用真实 curl 打一遍、打印响应、再关掉。
  ② 手动:python 01_hello.py serve,再另开终端:
        curl http://127.0.0.1:8021/            # 纯文本
        curl http://127.0.0.1:8021/json        # JSON
        浏览器打开 http://127.0.0.1:8021/docs   # 自动生成的交互文档(FastAPI 特色)

FastAPI 是异步 ASGI 框架:@app.get 装饰器 + async 函数,返回 dict 自动转 JSON。
ASGI = 异步服务器网关接口,支持 async/await 的 Web 应用与服务器标准接口。
需要 uvicorn 这类 ASGI 服务器来跑。
================================================================================
"""
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

PORT = 8021
app = FastAPI()


@app.get("/", response_class=PlainTextResponse)   # 指定纯文本响应
async def index():
    """返回纯文本。"""
    return "Hello FastAPI"


@app.get("/json")
async def hello_json():
    """返回 JSON:直接 return dict,FastAPI 自动序列化(中文不转义)。"""
    return {"framework": "fastapi", "msg": "你好"}


CURL_CASES = [
    {"desc": "根路由,返回纯文本", "path": "/"},
    {"desc": "返回 JSON", "path": "/json"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # 阻塞启动 ASGI 服务(供手动 curl);log_level 降噪
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
