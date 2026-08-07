"""09_middleware.py 的 requests 客户端。先启动: python 09_middleware.py --serve"""

from _utils import get

BASE = "http://127.0.0.1:8029"

get(f"{BASE}/", show_headers=True)
get(f"{BASE}/slow", show_headers=True)
