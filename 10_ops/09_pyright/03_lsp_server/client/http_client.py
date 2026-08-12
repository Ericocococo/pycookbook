"""
HTTP 客户端 —— 用 requests 访问 01_http_server.py 和 FastAPI 服务

掌握：
  - 用 requests 调用同事的 HTTP 页面服务和健康检查
  - 用 requests 调用 FastAPI 方案的 /health 端点（websockets 方案无 HTTP 端点）

运行方式（在项目根目录）：
  python 10_ops/09_pyright/04_monaco_lsp/client/http_client.py

依赖：
  pip install requests
"""

import json
import requests

BASE_URL = "http://127.0.0.1:{port}"


def call_http_server():
    """调用 01_http_server.py（端口 8080）"""
    url = BASE_URL.format(port=8080)

    resp = requests.get(url)
    print(f"状态码: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    print(f"页面长度: {len(resp.text)} 字符")
    print(f"前 60 个字符: {resp.text[:60]}...")


def call_fastapi_health():
    """调用 03_lsp_bridge_fastapi.py 的 /health（端口 3002）"""
    url = BASE_URL.format(port=3002) + "/health"

    resp = requests.get(url)
    data = resp.json()
    print(f"状态码: {resp.status_code}")
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")


def call_fastapi_docs():
    """调用 FastAPI 自动文档页面"""
    url = BASE_URL.format(port=3002) + "/docs"

    resp = requests.get(url)
    print(f"状态码: {resp.status_code}")
    print(f"页面长度: {len(resp.text)} 字符")


if __name__ == "__main__":
    print("=" * 40)
    print("① 同事的页面服务 (8080)")
    print("=" * 40)
    try:
        call_http_server()
    except requests.ConnectionError:
        print("⚠ 连接失败，请先启动 01_http_server.py --serve")

    print("\n" + "=" * 40)
    print("② FastAPI 健康检查 (3002)")
    print("=" * 40)
    try:
        call_fastapi_health()
    except requests.ConnectionError:
        print("⚠ 连接失败，请先启动 03_lsp_bridge_fastapi.py --serve")

    print("\n" + "=" * 40)
    print("③ FastAPI 自动文档 (/docs)")
    print("=" * 40)
    try:
        call_fastapi_docs()
    except requests.ConnectionError:
        print("⚠ 连接失败")
