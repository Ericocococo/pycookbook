"""03_request_response.py 的 requests 客户端。先启动: python 03_request_response.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8023"

post(f"{BASE}/echo", json={"name": "王五", "age": 18})
get(f"{BASE}/headers", headers={"User-Agent": "demo/1.0"}, show_headers=True)
post(f"{BASE}/created", show_headers=True)
