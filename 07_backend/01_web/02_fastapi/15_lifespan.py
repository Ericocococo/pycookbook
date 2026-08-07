"""
15_lifespan.py —— 生命周期事件：启动初始化 / 关闭清理
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 15_lifespan.py         # 自测
  python 15_lifespan.py --serve  # 起服务（看控制台的启动/关闭日志）

要点:
  ① @asynccontextmanager + lifespan —— FastAPI 推荐的生命周期管理方式
  ② yield 之前 = 启动时执行（初始化数据库连接池、加载模型等）
  ③ yield 之后 = 关闭时执行（释放连接、保存状态等）
  ④ 旧写法 @app.on_event("startup") 已弃用，用 lifespan 替代
================================================================================
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

PORT = 8035


# ── ① lifespan：启动和关闭时的钩子 ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    yield 前 = 服务启动时执行（类比 Python 的 __enter__）
    yield 后 = 服务关闭时执行（类比 Python 的 __exit__）
    """
    # ② 启动时：初始化资源
    print("[lifespan] 服务启动：初始化数据库连接池...")
    app.state.db_pool = {"status": "connected", "max_connections": 10}
    print("[lifespan] 服务启动：加载 ML 模型...")
    app.state.model = {"name": "demo-model", "version": "1.0"}

    yield  # ← 服务运行中...

    # ③ 关闭时：释放资源
    print("[lifespan] 服务关闭：释放数据库连接池...")
    app.state.db_pool = None
    print("[lifespan] 服务关闭：卸载模型...")
    app.state.model = None


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "db_pool": app.state.db_pool,
        "model": app.state.model,
    }


@app.get("/health")
async def health():
    """健康检查：确认资源已初始化。"""
    return {"status": "ok", "db": app.state.db_pool is not None}


CURL_CASES = [
    {"desc": "查看启动时初始化的资源", "path": "/"},
    {"desc": "健康检查", "path": "/health"},
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
