"""
Monaco Editor 前端页面服务（模拟后端同事的工作）

职责：
  - 提供 Monaco Editor 前端页面（HTTP）
  - 前端自己连 WebSocket 到 LSP 桥接服务

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/01_http_server.py --serve

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
    parser.add_argument("--port", type=int, default=8080)
    # args = parser.parse_args()
    args = parser.parse_args([
        '--serve',
    ])

    if args.serve:
        print(f"Monaco Editor:  http://{args.host}:{args.port}")
        print("需同时启动 LSP 桥接服务才能使用补全/诊断功能")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        print("Monaco Editor 前端页面服务")
        print()
        print("启动：python 01_http_server.py --serve")
        print("访问：http://127.0.0.1:8080")
