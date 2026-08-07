"""15_lifespan.py 的 requests 客户端。先启动: python 15_lifespan.py --serve"""

from _utils import get

BASE = "http://127.0.0.1:8035"

get(f"{BASE}/")
get(f"{BASE}/health")
