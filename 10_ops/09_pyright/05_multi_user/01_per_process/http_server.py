"""
Monaco Editor 前端页面服务（三个阶段共用）

运行方式（在项目根目录）：
  python 10_ops/09_pyright/05_multi_user/http_server.py --serve

访问：
  http://127.0.0.1:8080?ws=ws://127.0.0.1:3001/lsp   → 阶段1
  http://127.0.0.1:8080?ws=ws://127.0.0.1:3002/lsp   → 阶段2
  http://127.0.0.1:8080?ws=ws://127.0.0.1:3003/lsp   → 阶段3

依赖：
  pip install fastapi uvicorn
"""

import argparse
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Monaco Editor Frontend")


@app.get("/")
async def index():
    """返回 Monaco Editor 前端页面"""
    return FileResponse(_DIR / "templates" / "index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monaco Editor 前端页面服务")
    parser.add_argument("--serve", action="store_true", help="启动服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args(["--serve"])

    if args.serve:
        print(f"Monaco Editor:  http://{args.host}:{args.port}")
        print("URL 参数 ?ws=ws://127.0.0.1:3001/lsp 选择桥接服务")
        uvicorn.run(app, host=args.host, port=args.port)
