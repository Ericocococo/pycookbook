"""
17_deploy.py —— 生产部署配置
================================================================================
所属: 三方库 FastAPI + uvicorn | Python 3.12

运行:
  python 17_deploy.py         # 展示各种部署配置
  python 17_deploy.py --serve  # 用生产配置启动

要点:
  ① uvicorn 生产参数 —— workers / host / port / log-level / access-log
  ② Gunicorn + Uvicorn —— 多进程部署（Linux）
  ③ Docker 部署 —— Dockerfile 示例
  ④ HTTPS —— 证书配置
================================================================================
"""

import uvicorn
from fastapi import FastAPI

PORT = 8037
app = FastAPI(
    title="生产级 API",
    version="1.0.0",
    docs_url="/docs",       # Swagger 文档地址（生产可设 None 关闭）
    redoc_url="/redoc",     # ReDoc 文档地址
)


@app.get("/")
async def root():
    return {"status": "running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查端点（负载均衡器探活用）。"""
    return {"status": "ok"}


if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true")
    args = _ap.parse_args()

    if args.serve:
        # ── ① uvicorn 生产参数 ──
        uvicorn.run(
            "17_deploy:app",     # 字符串形式，支持 reload 和 workers
            host="0.0.0.0",      # 监听所有网卡（不只 127.0.0.1）
            port=PORT,
            workers=2,           # 多进程（Linux 上用，Windows 不支持）
            log_level="info",
            access_log=True,     # 记录每个请求
        )
    else:
        print("=" * 60)
        print("FastAPI 生产部署配置速查")
        print("=" * 60)

        print("""
── ① uvicorn 命令行启动（开发） ──
  uvicorn 17_deploy:app --reload --host 127.0.0.1 --port 8037

── ② uvicorn 生产启动 ──
  uvicorn 17_deploy:app --host 0.0.0.0 --port 8000 --workers 4

── ③ Gunicorn + Uvicorn（Linux 多进程，推荐） ──
  pip install gunicorn
  gunicorn 17_deploy:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

── ④ Docker 部署 ──
  # Dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["uvicorn", "17_deploy:app", "--host", "0.0.0.0", "--port", "8000"]

  # 构建 & 运行
  docker build -t myapi .
  docker run -p 8000:8000 myapi

── ⑤ HTTPS（证书） ──
  uvicorn 17_deploy:app --ssl-keyfile key.pem --ssl-certfile cert.pem

── ⑥ 生产 checklist ──
  □ docs_url=None（关闭 Swagger 文档）
  □ CORS 只允许特定域名
  □ 环境变量管理 SECRET_KEY 等敏感信息
  □ 健康检查端点 /health
  □ 日志配置（文件 + 轮转）
  □ 限流 / 防刷（slowapi 或 Nginx）
""")
