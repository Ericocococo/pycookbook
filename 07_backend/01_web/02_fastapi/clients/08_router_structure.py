"""08_router_structure.py 的 requests 客户端。先启动: python 08_router_structure.py --serve"""

from _utils import get

BASE = "http://127.0.0.1:8028"

get(f"{BASE}/")
get(f"{BASE}/api/users/")
get(f"{BASE}/api/users/1")
get(f"{BASE}/api/items/")
