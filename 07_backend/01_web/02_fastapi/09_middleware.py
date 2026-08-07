"""
09_middleware.py —— 中间件：CORS、请求计时、日志
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 09_middleware.py         # 自测
  python 09_middleware.py --serve  # 起服务

要点:
  ① CORSMiddleware —— 跨域资源共享，前端 JS 跨域请求必须配
  ② @app.middleware("http") —— 自定义中间件：在请求前后插入逻辑
  ③ 请求计时 —— 中间件计算耗时，写到响应头 X-Process-Time

  中间件执行顺序（洋葱模型）：
    请求进来 → middleware_1(前) → middleware_2(前) → 路由处理
    响应出去 ← middleware_1(后) ← middleware_2(后) ← 路由返回
================================================================================
"""

import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

PORT = 8029
app = FastAPI()

# ── ① CORS 中间件：允许前端跨域请求 ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许的来源（生产环境不要用 *）
    allow_methods=["*"],       # 允许的 HTTP 方法
    allow_headers=["*"],       # 允许的请求头
)


# ── ② 自定义中间件：请求计时 ──
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """
    每个请求都经过这里。
    call_next(request) = 继续执行后面的中间件和路由处理函数。
    """
    start = time.perf_counter()
    response = await call_next(request)  # 继续执行，拿到响应
    elapsed = time.perf_counter() - start
    # ③ 把耗时写到响应头
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    print(f"[中间件] {request.method} {request.url.path} → {elapsed:.4f}s")
    return response


@app.get("/")
async def root():
    return {"msg": "看响应头里的 X-Process-Time"}


@app.get("/slow")
async def slow():
    """模拟慢请求。"""
    import asyncio
    await asyncio.sleep(0.5)
    return {"msg": "慢请求完成"}


CURL_CASES = [
    {"desc": "普通请求 → 看 X-Process-Time 响应头", "path": "/", "show_headers": True},
    {"desc": "慢请求 → X-Process-Time ≈ 0.5s", "path": "/slow", "show_headers": True},
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
